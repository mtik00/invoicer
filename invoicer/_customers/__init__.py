from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..common import login_required, color_themes
from ..models import Customer, Invoice, Profile
from ..database import db
from .forms import CustomerForm

customers_page = Blueprint('customers_page', __name__, template_folder='templates')


def customer_has_invoices(customer_id):
    return Invoice.query.filter(Customer.id == 1).count() > 0


def get_next_customer_number(starting=4000, increment=10):
    numbers = [round(float(x.number), -1) for x in Customer.query.all()]

    customer_number = starting
    for number in numbers:
        if number > customer_number:
            customer_number = number

    return int(customer_number + increment)


def get_customer(customer_id):
    return Customer.query.get(customer_id)


@customers_page.route('/<customer_id>/update', methods=["GET", "POST"])
@login_required
def update(customer_id):
    customer = Customer.query.get(customer_id)
    form = CustomerForm(request.form, obj=customer)

    theme_choices = [(x, x) for x in color_themes]
    form.w3_theme.choices = theme_choices

    # if request.method == 'GET':
    #     # Set the default them only for `GET` or the value will never change.
    #     form.w3_theme.process_data(customer.w3_theme or me.w3_theme)

    if form.validate_on_submit():
        form['state'].data = form['state'].data.upper()

        # Only change the customer number there are no invoices and the new
        # number isn't already taken.
        number = form['number'].data
        if (number != customer.number) and customer_has_invoices(customer_id):
            flash('cannot change customer numbers if they have invoices', 'warning')
            form['number'].data = customer.number
        elif (number != customer.number) and Customer.query.filter(Customer.number == number):
            flash('that customer number is already in use', 'warning')
            form['number'].data = customer.number

        form.populate_obj(customer)
        db.session.add(customer)
        db.session.commit()
        flash('address updated', 'success')
        return redirect(url_for('customers_page.index'))

    return render_template('customers/customer_form.html', form=form, customer_id=customer_id)


@customers_page.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = CustomerForm(request.form, number=get_next_customer_number())
    form.w3_theme.choices = [(x, x) for x in color_themes]

    if form.validate_on_submit():
        customer = Customer()
        form.populate_obj(customer)
        db.session.add(customer)
        db.session.commit()

        flash('address added', 'success')
        return redirect(url_for('customers_page.index'))

    return render_template('customers/customer_form.html', form=form)


@customers_page.route('/')
@login_required
def index():
    customers = Customer.query.all()
    return render_template('customers/customers.html', customers=customers)