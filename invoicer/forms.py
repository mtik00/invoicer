from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class AddressForm(FlaskForm):
    name1 = StringField('name1', validators=[DataRequired()])
    name2 = StringField('name2')
    addrline1 = StringField('addrline1', validators=[DataRequired()])
    addrline2 = StringField('addrline2')
    city = StringField('city', validators=[DataRequired()])
    state = StringField('state', validators=[DataRequired()])
    zipcode = StringField('zipcode', validators=[DataRequired()])
    email = StringField('email')
    terms = StringField('terms')


class InvoiceForm(FlaskForm):
    description = StringField(u'description', validators=[DataRequired()])
    to_address = SelectField(u'to_address', coerce=int)