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
    starting_customer_number = db.Column(db.Integer, default=1000)
    customer_increment = db.Column(db.Integer, default=10)
    index_items_per_page = db.Column(db.Integer, default=10)

    site_theme_id = db.Column(db.Integer, db.ForeignKey('site_themes.id'))
    site_theme = relationship("SiteTheme", foreign_keys=site_theme_id)

    invoice_theme_id = db.Column(db.Integer, db.ForeignKey('invoice_themes.id'))
    invoice_theme = relationship("InvoiceTheme", foreign_keys=invoice_theme_id)

    enable_pdf = db.Column(db.Boolean, default=True)

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

    invoice_theme_id = db.Column(db.Integer, db.ForeignKey('invoice_themes.id'))
    invoice_theme = relationship("InvoiceTheme")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="customers")

    def __repr__(self):
        return '<Customer %r>' % (self.name1)

    def format_address(self, html=True, include_email=True):
        join_with = '<br>' if html else '\n'
        name = join_with.join([x for x in [self.name1, self.name2] if x])
        street = join_with.join([x for x in [self.addrline1, self.addrline2] if x])
        city = '%s, %s %s' % (self.city, self.state.upper(), self.zip)

        lines = [name, street, city]
        if include_email:
            lines.append(self.email)

        return join_with.join(lines)

    def format_email(self, join_with='<br>'):
        email = self.email

        if '|' in email:
            name, domain = email.split('@')
            return join_with.join(['%s@%s' % (x, domain) for x in name.split('|')])

        return email


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
    __table_args__ = (UniqueConstraint('user_id', 'number', name='user_number'),)

    id = db.Column(db.Integer, primary_key=True)
    submitted_date = db.Column(ArrowType)
    description = db.Column(db.String(150))
    due_date = db.Column(ArrowType)
    number = db.Column(db.String(50))
    total = db.Column(db.Float)
    items = relationship("Item", back_populates="invoice")
    terms = db.Column(db.Integer)

    invoice_theme_id = db.Column(db.Integer, db.ForeignKey('invoice_themes.id'))
    invoice_theme = relationship("InvoiceTheme")

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

        if (not self.paid_date) and (arrow.now() > self.due_date):
            return True
        elif self.paid_date and (self.paid_date.paid_date > self.due_date):
            return True

        return False

    def get_theme(self):
        """
        Returns the appropriate theme for presenting the invoice.
        """
        if self.invoice_theme:
            return self.invoice_theme.name

        customer = Customer.query.get(self.customer_id)
        if customer.invoice_theme:
            return customer.invoice_theme.name

        profile = User.query.get(self.user_id).profile
        if profile.invoice_theme:
            return profile.invoice_theme.name

        return None


@event.listens_for(Invoice, 'before_insert')
def receive_before_insert(mapper, connection, invoice):
    if isinstance(invoice.submitted_date, basestring):
        invoice.submitted_date = arrow.get(invoice.submitted_date)

    if (invoice.submitted_date and invoice.terms):
        invoice.due_date = invoice.submitted_date.replace(days=+invoice.terms)

    # For an insert, we can't assume that all of the Items have been inserted
    # prior to this invoice.  However, any items will be associated through the
    # `relationship`.
    invoice.total = sum([x.unit_price * x.quantity for x in invoice.items])


# NOTE: This will not fire if you use Invoice.query.filter(...).update({}).  It
# will fire, however, if you use: `invoice.description = 'asdf'; db.session.commit()`
@event.listens_for(Invoice, 'before_update')
def receive_before_update(mapper, connection, invoice):
    if isinstance(invoice.submitted_date, basestring):
        invoice.submitted_date = arrow.get(invoice.submitted_date)

    if (invoice.submitted_date and invoice.terms):
        invoice.due_date = invoice.submitted_date.replace(days=+invoice.terms)

    # For the update, we can't assume that the invoice has all of the items
    # associated yet.  Therefore, run a query, and use that sum.
    items = Item.query.filter_by(invoice=invoice).all()
    invoice.total = sum([x.unit_price * x.quantity for x in items])


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


class SiteTheme(db.Model):
    __tablename__ = 'site_themes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    top = db.Column(db.String(8))
    bottom = db.Column(db.String(8))

    def __str__(self):
        return self.name


class InvoiceTheme(db.Model):
    __tablename__ = 'invoice_themes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    banner_color = db.Column(db.String(8))
    banner_background_color = db.Column(db.String(8))
    table_header_color = db.Column(db.String(8))
    table_header_background_color = db.Column(db.String(8))

    def __str__(self):
        return self.name
