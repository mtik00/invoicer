import json
from flask import Blueprint, render_template, redirect, url_for, session

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
    date_by_year = {
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

    return render_template(
        'index/lb-index.html',
        invoices=invoices,
        date_by_year=json.dumps(date_by_year)
    )

@index_page.route('/t1')
def t1():
    return render_template('lb/dashboard.html')
