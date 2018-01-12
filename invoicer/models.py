import arrow
from sqlalchemy.orm import relationship
from .database import db


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), unique=True)
    street = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    email = db.Column(db.String(120))
    terms = db.Column(db.Integer(), default=30)
    w3_theme = db.Column(db.String(120), default='cyan')
    w3_theme_invoice = db.Column(db.String(120), default='cyan')

    def __repr__(self):
        return '<Address %r>' % (self.full_name)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(50), unique=True)
    name2 = db.Column(db.String(50))
    addrline1 = db.Column(db.String(50))
    addrline2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    email = db.Column(db.String(120))
    terms = db.Column(db.Integer)
    number = db.Column(db.Integer, unique=True, nullable=False)
    invoices = relationship("Invoice", back_populates="customer")
    items = relationship("Item", back_populates="customer")
    w3_theme = db.Column(db.String(120))

    def __repr__(self):
        return '<Customer %r>' % (self.name1)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    invoice = relationship("Invoice", back_populates="items")

    date = db.Column(db.String(50))
    description = db.Column(db.String(150))
    unit_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    units = db.Column(db.String(50))

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="items")

    def __repr__(self):
        return '<Item %r>' % (self.description)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    submitted_date = db.Column(db.String(50))
    description = db.Column(db.String(150))
    paid_date = db.Column(db.String(50))
    number = db.Column(db.String(50), unique=True, nullable=False)
    total = db.Column(db.Float)
    items = relationship("Item", back_populates="invoice")
    terms = db.Column(db.Integer)
    w3_theme = db.Column(db.String(120))

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="invoices")

    def __repr__(self):
        return '<Invoice %r>' % (self.number)

    def overdue(self):
        """
        Returns True if this invoice is overdue:
            submitted and not paid by the due date
            paid after the due date
        """
        if not self.submitted_date:
            return False

        due = self.due(as_string=False)

        if due and (arrow.now() > due):
            return True

        if due and self.paid_date:
            paid_date = arrow.get(self.paid_date, 'DD-MMM-YYYY')
            return paid_date > due

        return False

    def due(self, as_string=True):
        if not self.submitted_date:
            return None

        due_date = arrow.get(self.submitted_date, 'DD-MMM-YYYY').replace(days=+self.terms)

        if as_string:
            due_date = due_date.format('DD-MMM-YYYY')

        return due_date

    def get_theme(self):
        """
        Returns the appropriate theme for presenting the invoice.
        """
        if self.w3_theme:
            return self.w3_theme

        customer = Customer.query.get(self.customer_id)
        if customer.w3_theme:
            return customer.w3_theme

        user = Address.query.get(1)
        if user.w3_theme_invoice:
            return user.w3_theme_invoice

        if user.w3_theme:
            return user.w3_theme

        return None


class UnitPrice(db.Model):
    __tablename__ = 'unit_prices'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150))
    unit_price = db.Column(db.Float)
    units = db.Column(db.String(50))

    def __repr__(self):
        return '<UnitPrice %r>' % (self.description)