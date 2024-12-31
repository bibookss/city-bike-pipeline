import logging

import pandas as pd
import requests

from ingestion.utils import flatten_dataframe, send_request

_logger = logging.getLogger("ingestion")

# API endpoints and fields for requests
NETWORKS_URL = "http://api.citybik.es/v2/networks"
NETWORKS_FIELDS = ["id", "name", "location", "company"]
STATIONS_URL_TEMPLATE = "http://api.citybik.es/v2/networks/{id}"
STATIONS_FIELDS = ["id", "stations"]


class CityBike:
    """
    Wrapper for interacting with the CityBike API (https://api.citybik.es/).

    Provides methods to fetch bike network information and stations from the API.
    Data is returned as Pandas DataFrames.

    :param session: The session object used for HTTP requests.
    """

    def __init__(self):
        """
        Initializes the CityBike instance with a session for HTTP requests.
        """
        self.session = requests.Session()

    def get_networks(self, country: str, city: str) -> pd.DataFrame:
        """
        Fetches bike networks from the CityBike API and flattens the `location` column.

        :param str country: The country to filter networks by.
        :param str city: The city to filter networks by.
        :return: A DataFrame containing bike network data with flattened location.
        :rtype: pd.DataFrame
        :raises requests.RequestException: If there is an HTTP request issue.
        :raises ValueError: If the API response is missing expected data.
        """
        _logger.info("Getting networks...")
        fields = ",".join(NETWORKS_FIELDS)
        response = send_request(
            session=self.session,
            method="GET",
            url=NETWORKS_URL,
            params={"fields": fields},
        ).json()

        if "networks" not in response:
            _logger.error("Error: Missing 'networks' in the API response.")
            raise ValueError("Missing 'networks' in the API response.")

        networks_df = pd.DataFrame(response["networks"])
        networks_df = flatten_dataframe(networks_df)

        if country:
            country_filter = networks_df["location_country"] == country
            networks_df.where(country_filter, inplace=True)

        if city:
            city_filter = (
                networks_df["location_city"].str.replace(" ", "").str.replace(",", "-")
                == city
            )
            networks_df.where(city_filter, inplace=True)

        networks_df = networks_df.dropna()
        return networks_df

    def get_stations(self, id: str) -> pd.DataFrame:
        """
        Fetches stations for a specific bike network and flattens the `extra` column.

        :param str id: The ID of the bike network to fetch stations for.
        :return: A DataFrame with station data, including flattened 'location' and 'extra' columns.
        :rtype: pd.DataFrame
        :raises requests.RequestException: If the HTTP request fails.
        :raises ValueError: If the API response is missing expected data.
        """
        _logger.info("Getting stations from network with id %s", id)
        fields = ",".join(STATIONS_FIELDS)
        response = send_request(
            session=self.session,
            method="GET",
            url=STATIONS_URL_TEMPLATE.format(id=id),
            params={"fields": fields},
        ).json()

        if "network" not in response or "stations" not in response["network"]:
            _logger.error(
                "Error: Missing 'stations' in the API response for network ID %s", id
            )
            raise ValueError(
                f"Missing 'stations' for network ID {id} in the API response."
            )

        stations_df = pd.DataFrame(response["network"]["stations"])
        stations_df = flatten_dataframe(stations_df)

        stations_df["network_id"] = id
        return stations_df
