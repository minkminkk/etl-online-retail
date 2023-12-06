FROM apache/airflow:2.7.3
EXPOSE 8080

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required Python libraries
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT ["airflow", "standalone"]