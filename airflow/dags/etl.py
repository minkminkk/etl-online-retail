# Airflow-related dependencies
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta

# DAG-related dependencies
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy.types as dtypes

DIR_DATA = "/data"
DIR_TEMP = "/opt/airflow/temp"

default_args = {
    "depends_on_past": False,
    "retries": 0,   # For easier run test, please enable in real applications
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id = "etl_online_retail",
    default_args = default_args,
    description = "Data from csv file is extracted, \
        transformed, and loaded to PostgreSQL DWH",
    schedule = None,
    start_date = datetime(2009, 1, 1),
    catchup = False,
    tags = ["ingestion"],
) as dag:

    # Create tables with constraints    
    init_db = PostgresOperator(
        task_id = "init_db",
        sql = "sql/init_db.sql",
    )


    # Initial cleaning of source data
    @task(task_id = "initial_clean")
    def initial_clean():
        # Cast customer ID column as Int32 to remove decimals
        df = pd.read_csv(
            f"{DIR_DATA}/online_retail.csv", 
            dtype = {"Customer ID": "Int32"},
            parse_dates = ["InvoiceDate"],
            date_format = "%Y-%m-%d %H:%M:%S"
        ) \
            .rename(    # Rename columns
                columns = {
                    "Invoice": "invoice_id",
                    "StockCode": "stock_code",
                    "Description": "description",
                    "Quantity": "quantity",
                    "InvoiceDate": "invoice_date",
                    "Price": "unit_price",
                    "Customer ID": "customer_id",
                    "Country": "country"
                }
            )
        
        # Drop duplicates
        df = df.drop_duplicates() \
            .dropna(
                how = "all", 
                subset = ["invoice_id", "quantity", "invoice_date", "unit_price"],
        ) \
            .sort_values(["invoice_id"])
        
        # Cast stock_code, customer_id into strings and fill default values for null
        df["stock_code"] = df["stock_code"].astype("string").fillna("00000")
        df["customer_id"] = df["customer_id"].astype("string").fillna("00000")

        # Filter based on field conditions
        df = df.loc[df["quantity"] > 0]
        df = df.loc[df["unit_price"] > 0]
        df = df.loc[
            (df["invoice_id"].str.len() == 6) & (df["invoice_id"].str.isdigit())
        ]   # Filter out invalid and cancelled invoices
        df = df.loc[
            (df["stock_code"].str.len() == 5) & (df["stock_code"].str.isdigit())
        ]
        df = df.loc[
            (df["customer_id"].str.len() == 5) & (df["customer_id"].str.isdigit())
        ]

        # Add date columns
        df["year"] = df["invoice_date"].dt.year
        df["month"] = df["invoice_date"].dt.month
        df["day"] = df["invoice_date"].dt.day
        df["day_of_week"] = df["invoice_date"].dt.day_of_week
        df["invoice_date"] = df["invoice_date"].dt.date

        # Save as temp data
        df.to_csv(f"{DIR_TEMP}/initial_cleaned.csv", index = False)
    ini_clean = initial_clean()


    # Read raw xlsx file into pd.DataFrame. Clean data. Write as cleaned csv.
    @task(task_id = "stage_dims")
    def stage_dims():
        df = pd.read_csv(
            f"{DIR_TEMP}/initial_cleaned.csv",
            dtype = {"customer_id": "string"}   # to use df.merge()
        )

        # Stage db into tables in schema and write to csv files
        # dim_dates
        tbl_date = df[["invoice_date", "year", "month", "day", "day_of_week"]] \
            .rename(columns = {"invoice_date": "date"}) \
            .drop_duplicates()
        tbl_date.to_csv(f"{DIR_TEMP}/dim_dates.csv", index = False)

        # dim_customers
        # Slowly changing dim, so take most recent record of same customer_id (type 1)
        tbl_customers = df[["customer_id", "country"]] \
            .loc[df["customer_id"] != "00000"] \
            .drop_duplicates(subset = "customer_id", keep = "last")
        tbl_customers.to_csv(
            f"{DIR_TEMP}/dim_customers.csv", 
            index = False
        )

        # dim_products
        # Slowly changing dim, so take most recent record of same stock_code (type 1)
        tbl_products = df[["stock_code", "description"]] \
            .loc[df["stock_code"] != "00000"] \
            .drop_duplicates(subset = "stock_code", keep = "last")
        tbl_products.to_csv(
            f"{DIR_TEMP}/dim_products.csv", 
            index = False
        )
    st_dims = stage_dims()


    # Load dims into DWH
    @task(task_id = "load_dims")
    def load_dims():
        # SQLAlchemy engine for df.to_sql()
        engine = create_engine("postgresql://airflow:airflow@postgres:5432/")

        # Load each dim table
        for tbl in ["dim_dates", "dim_customers", "dim_products"]:
            df = pd.read_csv(
                f"{DIR_TEMP}/{tbl}.csv"
            )
            df.to_sql(
                name = tbl, 
                schema = "retail",
                con = engine,
                if_exists = "append",
                index = False,
                dtype = {
                    "date": dtypes.DATE(),
                    "year": dtypes.SMALLINT(),
                    "month": dtypes.SMALLINT(),
                    "day": dtypes.SMALLINT(),
                    "day_of_week": dtypes.SMALLINT(),
                    "customer_id": dtypes.CHAR(5),
                    "country": dtypes.VARCHAR(),
                    "stock_code": dtypes.CHAR(5),
                    "description": dtypes.VARCHAR()
                }
            )
    l_dims = load_dims()


    # Stage fact and bridge table
    @task(task_id = "stage_fact")
    def stage_fact():
        # SQLAlchemy engine for df.read_sql()
        engine = create_engine("postgresql://airflow:airflow@postgres:5432/")
        
        # Get data frames: customer_id, stock_code inferred as int by pandas
        # Therefore cast them to string type to facilitate pd.merge()
        df = pd.read_csv(
            f"{DIR_TEMP}/initial_cleaned.csv",
            dtype = {
                "customer_id": "string",
                "stock_code": "string"
            }
        )
        df_customers = pd.read_sql(
            sql = "SELECT * FROM retail.dim_customers;",
            con = engine
        )
        df_products = pd.read_sql(
            sql = "SELECT * FROM retail.dim_products;",
            con = engine
        )
        tbl_invoices = df[[
            "invoice_id",
            "stock_code",
            "invoice_date",
            "customer_id",
            "unit_price",
            "quantity"
        ]]

        # Join stock_code, unit_price to dim tables to get respective dim_id
        tbl_invoices["customer_dim_id"] = tbl_invoices.merge(
            df_customers,
            how = "left",
            on = "customer_id"
        )["customer_dim_id"]
        tbl_invoices["product_dim_id"] = tbl_invoices.merge(
            df_products,
            how = "left",
            on = "stock_code"
        )["product_dim_id"]
        tbl_invoices = tbl_invoices \
            .drop(columns = ["customer_id", "stock_code"])
        tbl_invoices.to_csv(
            f"{DIR_TEMP}/fct_invoices.csv", 
            index = False
        )
    st_fct = stage_fact()


    # Load fact and bridge table
    @task(task_id = "load_fact")
    def load_fact():
        # SQLAlchemy engine for df.to_sql()
        engine = create_engine("postgresql://airflow:airflow@postgres:5432/")

        # Load each dim table
        df = pd.read_csv(
            f"{DIR_TEMP}/fct_invoices.csv"
        )
        df.to_sql(
            name = "fct_invoices", 
            schema = "retail",
            con = engine,
            if_exists = "append",
            index = False,
            dtype = {
                "invoice_id": dtypes.CHAR(6),
                "product_dim_id": dtypes.INTEGER(),
                "invoice_date": dtypes.DATE(),
                "customer_dim_id": dtypes.INTEGER(),
                "unit_price": dtypes.DECIMAL(8,2),
                "quantity": dtypes.SMALLINT(),
            }
        )
    l_fct = load_fact()


    # Clean up temp files (temporary approach as might affect
    # temp files of concurrently running DAGs)
    clean_up = BashOperator(
        task_id = "clean_up",
        bash_command = "rm -f /opt/airflow/temp/*",
        trigger_rule = "all_done"
    )


    # Set dependencies
    ini_clean >> st_dims >> l_dims >> st_fct >> l_fct >> clean_up
    init_db >> l_dims