import re
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, ValidationError


class CustomerForm(FlaskForm):
    name1 = StringField('Name 1*', validators=[DataRequired()])
    name2 = StringField('Name 2')
    addrline1 = StringField('Address Line 1*', validators=[DataRequired()])
    addrline2 = StringField('Address Line 2')
    city = StringField('City*', validators=[DataRequired()])
    state = StringField('State*', validators=[DataRequired()])
    zip = StringField('Zipcode*', validators=[DataRequired()])
    email = StringField('Email')
    terms = StringField('Terms')
    number = IntegerField('Number*', validators=[DataRequired()])

    def validate_terms(form, field):
        if field.data and (not re.search('\d+\s*?days', field.data, re.IGNORECASE)):
            raise ValidationError('Terms must be in the form: ...## days... (e.g. NET 45 days)')
