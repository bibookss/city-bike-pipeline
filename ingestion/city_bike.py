import logging

import requests
import pandas as pd
from ingestion.utils import send_request

# Logger setup
_logger = logging.getLogger("ingestion")

# API endpoints and fields for requests
NETWORKS_URL = "http://api.citybik.es/v2/networks"
NETWORKS_FIELDS = ["id", "name", "location", "company"]
STATIONS_URL_TEMPLATE = "http://api.citybik.es/v2/networks/{id}"
STATIONS_FIELDS = ["id", "stations"]


class CityBike:
    """
    Wrapper for interacting with the CityBike API (https://api.citybik.es/).

    This class provides methods to fetch bike network information and stations
    from the CityBike API. The data is returned as Pandas DataFrames for easy
    manipulation and analysis.

    Attributes:
        session (requests.Session): The session object used for making HTTP requests.
    """

    def __init__(self):
        """
        Initializes a new CityBike instance with a session for making HTTP requests.

        Sets up the `requests.Session` to handle all requests made by this class.
        """
        self.session = requests.Session()

    def get_networks(self) -> pd.DataFrame:
        """
        Fetches a list of bike networks from the CityBike API.

        This method sends a GET request to the CityBike API to retrieve a list of
        available bike-sharing networks. It then parses the response into a Pandas DataFrame
        containing the network data. The DataFrame includes the fields specified in `NETWORKS_FIELDS`
        such as network ID, name, location, and company.

        Returns:
            pd.DataFrame: A DataFrame containing the bike network data.

        Raises:
            requests.RequestException: If there is an issue with the HTTP request.
            ValueError: If the response does not contain the expected data.
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
        
        return pd.DataFrame(response["networks"])

    def get_stations(self, id: str) -> pd.DataFrame:
        """
        Fetches a list of stations for a specific bike network from the CityBike API.

        This method sends a GET request to the CityBike API using a network `id` to retrieve
        the list of stations in that network. The stations are then augmented with the `network_id`
        to associate them with the correct network. The data is returned as a Pandas DataFrame containing
        the station information.

        Args:
            id (str): The ID of the bike network for which stations are to be fetched.

        Returns:
            pd.DataFrame: A DataFrame containing the stations' data for the given network.

        Raises:
            requests.RequestException: If there is an issue with the HTTP request.
            ValueError: If the response does not contain the expected station data.
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
            _logger.error("Error: Missing 'stations' in the API response for network ID %s", id)
            raise ValueError(f"Missing 'stations' for network ID {id} in the API response.")
        
        df = pd.DataFrame(response["network"]["stations"])
        df["network_id"] = id
        return df
