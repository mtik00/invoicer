from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired


class EmptyForm(FlaskForm):
    pass


class ItemForm(FlaskForm):
    date = StringField(u'Date', validators=[DataRequired()], id="datepicker")
    description = StringField(u'Description', validators=[DataRequired()])
    unit_price = SelectField(u'Unit Price', coerce=int)
    quantity = IntegerField(u'Quantity', validators=[DataRequired()])


class UnitForm(FlaskForm):
    description = StringField(u'Description', validators=[DataRequired()])
    unit_price = FloatField(u'Unit Price', validators=[DataRequired()])
    units = StringField(u'Units (e.g. hr, day, etc)')