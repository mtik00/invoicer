from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=1024)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=1024)])


class TwoFAEnableForm(FlaskForm):
    token = StringField('2FA Token', validators=[DataRequired(), Regexp('\d{6}', message='Token must be 6 digits')])
