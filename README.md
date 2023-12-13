# etl-online-retail

A mini ETL project.

## 1. About this project

This project aims to implement a manual (i.e. no scheduling) ETL pipeline for an online retail store which:
- Extracts and transforms a source `.csv` file from [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
- Loads the transformed data into tables of a data warehouse.

![Airflow DAG](imgs/airflow_dag.png)
*DAG of ETL pipeline*

The data warehouse schema is designed following the [Kimball's dimensional modelling technique](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) with the available data from the source `.csv` file.

![Data warehouse schema](imgs/dwh_schema.png)
*Data warehouse schema*

## 2. Technologies used

- **Apache Airflow** for data orchestration.
- **pandas** as the main data processing library.
- **Docker** and **Docker Compose** for the containerized approach.

## 3. Installation

### 3.1. Set up

1. Clone this repo and navigate to project directory:

```shell
git clone https://github.com/minkminkk/etl-online-retail
cd etl-online-retail
```

2. Build images and start containers:

```shell
docker compose up
```

If you already have the containers set up and do not want to recreate containers, do:

```shell
docker compose start
```

3. Then access Airflow webserver for usage at `localhost:8080`.

### 3.2. Tear down

After you are done, if you want to simply stop containers, do:

```shell
docker compose stop
```

Then next time, you can do `docker compose start` to restart your containers.

If you want to remove all containers, do:

```shell
docker compose down
```

## 4. Usage

After executing part `3.1`, upon accessing webserver, you will be prompted to login. Type `airflow` in both username and password.

You will be transferred to the main Airflow UI:

![The Airflow UI](imgs/airflow_ui.png)
*Airflow UI*

To run the DAG, just click on the "play" button on the `Actions` column.

