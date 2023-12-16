FROM apache/airflow:slim-2.7.3

COPY ./requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT [ "airflow", "standalone" ]