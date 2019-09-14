import os
from datetime import timedelta

from flask import Flask, current_app, session
from werkzeug.routing import BaseConverter
from flask_migrate import Migrate
from flask_qrcode import QRcode

from .database import db
from .cache import app_cache
from .login_manager import login_manager
from .password import password_hasher

from ._index import index_page
from ._profile import profile_page
from ._units import unit_page
from ._customers import customers_page
from ._login import login_page
from ._invoice import invoice_page
from ._settings import settings_page


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

    instance_path = os.path.abspath(app.instance_path)

    # Load default config and override config from an environment variable
    app.config.update(dict(
        DATABASE=os.path.join(instance_path, 'invoicer.db'),
        SECRET_KEY='development key',  # NOTE: This should be overriden by `application.cfg`
        BACKUP_DIR=instance_path,
        SESSION_TIMEOUT_MINUTES=30,

        # https://www.w3schools.com/w3css/w3css_color_themes.asp
        # Replace this with the short name (e.g. w3-theme-cyan --> 'cyan')
        INVOICE_THEME='blue-grey',

        SITE_THEME='black',
        SITE_THEME_TOP='#777777',
        SITE_THEME_BOTTOM='#777777',

        # You must add this to your configuration to enable PDF functionality
        WKHTMLTOPDF=None,

        EMAIL_FROM=None,
        EMAIL_USERNAME=None,
        EMAIL_PASSWORD=None,
        EMAIL_SERVER=None,
        EMAIL_STARTTLS=True,

        DEFAULT_TERMS=30
    ))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('INVOICER_SETTINGS', silent=True)

    app.config.from_pyfile(os.path.join(instance_path, 'application.cfg'), silent=True)
    password_hasher.reset(**app.config.get('ARGON2_CONFIG', {}))

    app.url_map.converters['regex'] = RegexConverter

    app.register_blueprint(index_page)
    app.register_blueprint(profile_page, url_prefix='/profile')
    app.register_blueprint(unit_page, url_prefix='/units')
    app.register_blueprint(customers_page, url_prefix='/customers')
    app.register_blueprint(invoice_page, url_prefix='/invoice')
    app.register_blueprint(settings_page, url_prefix='/settings')
    app.register_blueprint(login_page)

    if app.config.get('SESSION_TIMEOUT_MINUTES'):
        app.before_request(make_session_permanent)

    db.init_app(app)
    app.db = db
    Migrate(app, db)
    QRcode(app)

    cache_config = app.config.get('CACHE_CONFIG') or {'CACHE_TYPE': 'simple'}
    app_cache.init_app(app, config=cache_config)

    login_manager.init_app(app)

    return app
