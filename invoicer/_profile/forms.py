import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = IntegerField('Terms (NET number of days)')
    w3_theme = SelectField('Theme')
