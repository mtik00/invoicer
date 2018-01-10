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
    terms = db.Column(db.String(120))

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
    terms = db.Column(db.String(120))
    number = db.Column(db.Integer)
    invoices = relationship("Invoice", back_populates="customer")
    items = relationship("Item", back_populates="customer")

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
    number = db.Column(db.String(50))
    total = db.Column(db.Float)
    items = relationship("Item", back_populates="invoice")

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="invoices")

    def __repr__(self):
        return '<Invoice %r>' % (self.number)


class UnitPrice(db.Model):
    __tablename__ = 'unit_prices'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150))
    unit_price = db.Column(db.Float)
    units = db.Column(db.String(50))

    def __repr__(self):
        return '<UnitPrice %r>' % (self.description)