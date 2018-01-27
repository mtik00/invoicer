import arrow
from sqlalchemy import event, UniqueConstraint
from sqlalchemy_utils.types import ArrowType
from sqlalchemy.orm import relationship

from .database import db


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), unique=True)
    street = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    email = db.Column(db.String(120))
    terms = db.Column(db.Integer(), default=30)
    w3_theme = db.Column(db.String(120), default='blue-grey')
    w3_theme_invoice = db.Column(db.String(120), default='dark-grey')

    def __repr__(self):
        return '<Profile %r>' % (self.full_name)


class Customer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = (UniqueConstraint('user_id', 'number', name='user_number'),)

    id = db.Column(db.Integer, primary_key=True)
    name1 = db.Column(db.String(50))
    name2 = db.Column(db.String(50))
    addrline1 = db.Column(db.String(50))
    addrline2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    email = db.Column(db.String(120))
    terms = db.Column(db.Integer)
    number = db.Column(db.Integer, nullable=False)
    invoices = relationship("Invoice", back_populates="customer")
    items = relationship("Item", back_populates="customer")
    w3_theme = db.Column(db.String(120))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="customers")

    def __repr__(self):
        return '<Customer %r>' % (self.name1)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    invoice = relationship("Invoice", back_populates="items")

    date = db.Column(ArrowType)
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
    submitted_date = db.Column(ArrowType)
    description = db.Column(db.String(150))
    due_date = db.Column(ArrowType)
    number = db.Column(db.String(50), unique=True, nullable=False)
    total = db.Column(db.Float)
    items = relationship("Item", back_populates="invoice")
    terms = db.Column(db.Integer)
    w3_theme = db.Column(db.String(120))

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="invoices")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="invoices")

    paid_date_id = db.Column(db.Integer, db.ForeignKey('invoice_paid_dates.id', use_alter=True, name='fk_invoice_paid_dates_id'))
    paid_date = db.relationship('InvoicePaidDate', foreign_keys=paid_date_id, post_update=True)

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

        if (arrow.now() > self.due_date):
            return True
        elif self.paid_date and (self.paid_date.paid_date > self.due_date):
            return True

        return False

    def get_theme(self):
        """
        Returns the appropriate theme for presenting the invoice.
        """
        if self.w3_theme:
            return self.w3_theme

        customer = Customer.query.get(self.customer_id)
        if customer.w3_theme:
            return customer.w3_theme

        user = Profile.query.get(1)
        if user.w3_theme_invoice:
            return user.w3_theme_invoice

        if user.w3_theme:
            return user.w3_theme

        return None


@event.listens_for(Invoice, 'before_insert')
def receive_before_insert(mapper, connection, invoice):
    if isinstance(invoice.submitted_date, basestring):
        invoice.submitted_date = arrow.get(invoice.submitted_date)

    if (invoice.submitted_date and invoice.terms):
        invoice.due_date = invoice.submitted_date.replace(days=+invoice.terms)


# NOTE: This will not fire if you use Invoice.query.filter(...).update({}).  It
# will fire, however, if you use: `invoice.description = 'asdf'; db.session.commit()`
@event.listens_for(Invoice, 'before_update')
def receive_before_update(mapper, connection, invoice):
    if isinstance(invoice.submitted_date, basestring):
        invoice.submitted_date = arrow.get(invoice.submitted_date)

    if (invoice.submitted_date and invoice.terms):
        invoice.due_date = invoice.submitted_date.replace(days=+invoice.terms)


class UnitPrice(db.Model):
    __tablename__ = 'unit_prices'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150))
    unit_price = db.Column(db.Float)
    units = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="units")

    def __repr__(self):
        return '<UnitPrice %r>' % (self.description)


class InvoicePaidDate(db.Model):
    __tablename__ = 'invoice_paid_dates'
    id = db.Column(db.Integer, primary_key=True)
    paid_date = db.Column(ArrowType)
    description = db.Column(db.String(150))

    def __repr__(self):
        return '<InvoicePaidDate %r>' % (self.paid_date)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    hashed_password = db.Column(db.String(100))  # FYI: Argon2 hashes to 73 chars w/ single-digit time_cost
    invoices = relationship("Invoice", back_populates="user")
    units = relationship("UnitPrice", back_populates="user")
    customers = relationship("Customer", back_populates="user")

    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', use_alter=True, name='fk_profile_id'))
    profile = db.relationship('Profile', foreign_keys=profile_id, post_update=True)

    application_settings_id = db.Column(db.Integer, db.ForeignKey('application_settings.id', use_alter=True, name='fk_application_settings_id'))
    application_settings = db.relationship('ApplicationSettings', foreign_keys=application_settings_id, post_update=True)

    def __repr__(self):
        return '<User %r>' % (self.username)


class ApplicationSettings(db.Model):
    __tablename__ = 'application_settings'
    id = db.Column(db.Integer, primary_key=True)
    debug_mode = db.Column(db.Boolean)
