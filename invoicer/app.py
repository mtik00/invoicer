import os
from datetime import timedelta

from flask import Flask, current_app, session
from werkzeug.routing import BaseConverter

from .database import db

from .models import Profile
from ._profile import profile_page
from ._units import unit_page
from ._customers import customers_page
from ._login import login_page
from ._invoice import invoice_page


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def make_session_permanent():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=current_app.config.get('SESSION_TIMEOUT_MINUTES'))


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)

    # Load default config and override config from an environment variable
    app.config.update(dict(
        DATABASE=os.path.join(app.instance_path, 'invoicer.db'),
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD_HASH='$argon2i$v=19$m=512,t=2,p=2$+w4dAmcJGnaqsgob82pqcQ$4uGfP7JerZJPqAq5cWZ0bw',  # 'default'
        WKHTMLTOPDF="c:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe",
        BACKUP_DIR=app.instance_path,
        SESSION_TIMEOUT_MINUTES=30,

        # https://www.w3schools.com/w3css/w3css_color_themes.asp
        # Replace this with the short name (e.g. w3-theme-cyan --> 'cyan')
        W3_THEME='blue-grey',

        EMAIL_USERNAME=None,
        EMAIL_PASSWORD=None,
        EMAIL_SERVER=None
    ))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('INVOICER_SETTINGS', silent=True)
    app.config.from_pyfile(os.path.join(app.instance_path, 'application.cfg'), silent=True)
    app.url_map.converters['regex'] = RegexConverter

    app.register_blueprint(profile_page, url_prefix='/profile')
    app.register_blueprint(unit_page, url_prefix='/units')
    app.register_blueprint(customers_page, url_prefix='/customers')
    app.register_blueprint(invoice_page, url_prefix='/invoice')
    app.register_blueprint(login_page)

    if app.config.get('SESSION_TIMEOUT_MINUTES'):
        app.before_request(make_session_permanent)

    db.init_app(app)

    with app.app_context():
        try:
            profile = Profile.query.first()
            if profile:
                app.config['W3_THEME'] = profile.w3_theme or app.config['W3_THEME']
        except Exception:
            app.config['W3_THEME'] = 'dark-grey'

    return app
