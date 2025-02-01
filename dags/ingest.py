from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2025, 2, 1),
}

dag = DAG(
    "city_bike_ingestion",
    default_args=default_args,
    description="DAG for City Bike Data Ingestion",
    schedule_interval=None,
    catchup=False,
)

city_bike_ingest_task = DockerOperator(
    task_id="city_bike_ingest_task",
    image="city_bike_ingest",
    command=(
        "--country=US "
        '--city="New York, NY" '
        "--staging_path=staging "
        "--logconf_path=./config/ingestion.logconf "
        "--db_name=city_bike "
        "--db_user=root "
        "--db_password=root "
        "--db_host=pgdatabase "
        "--db_port=5432"
    ),
    network_mode="city_bike_network",
    auto_remove=True,
    dag=dag,
)

city_bike_ingest_task
