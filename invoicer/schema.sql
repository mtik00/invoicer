
drop table if exists addresses;
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY,
    full_name text,
    street text,
    city text,
    'state' text,
    zip text,
    email text,
    terms text
);

drop table if exists customers;
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name1 text,
    name2 text,
    addrline1 text,
    addrline2 text,
    city text,
    'state' text,
    zip text,
    email text,
    terms text,
    'number' INTEGER
);

drop table if exists invoices;
CREATE TABLE invoices (
    id integer PRIMARY KEY,
    submitted_date text,
    'description' text,
    customer_id integer,
    paid_date text,
    'number' text,
    total real
);

drop table if exists items;
CREATE TABLE items (
    id integer PRIMARY KEY,
    invoice_id integer,
    'date' text,
    'description' text,
    unit_price real,
    quantity integer,
    'units' text
);

drop table if exists unit_prices;
CREATE TABLE unit_prices (
    id integer PRIMARY KEY,
    'description' text,
    unit_price real,
    'units' text
);