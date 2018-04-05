from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, session,
    abort)

from flask_login import login_user, logout_user, login_required, current_user

from ..common import is_safe_url
from ..password import verify_password, hash_password
from ..models import User
from ..logger import AUTH_LOG
from ..database import db
from .forms import LoginForm, TwoFAEnableForm


login_page = Blueprint('login_page', __name__, template_folder='templates')


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('index_page.dashboard'))

    form = LoginForm(request.form)
    error = False
    hashed_password = ''

    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data[:1024]).first()
        hashed_password = user.hashed_password if user else ''

        try:
            verify_password(hashed_password, form.password.data[:1024])
        except Exception:
            error = True

        if error:
            # NOTE: You must not change this format without changing the
            # fail2ban filter.
            AUTH_LOG.error(
                "Invalid login for username [{0}] from [{1}]".format(
                    form.username.data[:1024],
                    request.remote_addr)
            )

            flash('Invalid username and/or password', 'error')
            return redirect(url_for('.login'), code=401)

        if not user.is_active:
            flash('You account is not active', 'error')
            return redirect(url_for('.login'), code=401)

        if getattr(user, 'rehash_password', False):
            user.hashed_password = hash_password(form.password.data[:1024])
            user.rehash_password = False
            db.session.add(user)
            db.session.commit()

        if user.totp_enabled:
            session['user_id'] = user.id
            return redirect(url_for('.two_fa'))

        return complete_login(user)
    elif form.errors:
        flash(', '.join(form.errors), 'error')

    return render_template('login/login.html', form=form)


@login_page.route('/logout')
@login_required
def logout():
    current_user.is_authenticated = False
    db.session.commit()
    session.pop('logged_in', None)
    session.pop('user_id', None)
    logout_user()
    flash('You were logged out', 'success')
    return redirect(url_for('.login'))


@login_page.route('/2fa', methods=['GET', 'POST'])
def two_fa():
    user = User.query.get(session['user_id'])
    form = TwoFAEnableForm()

    if form.validate_on_submit():
        if current_user.verify_totp(form.token.data):
            return complete_login(user)
        else:
            flash('Invalid 2FA token', 'error')
            form.token.errors = ['Invalid 2FA token']

    return render_template('login/2fa.html', form=form)


def complete_login(user):
    login_user(user)
    current_user.is_authenticated = True
    db.session.commit()

    session['logged_in'] = True
    session['user_debug'] = user.application_settings.debug_mode
    session['site_theme'] = user.profile.site_theme.name if user.profile.site_theme else 'black'
    session['site_theme_top'] = user.profile.site_theme.top if user.profile.site_theme else '#777777'
    session['site_theme_bottom'] = user.profile.site_theme.bottom if user.profile.site_theme else '#777777'

    flash('You were logged in', 'success')

    next_url = request.form.get('next')
    if not is_safe_url(next_url):
        return abort(400)

    return redirect(next_url or url_for('index_page.dashboard'))
