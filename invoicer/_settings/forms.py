from flask_wtf import FlaskForm
from wtforms import BooleanField


class SettingsForm(FlaskForm):
    debug_mode = BooleanField('Debug mode')
