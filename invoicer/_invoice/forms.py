from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional
from wtforms.compat import iteritems

from ..models import InvoiceTheme


class ItemForm(FlaskForm):
    date = StringField(u'Date', validators=[DataRequired()], id="datepicker")
    description = StringField(u'Description', validators=[DataRequired()])
    quantity = IntegerField(u'Quantity', validators=[DataRequired()])


class InvoiceForm(FlaskForm):
    description = StringField(u'Description Of Work', validators=[DataRequired()])
    customer = SelectField(u'Bill To Address', coerce=int)
    submitted_date = StringField(u'Submitted Date', id="datepicker1")
    paid_date = StringField(u'Paid Date', id="datepicker2")
    paid_date_notes = StringField(u'Notes', validators=[Optional()])
    terms = IntegerField(u'Terms (number of days)')
    invoice_theme = SelectField('Theme')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name == 'invoice_theme':
                continue

            field.populate_obj(obj, name)

        obj.invoice_theme = InvoiceTheme.query.filter_by(theme=self.invoice_theme.data).first()
