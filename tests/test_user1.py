import re
import pytest
from flask import url_for, session


@pytest.fixture
def user1(client):
    login_url = url_for('login_page.login')
    client.post(login_url, data=dict(username='admin', password='default'))
    assert session.get('user_id', 0) == 1

    yield

    # Make sure we can log out
    client.get(url_for('login_page.logout'))
    assert 'user_id' not in session


def test_index(client, user1):
    """
    We should have 4 invoices on the index page
    """
    response = client.get(url_for('index_page.index'))
    assert response.status_code == 200
    assert response.data.count('<td>1010-2018') == 3
    assert response.data.count('<td>1020-2018') == 1


def test_invoice1(client, user1):
    """
    Ensure invoice 1 is rendered
    """
    url = url_for('invoice_page.invoice_by_number', invoice_number='1010-2018-001')
    response = client.get(url)
    assert response.status_code == 200

    url = url_for('invoice_page.simplified_invoice', invoice_number='1010-2018-001')
    response = client.get(url)
    assert response.status_code == 200
    assert re.search('Invoice Total:.*.6,400\.00', response.data, re.IGNORECASE)
    assert re.search('.td..6,400\.00./td.', response.data, re.IGNORECASE)


def test_customers(client, user1):
    """
    Ensure user 1 has customers
    """
    url = url_for('customers_page.index')
    response = client.get(url)
    assert response.status_code == 200

    assert re.search('<td>1010</td>', response.data, re.IGNORECASE)
    assert re.search('<td>1020</td>', response.data, re.IGNORECASE)

    # There should be 3 emails for customer 1
    assert re.search('<td>boss@example.com<br>mike@example.com<br>larry@example.com</td>', response.data, re.IGNORECASE)


def test_customer1_detail(client, user1):
    url = url_for('customers_page.detail', number=1010)
    response = client.get(url)
    assert response.status_code == 200

    assert re.search('Annual Summary', response.data, re.IGNORECASE)

    # This customer has 3 invoices
    assert response.data.count('<td>1010-2018') == 3

    # total submitted is 14.4k
    assert re.search('.14,400\.00', response.data, re.IGNORECASE)
