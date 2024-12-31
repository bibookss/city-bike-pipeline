import logging

import requests
from pydantic import ValidationError, parse_obj_as

from ingestion.models import Network, Station
from ingestion.utils import send_request

_logger = logging.getLogger(__name__)

# API endpoints and fields for requests
NETWORKS_URL = "http://api.citybik.es/v2/networks"
NETWORKS_FIELDS = ["id", "name", "location", "company"]
STATIONS_URL_TEMPLATE = "http://api.citybik.es/v2/networks/{id}"
STATIONS_FIELDS = ["id", "stations"]


class CityBike:
    """
    Wrapper for interacting with the CityBike API (https://api.citybik.es/).

    This class provides methods to fetch bike network information and stations
    from the CityBike API. The data is parsed into Pydantic models for easier
    handling and validation.

    Attributes:
        session (requests.Session): The session object used for making HTTP requests.
    """

    def __init__(self):
        """
        Initializes a new CityBike instance with a session for making HTTP requests.

        Sets up the `requests.Session` to handle all requests made by this class.
        """
        self.session = requests.Session()

    def get_networks(self) -> list[Network]:
        """
        Fetches a list of bike networks from the CityBike API.

        This method sends a GET request to the CityBike API to retrieve a list of
        available bike-sharing networks. It then parses the response into a list of
        `Network` objects using Pydantic's `parse_obj_as`.

        Returns:
            list[Network]: A list of `Network` objects representing bike-sharing networks.

        Raises:
            ValidationError: If the response cannot be parsed into valid `Network` objects.
        """
        _logger.info("Getting networks...")
        fields = ",".join(NETWORKS_FIELDS)
        response = send_request(
            session=self.session,
            method="GET",
            url=NETWORKS_URL,
            params={"fields": fields},
        ).json()

        try:
            networks = parse_obj_as(list[Network], response["networks"])
            return networks
        except ValidationError as e:
            _logger.error("Failed validating networks: %s", e.errors())
            raise

    def get_stations(self, id: str) -> list[Station]:
        """
        Fetches a list of stations for a specific bike network from the CityBike API.

        This method sends a GET request to the CityBike API using a network `id` to retrieve
        the list of stations in that network. Each station is augmented with the `network_id`
        to associate it with the appropriate network. The response is then parsed into a list of
        `Station` objects using Pydantic's `parse_obj_as`.

        Args:
            id (str): The ID of the bike network for which stations are to be fetched.

        Returns:
            list[Station]: A list of `Station` objects representing the stations in the network.

        Raises:
            ValidationError: If the response cannot be parsed into valid `Station` objects.
        """
        _logger.info("Getting stations from network with id %s", id)
        fields = ",".join(STATIONS_FIELDS)
        response = send_request(
            session=self.session,
            method="GET",
            url=STATIONS_URL_TEMPLATE.format(id=id),
            params={"fields": fields},
        ).json()

        stations_with_id = []
        for station in response["network"]["stations"]:
            station["network_id"] = id  # Adding network_id to the station
            stations_with_id.append(station)

        try:
            stations = parse_obj_as(list[Station], stations_with_id)
            return stations
        except ValidationError as e:
            _logger.error("Failed validating stations: %s", e.errors())
            _logger.error("Invalid stations data: %s", stations_with_id)
            raise
