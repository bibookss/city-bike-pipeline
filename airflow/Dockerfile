FROM apache/airflow:latest

WORKDIR /opt/airflow

COPY dags /opt/airflow/dags/
COPY airflow/entrypoint.sh /entrypoint.sh

USER root

RUN apt-get update && apt-get install -y docker.io
RUN chmod +x /entrypoint.sh

USER airflow
RUN pip install apache-airflow-providers-docker  

ENTRYPOINT ["/entrypoint.sh"]
