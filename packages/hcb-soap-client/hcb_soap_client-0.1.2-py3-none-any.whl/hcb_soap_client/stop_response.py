"""Define a stop object."""

from datetime import datetime, time
from typing import Annotated, Self

from dateutil import parser
from lxml import etree
from pydantic import BaseModel, BeforeValidator

from . import parse_time_str, parse_yn_bool, xpath_element, xpath_elements

# Type aliases for cleaner field definitions
TimeStr = Annotated[time, BeforeValidator(parse_time_str)]
YNBool = Annotated[bool, BeforeValidator(parse_yn_bool)]


def _parse_float(value: str) -> float:
    """Parse float from string, defaulting to 0 for empty."""
    return 0.0 if value == "" else float(value)


def _parse_datetime(value: str) -> datetime:
    """Parse datetime string."""
    return parser.parse(value)


FloatStr = Annotated[float, BeforeValidator(_parse_float)]
DateTimeStr = Annotated[datetime, BeforeValidator(_parse_datetime)]


class StudentStop(BaseModel):
    """Define a student stop."""

    name: str
    latitude: FloatStr
    longitude: FloatStr
    start_time: TimeStr
    stop_type: str
    substitute_vehicle_name: str
    vehicle_name: str
    stop_id: str
    arrival_time: TimeStr
    time_of_day_id: str
    vehicle_id: str
    esn: str
    tier_start_time: TimeStr
    bus_visibility_start_offset: int

    @classmethod
    def from_element(cls, elem: etree._Element) -> "StudentStop":
        """Create from lxml element."""
        return cls(
            name=elem.get("Name", ""),
            latitude=elem.get("Latitude", "0"),
            longitude=elem.get("Longitude", "0"),
            start_time=elem.get("StartTime", "00:00:00"),
            stop_type=elem.get("StopType", ""),
            substitute_vehicle_name=elem.get("SubstituteVehicleName", ""),
            vehicle_name=elem.get("VehicleName", ""),
            stop_id=elem.get("StopId", ""),
            arrival_time=elem.get("ArrivalTime", "00:00:00"),
            time_of_day_id=elem.get("TimeOfDayId", ""),
            vehicle_id=elem.get("VehicleId", ""),
            esn=elem.get("Esn", ""),
            tier_start_time=elem.get("TierStartTime", "00:00:00"),
            bus_visibility_start_offset=int(elem.get("BusVisibilityStartOffset", "0")),
        )


class VehicleLocation(BaseModel):
    """Define a student vehicle location."""

    name: str
    latitude: FloatStr
    longitude: FloatStr
    log_time: DateTimeStr
    ignition: YNBool
    latent: YNBool
    time_zone_offset: int
    heading: str
    speed: int
    address: str
    message_code: int
    display_on_map: YNBool

    @classmethod
    def from_element(cls, elem: etree._Element) -> "VehicleLocation":
        """Create from lxml element."""
        return cls(
            name=elem.get("Name", ""),
            latitude=elem.get("Latitude", "0"),
            longitude=elem.get("Longitude", "0"),
            log_time=elem.get("LogTime", ""),
            ignition=elem.get("Ignition", "N"),
            latent=elem.get("Latent", "N"),
            time_zone_offset=int(elem.get("TimeZoneOffset", "0")),
            heading=elem.get("Heading", ""),
            speed=int(elem.get("Speed", "0")),
            address=elem.get("Address", ""),
            message_code=int(elem.get("MessageCode", "0")),
            display_on_map=elem.get("DisplayOnMap", "N"),
        )


class StopResponse(BaseModel):
    """Define a stop object."""

    vehicle_location: VehicleLocation | None
    student_stops: list[StudentStop]

    @classmethod
    def from_text(cls, response_text: str) -> Self:
        """Create a new instance from text."""
        root = etree.fromstring(response_text.encode())

        vehicle_elem = xpath_element(root, "//*[local-name()='VehicleLocation']")
        vehicle_location = (
            VehicleLocation.from_element(vehicle_elem)
            if vehicle_elem is not None
            else None
        )

        stop_elements = xpath_elements(root, "//*[local-name()='StudentStop']")
        student_stops = [StudentStop.from_element(e) for e in stop_elements]

        return cls(vehicle_location=vehicle_location, student_stops=student_stops)
