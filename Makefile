init:
	docker run \
		-p 8080:8080 \
		--name airflow-container \
		--mount type=bind,src=./data,dst=/data \
		--mount type=bind,src=./airflow/dags,dst=/opt/airflow/dags \
		airflow

start:
	docker start airflow-container

stop:
	docker stop airflow-container

restart:
	docker restart airflow-container

