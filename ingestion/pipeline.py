import logging.config
from dataclasses import dataclass

import fire
import psycopg2

from ingestion.city_bike import CityBike


@dataclass
class JobParameters:
    staging_path: str
    logconf_path: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    country: str | None = None
    city: str | None = None


def main(params: JobParameters):
    try:
        logging.config.fileConfig(params.logconf_path)
    except Exception as e:
        raise ValueError(
            f"Error loading logging configuration from {params.logconf_path}: {str(e)}"
        )

    _logger = logging.getLogger("ingestion")
    _logger.info(
        "Ingesting CityBike data in country [%s] and city [%s]...",
        params.country,
        params.city,
    )

    city_bike = CityBike()

    networks = city_bike.get_networks()
    filtered_networks = []
    for network in networks:
        if (params.country is None or network.country == params.country) and (
            params.city is None or network.city == params.city
        ):
            filtered_networks.append(network)

    stations = []
    for network in filtered_networks:
        _station = city_bike.get_stations_by_network_id(network.id)
        stations.extend(_station)

    _logger.info("Saving db to staging...")
    conn = psycopg2.connect(
        dbname=params.db_name,
        user=params.db_user,
        password=params.db_password,
        host=params.db_host,
        port=params.db_port,
    )
    cursor = conn.cursor()

    _logger.info("Creating networks table...")
    create_networks_table_query = """
        CREATE TABLE IF NOT EXISTS networks (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            city VARCHAR NOT NULL,
            country VARCHAR NOT NULL,
            company VARCHAR
        );
    """
    cursor.execute(create_networks_table_query)

    _logger.info("Creating stations table...")
    create_stations_table_query = """
        CREATE TABLE IF NOT EXISTS stations (
            id VARCHAR NOT NULL,
            network_id VARCHAR NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            is_renting BOOLEAN NOT NULL,
            is_returning BOOLEAN NOT NULL,
            last_updated_s INT NOT NULL,
            address VARCHAR,
            post_code VARCHAR,
            payment VARCHAR,
            has_payment_terminal BOOLEAN NOT NULL,
            altitude FLOAT,
            slots INT NOT NULL,
            has_ebikes BOOLEAN NOT NULL,
            num_ebikes INT,
            PRIMARY KEY (id, timestamp),
            FOREIGN KEY (network_id) REFERENCES networks(id)
        );
    """
    cursor.execute(create_stations_table_query)

    for network in networks:
        query = """
            INSERT INTO networks (id, name, latitude, longitude, city, country, company)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING; 
        """
        cursor.execute(
            query,
            (
                network.id,
                network.name,
                network.latitude,
                network.longitude,
                network.city,
                network.country,
                "&&".join(network.company),
            ),
        )

    for station in stations:
        query = """
            INSERT INTO stations (id, network_id, timestamp, name, latitude, longitude, 
                                is_renting, is_returning, last_updated_s, address, post_code, 
                                payment, has_payment_terminal, altitude, slots, has_ebikes, num_ebikes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id, timestamp) DO NOTHING;  
        """
        cursor.execute(
            query,
            (
                station.id,
                station.network_id,
                station.timestamp,
                station.name,
                station.latitude,
                station.longitude,
                station.is_renting,
                station.is_returning,
                station.last_updated_s,
                station.address,
                station.post_code,
                "&&".join(station.payment),
                station.has_payment_terminal,
                station.altitude,
                station.slots,
                station.has_ebikes,
                station.num_ebikes,
            ),
        )

    conn.commit()
    conn.close()

    _logger.info("Ingestion complete!")


if __name__ == "__main__":
    fire.Fire(lambda **kwargs: main(JobParameters(**kwargs)))
