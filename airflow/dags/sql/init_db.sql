-- Refresh schema
-- DROP SCHEMA IF EXISTS retail;
CREATE SCHEMA IF NOT EXISTS retail;

DROP TABLE IF EXISTS retail.dim_customers CASCADE;
DROP TABLE IF EXISTS retail.dim_products CASCADE;
DROP TABLE IF EXISTS retail.dim_dates CASCADE;
DROP TABLE IF EXISTS retail.fct_invoices CASCADE;
DROP TABLE IF EXISTS retail.br_invoice_details CASCADE;

-- Dimension Tables
CREATE TABLE IF NOT EXISTS retail.dim_customers (
    customer_dim_id SERIAL PRIMARY KEY,
    customer_id CHAR(5) NOT NULL,
    country VARCHAR
);
INSERT INTO retail.dim_customers (customer_id, country) 
    VALUES ('00000', 'Not Available');

CREATE TABLE IF NOT EXISTS retail.dim_products (
    product_dim_id SERIAL PRIMARY KEY,
    stock_code CHAR(5) NOT NULL,
    description TEXT
);
INSERT INTO retail.dim_products (stock_code, description) 
    VALUES ('00000', 'Not Available');

CREATE TABLE IF NOT EXISTS retail.dim_dates (
    date DATE PRIMARY KEY,
    year SMALLINT,
    month SMALLINT,
    day SMALLINT,
    day_of_week SMALLINT
);


-- Fact & Bridge Tables
CREATE TABLE IF NOT EXISTS retail.fct_invoices (
    invoice_id CHAR(6) PRIMARY KEY, 
    invoice_date DATE REFERENCES retail.dim_dates (date),
    customer_dim_id INTEGER
);

CREATE TABLE IF NOT EXISTS retail.br_invoice_details (
    invoice_id CHAR(6) REFERENCES retail.fct_invoices (invoice_id),
    product_dim_id INTEGER REFERENCES retail.dim_products (product_dim_id),
    unit_price DECIMAL(8,2) NOT NULL,
    quantity INTEGER NOT NULL
);
