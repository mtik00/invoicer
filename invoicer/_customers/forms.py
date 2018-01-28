from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional
from wtforms.compat import iteritems

from ..models import W3Theme


class CustomerForm(FlaskForm):
    name1 = StringField('Name 1*', validators=[DataRequired()])
    name2 = StringField('Name 2')
    addrline1 = StringField('Address Line 1*', validators=[DataRequired()])
    addrline2 = StringField('Address Line 2')
    city = StringField('City*', validators=[DataRequired()])
    state = StringField('State*', validators=[DataRequired()])
    zip = StringField('Zipcode*', validators=[DataRequired()])
    email = StringField('Email')
    terms = IntegerField('Terms', validators=[Optional()])
    number = IntegerField('Number*', validators=[DataRequired()])
    w3_theme = SelectField('Default Invoice Theme')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name == 'w3_theme':
                continue

            field.populate_obj(obj, name)

        obj.w3_theme = W3Theme.query.filter_by(theme=self.w3_theme.data).first()
