from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from ..common import login_required
from ..models import Address
from ..database import db
from .forms import ProfileForm

profile_page = Blueprint('profile_page', __name__, template_folder='templates')


color_themes = [
    'red', 'pink', 'purple', 'deep-purple', 'blue', 'light-blue', 'cyan', 'teal',
    'green', 'light-green', 'lime', 'khaki', 'yellow', 'amber', 'orange',
    'deep-orange', 'blue-grey', 'brown', 'grey', 'dark-grey', 'black'
]


@profile_page.route('/')
@login_required
def index():
    profile = Address.query.get(1)
    return render_template('profile/index.html', profile=profile)


@profile_page.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
    profile = Address.query.get(1)
    form = ProfileForm(request.form, obj=profile)

    theme_choices = [(x, x) for x in color_themes]
    form.w3_theme.choices = theme_choices

    if request.method == 'GET':
        # Set the default them only for `GET` or the value will never change.
        form.w3_theme.process_data(profile.w3_theme)

    if form.validate_on_submit():
        form['state'].data = form['state'].data.upper()
        form.populate_obj(profile)

        db.session.add(profile)
        db.session.commit()

        current_app.config['W3_THEME'] = profile.w3_theme

        flash('profile updated', 'success')
        return redirect(url_for('profile_page.index'))

    return render_template('profile/profile_form.html', form=form)
