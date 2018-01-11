from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired


class UnitForm(FlaskForm):
    description = StringField(u'Description', validators=[DataRequired()])
    unit_price = FloatField(u'Unit Price', validators=[DataRequired()])
    units = StringField(u'Units (e.g. hr, day, etc)')