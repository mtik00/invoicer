import os
import re
import time
import locale
import zipfile

import click
import arrow
from flask import render_template, url_for, redirect, session
from wtforms import Field

from .app import create_app
from .submitter import sendmail
from .database import init_db, export as export_db, import_clean_json, add_user
from .models import Invoice, Customer, User
from .common import login_required


locale.setlocale(locale.LC_ALL, '')
app = create_app()


@app.template_filter('currency')
def currency(value):
    return locale.currency(value or 0, symbol=True, grouping=True, international=False)


@app.template_filter('billto')
def billto(customer_id):
    return Customer.query.filter(Customer.id == customer_id).first().name1


@app.template_filter('isfield')
def is_field(item):
    """Returns `True` if the item is a WTForm Field object, False otherwise"""
    return isinstance(item, Field)


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


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    click.echo("WARNING: Continue will delete all data in the databse")
    if not click.confirm('Do you want to continue?'):
        raise click.Abort()

    if click.confirm('Populate with sample data?'):
        init_db(True, apply_migrations=True)
        click.echo('Sample data added to database.')
    else:
        init_db(False, apply_migrations=True)
    click.echo('Initialized the database.')


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
        server=app.config['EMAIL_SERVER'],
        body_type="html",
        attachments=None,
        username=app.config['EMAIL_USERNAME'],
        password=app.config['EMAIL_PASSWORD'],
        starttls=True
    )


@app.cli.command('export-json')
@click.argument('path')
def export_json(path):
    """
    Export the database into JSON format.
    """
    export_db(path)


@app.cli.command('import-json')
@click.argument('path', type=click.Path(exists=True))
def import_json(path):
    """
    Import the JSON data into the database.
    """
    click.echo("WARNING: Continue will delete all data in the databse")
    if not click.confirm('Do you want to continue?'):
        raise click.Abort()

    init_db(False)
    import_clean_json(path)
    click.echo('JSON data has been imported')


@app.cli.command('add-user')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
def new_user(username, password):
    add_user(username=username, password=password)
    click.echo("User [%s] has been added to the database" % username)
