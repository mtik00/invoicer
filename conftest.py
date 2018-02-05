import pytest
from invoicer import app as the_app
from invoicer.database import init_db


@pytest.fixture
def app():
    the_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    the_app.config['WTF_CSRF_ENABLED'] = False

    with the_app.app_context():
        init_db(sample_data=True, apply_migrations=False)

    return the_app
