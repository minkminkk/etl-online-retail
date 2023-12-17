# Based on Superset's quickstart documentation
# (https://superset.apache.org/docs/quickstart)
FROM apache/superset:2.1.3

# Download PostgreSQL db driver
RUN pip install --no-cache-dir psycopg2

# Environment variables
# (SECRET_KEY init at build time therefore use RUN instruction)
RUN export SUPERSET_SECRET_KEY=$(openssl rand -base64 42)
ENV SUPERSET_SECRET_KEY=$(SUPERSET_SECRET_KEY) \
    TALISMAN_ENABLED=False

# Create account
RUN superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --email admin@localhost \
    --password admin

# Init Superset metastore
RUN superset db upgrade
