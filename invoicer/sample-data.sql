insert into addresses
    (full_name, street, city, state, zip, email, terms)
values
    -- The first address is assumed to be *you*
    ('Tom Smith', '1313 Mockingbird Ln', 'New York', 'NY', '11111', 'me@example.com', 'NET 60 days')
;

insert into customers
    (name1, addrline1, city, state, zip, email, terms, number)
values
    -- The first address is assumed to be *you*
    ('Some Employer', '111 9th Ave N', 'New York', 'NY', '11222', 'boss|mike|larry@example.com', 'NET 30 days', '4010')
    ,('Employer #2', '1234 45th St', 'New York', 'NY', '11133', 'billing@example.com', NULL, '4020')
;

insert into unit_prices
    (description, unit_price, units)
values
    -- These make adding items easier
    ('Design', 200, 'hr')
    ,('Development', 250, 'hr')
    ,('Maintenance', 50, 'hr')
    ,('Employer #2: Design', 100, 'hr')
    ,('Employer #2: Development', 150, 'hr')
    ,('Employer #2: Maintenance', 75, 'hr')
;

insert into invoices
    (submitted_date, description, customer_id, paid_date, 'number', total)
values
    ('20-JAN-2018', '2018 Website Redesign', 1, '07-FEB-2018', '4010-2018-001', 6400)
    ,('20-FEB-2018', '2018 Website Development', 1, NULL, '4010-2018-002', 8000)
    ,(NULL, '2018 Website Maintenance', 1, NULL, '4010-2018-003', 1600)
    ,(NULL, '2018 Website Maintenance', 2, NULL, '4020-2018-001', 2400)
;

/*
    The `items` table purposefully doesn't use foreign keys for `unit_price`
    and `units` to make updating things easier.
*/
insert into items
    (invoice_id, date, description, unit_price, quantity, units)
values
    (1, '01-JAN-2018', 'Backend design', 200.0, 8, 'hr')
    ,(1, '04-JAN-2018', 'Backend design', 200.0, 8, 'hr')
    ,(1, '06-JAN-2018', 'Frontend design', 200.0, 8, 'hr')
    ,(1, '10-JAN-2018', 'Frontend design', 200.0, 8, 'hr')

    ,(2, '01-FEB-2018', 'Backend development', 250.0, 8, 'hr')
    ,(2, '04-FEB-2018', 'Backend development', 250.0, 8, 'hr')
    ,(2, '05-FEB-2018', 'Frontend development', 250.0, 8, 'hr')
    ,(2, '07-FEB-2018', 'Frontend development', 250.0, 8, 'hr')

    ,(3, '01-MAR-2018', 'Website maintenance', 50, 8, 'hr')
    ,(3, '04-MAR-2018', 'Website maintenance', 50, 8, 'hr')
    ,(3, '05-MAR-2018', 'Website maintenance', 50, 8, 'hr')
    ,(3, '07-MAR-2018', 'Website maintenance', 50, 8, 'hr')

    ,(4, '01-APR-2018', 'Website maintenance', 75, 8, 'hr')
    ,(4, '04-APR-2018', 'Website maintenance', 75, 8, 'hr')
    ,(4, '05-APR-2018', 'Website maintenance', 75, 8, 'hr')
    ,(4, '07-APR-2018', 'Website maintenance', 75, 8, 'hr')
;