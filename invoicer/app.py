import os
from flask import Flask
from .database import db


from ._profile import profile_page
from ._units import unit_page
from ._customers import customers_page
from ._login import login_page


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

        EMAIL_USERNAME=None,
        EMAIL_PASSWORD=None,
        EMAIL_SERVER=None
    ))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config.from_envvar('INVOICER_SETTINGS', silent=True)
    app.config.from_pyfile(os.path.join(app.instance_path, 'application.cfg'), silent=True)
    app.register_blueprint(profile_page, url_prefix='/profile')
    app.register_blueprint(unit_page, url_prefix='/units')
    app.register_blueprint(customers_page, url_prefix='/customers')
    app.register_blueprint(login_page)
    db.init_app(app)
    return app
