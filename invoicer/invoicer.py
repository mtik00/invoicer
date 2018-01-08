import os
import re
import json
import time
import sqlite3
import zipfile
from functools import wraps
from datetime import timedelta

import click
import pdfkit
from pdfkit.configuration import Configuration
import arrow
from flask import (Flask, request, session, g, redirect, url_for, abort,
     render_template, flash, send_file, Response)
from .forms import AddressForm, InvoiceForm, ItemForm, EmptyForm
from argon2 import PasswordHasher


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.instance_path, 'invoicer.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD_HASH='$argon2i$v=19$m=512,t=2,p=2$+w4dAmcJGnaqsgob82pqcQ$4uGfP7JerZJPqAq5cWZ0bw',  # 'default'
    NAME='John Doe',
    WKHTMLTOPDF="c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
    BACKUP_DIR=app.instance_path,
    SESSION_TIMEOUT_MINUTES=30,
))
app.config.from_envvar('INVOICER_SETTINGS', silent=True)
app.config.from_pyfile(os.path.join(app.instance_path, 'application.cfg'), silent=True)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# Expire the session if the user sets `SESSION_TIMEOUT_MINUTES` ###############
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=app.config.get('SESSION_TIMEOUT_MINUTES'))

if app.config.get('SESSION_TIMEOUT_MINUTES'):
    app.before_request(make_session_permanent)
###############################################################################

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    click.echo("WARNING: Continue will delete all data in the databse")
    if not click.confirm('Do you want to continue?'):
        return

    db = get_db()
    with app.open_resource('schema.sql', mode='r') as fh:
        db.cursor().executescript(fh.read())
    db.commit()
    click.echo('Initialized the database.')

    if click.confirm('Populate with sample data?'):
        with app.open_resource('sample-data.sql', mode='r') as fh:
            db.cursor().executescript(fh.read())
        db.commit()
        click.echo('Sample data added to database.')


@app.route('/')
@login_required
def index():
    db = get_db()
    cur = db.execute('select id, submitted_date, description, paid_date from invoices order by id desc')
    invoices = cur.fetchall()
    return render_template('index.html', invoices=invoices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            ph = PasswordHasher()
            ph.verify(app.config['PASSWORD_HASH'], request.form['password'])
        except:
            error = 'Invalid username/password'

        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username/password'

        if not error:
            session['logged_in'] = True
            flash('You were logged in')

            if 'next' in request.form:
                return redirect(request.form['next'])

            return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'info')
    return redirect(url_for('index'))


@app.route('/invoice/<invoice_id>/items/delete', methods=["GET","POST"])
@login_required
def delete_items(invoice_id):
    form = EmptyForm()
    db = get_db()
    cur = db.execute('select * from items where invoice_id = ?', [invoice_id])
    items = cur.fetchall()

    if form.validate_on_submit():
        items_to_delete = [y for x, y in request.form.items() if x.startswith('item_')]
        if not items_to_delete:
            return redirect(url_for('invoice', invoice=invoice_id))

        for item_id in items_to_delete:
            db.execute('delete from items where id = ?', [item_id])

        db.commit()
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('delete_items_form.html', form=form, items=items, invoice_id=invoice_id)


@app.route('/invoice/<int:invoice_id>/items/new', methods=["GET","POST"])
@login_required
def new_item(invoice_id):
    form = ItemForm()
    db = get_db()
    cur = db.execute('select * from unit_prices')
    unit_prices = cur.fetchall()
    unit_price_choices = [
        (x['id'], "%d: %s ($%.02f/%s)" % (x['id'], x['description'], x['unit_price'], x['units']))
        for x in unit_prices
    ]
    form.unit_price.choices = unit_price_choices

    if form.validate_on_submit():
        cur = db.execute('select * from unit_prices where id = ?', [request.form['unit_price']])
        unit_price_row = cur.fetchone()

        # Now insert
        db.execute('''
            insert into items (invoice_id, date, description, unit_price, quantity, units) values (?, ?, ?, ?, ?, ?)''',
            [
                invoice_id,
                request.form['date'].upper(),
                request.form['description'],
                unit_price_row['unit_price'],
                request.form['quantity'],
                unit_price_row['units'],
            ]
        )
        db.commit()

        flash('item added to invoice %d' % invoice_id, 'success')
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('item_form.html', form=form, invoice_id=invoice_id)


@app.route('/invoice/<invoice_id>/update', methods=["GET","POST"])
@login_required
def update_invoice(invoice_id):
    db = get_db()
    cur = db.execute('select * from addresses order by id desc')
    addresses = cur.fetchall()
    addr_choices = [(x['id'], x['name1']) for x in addresses]

    cur = db.execute('select * from invoices where id = ?', [invoice_id])
    invoice = cur.fetchone()

    form = InvoiceForm(description=invoice['description'])
    form.to_address.choices = addr_choices
    form.to_address.process_data(invoice['to_address'])

    if form.validate_on_submit():
        to_address_id = int(request.form['to_address'])

        # Now insert
        db.execute('''
            update invoices set description = ?, to_address = ? where id = ?''',
            [
                request.form['description'],
                to_address_id,
                invoice_id
            ]
        )
        db.commit()

        flash('invoice updated', 'success')
        return redirect(url_for('invoice', invoice=invoice_id))

    return render_template('invoice_form.html', form=form, invoice_id=invoice_id)


@app.route('/invoice/new', methods=["GET","POST"])
@login_required
def new_invoice():
    form = InvoiceForm()
    db = get_db()
    cur = db.execute('select * from addresses order by id desc')
    addresses = cur.fetchall()
    addr_choices = [(x['id'], x['name1']) for x in addresses]
    form.to_address.choices = addr_choices

    if form.validate_on_submit():
        to_address_id = int(request.form['to_address'])

        # Now insert
        db.execute('''
            insert into invoices (description, to_address) values (?, ?)''',
            [
                request.form['description'],
                to_address_id,
            ]
        )
        db.commit()

        flash('invoice added', 'success')
        return redirect(url_for('last_invoice'))

    return render_template('invoice_form.html', form=form)


@app.route('/invoice/<int:invoice_id>/delete')
@login_required
def delete_invoice(invoice_id):
    db = get_db()
    db.execute('DELETE FROM invoices WHERE id = ?', [str(invoice_id)])
    db.execute('DELETE FROM items WHERE invoice_id = ?', [str(invoice_id)])
    db.commit()
    flash('Invoice %d has been deleted' % invoice_id, 'warning')
    return redirect(url_for('last_invoice'))


@app.route('/invoice/<int:invoice_id>/pdf')
@login_required
def to_pdf(invoice_id):
    text = raw_invoice(invoice_id)
    fname = "invoice-%03i.pdf" % int(invoice_id)
    fpath = os.path.join(app.instance_path, fname)
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


@app.route('/addresses/new', methods=["GET","POST"])
@login_required
def new_address():
    form = AddressForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute('''
            insert into addresses (name1, name2, addrline1, addrline2, city, state, zip, email, terms) values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [
                request.form['name1'],
                request.form['name2'],
                request.form['addrline1'],
                request.form['addrline2'],
                request.form['city'],
                request.form['state'],
                request.form['zipcode'],
                request.form['email'],
                request.form['terms'],
            ]
        )
        db.commit()

        flash('address added', 'success')
        return redirect(url_for('addresses'))

    return render_template('address_form.html', form=form)


@app.route('/addresses')
@login_required
def addresses():
    db = get_db()
    cur = db.execute('select * from addresses')
    addresses = cur.fetchall()

    return render_template('addresses.html', addresses=addresses)


def get_invoice_ids():
    db = get_db()
    cur = db.execute('select id from invoices order by id asc')
    invoice_ids = cur.fetchall()
    return [x[0] for x in invoice_ids]


def last_invoice_id():
    db = get_db()
    cur = db.execute('select id from invoices order by id desc')
    invoice_id = cur.fetchone()
    return invoice_id[0]


@app.route('/invoice')
@login_required
def last_invoice():
    return redirect(url_for('invoice', invoice=last_invoice_id()))


@app.route('/invoice/<int:invoice>')
@login_required
def invoice(invoice=None):
    # Always show the last invoice first
    if invoice is None:
        show_id = last_invoice_id()
    else:
        show_id = invoice

    db = get_db()
    cur = db.execute('select * from invoices where id = ?', [str(invoice)])
    invoice_obj = cur.fetchone()

    # Figure out next/previous
    invoice_ids = get_invoice_ids()
    current_pos = invoice_ids.index(show_id)
    if current_pos == len(invoice_ids) - 1:
        next_id = None
    else:
        next_id = invoice_ids[current_pos + 1]

    if current_pos == 0:
        previous_id = None
    else:
        previous_id = invoice_ids[current_pos - 1]

    return render_template(
        'invoices.html',
        invoice_id=show_id,
        next_id=next_id,
        previous_id=previous_id,
        max_invoices=last_invoice_id(),
        invoice_obj=invoice_obj
    )


@app.route('/raw-invoice/<int:invoice_id>')
@login_required
def raw_invoice(invoice_id):
    """
    Displays a single invoice
    """
    db = get_db()
    cur = db.execute('select * from items where invoice_id=?', str(invoice_id))
    items = cur.fetchall()
    invoice_id, submitted, description, to_address_id, paid = db.execute('select * from invoices where id=?', str(invoice_id)).fetchone()
    to_address = format_address(str(to_address_id))
    submit_address = format_address("1")

    if submitted:
        submitted = arrow.get(submitted, 'DD-MMM-YYYY')
    else:
        submitted = None

    due = submitted.replace(days=+30).format('DD-MMM-YYYY') if submitted else None
    submitted = submitted.format('DD-MMM-YYYY') if submitted else None

    return render_template(
        'invoice.html',
        invoice_number=invoice_id,
        invoice_description=description,
        items=items,
        total=sum([x['quantity'] * x['unit_price'] for x in items]),
        submitted=submitted,
        due=due,
        to_address=to_address,
        submit_address=submit_address,
        terms=get_terms(to_address_id),
        paid=paid
    )


@app.template_filter('currency')
def currency(value):
    return "$%.2f" % float(value)


def format_address(address_id):
    db = get_db()
    _, name1, name2, addrline1, addrline2, city, state, zipcode, email, _ = db.execute('select * from addresses where id=?', str(address_id)).fetchone()

    name = '<br>'.join([x for x in [name1, name2] if x])
    street = '<br>'.join([x for x in [addrline1, addrline2] if x])
    city = '%s, %s %s' % (city, state.upper(), zipcode)

    return '<br>'.join([name, street, city, email])

def get_terms(address_id):
    db = get_db()
    terms = db.execute('select terms from addresses where id=?', str(address_id)).fetchone()

    if terms[0]:
        return terms[0]

    return db.execute('select terms from addresses where id=?', '1').fetchone()[0]


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
