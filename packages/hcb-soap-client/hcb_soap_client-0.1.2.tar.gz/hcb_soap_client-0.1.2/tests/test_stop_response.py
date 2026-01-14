"""Test the stop response."""

from datetime import datetime, time

from hcb_soap_client.stop_response import StopResponse
from tests import read_file


def test_stop_response_from_dict_am() -> None:
    """Test the from text."""
    response_text = read_file("s1158_AM.xml")

    stop_response = StopResponse.from_text(response_text)
    assert stop_response.vehicle_location is not None
    assert stop_response.vehicle_location.name == "20-05"
    assert stop_response.vehicle_location.latitude == 34.7902536
    assert stop_response.vehicle_location.longitude == -86.782654999999991
    assert stop_response.vehicle_location.log_time == datetime(2024, 10, 31, 7, 0)
    assert not stop_response.vehicle_location.ignition
    assert not stop_response.vehicle_location.latent
    assert stop_response.vehicle_location.time_zone_offset == -1
    assert stop_response.vehicle_location.heading == "E "
    assert stop_response.vehicle_location.speed == 35
    assert stop_response.vehicle_location.address == "Endeavor Elementary School"
    assert stop_response.vehicle_location.message_code == 2
    assert not stop_response.vehicle_location.display_on_map
    assert len(stop_response.student_stops) == 2
    assert stop_response.student_stops[0].name == "Endeavor Elementary School (AM)"
    assert stop_response.student_stops[0].latitude == 34.790386
    assert stop_response.student_stops[0].longitude == -86.784177
    assert stop_response.student_stops[0].start_time == time(7, 0, 0)
    assert stop_response.student_stops[0].stop_type == "School"
    assert stop_response.student_stops[0].substitute_vehicle_name == ""
    assert stop_response.student_stops[0].vehicle_name == "20-05"
    assert (
        stop_response.student_stops[0].stop_id == "275FD0B6-3836-4FAE-A185-14C0C1ED861D"
    )
    assert stop_response.student_stops[0].arrival_time == time(6, 0, 0)
    assert (
        stop_response.student_stops[0].time_of_day_id
        == "55632A13-35C5-4169-B872-F5ABDC25DF6A"
    )
    assert (
        stop_response.student_stops[0].vehicle_id
        == "546DE805-C8DF-4464-B6FE-9DB2D05BA9DD"
    )
    assert stop_response.student_stops[0].esn == "123456"
    assert stop_response.student_stops[0].tier_start_time == time(5, 42, 0)
    assert stop_response.student_stops[0].bus_visibility_start_offset == 0
    assert stop_response.student_stops[1].name == "Circle K (AM)"
    assert stop_response.student_stops[1].latitude == 34.807730
    assert stop_response.student_stops[1].longitude == -86.749860
    assert stop_response.student_stops[1].start_time == time(7, 0, 0)
    assert stop_response.student_stops[1].stop_type == "Stop"
    assert stop_response.student_stops[1].substitute_vehicle_name == ""
    assert stop_response.student_stops[1].vehicle_name == "20-05"
    assert (
        stop_response.student_stops[1].stop_id == "CBD14468-96E3-4648-9DBA-F0B8687A02BC"
    )
    assert stop_response.student_stops[1].arrival_time == time(6, 5, 0)
    assert (
        stop_response.student_stops[1].time_of_day_id
        == "55632A13-35C5-4169-B872-F5ABDC25DF6A"
    )
    assert (
        stop_response.student_stops[1].vehicle_id
        == "546DE805-C8DF-4464-B6FE-9DB2D05BA9DD"
    )
    assert stop_response.student_stops[1].esn == "123456"
    assert stop_response.student_stops[1].tier_start_time == time(5, 42, 0)
    assert stop_response.student_stops[1].bus_visibility_start_offset == 0


def test_stop_response_from_dict_pm() -> None:
    """Test the from text."""
    response_text = read_file("s1158_PM.xml")
    stop_response = StopResponse.from_text(response_text)
    assert stop_response.vehicle_location is not None
    assert stop_response.vehicle_location.name == "20-05"
    assert stop_response.vehicle_location.latitude == 34.7902536
    assert stop_response.vehicle_location.longitude == -86.782654999999991
    assert stop_response.vehicle_location.log_time == datetime(2024, 10, 31, 7, 0)
    assert not stop_response.vehicle_location.ignition
    assert not stop_response.vehicle_location.latent
    assert stop_response.vehicle_location.time_zone_offset == -1
    assert stop_response.vehicle_location.heading == "E "
    assert stop_response.vehicle_location.speed == 35
    assert stop_response.vehicle_location.address == "Endeavor Elementary School"
    assert stop_response.vehicle_location.message_code == 2
    assert not stop_response.vehicle_location.display_on_map
    assert len(stop_response.student_stops) == 2
    assert stop_response.student_stops[0].name == "Endeavor Elementary School PM"
    assert stop_response.student_stops[0].latitude == 34.790386
    assert stop_response.student_stops[0].longitude == -86.784177
    assert stop_response.student_stops[0].start_time == time(7, 0, 0)
    assert stop_response.student_stops[0].stop_type == "School"
    assert stop_response.student_stops[0].substitute_vehicle_name == ""
    assert stop_response.student_stops[0].vehicle_name == "20-05"
    assert (
        stop_response.student_stops[0].stop_id == "9A361D75-F0BA-4F7D-94ED-BE6838BFAA6B"
    )
    assert stop_response.student_stops[0].arrival_time == time(6, 0, 0)
    assert (
        stop_response.student_stops[0].time_of_day_id
        == "6E7A050E-0295-4200-8EDC-3611BB5DE1C1"
    )
    assert (
        stop_response.student_stops[0].vehicle_id
        == "546DE805-C8DF-4464-B6FE-9DB2D05BA9DD"
    )
    assert stop_response.student_stops[0].esn == "123456"
    assert stop_response.student_stops[0].tier_start_time == time(5, 42, 0)
    assert stop_response.student_stops[0].bus_visibility_start_offset == 0
    assert stop_response.student_stops[1].name == "Circle K (PM)"
    assert stop_response.student_stops[1].latitude == 34.807730
    assert stop_response.student_stops[1].longitude == -86.749860
    assert stop_response.student_stops[1].start_time == time(7, 0, 0)
    assert stop_response.student_stops[1].stop_type == "Stop"
    assert stop_response.student_stops[1].substitute_vehicle_name == ""
    assert stop_response.student_stops[1].vehicle_name == "20-05"
    assert (
        stop_response.student_stops[1].stop_id == "D67ADB46-0D81-4E9F-9520-B5569098A9D2"
    )
    assert stop_response.student_stops[1].arrival_time == time(6, 5, 0)
    assert (
        stop_response.student_stops[1].time_of_day_id
        == "6E7A050E-0295-4200-8EDC-3611BB5DE1C1"
    )
    assert (
        stop_response.student_stops[1].vehicle_id
        == "546DE805-C8DF-4464-B6FE-9DB2D05BA9DD"
    )
    assert stop_response.student_stops[1].esn == "123456"
    assert stop_response.student_stops[1].tier_start_time == time(5, 42, 0)
    assert stop_response.student_stops[1].bus_visibility_start_offset == 0
