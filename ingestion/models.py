from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, validator


class JobParameters(BaseModel):
    country: Optional[str] = Field(default="all")
    city: Optional[str] = Field(default=None)
    timezone: ZoneInfo
    staging_path: str
    logconf_path: str

    @validator("timezone", pre=True)
    def convert_to_zoneinfo(cls, value):
        try:
            return ZoneInfo(value) if isinstance(value, str) else value
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {value}")


# class Location(BaseModel):
#     latitude: float
#     longitude: float
#     city: str
#     country: str


# class Extra(BaseModel):
#     uid: str
#     renting: bool
#     returning: bool
#     last_updated: int
#     address: str
#     post_code: Optional[str]
#     payment: Optional[List[str]]
#     payment_terminal: Optional[bool] = Field(..., alias="payment-terminal")
#     altitude: Optional[float]
#     slots: Optional[int]
#     has_ebikes: Optional[bool]
#     ebikes: Optional[int]
#     normal_bikes: Optional[int]


# class Station(BaseModel):
#     id: str
#     network_id: str
#     name: str
#     latitude: float
#     longitude: float
#     timestamp: datetime
#     free_bikes: int
#     empty_slots: int
#     extra: Extra


# class Network(BaseModel):
#     id: str
#     name: str
#     location: Location
#     company: List[str]
