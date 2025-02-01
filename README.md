# City Bike Data Ingestion with Airflow

This project sets up Apache Airflow to run City Bike data ingestion tasks using Docker. The ingestion process pulls data for a given city and stores it in a PostgreSQL database.

## Prerequisites

Before running the project, make sure you have the following installed:

- **Docker**: The entire application is containerized using Docker.
- **Docker Compose**: To manage the multi-container application.

## Project Structure

```
.
├── airflow/                # Contains Airflow configurations and Dockerfile
│   ├── Dockerfile          # Airflow Dockerfile
│   ├── entrypoint.sh       # Custom entrypoint for Airflow
├── dags/                   # Airflow DAGs
│   └── ingest.py           # Sample DAG for City Bike data ingestion
├── ingestion/
│   ├── __init__.py         
│   ├── city_bike.py        # Wrapper for City Bike API
│   ├── Dockerfile          # Dockerfile for the City Bike ingestion container
│   ├── pipeline.py         # Main script for managing City Bike data ingestion
│   ├── utils.py            # Utility functions
├── transformation/
│   ├── __init__.py         
├── config/                 # Configuration files
├── logs/                   # Logs directory for general use
├── Makefile                # Makefile for easy task execution
├── pyproject.toml          # Python project configuration
├── README.md               # This file
├── docker-compose.yaml     # Docker Compose configuration file
└── uv.lock                 # Lock file for uv package manager
```

## Setup and Configuration

### 1. Build Docker Images

First, build City Bike ingestion image.

```bash
docker build -t city_bike_ingest -f ingestion/Dockerfile
```

### 2. Update Docker Compose Configuration

Ensure that the `docker-compose.yml` file includes the following configurations:

- **Airflow Webserver and Scheduler**:
  - Runs Airflow web UI and scheduler.
  - Connects to a PostgreSQL database for metadata storage.
  - Edit the default user in [entrypoint.sh](airflow/entrypoint.sh)
  
- **PostgreSQL Database**:
  - Stores the City Bike data.

- **Docker Socket**:
  - Airflow requires access to Docker to run `DockerOperator`. Make sure that the Docker socket is mounted.
  - `sudo chmod 666 /var/run/docker.sock` to grant permission to the images in your machine.

### 3. Run the Application

Once everything is configured, run the entire stack using Docker Compose:

```bash
docker-compose up -d
```

This will start the following services:

- **Airflow** (Webserver and Scheduler)
- **PostgreSQL** (for storing City Bike data)
- **PgAdmin** (web interface for PostgreSQL)

### 4. Access Airflow

After the containers are up, access the Airflow web UI at `http://localhost:8081`. The default credentials are:

- **Username**: `admin`
- **Password**: `admin`

### 5. Trigger the DAG

Once inside the Airflow web UI:

1. You should see the DAG named `city_bike_ingestion` in the list.
2. Trigger the DAG manually by clicking the play button next to it.

### 6. Monitor Logs

You can monitor the logs for each task and check the status of the ingestion process.

### 7. Access PgAdmin

To view and manage the PostgreSQL database, access the PgAdmin interface at `http://localhost:8082`. The login credentials are:

- **Email**: `admin@admin.com`
- **Password**: `root`

You can then connect to the `pgdatabase` service and manage the `city_bike` database.
