\set ON_ERROR_STOP on

INSERT INTO sd_beg_050_t01.customers (id, email) VALUES
    (1, 'ada@example.test'),
    (2, 'grace@example.test');

INSERT INTO sd_beg_050_t01.orders (id, customer_id, total) VALUES
    (101, 1, 24.50),
    (102, 1, 10.00),
    (103, 2, 99.95);
