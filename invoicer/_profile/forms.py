from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired
from wtforms.compat import iteritems

from ..models import InvoiceTheme, BS4Theme


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = IntegerField('Terms (NET number of days)')
    bs4_theme = SelectField('Site Theme')
    w3_theme_invoice = SelectField('Invoice Theme')

    starting_customer_number = IntegerField('Starting customer number')
    customer_increment = IntegerField('Number between customer numbers')
    index_items_per_page = IntegerField('Number of invoices per page on index page')

    enable_pdf = BooleanField('Enable PDF Generation')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name in ['bs4_theme', 'w3_theme_invoice']:
                continue

            field.populate_obj(obj, name)

        obj.bs4_theme = BS4Theme.query.filter_by(theme=self.bs4_theme.data).first()
        obj.w3_theme_invoice = InvoiceTheme.query.filter_by(theme=self.w3_theme_invoice.data).first()
