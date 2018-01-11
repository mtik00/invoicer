from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class InvoiceForm(FlaskForm):
    description = StringField(u'Description', validators=[DataRequired()])
    customer = SelectField(u'Bill To Address', coerce=int)
    submitted_date = StringField(u'Submitted Date', id="datepicker1")
    paid_date = StringField(u'Paid Date', id="datepicker2")