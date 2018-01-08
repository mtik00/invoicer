insert into addresses
    (name1, addrline1, city, state, zip, email, terms)
values
    -- The first address is assumed to be *you*
    ('Tom Smith', '1313 Mockingbird Ln', 'New York', 'NY', '11111', 'me@nowhere.com', 'NET 60 days'),
    ('Some Employer', '111 9th Ave N', 'New York', 'NY', '11222', 'boss@company.com', 'NET 30 days');

insert into unit_prices
    (description, unit_price, units)
values
    -- These make adding items easier
    ('Design', 200, 'hr'),
    ('Development', 250, 'hr'),
    ('Maintenance', 50, 'hr');

insert into invoices
    (submitted_date, description, to_address, paid_date)
values
    ('20-JAN-2018', '2018 Website Redesign', 2, NULL),
    ('20-FEB-2018', '2018 Website Development', 2, NULL),
    ('20-MAR-2018', '2018 Website Maintenance', 2, NULL);

/*
    The `items` table purposefully doesn't use foreign keys for `unit_price`
    and `units` to make updating things easier.
*/
insert into items
    (invoice_id, date, description, unit_price, quantity, units)
values
    (1, '01-JAN-2018', 'Backend design', 200.0, 8, 'hr'),
    (1, '04-JAN-2018', 'Backend design', 200.0, 8, 'hr'),
    (1, '06-JAN-2018', 'Frontend design', 200.0, 8, 'hr'),
    (1, '10-JAN-2018', 'Frontend design', 200.0, 8, 'hr'),

    (2, '01-FEB-2018', 'Backend development', 250.0, 8, 'hr'),
    (2, '04-FEB-2018', 'Backend development', 250.0, 8, 'hr'),
    (2, '05-FEB-2018', 'Frontend development', 250.0, 8, 'hr'),
    (2, '07-FEB-2018', 'Frontend development', 250.0, 8, 'hr'),

    (3, '01-MAR-2018', 'Website maintenance', 50, 8, 'hr'),
    (3, '04-MAR-2018', 'Website maintenance', 50, 8, 'hr'),
    (3, '05-MAR-2018', 'Website maintenance', 50, 8, 'hr'),
    (3, '07-MAR-2018', 'Website maintenance', 50, 8, 'hr');