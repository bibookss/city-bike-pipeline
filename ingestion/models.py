from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    latitude: float
    longitude: float
    city: str
    country: str


class Extra(BaseModel):
    uid: str
    renting: bool
    returning: bool
    last_updated: int
    address: str
    post_code: str
    payment: List[str]
    payment_terminal: bool = Field(..., alias="payment-terminal")
    altitude: Optional[float]
    slots: int


class Station(BaseModel):
    id: str
    network_id: str
    name: str
    latitude: float
    longitude: float
    timestamp: datetime
    free_bikes: int
    empty_slots: int
    extra: Extra


class Network(BaseModel):
    id: str
    name: str
    location: Location
    company: List[str]
