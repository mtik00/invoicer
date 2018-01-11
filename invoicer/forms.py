from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired


class EmptyForm(FlaskForm):
    pass


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = StringField('Terms')


class InvoiceForm(FlaskForm):
    description = StringField(u'Description', validators=[DataRequired()])
    customer = SelectField(u'Bill To Address', coerce=int)
    submitted_date = StringField(u'Submitted Date', id="datepicker1")
    paid_date = StringField(u'Paid Date', id="datepicker2")


class ItemForm(FlaskForm):
    date = StringField(u'Date', validators=[DataRequired()], id="datepicker")
    description = StringField(u'Description', validators=[DataRequired()])
    unit_price = SelectField(u'Unit Price', coerce=int)
    quantity = IntegerField(u'Quantity', validators=[DataRequired()])


class UnitForm(FlaskForm):
    description = StringField(u'Description', validators=[DataRequired()])
    unit_price = FloatField(u'Unit Price', validators=[DataRequired()])
    units = StringField(u'Units (e.g. hr, day, etc)')