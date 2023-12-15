FROM apache/airflow:2.7.3

ENV AIRFLOW__CORE__LOAD_EXAMPLES: "False" \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: "sqlite:////opt/airflow/airflow.db" \
    AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS: "False" \
    AIRFLOW_CONN_POSTGRES_DEFAULT: "postgresql://airflow:airflow@postgres:5432/warehouse"

COPY ./requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT [ "airflow", "standalone" ]