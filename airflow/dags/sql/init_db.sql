-- Create schema
CREATE SCHEMA IF NOT EXISTS retail;


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


-- Fact Table
CREATE TABLE IF NOT EXISTS retail.fct_invoices (
    invoice_id CHAR(6), 
    product_dim_id INTEGER REFERENCES retail.dim_products (product_dim_id),
    invoice_date DATE REFERENCES retail.dim_dates (date),
    customer_dim_id INTEGER REFERENCES retail.dim_customers (customer_dim_id),
    unit_price DECIMAL(8,2) NOT NULL,
    quantity INTEGER NOT NULL
);