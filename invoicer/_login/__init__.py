from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app,
    session)

from .forms import LoginForm
from ..common import login_required
from ..password import verify_password
from ..models import User

login_page = Blueprint('login_page', __name__, template_folder='templates')


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = False
    hashed_password = ''

    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if not user:
            error = True
        else:
            hashed_password = user.hashed_password

        try:
            verify_password(hashed_password, form.password.data)
        except Exception:
            error = True

        if error:
            flash('Invalid username and/or password', 'error')
            return redirect(url_for('.login'), code=401)
        else:
            if not error:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['user_debug'] = user.application_settings.debug_mode
                current_app.config['BS4_THEME'] = user.profile.bs4_theme

                flash('You were logged in', 'success')

                if 'next' in request.form:
                    return redirect(request.form['next'])

                return redirect(url_for('index_page.dashboard'))
    elif form.errors:
        flash(', '.join(form.errors), 'error')

    return render_template('login/login.html', form=form)


@login_page.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('You were logged out', 'success')
    return redirect(url_for('.login'))
