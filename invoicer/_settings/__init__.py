from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, session)
from flask_login import login_required, current_user

from ..models import User, ApplicationSettings
from ..database import db
from .forms import SettingsForm

settings_page = Blueprint('settings_page', __name__, template_folder='templates')


@settings_page.route('/')
@login_required
def index():
    settings = User.query.get(current_user.id).application_settings
    return render_template('settings/index.html', settings=settings)


@settings_page.route('/<settings_id>/update', methods=["GET", "POST"])
@login_required
def update(settings_id):
    user = User.query.get(current_user.id)
    settings = ApplicationSettings.query.filter_by(id=user.application_settings_id).first_or_404()
    form = SettingsForm(request.form, obj=settings)

    if form.validate_on_submit():
        if 'cancel' in request.form:
            flash('settings updated canceled', 'warning')
        else:
            form.populate_obj(settings)
            db.session.add(settings)
            db.session.commit()
            flash('settings updated', 'success')

            session['user_debug'] = settings.debug_mode

        return redirect(url_for('settings_page.index'))

    return render_template('settings/settings_form.html', form=form, settings=settings)
