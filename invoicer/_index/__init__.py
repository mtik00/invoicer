import json
from flask import Blueprint, render_template, redirect, url_for, session
import arrow

from ..common import login_required
from ..models import User, Invoice


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
    date_by_year = get_invoice_stats()

    return render_template(
        'index/lb-index.html',
        invoices=invoices,
        date_by_year=json.dumps(date_by_year)
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
            self.data[year]['paid'] = {month: total}
        else:
            self.data[year]['paid'][month] += total

    def add_submit(self, submit_date, total):
        month = submit_date.month
        year = submit_date.year

        if year not in self.data:
            self.data[year] = {
                'paid': {month: 0},
                'submit': {month: total}
            }
            return

        if month not in self.data[year]['submit']:
            self.data[year]['submit'] = {month: total}
        else:
            self.data[year]['submit'][month] += total

    def serialize(self):
        '''Return a dict suitable for use by chartist.js'''
        result = {}

        # {2018: {'submit': {3: 2400.0}, 'paid': {2: 6400.0}}}
        for year, series in self.data.items():
            result[year] = {
                'labels': [],
                'series': [[], []]
            }

            # in_it = False
            for month in xrange(1, 13):
                # if (not in_it) and ((month in series['submit']) or (month in series['paid'])):
                #     in_it = True

                # if not in_it:
                #     continue

                result[year]['labels'].append(arrow.get('2017-%02d-01' % month, 'YYYY-MM-DD').format('MMM'))

                total = series['submit'].get(month, 0)
                result[year]['series'][0].append(total)

                total = series['paid'].get(month, 0)
                result[year]['series'][1].append(total)

        return result


def get_invoice_stats():
    result = InvoiceStats()

    for invoice in Invoice.query.filter_by(user=User.query.get(session['user_id'])).all():
        if invoice.submitted_date:
            result.add_submit(invoice.submitted_date, invoice.total)

        if invoice.paid_date:
            result.add_paid(invoice.paid_date.paid_date, invoice.total)

    return result.serialize()
    import pdb; pdb.set_trace()

    return {
        '2018': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr'],
            'series': [
                [287, 385, 490, 492],
                [67, 152, 143, 240],
            ]
        },
        '2017': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'series': [
                [287, 385, 490, 492, 500, 550, 623, 676, 710, 799, 811, 900],
                [67, 152, 143, 240, 275, 334, 455, 498, 554, 577, 654, 732],
            ]
        }
    }
