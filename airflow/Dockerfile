FROM apache/airflow:latest

WORKDIR /opt/airflow

COPY dags /opt/airflow/dags/
COPY airflow/entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh

USER airflow

ENTRYPOINT ["/entrypoint.sh"]
