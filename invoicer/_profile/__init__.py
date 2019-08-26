import pyotp
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user

from ..models import Profile, User, InvoiceTheme, SiteTheme
from ..database import db
from ..cache import app_cache
from .forms import ProfileForm, TwoFAEnableForm

profile_page = Blueprint('profile_page', __name__, template_folder='templates')


@app_cache.cached(key_prefix='bs4_color_themes')
def bs4_color_themes():
    return [x.name for x in SiteTheme.query.all()]


@app_cache.cached(key_prefix='invoice_themes')
def get_color_theme_data():
    '''
    Convert the invoice theme data into something a bit more usable.
    '''
    result = {}
    for theme in InvoiceTheme.query.all():
        result[theme.name] = {
            'banner_color': theme.banner_color,
            'banner_background_color': theme.banner_background_color,
            'table_header_color': theme.table_header_color,
            'table_header_background_color': theme.table_header_background_color
        }

    return result


@profile_page.route('/')
@login_required
def index():
    profile = User.query.get(current_user.id).profile
    return render_template('profile/index.html', profile=profile)


@profile_page.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
    user = User.query.get(current_user.id)
    form = ProfileForm(request.form, obj=user.profile)

    site_theme_choices = [(x, x) for x in bs4_color_themes()]
    form.site_theme.choices = site_theme_choices

    theme_choices = [('', '')] + [(x, x) for x in get_color_theme_data().keys()]
    form.invoice_theme.choices = theme_choices

    default_user_theme = session['site_theme']
    if user.profile and user.profile.site_theme:
        default_user_theme = user.profile.site_theme.name

    default_invoice_theme = ''
    if user.profile and user.profile.invoice_theme:
        default_invoice_theme = user.profile.invoice_theme.name

    if request.method == 'GET':
        # Set the default them only for `GET` or the value will never change.
        form.site_theme.process_data(default_user_theme)
        form.invoice_theme.process_data(default_invoice_theme)
    elif form.validate_on_submit():
        if 'cancel' in request.form:
            flash('profile updated canceled', 'warning')
        else:
            if not user.profile:
                user.profile = Profile()

            form.populate_obj(user.profile)

            db.session.add(user)
            db.session.commit()

            if user.profile.invoice_theme:
                session['invoice_theme'] = user.profile.invoice_theme.name

            if user.profile.site_theme:
                session['site_theme'] = user.profile.site_theme.name
                session['site_theme_top'] = user.profile.site_theme.top
                session['site_theme_bottom'] = user.profile.site_theme.bottom

            flash('profile updated', 'success')
        return redirect(url_for('profile_page.index'))

    return render_template(
        'profile/profile_form.html', form=form, profile=user.profile,
        theme_choices=theme_choices, site_theme_choices=site_theme_choices)


@profile_page.route('/enable-2fa', methods=["GET", "POST"])
@login_required
def enable_2fa():
    if 'cancel' in request.form:
        current_user.totp_secret = None
        current_user.totp_enabled = False
        db.session.commit()

        flash('2FA enable canceled', 'warning')
        return redirect(url_for('profile_page.index'))

    if not current_user.totp_secret:
        current_user.totp_secret = pyotp.random_base32()
        db.session.commit()

    qr_uri = current_user.get_totp_uri()
    form = TwoFAEnableForm(request.form, qr_uri=qr_uri)

    if form.validate_on_submit():
        if current_user.verify_totp(form.token.data):
            current_user.totp_enabled = True
            db.session.commit()
            flash('2FA authentication enabled', 'success')
            return redirect(url_for('profile_page.index'))
        else:
            flash('Invalid 2FA token', 'error')
            form.token.errors = ['Invalid 2FA token']

    return render_template(
        'profile/enable_2fa.html', qr_uri=qr_uri, form=form
    ), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }


@profile_page.route('/disable-2fa', methods=["POST"])
@login_required
def disable_2fa():
    '''Disables 2FA'''

    # Re-generate the secret so the next time they enable 2FA it's different
    current_user.totp_secret = pyotp.random_base32()
    current_user.totp_enabled = False
    db.session.commit()

    flash('2FA has been disabled', 'warning')
    return redirect(url_for('profile_page.index'))
