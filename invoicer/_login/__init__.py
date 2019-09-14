from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, session)

from flask_login import login_user, logout_user, login_required, current_user

from ..common import is_safe_url
from ..password import verify_password, hash_password
from ..models import User
from ..logger import AUTH_LOG
from ..database import db
from .forms import LoginForm, TwoFAEnableForm


login_page = Blueprint('login_page', __name__, template_folder='templates')


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = get_redirect_target()
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('index_page.dashboard'))

    next_url = get_redirect_target()
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
                "Invalid login for username [%s] from [%s]",
                    form.username.data[:1024],
                    request.remote_addr,
            )

            flash('Invalid username and/or password', 'error')
            return render_template('login/login.html', form=form, next_url=next_url), 401

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
            return redirect(url_for('.two_fa', next=next_url))

        return complete_login(user)
    elif form.errors:
        flash(', '.join(form.errors), 'error')

    return render_template('login/login.html', form=form, next_url=next_url)


@login_page.route('/logout')
@login_required
def logout():
    current_user.is_authenticated = False
    session.pop('logged_in', None)
    session.pop('user_id', None)
    logout_user()
    flash('You were logged out', 'success')
    return redirect(url_for('.login'))


@login_page.route('/2fa', methods=['GET', 'POST'])
def two_fa(next=None):
    next_url = next or get_redirect_target()
    user = User.query.get(session['user_id'])
    form = TwoFAEnableForm()

    if form.validate_on_submit():
        if current_user.verify_totp(form.token.data):
            return complete_login(user)
        else:
            flash('Invalid 2FA token', 'error')
            form.token.errors = ['Invalid 2FA token']

    return render_template('login/2fa.html', form=form, next_url=next_url)


def complete_login(user):
    login_user(user)
    current_user.is_authenticated = True

    session['logged_in'] = True
    session['user_debug'] = user.application_settings.debug_mode
    session['site_theme'] = user.profile.site_theme.name if user.profile.site_theme else 'black'
    session['site_theme_top'] = user.profile.site_theme.top if user.profile.site_theme else '#777777'
    session['site_theme_bottom'] = user.profile.site_theme.bottom if user.profile.site_theme else '#777777'

    flash('You were logged in', 'success')

    return redirect_back('index_page.dashboard')
