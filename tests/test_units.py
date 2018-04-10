from flask import url_for


def test_index(client, user2):
    '''Test UnitPrice index'''
    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200
    assert 'User2 Unit Price' in response.data
    assert 'Units: hr' in response.data
    assert 'Price: $99.99' in response.data


def test_update(client, user2):
    '''Can update a UnitPrice'''
    response = client.post(
        url_for('unit_page.update', unit_id=7),
        data=dict(
            description='User2 Unit Price',
            unit_price=99.99,
            units='hour'
        )
    )

    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200

    assert 'Units: hour' in response.data


def test_create(client, user2):
    '''Can create a UnitPrice'''
    response = client.post(
        url_for('unit_page.create'),
        data=dict(
            description='User2: A new unit price',
            unit_price=499.00,
            units='day'
        )
    )

    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200

    assert 'User2: A new unit price' in response.data
    assert 'Units: day' in response.data
    assert 'Price: $499.00' in response.data


def test_delete(client, user2):
    '''Can delete a UnitPrice'''
    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200
    assert 'User2: A new unit price' in response.data

    # This should not work since we don't have 'validate_delete'
    response = client.post(
        url_for('unit_page.delete', unit_id=8),
    )

    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200
    assert 'User2: A new unit price' in response.data

    # Now really delete it
    response = client.post(
        url_for('unit_page.delete', unit_id=8),
        data={'validate_delete': 'delete'}
    )

    response = client.get(url_for('unit_page.index'))
    assert response.status_code == 200
    assert 'User2: A new unit price' not in response.data


def test_delete_otheruser(client, user2):
    '''User2 can't delete user1's UnitPrice'''
    response = client.post(
        url_for('unit_page.delete', unit_id=1),
        data={'validate_delete': 'delete'}
    )
    assert response.status_code == 404


def test_update_otheruser(client, user2):
    '''User2 can't delete user1's UnitPrice'''
    response = client.post(
        url_for('unit_page.update', unit_id=1),
        data=dict(
            description='User2 Unit Price',
            unit_price=99.99,
            units='hour'
        )
    )

    assert response.status_code == 404
