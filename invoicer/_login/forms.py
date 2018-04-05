from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=1024)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=1024)])
