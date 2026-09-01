\set ON_ERROR_STOP on

CREATE SCHEMA sd_beg_050_t01;

CREATE TABLE sd_beg_050_t01.customers (
    id bigint PRIMARY KEY,
    email text NOT NULL UNIQUE
);

CREATE TABLE sd_beg_050_t01.orders (
    id bigint PRIMARY KEY,
    customer_id bigint NOT NULL REFERENCES sd_beg_050_t01.customers(id),
    total numeric(12, 2) NOT NULL CHECK (total >= 0)
);
