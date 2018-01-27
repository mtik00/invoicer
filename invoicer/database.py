import json
import string

import arrow
from flask_sqlalchemy import SQLAlchemy

from .password import hash_password

db = SQLAlchemy()


def init_db(sample_data=False):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import invoicer.models
    import models
    db.drop_all()
    db.create_all()

    if sample_data:

        addr = models.Profile(
            full_name='Tom Smith', email='me@example.com',
            street='1313 Mockingbird Ln', city='New York',
            state='NY', zip='11111', terms=45
        )
        user = models.User(
            username='admin',
            hashed_password=hash_password('default'),
            profile=addr
        )
        db.session.add_all([addr, user])

        customer1 = models.Customer(
            name1='Some Employer', addrline1='111 9th Ave N', city='New York',
            state='NY', zip='11222', email='boss|mike|larry@example.com',
            terms=30, number=1010, user=user)

        invoice1 = models.Invoice(
            customer=customer1,
            submitted_date=arrow.get('20-JAN-2018', 'DD-MMM-YYYY'),
            description='2018 Website Redesign',
            number='1010-2018-001',
            total=6400,
            terms=30,
            paid_date=models.InvoicePaidDate(
                paid_date=arrow.get('07-FEB-2018', 'DD-MMM-YYYY'),
                description='Check 1234'),
            user=user
        )

        db.session.add_all([
            models.Item(
                date=arrow.get('01-JAN-2018', 'DD-MMM-YYYY'),
                description='Backend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date=arrow.get('04-JAN-2018', 'DD-MMM-YYYY'),
                description='Backend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-JAN-2018', 'DD-MMM-YYYY'),
                description='Frontend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date=arrow.get('10-JAN-2018', 'DD-MMM-YYYY'),
                description='Frontend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
        ])

        invoice2 = models.Invoice(
            customer=customer1,
            submitted_date=arrow.get('20-FEB-2018-2018', 'DD-MMM-YYYY'),
            description='2018 Website Development',
            paid_date=None,
            number='1010-2018-002',
            total=8000,
            terms=45,
            user=user)

        db.session.add_all([
            models.Item(
                date=arrow.get('01-FEB-2018', 'DD-MMM-YYYY'),
                description='Backend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date=arrow.get('04-FEB-2018', 'DD-MMM-YYYY'),
                description='Backend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date=arrow.get('05-FEB-2018', 'DD-MMM-YYYY'),
                description='Frontend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-FEB-2018', 'DD-MMM-YYYY'),
                description='Frontend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
        ])

        invoice3 = models.Invoice(
            customer=customer1,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='1010-2018-003',
            total=1600,
            terms=22,
            user=user)

        db.session.add_all([
            models.Item(
                date=arrow.get('01-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('04-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('05-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
        ])

        customer2 = models.Customer(
            name1='Employer #2', addrline1='1234 45th St', city='New York',
            state='NY', zip='11133', email='billing@example.com', number=1020,
            user=user)

        invoice4 = models.Invoice(
            customer=customer2,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='1020-2018-001',
            total=2400,
            terms=45,
            user=user)

        db.session.add_all([
            models.Item(
                date=arrow.get('01-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date=arrow.get('04-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date=arrow.get('05-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
        ])

        db.session.add_all([
            models.UnitPrice(description='Design', unit_price=200, units='hr', user=user),
            models.UnitPrice(description='Development', unit_price=250, units='hr', user=user),
            models.UnitPrice(description='Maintenance', unit_price=50, units='hr', user=user),
            models.UnitPrice(description='Employer #2: Design', unit_price=100, units='hr', user=user),
            models.UnitPrice(description='Employer #2: Development', unit_price=150, units='hr'),
            models.UnitPrice(description='Employer #2: Maintenance', unit_price=75, units='hr'),
        ])

        db.session.commit()


def myconverter(o):
    if isinstance(o, arrow.Arrow):
        return o.for_json()


def export(path):
    """
    Exports all of the data (no metadata) to a json file.
    """
    import models
    result = {}

    # May need to change this if it starts being wierd.  This is also dependent
    # on all of the models located in `models`.
    model_names = [x for x in dir(models) if (x[0] in string.uppercase) and ('Type' not in x) and ('Constraint' not in x)]
    if not model_names:
        raise Exception('No model names found in `models`')

    for model in [getattr(models, model_name) for model_name in model_names]:
        items = model.query.all()
        result[model.__tablename__] = [{key: getattr(item, key) for key in model.__table__.columns.keys()} for item in items]

    formatted_json = json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '), default=myconverter)

    with open(path, 'wb') as fh:
        fh.write(formatted_json)


def import_clean_json(path):
    """
    Imports the data in the JSON file.

    NOTE: This is meant to be called with no data in the databse!
    """
    import models
    with open(path) as fh:
        json_data = json.load(fh)

    profiles = json_data.get('profiles', {})
    db.session.add_all([
        models.Profile(**data) for data in profiles
    ])

    users = json_data.get('users', {})
    db.session.add_all([
        models.User(**data) for data in users
    ])

    customers = json_data.get('customers', {})
    db.session.add_all([
        models.Customer(**data) for data in customers
    ])

    paid_dates = json_data.get('invoice_paid_dates', {})
    db.session.add_all([
        models.InvoicePaidDate(**data) for data in paid_dates
    ])

    invoices = json_data.get('invoices', {})
    db.session.add_all([
        models.Invoice(**data) for data in invoices
    ])

    items = json_data.get('items', {})
    db.session.add_all([
        models.Item(**data) for data in items
    ])

    unit_prices = json_data.get('unit_prices', {})
    db.session.add_all([
        models.UnitPrice(**data) for data in unit_prices
    ])

    db.session.commit()


def add_user(username, password):
    """
    Adds a new user to the database.
    """
    import models
    hashed_password = hash_password(password)

    user = models.User(
        username=username,
        hashed_password=hashed_password
    )

    db.session.add(user)
    db.session.commit()
