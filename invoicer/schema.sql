
drop table if exists addresses;
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY,
    name1 text,
    name2 text,
    addrline1 text,
    addrline2 text,
    city text,
    'state' text,
    zip text,
    email text,
    terms text
);

drop table if exists invoices;
CREATE TABLE invoices (
    id integer PRIMARY KEY,
    submitted_date text,
    'description' text,
    to_address integer,
    paid_date text,
    FOREIGN KEY(to_address) REFERENCES addresses(id)
);

drop table if exists items;
CREATE TABLE items (
    invoice_id integer,
    'date' text,
    'description' text,
    unit_price real,
    quantity integer,
    'units' text
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
);

drop table if exists unit_prices;
CREATE TABLE unit_prices (
    id integer PRIMARY KEY,
    'description' text,
    unit_price real,
    'units' text
);