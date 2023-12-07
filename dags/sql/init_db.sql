/* TABLE jobs
Include basic information about orders

Columns:
    invoice_no [varchar(7)] PK: 6-digit number unique to each order. 
        If starts with "c" -> cancellation.
    stock_code [varchar(6)]: Product code.
    description [varchar]: Product name.
    quantity [smallint]: Quantity of products in that order.
    invoice_date [timestamp(0)]: Timestamp that order was generated.
    unit_price [decimal(8,2)]: Unit price of product (in GBP pound).
    customer_id [char(5)]: ID of customer.
    country [varchar]: Country where the customer resides.
*/

CREATE SCHEMA IF NOT EXISTS retail;

CREATE TABLE IF NOT EXISTS retail.orders (
    invoice_no VARCHAR(7),
    stock_code VARCHAR,
    description VARCHAR,
    quantity SMALLINT,
    invoice_date TIMESTAMP(0) DEFAULT NOW(),
    unit_price DECIMAL(8,2),
    customer_id CHAR(5),
    country VARCHAR
);