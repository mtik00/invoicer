import pytest
from flask import url_for, session
from invoicer import app as the_app
from invoicer.database import init_db

import arrow
import warnings
from arrow.factory import ArrowParseWarning
warnings.simplefilter("ignore", ArrowParseWarning)


@pytest.fixture(scope="module")
def app():
    the_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    the_app.config['WTF_CSRF_ENABLED'] = False

    with the_app.app_context():
        init_db(sample_data=True)

    return the_app


@pytest.fixture
def user1(client):
    login_url = url_for('login_page.login')
    client.post(login_url, data=dict(username='admin', password='default'))
    assert session.get('user_id', 0) == '1'

    yield

    # Make sure we can log out
    client.get(url_for('login_page.logout'))
    assert 'user_id' not in session


@pytest.fixture
def user2(client):
    login_url = url_for('login_page.login')
    client.post(login_url, data=dict(username='user2', password='user2'))
    assert session.get('user_id', 0) == '2'

    yield

    # Make sure we can log out
    client.get(url_for('login_page.logout'))
    assert 'user_id' not in session
