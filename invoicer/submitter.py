#!/usr/bin/env python2.7
# coding: utf-8
'''
This module is used to send emails.
'''

# Imports #####################################################################
import os
import smtplib
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '08-JAN-2018'


# Globals #####################################################################
def sendmail(
    sender, to, subject, server, text_body=None, html_body=None,
    attachments=None, username=None, password=None, cc=None, starttls=False,
    encode_body=True,
    stream_attachments=None
):
    '''Send an email message using the specified mail server using Python's
    standard `smtplib` library and some extras (e.g. attachments).
    NOTE: This function has not been tested with authentication.  It
    was written for a mail server that already does sender/recipient validation.
    WARNING: This is a non-streaming message system.  You should not send large
    files with this function!
    :param str sender: The email address of the 'person' sending the email
    :param list(str) to: One or more email addresses to send the message to
    :param str subject: The subject of the message
    :param str body: The body of the message
    :param str server: The email server to use to send the message
    :param str body_type: The type of the message body (e.g. "plain", "html")
    :param list(str) attachments: Any attachments you want to send with the
        email.  This should be a list of absolute paths of the files.
    :param str username: The username used to log in to the SMTP server
    :param str password: The password used to log in to the SMTP server
    :param list(str) cc: One or more email addresses to CC the message
    :param bool starttls: Whether or not to call `starttls` on the SMTP server
        object.
    :param bool encode_body: Whether or not to base64 encode the message body
    :param list stream_attachments: This is a list of tuples that will be
        attached in the form of ``[(filename, handle)]``.  The filename will be
        used to figure out the MIMEType and used as the attachment name.
        ``handle`` must be a file-like object that responds to ``.read()`` that
        will be used to obtain the attachment data.

    stream attachments
    ==================

    The most common way of using the stream attachments is by using the
    ``StringIO`` object.  For exmaple:

        >>> from cStringIO import StringIO
        >>> x = StringIO()
        >>> x.write('Hello, World!\n')
        >>> x.seek(0)
        >>> sendmail(stream_attachments=[('readme.txt', x)])
    '''
    def get_message(content, body_type, encode=True):
        if encode_body:
            msg = MIMEBase('text', body_type, _charset='utf-8')
            msg.set_payload(content.encode('utf-8'))
            encoders.encode_base64(msg)
            return msg
        else:
            return MIMEText(content.encode('utf-8'), body_type, 'utf-8')

    attachments = [] if attachments is None else attachments
    stream_attachments = [] if stream_attachments is None else stream_attachments

    s = smtplib.SMTP(server)

    if starttls:
        s.starttls()

    if username and password:
        s.login(username, password)

    if text_body and html_body:
        outer = MIMEMultipart('alternative')
    else:
        outer = MIMEMultipart()

    outer['Subject'] = subject
    outer['From'] = sender
    outer['To'] = ', '.join(to)

    if cc:
        outer['Cc'] = ', '.join(cc)
    else:
        cc = []

    if text_body and html_body:
        text_msg = get_message(text_body, 'plain', encode=encode_body)
        html_msg = get_message(html_body, 'html', encode=encode_body)
        outer.attach(text_msg)
        outer.attach(html_msg)
    elif html_body:
        html_msg = get_message(html_body, 'html', encode=encode_body)
        outer.attach(html_msg)
    elif text_body:
        text_msg = get_message(text_body, 'plain', encode=False)
        outer.attach(text_msg)

    # Take care of the stream attachments.  In this case, stream_attachments
    # must be a list of tuples in the form of [(filename, stream)].
    for filename, stream in stream_attachments:
        ctype, encoding = mimetypes.guess_type(filename)

        maintype, subtype = ctype.split('/', 1)

        if maintype == 'text':
            msg = MIMEText(stream.read(), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(stream.read(), _subtype=subtype)
        elif maintype == 'application':
            msg = MIMEApplication(stream.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(stream.read())
            encoders.encode_base64(msg)

        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(msg)

    # Normal attachments are files already on the file system.
    for path in attachments:
        if not os.path.isfile(path):
            continue

        ctype, encoding = mimetypes.guess_type(path)

        if (ctype is None) or (encoding is not None):
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic type.
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)

        with open(path, 'rb') as stream:
            if maintype == 'text':
                msg = MIMEText(stream.read(), _subtype=subtype)
            elif maintype == 'image':
                msg = MIMEImage(stream.read(), _subtype=subtype)
            elif maintype == 'application':
                msg = MIMEApplication(stream.read(), _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(stream.read())
                encoders.encode_base64(msg)

        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
        outer.attach(msg)

    s.sendmail(sender, to + cc, outer.as_string())
    s.quit()
