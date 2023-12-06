from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.decorators import task
from datetime import datetime, timedelta

import pandas as pd

with DAG(
    "example",
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Example DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    
    @task(task_id = "write_df_csv")
    def transform_xlsx_to_csv():
        path = "/data/online_retail_II.xlsx"
        print("Importing data")
        df = pd.read_excel(path)
        df.to_csv("/data/online_retail.csv", index = False)
        return None
    transform = transform_xlsx_to_csv()
    
    end_of_dag = DummyOperator(task_id = "end_of_DAG")
    
    transform >> end_of_dag