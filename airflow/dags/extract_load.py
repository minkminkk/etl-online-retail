from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.decorators import task
from datetime import datetime, timedelta

import pandas as pd
import psycopg2 as pg

with DAG(
    "data_ingestion",
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Data extraction and ingestion to PostgreSQL database",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["ingestion"],
) as dag:
    
    @task(task_id = "ingest_data")
    def ingest_data():
        path = "/data/online_retail.csv"
        print("Reading data at", path)
        df = pd.read_csv(path)

        try:
            conn = pg.connect(
                dbname = "online_retail",
                username = "postgres",
                password = "postgres",
                host = "db",
                port = 5432
            )
            cur = conn.cursor()

            df.to_sql("orders", con = conn, if_exists = "replace", index = False)
        except:
            pass
        finally:
            cur.close()
            conn.close()
        

    ingest = ingest_data()
    
    end_of_dag = DummyOperator(task_id = "ingest_completed")
    
    ingest >> end_of_dag