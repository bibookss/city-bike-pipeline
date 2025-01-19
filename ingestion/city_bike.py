import logging
from dataclasses import dataclass
from datetime import datetime

import requests

from ingestion.utils import send_request

NETWORKS_URL = "http://api.citybik.es/v2/networks"
NETWORKS_FIELDS = ["id", "name", "location", "company"]
STATIONS_URL_TEMPLATE = "http://api.citybik.es/v2/networks/{id}"
STATIONS_FIELDS = ["id", "stations"]


@dataclass
class Network:
    id: str
    name: str
    latitude: float
    longitude: float
    city: str
    country: str
    company: list[str]


@dataclass
class Station:
    id: str
    network_id: str
    timestamp: datetime
    name: str
    latitude: float
    longitude: float
    is_renting: bool
    is_returning: bool
    last_updated_s: int
    address: str | None 
    post_code: str
    payment: list[str]
    has_payment_terminal: bool
    altitude: float | None 
    slots: int
    has_ebikes: bool
    num_ebikes: bool


_logger = logging.getLogger("ingestion")


class CityBike:
    """
    Wrapper for interacting with the CityBike API (https://api.citybik.es/).
    """

    def __init__(self):
        """
        Initializes the CityBike instance with a session for HTTP requests.
        """
        self.session = requests.Session()

    def get_networks(self) -> list[Network]:
        """
        Fetches bike networks from the CityBike API

        :return: A list containing network data
        :rtype: list[Network]
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

        networks = []
        for network in response["networks"]:
            _network = Network(
                id=network["id"],
                name=network["name"],
                latitude=network["location"]["latitude"],
                longitude=network["location"]["longitude"],
                country=network["location"]["country"],
                city=network["location"]["city"],
                company=network["company"],
            )
            networks.append(_network)

        return networks

    def get_stations_by_network_id(self, id: str) -> list[Station]:
        """
        Fetches stations for a specific bike network.

        :param id: The ID of the bike network to fetch stations for.
        :return: A list containing station data
        :rtype: list[Station]
        :raises requests.RequestException: If there is an HTTP request issue.
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

        stations = []
        for station in response["network"]["stations"]:
            _station = Station(
                id=station["id"],
                network_id=id,
                timestamp=datetime.strptime(
                    station["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                name=station["name"],
                latitude=station["latitude"],
                longitude=station["longitude"],
                is_renting=bool(station["extra"]["renting"]),
                is_returning=bool(station["extra"]["returning"]),
                last_updated_s=station["extra"]["last_updated"],
                address=station["extra"].get("address"),
                post_code=station["extra"].get("post_code"),
                payment=station["extra"]["payment"],
                has_payment_terminal=station["extra"]["payment-terminal"],
                altitude=station["extra"].get("altitude"),
                slots=station["extra"]["slots"],
                has_ebikes=station["extra"].get("has_ebikes"),
                num_ebikes=station["extra"].get("ebikes"),
            )
            stations.append(_station)

        return stations
