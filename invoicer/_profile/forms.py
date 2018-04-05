from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Regexp
from wtforms.compat import iteritems

from ..models import InvoiceTheme, SiteTheme


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name*', validators=[DataRequired()])
    email = StringField('Email')
    street = StringField('Street Address')
    city = StringField('City')
    state = StringField('State')
    zip = StringField('Zipcode')
    terms = IntegerField('Terms (NET number of days)')
    site_theme = SelectField('Site Theme')
    invoice_theme = SelectField('Invoice Theme')

    starting_customer_number = IntegerField('Starting customer number')
    customer_increment = IntegerField('Number between customer numbers')
    index_items_per_page = IntegerField('Number of invoices per page on index page')

    enable_pdf = BooleanField('Enable PDF Generation')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name in ['site_theme', 'invoice_theme']:
                continue

            field.populate_obj(obj, name)

        obj.site_theme = SiteTheme.query.filter_by(name=self.site_theme.data).first()
        obj.invoice_theme = InvoiceTheme.query.filter_by(name=self.invoice_theme.data).first()


class TwoFAEnableForm(FlaskForm):
    qr_uri = HiddenField()
    token = StringField('2FA Token', validators=[Regexp('\d{6}', message='Token must be 6 digits')])
