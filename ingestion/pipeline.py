import logging.config
import os

import fire
import pandas as pd

from ingestion.city_bike import CityBike
from ingestion.models import JobParameters
from ingestion.utils import save_file


def main(params: JobParameters):
    try:
        logging.config.fileConfig(params.logconf_path)
    except Exception as e:
        raise ValueError(
            f"Error loading logging configuration from {params.logconf_path}: {str(e)}"
        )

    _logger = logging.getLogger("ingestion")
    _logger.info(
        "Ingesting CityBike data in country = %s and city = %s...",
        params.country,
        params.city,
    )

    city_bike = CityBike()
    networks_df = city_bike.get_networks(country=params.country, city=params.city)

    stations = []
    for _, station in networks_df.iterrows():
        network_stations = city_bike.get_stations(id=station["id"])
        stations.append(network_stations)
    stations_df = pd.concat(stations)

    networks_file_path = os.path.join(params.staging_path, "networks.csv")
    save_file(networks_df, networks_file_path)

    stations_file_path = os.path.join(params.staging_path, "stations.csv")
    save_file(stations_df, stations_file_path)
    _logger.info("Ingestion done!")


if __name__ == "__main__":
    fire.Fire(lambda **kwargs: main(JobParameters(**kwargs)))
