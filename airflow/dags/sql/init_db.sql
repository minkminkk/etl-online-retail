-- Refresh schema
DROP SCHEMA IF EXISTS retail CASCADE;
CREATE SCHEMA IF NOT EXISTS retail;


-- Dimension Tables
CREATE TABLE IF NOT EXISTS retail.dim_customers (
    customer_dim_id SERIAL PRIMARY KEY,
    customer_id CHAR(5) NOT NULL,
    country VARCHAR
);
INSERT INTO retail.dim_customers (customer_id, country) 
    VALUES ('00000', NULL);

CREATE TABLE IF NOT EXISTS retail.dim_products (
    product_dim_id SERIAL PRIMARY KEY,
    stock_code CHAR(5) NOT NULL,
    description VARCHAR
);
INSERT INTO retail.dim_products (stock_code, description) 
    VALUES ('00000', NULL);

CREATE TABLE IF NOT EXISTS retail.dim_dates (
    date_dim_id INTEGER PRIMARY KEY, 
    date DATE,
    year SMALLINT,
    month SMALLINT,
    day SMALLINT,
    day_of_week SMALLINT,
    week SMALLINT
);


-- Fact Table
CREATE TABLE IF NOT EXISTS retail.fct_invoices (
    invoice_id CHAR(6), 
    invoice_date_dim_id INTEGER REFERENCES retail.dim_dates (date_dim_id),
    product_dim_id INTEGER REFERENCES retail.dim_products (product_dim_id),
    customer_dim_id INTEGER REFERENCES retail.dim_customers (customer_dim_id),
    unit_price DECIMAL(8,2) NOT NULL,
    quantity INTEGER NOT NULL
);