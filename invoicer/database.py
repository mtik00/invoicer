import json
import string

import arrow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import init, migrate

from .password import hash_password

db = SQLAlchemy()

# Default theme data ##########################################################
site_themes = {
    'black': {'top': '#777777', 'bottom': '#777777'},
    'blue': {'top': '#1F77D0', 'bottom': '#533CE1'},
    'azure': {'top': '#1DC7EA', 'bottom': '#4091FF'},
    'green': {'top': '#87CB16', 'bottom': '#6DC030'},
    'orange': {'top': '#FFA534', 'bottom': '#FF5221'},
    'red': {'top': '#FB404B', 'bottom': '#BB0502'},
    'purple': {'top': '#9368E9', 'bottom': '#943BEA'},
}

# See here https://www.w3schools.com/w3css/w3css_color_themes.asp
# `banner` is `w3-theme-d1`, and `table_header` is `w3-theme`
color_theme_data = {
    'red': {
        'banner_color': '#fff', 'banner_background_color': '#f32617',
        'table_header_color': '#fff', 'table_header_background_color': '#f44336',
    },
    'khaki': {
        'banner_color': '#fff', 'banner_background_color': '#ecdf6c',
        'table_header_color': '#000', 'table_header_background_color': '#f0e68c',
    },
    'blue-grey': {
        'banner_color': '#fff', 'banner_background_color': '#57707d',
        'table_header_color': '#fff', 'table_header_background_color': '#607d8b',
    },
    'indigo': {
        'banner_color': '#fff', 'banner_background_color': '#3949a3',
        'table_header_color': '#fff', 'table_header_background_color': '#3f51b5',
    },
    'teal': {
        'banner_color': '#fff', 'banner_background_color': '#008578',
        'table_header_color': '#fff', 'table_header_background_color': '#009688',
    },
    'deep-orange': {
        'banner_color': '#fff', 'banner_background_color': '#ff4107',
        'table_header_color': '#fff', 'table_header_background_color': '#ff5722',
    },
    'dark-grey': {
        'banner_color': '#fff', 'banner_background_color': '#575757',
        'table_header_color': '#fff', 'table_header_background_color': '#616161',
    },
}
###############################################################################


def init_db(sample_data=False, apply_migrations=False):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import invoicer.models
    import models
    db.drop_all()
    db.create_all()

    for name, data in site_themes.items():
        db.session.add(models.SiteTheme(name=name, **data))

    for name, data in color_theme_data.items():
        db.session.add(models.InvoiceTheme(name=name, **data))

    if apply_migrations:
        try:
            init()
        except Exception:
            pass

        try:
            migrate()
        except Exception:
            pass

    if sample_data:
        profile = models.Profile(
            full_name='Tom Smith', email='me@example.com',
            street='1313 Mockingbird Ln', city='New York',
            state='NY', zip='11111', terms=45,
            site_theme=models.SiteTheme.query.filter_by(name='black').first(),
        )

        user = models.User(
            username='admin',
            hashed_password=hash_password('default'),
            profile=profile,
            application_settings=models.ApplicationSettings(
                debug_mode=False,
            ),
        )

        customer1 = models.Customer(
            name1='Some Employer', addrline1='111 9th Ave N', city='New York',
            state='NY', zip='11222', email='boss|mike|larry@example.com',
            terms=30, number=1010, user=user)

        invoice1 = models.Invoice(
            customer=customer1,
            submitted_date=arrow.get('20-JAN-2018', 'DD-MMM-YYYY'),
            description='2018 Website Redesign',
            number='1010-2018-001',
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

        lots_of_items_count = 40
        lots_of_items_cost = 50
        invoice3 = models.Invoice(
            customer=customer1,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='1010-2018-003',
            terms=22,
            user=user)

        lots_of_items = []
        item_date = arrow.get('01-MAR-2018', 'DD-MMM-YYYY')
        for x in range(lots_of_items_count):
            lots_of_items.append(
                models.Item(
                    date=item_date,
                    description='Website maintenance', unit_price=lots_of_items_cost, units='hr',
                    quantity=8, invoice=invoice3, customer=customer1
                )
            )
            item_date = item_date.replace(days=+1)

        db.session.add_all(lots_of_items)

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

        profile2 = models.Profile(
            full_name='John Doe', email='j.doe@____.com',
            street='1313 Mockingbird Ln', city='New York',
            state='NY', zip='11111', terms=45,
            site_theme=models.SiteTheme.query.filter_by(name='orange').first(),
        )

        user2 = models.User(
            username='user2',
            hashed_password=hash_password('default'),
            profile=profile,
            application_settings=models.ApplicationSettings(
                debug_mode=False,
            ),
        )

        user2_customer1 = models.Customer(
            name1='Employer #3', addrline1='1234 45th St', city='New York',
            state='NY', zip='11133', email='billing@example.com', number=1010,
            user=user2)

        user2_invoice1 = models.Invoice(
            customer=user2_customer1,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='1010-2018-001',
            terms=45,
            user=user2)

        db.session.add_all([
            models.Item(
                date=arrow.get('01-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=user2_invoice1, customer=user2_customer1
            ),
            models.Item(
                date=arrow.get('04-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=user2_invoice1, customer=user2_customer1
            ),
            models.Item(
                date=arrow.get('05-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=user2_invoice1, customer=user2_customer1
            ),
            models.Item(
                date=arrow.get('06-MAR-2018', 'DD-MMM-YYYY'),
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=user2_invoice1, customer=user2_customer1
            ),
        ])

        db.session.add_all([profile2, user2, user2_customer1, user2_invoice1])

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

    profile = models.Profile()

    user = models.User(
        username=username,
        hashed_password=hashed_password,
        profile=profile
    )

    default_settings = models.ApplicationSettings(debug_mode=False)

    user.application_settings = default_settings

    db.session.add(user)
    db.session.commit()
