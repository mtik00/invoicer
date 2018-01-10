from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(50), unique=True)
    street = Column(String(50))
    city = Column(String(50))
    state = Column(String(2))
    zip = Column(String(10))
    email = Column(String(120))
    terms = Column(String(120))

    def __repr__(self):
        return '<Address %r>' % (self.full_name)


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name1 = Column(String(50), unique=True)
    name2 = Column(String(50))
    addrline1 = Column(String(50))
    addrline2 = Column(String(50))
    city = Column(String(50))
    state = Column(String(2))
    zip = Column(String(10))
    email = Column(String(120))
    terms = Column(String(120))
    number = Column(String(50))
    invoices = relationship("Invoice", back_populates="customer")
    items = relationship("Item", back_populates="customer")

    def __repr__(self):
        return '<Customer %r>' % (self.name1)


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    invoice = relationship("Invoice", back_populates="items")

    date = Column(String(50))
    description = Column(String(150))
    unit_price = Column(Float)
    quantity = Column(Integer)
    units = Column(String(50))

    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="items")

    def __repr__(self):
        return '<Item %r>' % (self.description)


class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    submitted_date = Column(String(50))
    description = Column(String(150))
    paid_date = Column(String(50))
    number = Column(String(50))
    total = Column(Float)
    items = relationship("Item", back_populates="invoice")

    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="invoices")

    def __repr__(self):
        return '<Invoice %r>' % (self.number)


class UnitPrice(Base):
    __tablename__ = 'unit_prices'
    id = Column(Integer, primary_key=True)
    description = Column(String(150))
    unit_price = Column(Float)
    units = Column(String(50))

    def __repr__(self):
        return '<UnitPrice %r>' % (self.description)