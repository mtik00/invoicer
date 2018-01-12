from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional


class CustomerForm(FlaskForm):
    name1 = StringField('Name 1*', validators=[DataRequired()])
    name2 = StringField('Name 2')
    addrline1 = StringField('Address Line 1*', validators=[DataRequired()])
    addrline2 = StringField('Address Line 2')
    city = StringField('City*', validators=[DataRequired()])
    state = StringField('State*', validators=[DataRequired()])
    zip = StringField('Zipcode*', validators=[DataRequired()])
    email = StringField('Email')
    terms = IntegerField('Terms', validators=[Optional()])
    number = IntegerField('Number*', validators=[DataRequired()])
    w3_theme = SelectField('Default Invoice Theme')
