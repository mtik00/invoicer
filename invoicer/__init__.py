from __future__ import print_function
import os
import re
import code
import time
import locale
import zipfile

import click
import arrow
from wtforms import Field
from jinja2 import Environment, StrictUndefined, FileSystemLoader
import ruamel.yaml

from .app import create_app
from .submitter import sendmail
from .database import (
    init_db, export as export_db, import_clean_json, add_user,
    rehash_passwords as force_rehash_passwords)
from .models import Customer


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
            print("deleting", fpath)
            os.unlink(fpath)


@app.cli.command('initdb')
@click.argument('force', default='n')
def initdb_command(force):
    """Initializes the database."""
    if force.lower().startswith('y'):
        init_db(True)
        click.echo('Sample data added to database.')
        click.echo('Initialized the database.')
        return

    click.echo("WARNING: Continue will delete all data in the databse")
    if not click.confirm('Do you want to continue?'):
        raise click.Abort()

    if click.confirm('Populate with sample data?'):
        init_db(True)
        click.echo('Sample data added to database.')
    else:
        init_db(False)
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


@app.cli.command('cli')
def interactive():
    """
    Launch an interactive REPL
    """
    code.interact(local=dict(globals(), **locals()))


@app.cli.command('build')
def build():
    """
    Build the configuration files
    """
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))
    instance_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    outdir = os.path.join(conf_dir, '..', '_build')

    options_file = os.path.join(instance_dir, 'site.yaml')
    if not os.path.exists(options_file):
        click.echo('ERROR: Could not find %s' % options_file)
        click.echo('...a sample is located in `conf`')
        click.echo('...copy `conf/site.yaml` to your instance folder, and modify it as needed')
        raise click.Abort()

    options = ruamel.yaml.safe_load(open(options_file).read())

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    env = Environment(
        loader=FileSystemLoader(conf_dir),
        undefined=StrictUndefined)

    ###########################################################################
    click.echo('Creating `_build/invoicer-uwsgi.ini')
    template = env.get_template('invoicer-uwsgi.ini.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'invoicer-uwsgi.ini'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/invoicer-systemd.service')
    template = env.get_template('invoicer-systemd.service.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'invoicer-systemd.service'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/invoicer-upstream.nginx')
    template = env.get_template('invoicer-upstream.nginx.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'invoicer-upstream.nginx'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')

    click.echo('Creating `_build/invoicer-location.nginx')
    template = env.get_template('invoicer-location.nginx.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'invoicer-location.nginx'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/fail2ban/filter.d/invoicer.local')
    f2b_filter_outdir = os.path.join(outdir, 'fail2ban', 'filter.d')
    if not os.path.isdir(f2b_filter_outdir):
        os.makedirs(f2b_filter_outdir)

    template = env.get_template('fail2ban/filter.d/invoicer.local.j2')
    content = template.render(**options)
    with open(os.path.join(f2b_filter_outdir, 'invoicer.local'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/fail2ban/jail.d/invoicer.local')
    f2b_filter_outdir = os.path.join(outdir, 'fail2ban', 'jail.d')
    if not os.path.isdir(f2b_filter_outdir):
        os.makedirs(f2b_filter_outdir)

    template = env.get_template('fail2ban/jail.d/invoicer.local.j2')
    content = template.render(**options)
    with open(os.path.join(f2b_filter_outdir, 'invoicer.local'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################

    ###########################################################################
    click.echo('Creating `_build/deploy.bash')
    template = env.get_template('deploy.bash.j2')
    content = template.render(**options)
    with open(os.path.join(outdir, 'deploy.bash'), 'wb') as fh:
        fh.write(content)
    click.echo('...done')
    ###########################################################################


@app.cli.command('rehash-passwords')
def rehash_passwords():
    '''
    App will rehash user passwords next time they log in
    '''
    try:
        force_rehash_passwords()
    except Exception as e:
        click.echo('Operation failed: %s' % e)
        return

    click.echo("User's passwords are set to be re-hashed")
