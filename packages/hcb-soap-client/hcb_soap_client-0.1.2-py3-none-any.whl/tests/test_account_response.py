"""Test the account response."""

from datetime import time

from hcb_soap_client.account_response import AccountResponse, Student, TimeOfDay
from tests import read_file


def test_account_response_from_dict() -> None:
    """Test the from text."""
    response_text = read_file("s1157.xml")
    account_response = AccountResponse.from_text(response_text)
    assert account_response.account_id == "55503A65D2F448AC8DB5F8181B305281"
    expected_students = 2
    assert len(account_response.students) == expected_students
    assert account_response.students[0] == Student(
        student_id="DC90F9C55C6142519C9CC9EFA1847922",
        first_name="Test1",
        last_name="Student1",
    )
    assert account_response.students[1] == Student(
        student_id="5A2AECC78C2E43FD9CC03CCE55D9806D",
        first_name="Test2",
        last_name="Student2",
    )
    expected_times = 3
    assert len(account_response.times) == expected_times
    assert account_response.times[0] == TimeOfDay(
        id="55632A13-35C5-4169-B872-F5ABDC25DF6A",
        name="LookupItem_RouteTimeOfDayType_AM",
        begin_time=time(hour=0, minute=0, second=0),
        end_time=time(hour=10, minute=0, second=0),
    )
    assert account_response.times[1] == TimeOfDay(
        id="27AADCA0-6D7E-4247-A80F-7847C448EEED",
        name="LookupItem_RouteTimeOfDayType_MID",
        begin_time=time(hour=10, minute=0, second=0),
        end_time=time(hour=13, minute=30, second=0),
    )
    assert account_response.times[2] == TimeOfDay(
        id="6E7A050E-0295-4200-8EDC-3611BB5DE1C1",
        name="LookupItem_RouteTimeOfDayType_PM",
        begin_time=time(hour=13, minute=30, second=0),
        end_time=time(hour=23, minute=59, second=59),
    )
