from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session

from .forms import LoginForm
from ..common import login_required
from ..password import password_hasher

login_page = Blueprint('login_page', __name__, template_folder='templates')


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = False

    if form.validate_on_submit():
        try:
            password_hasher.verify(current_app.config['PASSWORD_HASH'], form.password.data)
        except Exception:
            error = True

        if form.username.data != current_app.config['USERNAME']:
            error = True

        if error:
            flash('Invalid username and/or password', 'error')
        else:
            if not error:
                session['logged_in'] = True
                flash('You were logged in', 'success')

                if 'next' in request.form:
                    return redirect(request.form['next'])

                return redirect(url_for('index'))

    return render_template('login/login.html', form=form)


@login_page.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'warning')
    return redirect(url_for('index'))
