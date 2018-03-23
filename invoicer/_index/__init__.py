import sys
import json

import arrow
from flask import Blueprint, render_template, redirect, url_for, session

from ..common import login_required
from ..models import User, Invoice
from ..cache import app_cache


index_page = Blueprint('index_page', __name__, template_folder='templates')


@index_page.route('/p<int:page>')
@login_required
def paginate_index(page):
    per_page = User.query.get(session['user_id']).profile.index_items_per_page
    try:
        invoices = Invoice.query.filter_by(user=User.query.get(session['user_id'])).order_by(Invoice.id.desc()).paginate(page=page, per_page=per_page)
    except Exception:
        return redirect(url_for('.index'))

    return render_template(
        'index.html',
        invoices=invoices
    )


@index_page.route('/')
@login_required
def index():
    per_page = User.query.get(session['user_id']).profile.index_items_per_page
    invoices = Invoice.query.filter_by(user=User.query.get(session['user_id'])).order_by(Invoice.id.desc()).paginate(page=1, per_page=per_page)
    invoice_stats = get_invoice_stats(session['user_id'])

    return render_template(
        'index/lb-index.html',
        invoices=invoices,
        invoice_stats=json.dumps(invoice_stats)
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

                total = series['submit'].get(month, None)
                result[year]['series'][0].append(total)

                total = series['paid'].get(month, None)
                result[year]['series'][1].append(total)

            # Now that we have all of our data, we want to walk backwards through
            # the list and set the first "None" after actual data to 0.  This makes
            # the chart look better.
            found = False
            for index, _ in enumerate(result[year]['series'][0]):
                if result[year]['series'][0][index]:
                    found = True

                if found and (result[year]['series'][0][index] is None):
                    result[year]['series'][0][index] = 0
                    break

            found = False
            for index, _ in enumerate(result[year]['series'][1]):
                if result[year]['series'][1][index]:
                    found = True

                if found and (result[year]['series'][1][index] is None):
                    result[year]['series'][1][index] = 0
                    break

        return result


@app_cache.cached(timeout=30)
def get_invoice_stats(user_id):
    result = InvoiceStats()

    for invoice in Invoice.query.filter_by(user=User.query.get(user_id)).all():
        if invoice.submitted_date:
            result.add_submit(invoice.submitted_date, invoice.total)

        if invoice.paid_date:
            result.add_paid(invoice.paid_date.paid_date, invoice.total)

    return result.serialize_for_chartist()
