from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from ..common import login_required
from ..models import Address
from ..database import db
from .forms import ProfileForm

profile_page = Blueprint('profile_page', __name__, template_folder='templates')


@profile_page.route('/update', methods=["GET", "POST"])
@login_required
def update():
    profile = Address.query.get(1)
    form = ProfileForm(request.form, obj=profile)

    if form.validate_on_submit():
        form['state'].data = form['state'].data.upper()
        form.populate_obj(profile)
        db.session.add(profile)
        db.session.commit()

        g._userinfo = profile
        flash('profile updated', 'success')
        return redirect(url_for('profile_page.update'))

    return render_template('profile/profile_form.html', form=form)
