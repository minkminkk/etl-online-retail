from airflow import DAG
from airflow.decorators import task
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy.types as dtypes


default_args = {
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id = "data_ingestion",
    default_args = default_args,
    description = "Data extraction and ingestion to PostgreSQL database",
    schedule = timedelta(days=1),
    start_date = datetime(2021, 1, 1),
    catchup = False,
    tags = ["ingestion"],
) as dag:
    
    init_db = PostgresOperator(
        task_id = "init_db",
        sql = "sql/init_db.sql",
    )

    @task(task_id = "ingest_data")
    def ingest_data():
        path = "/data/online_retail.csv"
        df = pd.read_csv(
            path,
            dtype = {
                "Customer ID": "Int32"
            }   # Cast into Int32 to remove decimal points
        ) \
            .rename(
                columns = {
                    "Invoice": "invoice_no",
                    "StockCode": "stock_code",
                    "Description": "description",
                    "Quantity": "quantity",
                    "InvoiceDate": "invoice_date",
                    "Price": "unit_price",
                    "Customer ID": "customer_id",
                    "Country": "country"
                }
            )

        engine = create_engine("postgresql://airflow:airflow@postgres:5432/")
        # Specify dtypes to avoid changing type
        # https://stackoverflow.com/questions/53294611/pandas-to-sql-changing-datatype-in-database-table
        df.to_sql(
            name = "orders", 
            schema = "retail", 
            con = engine, 
            if_exists = "replace", 
            index = False,
            dtype = {
                "invoice_no": dtypes.VARCHAR(7),
                "stock_code": dtypes.VARCHAR(),
                "description": dtypes.VARCHAR(),
                "quantity": dtypes.SMALLINT(),
                "invoice_date": dtypes.TIMESTAMP(),
                "unit_price": dtypes.DECIMAL(8,2),
                "customer_id": dtypes.CHAR(5),
                "country": dtypes.VARCHAR()
            }
        )   
    ingest = ingest_data()
    
    init_db >> ingest

    #TODO: Clean data