from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from ..common import login_required, color_themes
from ..models import Profile, User
from ..database import db
from .forms import ProfileForm

profile_page = Blueprint('profile_page', __name__, template_folder='templates')


@profile_page.route('/')
@login_required
def index():
    profile = Profile.query.get(1)
    return render_template('profile/index.html', profile=profile)


@profile_page.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
    user = User.query.get(session['user_id'])
    # profile = user.profile
    form = ProfileForm(request.form, obj=user.profile)

    theme_choices = [(x, x) for x in color_themes]
    form.w3_theme.choices = theme_choices
    form.w3_theme_invoice.choices = theme_choices

    if request.method == 'GET':
        # Set the default them only for `GET` or the value will never change.
        form.w3_theme.process_data(user.profile.w3_theme if user.profile else 'blue-grey')
        form.w3_theme_invoice.process_data(user.profile.w3_theme_invoice if user.profile else 'dark-grey')

    if form.validate_on_submit():
        if 'cancel' in request.form:
            flash('invoice updated canceled', 'warning')
        else:
            if not user.profile:
                user.profile = Profile()

            form['state'].data = form['state'].data.upper()
            form.populate_obj(user.profile)

            db.session.add(user)
            db.session.commit()

            if user.profile.w3_theme:
                current_app.config['W3_THEME'] = user.profile.w3_theme

            flash('profile updated', 'success')
        return redirect(url_for('profile_page.index'))

    return render_template('profile/profile_form.html', form=form, profile=user.profile)
