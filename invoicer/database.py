from flask_sqlalchemy import SQLAlchemy

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
        db.session.add_all([addr])

        customer1 = models.Customer(
            name1='Some Employer', addrline1='111 9th Ave N', city='New York',
            state='NY', zip='11222', email='boss|mike|larry@example.com',
            terms=30, number='4010')

        invoice1 = models.Invoice(
            customer=customer1,
            submitted_date='20-JAN-2018',
            description='2018 Website Redesign',
            paid_date='07-FEB-2018',
            number='4010-2018-001',
            total=6400,
            terms=30)

        db.session.add_all([
            models.Item(
                date='01-JAN-2018',
                description='Backend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date='04-JAN-2018',
                description='Backend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date='06-JAN-2018',
                description='Frontend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
            models.Item(
                date='10-JAN-2018',
                description='Frontend design', unit_price=200.0, units='hr',
                quantity=8, invoice=invoice1, customer=customer1
            ),
        ])

        invoice2 = models.Invoice(
            customer=customer1,
            submitted_date='20-FEB-2018',
            description='2018 Website Development',
            paid_date=None,
            number='4010-2018-002',
            total=8000,
            terms=45)

        db.session.add_all([
            models.Item(
                date='01-FEB-2018',
                description='Backend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date='04-FEB-2018',
                description='Backend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date='05-FEB-2018',
                description='Frontend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
            models.Item(
                date='06-FEB-2018',
                description='Frontend development', unit_price=250, units='hr',
                quantity=8, invoice=invoice2, customer=customer1
            ),
        ])

        invoice3 = models.Invoice(
            customer=customer1,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='4010-2018-003',
            total=1600,
            terms=22)

        db.session.add_all([
            models.Item(
                date='01-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='04-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='05-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=50, units='hr',
                quantity=8, invoice=invoice3, customer=customer1
            ),
        ])

        customer2 = models.Customer(
            name1='Employer #2', addrline1='1234 45th St', city='New York',
            state='NY', zip='11133', email='billing@example.com', number='4020')

        invoice4 = models.Invoice(
            customer=customer2,
            submitted_date=None,
            description='2018 Website Maintenance',
            paid_date=None,
            number='4020-2018-001',
            total=2400,
            terms=45)

        db.session.add_all([
            models.Item(
                date='01-MAR-2018',
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date='04-MAR-2018',
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date='05-MAR-2018',
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
            models.Item(
                date='06-MAR-2018',
                description='Website maintenance', unit_price=75, units='hr',
                quantity=8, invoice=invoice4, customer=customer2
            ),
        ])

        db.session.add_all([
            models.UnitPrice(description='Design', unit_price=200, units='hr'),
            models.UnitPrice(description='Development', unit_price=250, units='hr'),
            models.UnitPrice(description='Maintenance', unit_price=50, units='hr'),
            models.UnitPrice(description='Employer #2: Design', unit_price=100, units='hr'),
            models.UnitPrice(description='Employer #2: Development', unit_price=150, units='hr'),
            models.UnitPrice(description='Employer #2: Maintenance', unit_price=75, units='hr'),
        ])

        db.session.commit()
