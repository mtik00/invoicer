import os
import re
from cStringIO import StringIO

import pdfkit
from pdfkit.configuration import Configuration
import arrow
from flask import (
    Blueprint, request, redirect, url_for, render_template, flash, current_app,
    Response, session)
from premailer import Premailer

from ..forms import EmptyForm
from ..submitter import sendmail
from ..database import db
from ..models import (
    Item, Invoice, Customer, UnitPrice, InvoicePaidDate, User, W3Theme)
from ..common import login_required, color_themes
from .forms import InvoiceForm, ItemForm


invoice_page = Blueprint('invoice_page', __name__, template_folder='templates')


def pdf_ok():
    return bool(
        os.path.exists(current_app.config.get('WKHTMLTOPDF') or '') and
        os.access(current_app.config['WKHTMLTOPDF'], os.R_OK)
    )


def can_submit(customer_id):
    """
    Returns `True` if we can submit an invoice by email to a customer, `False`
    otherwise.
    """
    if not (
        current_app.config.get('EMAIL_PASSWORD') and
        current_app.config.get('EMAIL_USERNAME') and
        current_app.config.get('EMAIL_SERVER')
    ):
        return False

    customer = Customer.query.filter(Customer.id == customer_id).first()
    if not (customer and customer.email):
        return False

    return True


def format_my_address(html=True):
    address = User.query.get(session['user_id']).profile
    join_with = '<br>' if html else '\n'

    result = join_with.join([
        address.full_name,
        address.street,
        '%s %s, %s' % (address.city, address.state, address.zip)]).upper()

    if address.email and html:
        # Prevent gmail from making this a link
        result += join_with + "<a rel='nofollow' style='text-decoration:none; color:#fff' href='#'>" + address.email + "</a>"
    elif address.email:
        result += join_with + address.email

    return result


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/items/delete', methods=["GET", "POST"])
@login_required
def delete_items(invoice_number):
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    items = Item.query.filter(Item.invoice_id == invoice.id)
    form = EmptyForm()

    if form.validate_on_submit():
        if request.form.get('validate_delete', '').lower() != 'delete':
            flash('Invalid delete request', 'error')
            return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

        item_ids_to_delete = [y for x, y in request.form.items() if x.startswith('item_')]
        items = Item.query.filter(Item.id.in_(item_ids_to_delete)).all()
        if not items:
            return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

        for item in items:
            db.session.delete(item)

        # Recalculate the invoice total
        items = Item.query.filter(Item.invoice_id == invoice.id).all()
        item_total = sum([x.quantity * x.unit_price for x in items])
        Invoice.query.filter(Invoice.id == invoice.id).update({'total': item_total})
        db.session.commit()

        flash('Item(s) deleted from %s' % invoice.number, 'success')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    return render_template('invoice/delete_items_form.html', form=form, items=items, invoice=invoice)


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/items/create', methods=["GET", "POST"])
@login_required
def create_item(invoice_number):
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    form = ItemForm(quantity=1)
    unit_prices = UnitPrice.query.filter_by(user_id=session['user_id']).all()

    if form.validate_on_submit():
        unit_price = float(request.form['unit_pricex'])
        units = request.form['unit_price_units']

        date = arrow.now()
        if form.date.data:
            date = arrow.get(form.date.data, 'DD-MMM-YYYY')

        item = Item(
            invoice_id=invoice.id,
            date=date,
            description=form.description.data,
            unit_price=unit_price,
            quantity=form.quantity.data,
            units=units,
            customer=invoice.customer
        )

        invoice.items.append(item)
        db.session.add_all([invoice, item])
        db.session.commit()

        flash('item added to invoice %s' % invoice.number, 'success')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    return render_template(
        'invoice/item_form.html',
        form=form,
        invoice=invoice,
        unit_price_objects=unit_prices,
    )


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/update', methods=["GET", "POST"])
@login_required
def update(invoice_number):
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()

    customers = Customer.query.filter_by(user_id=session['user_id']).all()
    addr_choices = [(x.id, x.name1) for x in customers]
    theme_choices = [(x, x) for x in color_themes]

    form = InvoiceForm(
        description=invoice.description,
        submitted_date=invoice.submitted_date.format('DD-MMM-YYYY').upper() if invoice.submitted_date else None,
        paid_date=invoice.paid_date.paid_date.format('DD-MMM-YYYY').upper() if invoice.paid_date else '',
        paid_date_notes=invoice.paid_date.description if invoice.paid_date else '',
        terms=invoice.terms,
    )
    form.customer.choices = addr_choices
    form.w3_theme.choices = theme_choices

    if request.method == 'GET':
        # Set the default them only for `GET` or the value will never change.
        form.customer.process_data(invoice.customer_id)
        form.w3_theme.process_data(invoice.w3_theme)
    elif form.validate_on_submit():
        if 'cancel' in request.form:
            flash('invoice updated canceled', 'warning')
        else:
            submitted_date = invoice.submitted_date
            if form.submitted_date.data:
                submitted_date = arrow.get(form.submitted_date.data, 'DD-MMM-YYYY')

            paid_date = None
            if form.paid_date.data:
                paid_date = InvoicePaidDate(
                    paid_date=arrow.get(form.paid_date.data, 'DD-MMM-YYYY'),
                    description=form.paid_date_notes.data
                )
                db.session.flush()

            terms = invoice.terms
            if form.terms.data:
                terms = form.terms.data

            invoice.description = form.description.data
            invoice.customer_id = form.customer.data
            invoice.submitted_date = submitted_date
            invoice.paid_date = paid_date
            invoice.terms = terms
            invoice.w3_theme = W3Theme.query.filter_by(theme=form.w3_theme.data).first()

            db.session.commit()

            flash('invoice updated', 'success')

        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    return render_template('invoice/invoice_form.html', form=form, invoice=invoice)


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>')
@login_required
def invoice_by_number(invoice_number):
    form = EmptyForm(request.form)
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    if not invoice:
        flash('Unknown invoice', 'error')
        return redirect(url_for('index'))

    # Figure out next/previous
    invoice_numbers = [x.number for x in Invoice.query.all()]
    if not invoice_numbers:
        current_pos = next_id = previous_id = 0
        to_emails = None
    else:
        to_emails = ', '.join(get_address_emails(invoice.customer_id))
        current_pos = invoice_numbers.index(invoice_number)
        if current_pos == len(invoice_numbers) - 1:
            next_id = None
        else:
            next_id = invoice_numbers[current_pos + 1]

        if current_pos == 0:
            previous_id = None
        else:
            previous_id = invoice_numbers[current_pos - 1]

    return render_template(
        'invoice/invoices.html',
        form=form,
        invoice=invoice,
        next_id=next_id,
        previous_id=previous_id,
        invoice_obj=invoice,
        to_emails=to_emails,
        can_submit=to_emails and invoice and can_submit(invoice.customer_id),
        pdf_ok=pdf_ok(),  # The binary exists
        show_pdf_button=User.query.get(session['user_id']).profile.enable_pdf,
    )


@invoice_page.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = InvoiceForm(request.form)
    customers = Customer.query.filter_by(user_id=session['user_id']).all()

    if not customers:
        flash('You must add at least 1 customer before creating invoices', 'error')
        return redirect(url_for('customers_page.create'))

    addr_choices = [(x.id, x.name1) for x in customers]
    form.customer.choices = addr_choices
    form.w3_theme.choices = [(x, x) for x in color_themes]
    me = User.query.get(session['user_id']).profile

    if form.validate_on_submit():
        customer_id = int(request.form['customer'])
        number = next_invoice_number(customer_id)
        customer = Customer.query.filter_by(id=customer_id, user_id=session['user_id']).first_or_404()

        submitted_date = None
        if form.submitted_date.data:
            submitted_date = arrow.get(form.submitted_date.data, 'DD-MMM-YYYY')

        terms = customer.terms or me.terms

        paid_date = None
        if form.paid_date.data:
            paid_date = InvoicePaidDate(
                paid_date=arrow.get(form.paid_date.data, 'DD-MMM-YYYY'),
                description=form.paid_date_notes.data
            )

        db.session.add(
            Invoice(
                description=form.description.data,
                customer_id=customer_id,
                number=number,
                terms=terms,
                submitted_date=submitted_date,
                paid_date=paid_date,
                user=User.query.get(session['user_id'])
            )
        )
        db.session.commit()

        flash('invoice added', 'success')
        return redirect(url_for('invoice_page.last_invoice'))

    return render_template('invoice/invoice_form.html', form=form)


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/delete', methods=['POST'])
@login_required
def delete(invoice_number):
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    form = EmptyForm(request.form)

    if request.form.get('validate_delete', '').lower() != 'delete':
        flash('Invalid delete request', 'error')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    if form.validate_on_submit():
        items = Item.query.filter_by(invoice_id=invoice.id).all()

        if invoice.paid_date:
            pd = InvoicePaidDate.query.get(invoice.paid_date.id)
            db.session.delete(pd)

        db.session.delete(invoice)

        for item in items:
            db.session.delete(item)

        db.session.commit()
        flash('Invoice %s has been deleted' % invoice_number, 'warning')
        return redirect(url_for('invoice_page.last_invoice'))
    else:
        flash('Error occurred when attempting to delete form', 'error')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice_number))


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/pdf')
@login_required
def to_pdf(invoice_number):
    if not pdf_ok():
        flash('PDF configuration not supported', 'error')
        return redirect(url_for('.invoice_by_number', invoice_number=invoice_by_number))

    text = raw_invoice(invoice_number)
    config = Configuration(current_app.config['WKHTMLTOPDF'])
    options = {
        'print-media-type': None,
        'page-size': 'letter',
        'no-outline': None,
        'quiet': None
    }

    return Response(
        pdfkit.from_string(text, False, options=options, configuration=config),
        mimetype='application/pdf'
    )


def get_address_emails(customer_id):
    if (session['user_debug'] or current_app.config['DEBUG']) and ('EMAIL_USERNAME' in current_app.config):
        return [current_app.config['EMAIL_USERNAME'] or '']

    email = Customer.query.get(customer_id).email

    if '|' in email:
        name, domain = email.split('@')
        return ['%s@%s' % (x, domain) for x in name.split('|')]

    return [email]


@login_required
def mark_invoice_submitted(invoice_number):
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()

    # Only update the submitted date if the invoice didn't have one in the
    # first place.  We want the user to be able to re-submit invoices to remind
    # customers of overdue conditions.
    if not invoice.submitted_date:
        invoice.submitted_date = arrow.now()
        db.session.add(invoice)
        db.session.commit()

        flash('Invoice has been marked as submitted; due on %s' % invoice.due_date.format('DD-MMM-YYYY'), 'success')
    else:
        flash('Invoice has already been marked as submitted<br>Download the PDF and email manually if needed', 'error')

    return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice_number))


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/submit', methods=["POST"])
@login_required
def submit_invoice(invoice_number):
    if 'mark' in request.form:
        return mark_invoice_submitted(invoice_number)

    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()

    # Only update the submitted date if the invoice didn't have one in the
    # first place.  We want the user to be able to re-submit invoices to remind
    # customers of overdue conditions.
    if not invoice.submitted_date:
        invoice.submitted_date = arrow.now()
        db.session.add(invoice)
        db.session.commit()

    html_text = raw_invoice(invoice_number)
    raw_text = text_invoice(invoice_number)

    stream_attachments = []
    pdf_fh = None
    if pdf_enabled():
        fname = "invoice-%s.pdf" % invoice_number
        config = Configuration(current_app.config['WKHTMLTOPDF'])
        options = {
            'print-media-type': None,
            'page-size': 'letter',
            'no-outline': None,
            'quiet': None
        }
        pdf_text = pdfkit.from_string(html_text, None, options=options, configuration=config)
        pdf_fh = StringIO()

        pdf_fh.write(pdf_text)
        pdf_fh.seek(0)  # Ensure `sendmail` gets the whole thing

        stream_attachments = [(fname, pdf_fh)]

    try:
        email_to = get_address_emails(invoice.customer_id)
        sendmail(
            sender=current_app.config['EMAIL_FROM'] or current_app.config['EMAIL_USERNAME'],
            to=email_to,
            cc=[current_app.config['EMAIL_USERNAME']],
            subject='Invoice %s from %s' % (invoice.number, User.query.get(session['user_id']).profile.full_name),
            server=current_app.config['EMAIL_SERVER'],
            html_body=Premailer(html_text, cssutils_logging_level='CRITICAL').transform(),
            text_body=raw_text,
            username=current_app.config['EMAIL_USERNAME'],
            password=current_app.config['EMAIL_PASSWORD'],
            starttls=current_app.config['EMAIL_STARTTLS'],
            encode_body=True,
            stream_attachments=stream_attachments,
        )
        flash('invoice was submitted to ' + ', '.join(email_to), 'success')
    except Exception as e:
        flash('Error while trying to email the invoice: %s' % e, 'error')
    finally:
        if pdf_fh:
            pdf_fh.close()

    return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))


def get_invoice_ids():
    return [x.id for x in Invoice.query.filter_by(user_id=session['user_id']).all()]


def last_invoice_id():
    invoice = Invoice.query.filter_by(user_id=session['user_id']).order_by(Invoice.id.desc()).first()

    if invoice:
        return invoice.id

    return 0


def last_invoice_number():
    invoice = Invoice.query.filter_by(user_id=session['user_id']).order_by(Invoice.id.desc()).first()
    if invoice:
        return invoice.number

    return 0


def next_invoice_number(customer_id):
    """
    Returns the next available invoice number in the format:
        YYYY-<customer number>-<invoice number>
    """
    customer = Customer.query.get(customer_id)
    number = customer.number

    this_years_invoice_numbers = '%s-%s' % (number, arrow.now().format('YYYY'))
    ilike = '%s%%' % this_years_invoice_numbers
    numbers = [x.number for x in Invoice.query.filter_by(user_id=session['user_id']).filter(Invoice.number.ilike(ilike)).all()]

    # import pdb; pdb.set_trace()

    last = 0
    for number in numbers:
        match = re.search('%s-(\d+)' % this_years_invoice_numbers, number)
        if match:
            value = int(match.group(1))
            if value > last:
                last = value

    return '%s-%03d' % (this_years_invoice_numbers, last + 1)


@invoice_page.route('/')
@login_required
def last_invoice():
    last_number = last_invoice_number()

    if not last_number:
        return redirect(url_for('invoice_page.create'))

    return redirect(url_for('invoice_page.invoice_by_number', invoice_number=last_number))


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/raw')
@login_required
def raw_invoice(invoice_number):
    """
    Displays a single invoice
    """
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    customer = Customer.query.get(invoice.customer_id)
    customer_address = customer.format_address()
    submit_address = format_my_address()

    terms = invoice.terms or customer.terms or User.query.get(session['user_id']).profile.terms

    return render_template(
        'invoice/w3-invoice.html',
        invoice=invoice,
        customer_address=customer_address,
        submit_address=submit_address,
        terms=terms,
        overdue=invoice.overdue(),
        w3_theme=invoice.get_theme() or current_app.config['W3_THEME']
    )


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>/text')
@login_required
def text_invoice(invoice_number):
    """
    Displays a single invoice
    """
    invoice = Invoice.query.filter_by(number=invoice_number, user_id=session['user_id']).first_or_404()
    customer = Customer.query.get(invoice.customer_id)
    customer_address = customer.format_address()
    submit_address = format_my_address(html=False)

    terms = invoice.terms or customer.terms or User.query.get(session['user_id']).profile.terms

    return render_template(
        'invoice/text-invoice.txt',
        invoice=invoice,
        customer_address=customer_address,
        submit_address=submit_address,
        terms=terms,
        overdue=invoice.overdue(),
        w3_theme=invoice.get_theme() or current_app.config['W3_THEME']
    )
