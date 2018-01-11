from argon2 import PasswordHasher
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session

from ..common import login_required

login_page = Blueprint('login_page', __name__, template_folder='templates')


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            ph = PasswordHasher()
            ph.verify(current_app.config['PASSWORD_HASH'], request.form['password'])
        except Exception:
            error = 'Invalid username/password'

        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username/password'

        if not error:
            session['logged_in'] = True
            flash('You were logged in', 'success')

            if 'next' in request.form:
                return redirect(request.form['next'])

            return redirect(url_for('index'))

    return render_template('login/login.html', error=error)


@login_page.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'info')
    return redirect(url_for('index'))
