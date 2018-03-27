from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, session,
    abort)

from .forms import LoginForm
from ..common import login_required, is_safe_url
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
                session['site_theme'] = user.profile.site_theme.name
                session['site_theme_top'] = user.profile.site_theme.top
                session['site_theme_bottom'] = user.profile.site_theme.bottom

                flash('You were logged in', 'success')

                # import pdb; pdb.set_trace()
                next_url = request.form.get('next')
                if not is_safe_url(next_url):
                    return abort(400)

                return redirect(next_url or url_for('index_page.dashboard'))
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
