#!/bin/env python2.7
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired


class EmptyForm(FlaskForm):
    pass


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