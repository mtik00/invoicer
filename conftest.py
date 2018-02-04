import pytest
from invoicer.app import create_app
from invoicer.database import init_db


@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    with app.app_context():
        init_db(sample_data=True, apply_migrations=False)

    return app
