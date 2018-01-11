import os
import re
import time
import zipfile
from datetime import timedelta

import click
import pdfkit
from pdfkit.configuration import Configuration
import arrow
from flask import (
    Flask, request, session, g, redirect, url_for, render_template, flash,
    Response)
from premailer import Premailer
from werkzeug.routing import BaseConverter

from .forms import InvoiceForm, ItemForm, EmptyForm
from .submitter import sendmail
from .database import db, init_db
from .models import Item, Invoice, Customer, Address, UnitPrice
from .common import login_required
from ._login import login_page
from ._profile import profile_page
from ._units import unit_page
from ._customers import customers_page


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.instance_path, 'invoicer.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD_HASH='$argon2i$v=19$m=512,t=2,p=2$+w4dAmcJGnaqsgob82pqcQ$4uGfP7JerZJPqAq5cWZ0bw',  # 'default'
    WKHTMLTOPDF="c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
    BACKUP_DIR=app.instance_path,
    SESSION_TIMEOUT_MINUTES=30,

    EMAIL_USERNAME=None,
    EMAIL_PASSWORD=None,
    EMAIL_SERVER=None
))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.from_envvar('INVOICER_SETTINGS', silent=True)
app.config.from_pyfile(os.path.join(app.instance_path, 'application.cfg'), silent=True)
app.register_blueprint(profile_page, url_prefix='/profile')
app.register_blueprint(unit_page, url_prefix='/units')
app.register_blueprint(customers_page, url_prefix='/customers')
app.register_blueprint(login_page)
db.init_app(app)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


def get_user_info(update=False):
    if update or (not hasattr(g, '_userinfo')):
        info = Address.query.get(1)
        if info:
            g._userinfo = info
        else:
            g._userinfo = Address()

    return g._userinfo


# Expire the session if the user sets `SESSION_TIMEOUT_MINUTES` ###############
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=app.config.get('SESSION_TIMEOUT_MINUTES'))


if app.config.get('SESSION_TIMEOUT_MINUTES'):
    app.before_request(make_session_permanent)
###############################################################################


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    click.echo("WARNING: Continue will delete all data in the databse")
    if not click.confirm('Do you want to continue?'):
        return

    if click.confirm('Populate with sample data?'):
        init_db(True)
        click.echo('Sample data added to database.')
    else:
        init_db(False)
    click.echo('Initialized the database.')


@app.route('/')
@login_required
def index():
    return render_template(
        'index.html',
        invoices=Invoice.query.order_by(Invoice.id.desc()).all()
    )


@app.route('/invoice/<invoice_id>/items/delete', methods=["GET", "POST"])
@login_required
def delete_items(invoice_id):
    form = EmptyForm()
    items = Item.query.filter(Item.invoice_id == invoice_id)

    if form.validate_on_submit():
        item_ids_to_delete = [y for x, y in request.form.items() if x.startswith('item_')]
        items = Item.query.filter(Item.id.in_(item_ids_to_delete)).all()
        if not items:
            return redirect(url_for('invoice', invoice=invoice_id))

        for item in items:
            db.session.delete(item)

        db.session.commit()
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('delete_items_form.html', form=form, items=items, invoice_id=invoice_id)


@app.route('/invoice/<int:invoice_id>/items/new', methods=["GET", "POST"])
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
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('item_form.html', form=form, invoice_id=invoice_id)


@app.route('/invoice/<invoice_id>/update', methods=["GET", "POST"])
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
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('invoice_form.html', form=form, invoice_id=invoice_id)


@app.route('/invoice/<regex("\d+-\d+-\d+"):invoice_number>')
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
        'invoices.html',
        invoice_id=invoice.id,
        next_id=next_id,
        previous_id=previous_id,
        invoice_obj=invoice,
        to_emails=to_emails,
        can_submit=to_emails and invoice and can_submit(invoice.customer_id)
    )


@app.route('/invoice/new', methods=["GET", "POST"])
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
        return redirect(url_for('last_invoice'))

    return render_template('invoice_form.html', form=form)


@app.route('/invoice/<int:invoice_id>/delete')
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.filter(Invoice.id == invoice_id).first()
    items = Item.query.filter(Item.invoice == invoice).all()

    db.session.delete(invoice)

    for item in items:
        db.session.delete(item)

    db.session.commit()
    flash('Invoice %d has been deleted' % invoice_id, 'warning')
    return redirect(url_for('last_invoice'))


@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def to_pdf(invoice_id):
    text = raw_invoice(invoice_id)
    config = Configuration(app.config['WKHTMLTOPDF'])
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
    if app.config['DEBUG'] and ('EMAIL_USERNAME' in app.config):
        return [app.config['EMAIL_USERNAME'] or '']

    email = Customer.query.get(customer_id).email

    if '|' in email:
        name, domain = email.split('@')
        return ['%s@%s' % (x, domain) for x in name.split('|')]

    return [email]


@app.route('/invoice/<invoice_id>/submit')
@login_required
def submit_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    invoice.submitted_date = arrow.now().format('DD-MMM-YYYY').upper()
    db.session.add(invoice)
    db.session.commit()

    text = raw_invoice(invoice_id)
    fname = "invoice-%03d.pdf" % int(invoice_id)
    fpath = os.path.join(app.instance_path, fname)
    config = Configuration(app.config['WKHTMLTOPDF'])
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
        cc=[app.config['EMAIL_USERNAME']],
        subject='Invoice %s from %s' % (invoice.number, get_user_info().full_name),
        body=Premailer(text, cssutils_logging_level='CRITICAL').transform(),
        server=app.config['EMAIL_SERVER'],
        body_type="html",
        attachments=[fpath],
        username=app.config['EMAIL_USERNAME'],
        password=app.config['EMAIL_PASSWORD'],
        starttls=True,
        encode_body=True
    )

    os.unlink(fpath)

    flash('invoice was submitted to ' + ', '.join(email_to), 'success')
    return redirect(url_for('invoice', invoice=invoice_id))


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


@app.route('/invoice')
@login_required
def last_invoice():
    return redirect(url_for('invoice_by_number', invoice_number=last_invoice_number()))


@app.route('/raw-invoice/<invoice_id>')
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
        'w3-invoice.html',
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
    )


@app.template_filter('currency')
def currency(value):
    return "$%.2f" % float(value or 0.0)


@app.template_filter('billto')
def billto(customer_id):
    return Customer.query.filter(Customer.id == customer_id).first().name1


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


def last_backup():
    files = [x for x in os.listdir(app.config['BACKUP_DIR']) if re.search('backup-(\d{4}).zip', x, re.IGNORECASE)]
    if not files:
        return 0

    backup_index = 0
    for fname in files:
        index = int(re.search('backup-(\d{4}).zip', fname, re.IGNORECASE).group(1))
        if index > backup_index:
            backup_index = index

    return backup_index


def create_backup(wait=True):
    index = last_backup() + 1
    if index > 9999:
        raise Exception("No more room for backups!")

    fname = 'backup-{index:04d}.zip'.format(index=index)
    fpath = os.path.join(app.config['BACKUP_DIR'], fname)

    tend = time.time() + 30
    journaling = [x for x in os.listdir(app.config['BACKUP_DIR']) if 'db-journal' in x]
    while journaling and (time.time() < tend):
        click.echo('Waiting for journal file to be removed')
        time.sleep(1)
        journaling = [x for x in os.listdir(app.config['BACKUP_DIR']) if 'db-journal' in x]

    if journaling:
        raise Exception("Timeout while waiting for journal to be written")

    with zipfile.ZipFile(fpath, 'w', zipfile.ZIP_DEFLATED) as myzip:
        myzip.write(app.config['DATABASE'], '/invoicer.db')

    click.echo(fname + " created")


def remove_older_backups(days=30):
    """
    Deletes all backup files older than `days`.
    """
    oldest = arrow.now().replace(days=-30).timestamp
    files = [os.path.join(app.config['BACKUP_DIR'], x) for x in os.listdir(app.config['BACKUP_DIR']) if re.search('backup-(\d{4}).zip', x, re.IGNORECASE)]
    for fpath in files:
        s = os.stat(fpath)
        if s.st_ctime < oldest:
            print "deleting", fpath
            os.unlink(fpath)


def can_submit(customer_id):
    """
    Returns `True` if we can submit an invoice by email to a customer, `False`
    otherwise.
    """
    if not (
        app.config.get('EMAIL_PASSWORD') and
        app.config.get('EMAIL_USERNAME') and
        app.config.get('EMAIL_SERVER')
    ):
        return False

    customer = Customer.query.filter(Customer.id == customer_id).first()
    if not (customer and customer.email):
        return False

    return True


@app.cli.command('rotate')
@click.argument('days', default=30)
def rotate(days):
    """
    Creates a new backup and possibly removes backups older than X days.

    NOTE: Backup creation will always happen; the code does not test for
    changes.
    """
    create_backup()
    remove_older_backups(days)


@app.cli.command('test-email')
def test_email():
    sendmail(
        sender='invoicer@host.com',
        to=[app.config['EMAIL_USERNAME']],
        subject='Test email from Invoicer',
        body="<h1>Hello, World!</h1>",
        server='%s:%d' % (app.config['EMAIL_SERVER'], app.config['EMAIL_PORT']),
        body_type="html",
        attachments=None,
        username=app.config['EMAIL_USERNAME'],
        password=app.config['EMAIL_PASSWORD'],
        starttls=True
    )
