import re
from urlparse import urlparse

from flask import url_for, session


def test_login_everywhere(client, app):
    """
    Everything except /login and /static should require a login.
    """

    login_url = url_for('login_page.login')

    # Only test the 'GET' methods here; 'POST' is more complicated
    for rule in app.url_map.iter_rules():
        if re.search('login|static', rule.endpoint, re.IGNORECASE):
            continue
        elif 'GET' not in rule.methods:
            print "skipping [%s]; no GET method" % rule
            continue

        options = {}
        for arg in rule.arguments:
            if arg == "invoice_number":
                options[arg] = "1111-2222-3333"
            else:
                options[arg] = "1"

        url = url_for(rule.endpoint, **options)
        response = client.get(url)

        print "testing:", url
        assert response.status_code != 404, "url was not found: %s" % url
        assert urlparse(response.location).path == login_url, "url wasn't the login page: %s" % url


def test_admin_login(client):
    login_url = url_for('login_page.login')
    client.post(login_url, data=dict(username='admin', password='default'))

    assert session.get('user_id', 0) == '1'
    assert session.get('logged_in') is True

    # Make sure we can log out
    logout_url = url_for('login_page.logout')
    client.get(logout_url)
    assert 'user_id' not in session
    assert 'logged_in' not in session


def test_user2_login(client):
    login_url = url_for('login_page.login')
    client.post(login_url, data=dict(username='user2', password='user2'))

    assert session.get('user_id', 0) == '2'
    assert session.get('logged_in') is True

    # Make sure we can log out
    logout_url = url_for('login_page.logout')
    client.get(logout_url)
    assert 'user_id' not in session
    assert 'logged_in' not in session
