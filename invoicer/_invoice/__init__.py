import os
import re

import pdfkit
from pdfkit.configuration import Configuration
import arrow
from flask import (
    Blueprint, request, redirect, url_for, render_template, flash, current_app,
    Response)
from premailer import Premailer

# from .app import create_app
from ..forms import EmptyForm
from ..submitter import sendmail
from ..database import db
from ..models import Item, Invoice, Customer, UnitPrice, Address
from ..common import login_required

from .forms import InvoiceForm, ItemForm


invoice_page = Blueprint('invoice_page', __name__, template_folder='templates')


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


def format_address(customer_id):
    customer = Customer.query.filter(Customer.id == customer_id).first()
    name = '<br>'.join([x for x in [customer.name1, customer.name2] if x])
    street = '<br>'.join([x for x in [customer.addrline1, customer.addrline2] if x])
    city = '%s, %s %s' % (customer.city, customer.state.upper(), customer.zip)

    return '<br>'.join([name, street, city, customer.email])


def format_my_address():
    address = Address.query.first()

    return '<br>'.join([
        address.full_name,
        address.street,
        '%s %s, %s' % (address.city, address.state, address.zip),
        address.email
    ])


def get_terms(customer_id):
    terms_description = 'NET 30 days'
    terms_days = 30

    customer_terms = Customer.query.filter(Customer.id == customer_id).first().terms
    if customer_terms:
        terms_description = customer_terms
    else:
        terms_description = Address.query.get(1).terms or terms_description

    match = re.search('(\d+).*?days', terms_description, re.IGNORECASE)
    if match:
        terms_days = int(match.group(1))

    return (terms_description, terms_days)


@invoice_page.route('/<invoice_id>/items/delete', methods=["GET", "POST"])
@login_required
def delete_items(invoice_id):
    form = EmptyForm()
    items = Item.query.filter(Item.invoice_id == invoice_id)

    if form.validate_on_submit():
        item_ids_to_delete = [y for x, y in request.form.items() if x.startswith('item_')]
        items = Item.query.filter(Item.id.in_(item_ids_to_delete)).all()
        if not items:
            return redirect(url_for('invoice_page.invoice_by_number', invoice_number=Invoice.query.get(invoice_id).number))

        for item in items:
            db.session.delete(item)

        db.session.commit()
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=Invoice.query.get(invoice_id).number))

    return render_template('invoice/delete_items_form.html', form=form, items=items, invoice_id=invoice_id)


@invoice_page.route('/<int:invoice_id>/items/new', methods=["GET", "POST"])
@login_required
def new_item(invoice_id):
    form = ItemForm(quantity=1)
    unit_prices = UnitPrice.query.all()

    unit_price_choices = [
        (x.id, "%d: %s ($%.02f/%s)" % (x.id, x.description, x.unit_price, x.units))
        for x in unit_prices
    ]
    form.unit_price.choices = unit_price_choices
    invoice = Invoice.query.filter(Invoice.id == invoice_id).first()

    if form.validate_on_submit():
        unit_price = UnitPrice.query.filter(UnitPrice.id == request.form['unit_price']).first()

        db.session.add(Item(
            invoice_id=invoice_id,
            date=request.form['date'].upper(),
            description=request.form['description'],
            unit_price=unit_price.unit_price,
            quantity=request.form['quantity'],
            units=unit_price.units,
            customer=invoice.customer
        ))

        db.session.commit()

        items = Item.query.filter(Item.invoice_id == invoice_id).all()
        item_total = sum([x.quantity * x.unit_price for x in items])
        Invoice.query.filter(Invoice.id == invoice_id).update({'total': item_total})

        db.session.commit()

        flash('item added to invoice %d' % invoice_id, 'success')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    return render_template('invoice/item_form.html', form=form, invoice_id=invoice_id)


@invoice_page.route('/<invoice_id>/update', methods=["GET", "POST"])
@login_required
def update_invoice(invoice_id):
    customers = Customer.query.all()
    addr_choices = [(x.id, x.name1) for x in customers]

    invoice = Invoice.query.filter(Invoice.id == invoice_id).first()

    form = InvoiceForm(
        description=invoice.description,
        submitted_date=invoice.submitted_date,
        paid_date=invoice.paid_date,
    )
    form.customer.choices = addr_choices
    form.customer.process_data(invoice.customer_id)

    if form.validate_on_submit():
        customer_id = int(request.form['customer'])
        Invoice.query.filter(Invoice.id == invoice_id).update({
            'description': request.form['description'],
            'customer_id': customer_id,
            'submitted_date': request.form['submitted_date'].upper(),
            'paid_date': request.form['paid_date'].upper()
        })

        db.session.commit()

        flash('invoice updated', 'success')
        return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))

    return render_template('invoice/invoice_form.html', form=form, invoice_id=invoice_id)


@invoice_page.route('/<regex("\d+-\d+-\d+"):invoice_number>')
@login_required
def invoice_by_number(invoice_number):
    invoice = Invoice.query.filter(Invoice.number == invoice_number).first()
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
        invoice_id=invoice.id,
        next_id=next_id,
        previous_id=previous_id,
        invoice_obj=invoice,
        to_emails=to_emails,
        can_submit=to_emails and invoice and can_submit(invoice.customer_id)
    )


@invoice_page.route('/new', methods=["GET", "POST"])
@login_required
def new_invoice():
    form = InvoiceForm()
    customers = Customer.query.all()
    addr_choices = [(x.id, x.name1) for x in customers]
    form.customer.choices = addr_choices

    if form.validate_on_submit():
        customer_id = int(request.form['customer'])
        number = next_invoice_number(customer_id)
        db.session.add(
            Invoice(
                description=request.form['description'],
                customer_id=customer_id,
                number=number
            )
        )
        db.session.commit()

        flash('invoice added', 'success')
        return redirect(url_for('invoice_page.last_invoice'))

    return render_template('invoice/invoice_form.html', form=form)


@invoice_page.route('/<int:invoice_id>/delete')
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.filter(Invoice.id == invoice_id).first()
    items = Item.query.filter(Item.invoice == invoice).all()

    db.session.delete(invoice)

    for item in items:
        db.session.delete(item)

    db.session.commit()
    flash('Invoice %d has been deleted' % invoice_id, 'warning')
    return redirect(url_for('invoice_page.last_invoice'))


@invoice_page.route('/<int:invoice_id>/pdf')
@login_required
def to_pdf(invoice_id):
    text = raw_invoice(invoice_id)
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
    if current_app.config['DEBUG'] and ('EMAIL_USERNAME' in current_app.config):
        return [current_app.config['EMAIL_USERNAME'] or '']

    email = Customer.query.get(customer_id).email

    if '|' in email:
        name, domain = email.split('@')
        return ['%s@%s' % (x, domain) for x in name.split('|')]

    return [email]


@invoice_page.route('/<invoice_id>/submit')
@login_required
def submit_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    invoice.submitted_date = arrow.now().format('DD-MMM-YYYY').upper()
    db.session.add(invoice)
    db.session.commit()

    text = raw_invoice(invoice_id)
    fname = "invoice-%03d.pdf" % int(invoice_id)
    fpath = os.path.join(current_app.instance_path, fname)
    config = Configuration(current_app.config['WKHTMLTOPDF'])
    options = {
        'print-media-type': None,
        'page-size': 'letter',
        'no-outline': None,
        'quiet': None
    }
    pdfkit.from_string(text, fpath, options=options, configuration=config)

    email_to = get_address_emails(invoice.customer_id)
    sendmail(
        sender='invoicer@host.com',
        to=email_to,
        cc=[current_app.config['EMAIL_USERNAME']],
        subject='Invoice %s from %s' % (invoice.number, Address.query.get(1).full_name),
        body=Premailer(text, cssutils_logging_level='CRITICAL').transform(),
        server=current_app.config['EMAIL_SERVER'],
        body_type="html",
        attachments=[fpath],
        username=current_app.config['EMAIL_USERNAME'],
        password=current_app.config['EMAIL_PASSWORD'],
        starttls=True,
        encode_body=True
    )

    os.unlink(fpath)

    flash('invoice was submitted to ' + ', '.join(email_to), 'success')
    return redirect(url_for('invoice_page.invoice_by_number', invoice_number=invoice.number))


def get_invoice_ids():
    return [x.id for x in Invoice.query.all()]


def last_invoice_id():
    invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if invoice:
        return invoice.id

    return 0


def last_invoice_number():
    invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if invoice:
        return invoice.number

    return 0


def next_invoice_number(customer_id):
    """
    Returns the next available invoice number in the format:
        YYYY-<customer number>-<invoice number>
    """
    customer = Customer.query.filter(Customer.id == customer_id).first()
    number = customer.number

    this_years_invoice_numbers = '%s-%s' % (number, arrow.now().format('YYYY'))
    ilike = '%s%%' % this_years_invoice_numbers
    numbers = [x.number for x in Invoice.query.filter(Invoice.number.ilike(ilike)).all()]

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
    return redirect(url_for('invoice_page.invoice_by_number', invoice_number=last_invoice_number()))


@invoice_page.route('/raw/<invoice_id>')
@login_required
def raw_invoice(invoice_id):
    """
    Displays a single invoice
    """
    if not isinstance(invoice_id, basestring):
        invoice_id = str(invoice_id)

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return render_template('w3-invoice.html')

    customer_address = format_address(invoice.customer_id)
    submit_address = format_my_address()
    terms_description, terms_days = get_terms(invoice.customer_id)

    if invoice.submitted_date:
        submitted = arrow.get(invoice.submitted_date, 'DD-MMM-YYYY')
        due = submitted.replace(days=+terms_days).format('DD-MMM-YYYY')
        submitted = submitted.format('DD-MMM-YYYY')
    else:
        submitted = None
        due = None

    return render_template(
        'invoice/w3-invoice.html',
        invoice_number=invoice.number,
        invoice_description=invoice.description,
        items=invoice.items,
        total=invoice.total,
        submitted=submitted,
        due=due,
        customer_address=customer_address,
        submit_address=submit_address,
        terms=terms_description,
        paid=invoice.paid_date,
        theme="deep-orange"
    )