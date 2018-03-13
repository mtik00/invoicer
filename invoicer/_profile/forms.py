from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired
from wtforms.compat import iteritems

from ..models import W3Theme


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = IntegerField('Terms (NET number of days)')
    # w3_theme = SelectField('Site Theme')
    w3_theme_invoice = SelectField('Invoice Theme')

    starting_customer_number = IntegerField('Starting customer number')
    customer_increment = IntegerField('Number of places in between customer numbers')
    index_items_per_page = IntegerField('Number of invoices per page on index page')

    enable_pdf = BooleanField('Enable PDF Generation')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name in ['w3_theme', 'w3_theme_invoice']:
                continue

            field.populate_obj(obj, name)

        obj.w3_theme = W3Theme.query.filter_by(theme=self.w3_theme.data).first()
        obj.w3_theme_invoice = W3Theme.query.filter_by(theme=self.w3_theme_invoice.data).first()
