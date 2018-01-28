from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, IntegerField


class SettingsForm(FlaskForm):
    debug_mode = BooleanField('Debug mode')
