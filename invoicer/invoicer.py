import os
import re
import json
import time
import sqlite3
import zipfile

import click
import pdfkit
from pdfkit.configuration import Configuration
import arrow
from flask import (Flask, request, session, g, redirect, url_for, abort,
     render_template, flash, send_file, Response)
from .forms import AddressForm


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.instance_path, 'invoicer.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    WKHTMLTOPDF="c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
    BACKUP_DIR=app.instance_path,
))
app.config.from_envvar('INVOICER_SETTINGS', silent=True)
app.config.from_pyfile(os.path.join(app.instance_path, 'application.cfg'), silent=True)


INVOICE_COUNT = 0

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


@app.route('/')
def index():
    if not session.get('logged_in'):
        flash('You must log in first', 'error')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('select id, submitted_date, description from invoices order by id desc')
    invoices = cur.fetchall()
    return render_template('index.html', invoices=invoices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'info')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    # db = get_db()
    # db.execute('insert into entries (title, text) values (?, ?)',
    #              [request.form['title'], request.form['text']])
    # db.commit()
    flash('New entry was successfully posted', 'success')
    return redirect(url_for('index'))


@app.route('/invoice/<int:invoice_id>/pdf')
def to_pdf(invoice_id):
    text = show_invoice(invoice_id)
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


@app.route('/new-invoice', methods=["GET","POST"])
def new_invoice():
    form = AddressForm()
    if form.validate_on_submit():
        flash('address added', 'success')
        return redirect(url_for('index'))

    return render_template('address_form.html', form=form)


@app.route('/invoices', methods=["GET","POST"])
def show_invoices(current_invoice=None):
    global INVOICE_COUNT

    if not INVOICE_COUNT:
        db = get_db()
        cur = db.execute('select count(*) from invoices')
        INVOICE_COUNT = cur.fetchone()[0]

    if request.method == "POST":
        current_invoice = int(request.form.get('current', 1))
        if 'next' in request.form:
            invoice_id = current_invoice + 1
        elif 'previous' in request.form:
            invoice_id = current_invoice - 1
        elif 'pdf' in request.form:
            return to_pdf(current_invoice)
        elif 'new' in request.form:
            return redirect(url_for('new_invoice'))

        return render_template(
            'invoices.html',
            invoice_id=invoice_id,
            max_invoices=INVOICE_COUNT
        )

    # Always show the last invoice first
    if request.args.get('current_invoice'):
        show_id = int(request.args.get('current_invoice'))
    elif current_invoice is None:
        show_id = INVOICE_COUNT
    else:
        show_id = current_invoice

    return render_template(
        'invoices.html',
        invoice_id=show_id,
        max_invoices=INVOICE_COUNT
    )


@app.route('/invoice/<int:invoice_id>')
def show_invoice(invoice_id):
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
        submitted = arrow.now()

    due = submitted.replace(days=+30).format('DD-MMM-YYYY')
    submitted = submitted.format('DD-MMM-YYYY')

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
