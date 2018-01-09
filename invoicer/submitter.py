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

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '08-JAN-2018'


# Globals #####################################################################
def sendmail(
    sender, to, subject, body, server, body_type="html",
    attachments=None, username=None, password=None, cc=None, starttls=False,
    encode_body=True
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
    '''
    attachments = [] if attachments is None else attachments

    s = smtplib.SMTP(server)

    if starttls:
        s.starttls()

    if username and password:
        s.login(username, password)

    outer = MIMEMultipart()
    outer['Subject'] = subject
    outer['From'] = sender
    outer['To'] = ', '.join(to)

    if cc:
        outer['Cc'] = ', '.join(cc)
    else:
        cc = []

    if encode_body:
        msg = MIMEBase('text', body_type, _charset='utf-8')
        msg.set_payload(body.encode('utf-8'))
        encoders.encode_base64(msg)
    else:
        msg = MIMEText(body.encode('utf-8'), body_type, 'utf-8')

    outer.attach(msg)

    for path in attachments:
        if not os.path.isfile(path):
            continue

        ctype, encoding = mimetypes.guess_type(path)

        if (ctype is None) or (encoding is not None):
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic type.
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)

        if maintype == 'text':
            msg = MIMEText(open(path).read(), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(open(path, 'rb').read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(open(path, 'rb').read())
            encoders.encode_base64(msg)

        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
        outer.attach(msg)

    s.sendmail(sender, to + cc, outer.as_string())
    s.quit()
