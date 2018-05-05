from flask import (
    Blueprint, render_template, request, flash, redirect, url_for)
from flask_login import login_required, current_user
import arrow

from ..common import form_is_deleting
from ..models import Customer, Invoice, User, InvoiceTheme
from ..database import db
from ..cache import app_cache
from .forms import CustomerForm

customers_page = Blueprint('customers_page', __name__, template_folder='templates')


def customer_has_invoices(customer_id):
    return Invoice.query.filter_by(customer_id=customer_id).count() > 0


def get_next_customer_number():
    user = User.query.get(current_user.id)
    starting = user.profile.starting_customer_number
    increment = user.profile.customer_increment

    numbers = [round(float(x.number), -1) for x in Customer.query.filter_by(user_id=current_user.id).all()]

    customer_number = starting
    for number in numbers:
        if number > customer_number:
            customer_number = number

    return int(customer_number + increment)


def get_customer(customer_id):
    return Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()


@customers_page.route('/<customer_id>/update', methods=["GET", "POST"])
@login_required
def update(customer_id):
    customer = get_customer(customer_id)
    form = CustomerForm(request.form, obj=customer)

    theme_choices = [('', '')] + [(x.name, x.name) for x in InvoiceTheme.query.all()]
    form.invoice_theme.choices = theme_choices

    if form.validate_on_submit():
        if form_is_deleting():
            return redirect(url_for('.delete', number=customer.number), code=307)

        # Only change the customer number there are no invoices and the new
        # number isn't already taken.
        number = form['number'].data
        if (number != customer.number) and customer_has_invoices(customer_id):
            flash('cannot change customer numbers if they have invoices', 'warning')
            form['number'].data = customer.number
        elif (number != customer.number) and Customer.query.filter_by(number=number).first():
            flash('that customer number is already in use', 'warning')
            form['number'].data = customer.number

        form.populate_obj(customer)

        db.session.add(customer)
        db.session.commit()
        flash('address updated', 'success')
        return redirect(url_for('customers_page.detail', number=customer.number))

    return render_template('customers/customer-form.html', form=form, customer=customer, theme_choices=theme_choices)


@customers_page.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = CustomerForm(request.form, number=get_next_customer_number())
    theme_choices = [('', '')] + [(x.name, x.name) for x in InvoiceTheme.query.all()]
    form.invoice_theme.choices = theme_choices

    if form.validate_on_submit():
        if Customer.query.filter_by(user_id=current_user.id, number=form.number.data).first():
            flash('The customer number "%s" is already in use' % form.number.data, 'error')
            form.number.data = get_next_customer_number()
            form.number.raw_data = [form.number.data]
        else:
            customer = Customer()
            form.populate_obj(customer)
            customer.user = User.query.get(current_user.id)
            db.session.add(customer)
            db.session.commit()

            flash('address added', 'success')
            return redirect(url_for('customers_page.detail', number=customer.number))

    return render_template('customers/customer-form.html', form=form, customer=None, theme_choices=theme_choices)


@customers_page.route('/')
@login_required
def index():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    return render_template('customers/customers.html', customers=customers)


@customers_page.route('/<number>')
@login_required
def detail(number):
    customer = Customer.query.filter_by(user_id=current_user.id, number=number).first_or_404()
    summary = {}

    for invoice in customer.invoices:
        if not invoice.submitted_date:
            continue

        year = invoice.submitted_date.format('YYYY')
        if year not in summary:
            summary[year] = {'year': year, 'submitted': 0, 'paid': 0}

        summary[year]['submitted'] += invoice.total

        if invoice.paid_date:
            year = invoice.paid_date.paid_date.format('YYYY')
            if year not in summary:
                summary[year] = {'year': year, 'submitted': 0, 'paid': 0}

            summary[year]['paid'] += invoice.total

    # Reformat the dict into a sorted list
    summary = [summary[key] for key in sorted(summary.keys(), reverse=True)]

    return render_template(
        'customers/detail.html',
        customer=customer,
        summary=summary,
        invoices=sorted(customer.invoices, cmp=lambda x,y: cmp(x.submitted_date or arrow.get(0), y.submitted_date or arrow.get(0)))
    )


@customers_page.route('/<number>/delete', methods=["POST"])
@login_required
def delete(number):
    if request.form['validate_delete'].lower() != 'delete':
        flash('Invalid delete request', 'error')
        return redirect(url_for('.detail', number=number))

    customer = Customer.query.filter_by(user_id=current_user.id, number=number).first_or_404()
    if customer.invoices:
        flash("You cannot delete a customer that has invoices", "error")
        return redirect(url_for('.detail', number=number))

    db.session.delete(customer)
    db.session.commit()

    flash("Customer %s deleted successfully" % number, "warning")
    return redirect(url_for('.index'))
