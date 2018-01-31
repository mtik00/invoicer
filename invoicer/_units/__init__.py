from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, session)
from ..common import login_required
from ..models import UnitPrice, User
from ..database import db
from .forms import UnitForm

unit_page = Blueprint('unit_page', __name__, template_folder='templates')


@unit_page.route('/')
@login_required
def index():
    units = UnitPrice.query.filter_by(user_id=session['user_id']).all()
    return render_template('units/index.html', units=units)


@unit_page.route('/<unit_id>/update', methods=["GET", "POST"])
@login_required
def update(unit_id):
    unit = UnitPrice.query.filter_by(user_id=session['user_id'], id=unit_id).first_or_404()
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

        return redirect(url_for('.index'))

    return render_template('units/unit_form.html', form=form, unit=unit)


@unit_page.route('/create', methods=["GET", "POST"])
@login_required
def create():
    form = UnitForm(request.form)

    if form.validate_on_submit():
        unit = UnitPrice()
        form.populate_obj(unit)
        unit.user = User.query.get(session['user_id'])
        db.session.add(unit)
        db.session.commit()

        flash('unit added', 'success')
        return redirect(url_for('.index'))

    return render_template('units/unit_form.html', form=form)


@unit_page.route('/<unit_id>/delete', methods=["POST"])
@login_required
def delete(unit_id):
    if request.form['validate_delete'].lower() != 'delete':
        flash('Invalid delete request', 'error')
        return redirect(url_for('.index'))

    unit = UnitPrice.query.filter_by(user_id=session['user_id'], id=unit_id).first_or_404()

    db.session.delete(unit)
    db.session.commit()

    flash("Unit deleted successfully", "warning")
    return redirect(url_for('.index'))
