import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, ValidationError


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = StringField('Terms')
    w3_theme = SelectField('Theme')

    def validate_terms(form, field):
        if field.data and (not re.search('\d+\s*?days', field.data, re.IGNORECASE)):
            raise ValidationError('Terms must be in the form: ...## days... (e.g. NET 45 days)')
