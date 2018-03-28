import json

import arrow
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required, current_user

from ..models import Invoice
from ..cache import app_cache


index_page = Blueprint('index_page', __name__, template_folder='templates')


@index_page.route('/')
def index():
    return redirect(url_for('.dashboard'))


@index_page.route('/dashboard')
@login_required
def dashboard():
    uid = current_user.id
    invoices = get_user_invoices(uid)
    invoice_stats = get_invoice_stats(uid)

    return render_template(
        'index/index.html',
        invoices=invoices,
        invoice_stats=json.dumps(invoice_stats),
        unpaid_invoices=get_unpaid_invoices(uid),
        unsubmitted_invoices=get_unsubmitted_invoices(uid)
    )


class InvoiceStats(object):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self):
        self.data = {}

    def add_paid(self, paid_date, total):
        month = paid_date.month
        year = paid_date.year

        if year not in self.data:
            self.data[year] = {
                'paid': {month: total},
                'submit': {month: 0}
            }
            return

        if month not in self.data[year]['paid']:
            self.data[year]['paid'][month] = total
        else:
            self.data[year]['paid'][month] += total

    def add_submit(self, submit_date, total):
        month = submit_date.month
        year = submit_date.year

        # import pdb; pdb.set_trace()
        if year not in self.data:
            self.data[year] = {
                'paid': {month: 0},
                'submit': {month: total}
            }
            return

        if month not in self.data[year]['submit']:
            self.data[year]['submit'][month] = total
        else:
            self.data[year]['submit'][month] += total

    def serialize_for_chartist(self):
        '''Return a dict suitable for use by chartist.js'''
        result = {}

        # {2018: {'submit': {3: 2400.0}, 'paid': {2: 6400.0}}}
        for year, series in self.data.items():
            result[year] = {
                'labels': [],
                'series': [[], []]
            }

            for month in xrange(1, 13):
                result[year]['labels'].append(arrow.get('2017-%02d-01' % month, 'YYYY-MM-DD').format('MMM'))

                total = series['submit'].get(month, 0)
                result[year]['series'][0].append(total)

                total = series['paid'].get(month, 0)
                result[year]['series'][1].append(total)

        return result


@app_cache.memoize(timeout=300)
def get_user_invoices(user_id):
    q = Invoice.query
    q = q.options(joinedload(Invoice.customer))
    q = q.options(joinedload(Invoice.paid_date))
    q = q.filter_by(user_id=user_id)
    q = q.order_by(Invoice.id.desc())
    return q.all()


@app_cache.memoize(timeout=300)
def get_invoice_stats(user_id):
    result = InvoiceStats()

    for invoice in get_user_invoices(user_id):
        if invoice.submitted_date:
            result.add_submit(invoice.submitted_date, invoice.total)

        if invoice.paid_date:
            result.add_paid(invoice.paid_date.paid_date, invoice.total)

    return result.serialize_for_chartist()


@app_cache.memoize(timeout=300)
def get_unpaid_invoices(user_id):
    '''
    Returns a list of {'number', 'submitted_date', 'total'}
    '''
    result = []

    for invoice in get_user_invoices(user_id):
        if invoice.submitted_date and (not invoice.paid_date):
            result.append(invoice)

    return result


@app_cache.memoize(timeout=300)
def get_unsubmitted_invoices(user_id):
    '''
    Returns a list of {'number', 'submitted_date', 'total'}
    '''
    result = []

    for invoice in get_user_invoices(user_id):
        if not invoice.submitted_date:
            result.append(invoice)

    return result
