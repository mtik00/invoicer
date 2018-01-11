from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..common import login_required
from ..models import UnitPrice
from ..database import db
from ..forms import UnitForm

unit_page = Blueprint('unit_page', __name__, template_folder='templates')


@unit_page.route('/')
def units():
    units = UnitPrice.query.all()
    return render_template('units/units.html', units=units)


@unit_page.route('/<unit_id>/update', methods=["GET", "POST"])
def update(unit_id):
    unit = UnitPrice.query.get(unit_id)
    form = UnitForm(request.form, obj=unit)

    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(unit)
            flash('unit deleted', 'warning')
        else:
            form.populate_obj(unit)
            db.session.add(unit)
            flash('unit updated', 'success')

        db.session.commit()

        return redirect(url_for('unit_page.units'))

    return render_template('units/unit_form.html', form=form, unit=unit)


@unit_page.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = UnitForm(request.form)

    if form.validate_on_submit():
        unit = UnitPrice()
        form.populate_obj(unit)
        db.session.add(unit)
        db.session.commit()

        flash('unit added', 'success')
        return redirect(url_for('unit_page.units'))

    return render_template('units/unit_form.html', form=form)
