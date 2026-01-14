"""Run a test against the live api."""

import os

import pytest

from hcb_soap_client.hcb_soap_client import HcbSoapClient


@pytest.mark.skip(reason="Live testing disabled.")
async def test_async() -> None:
    """Run the async test process."""
    client = HcbSoapClient()
    school_code = os.environ["HCB_SCHOOLCODE"]
    user_name = os.environ["HCB_USERNAME"]
    password = os.environ["HCB_PASSWORD"]
    school_id = await client.get_school_id(school_code)
    if school_id == "":
        msg = "school_id was blank."
        raise ValueError(msg)
    parent_info = await client.get_parent_info(school_id, user_name, password)
    if parent_info.account_id == "":
        msg = "account_id was blank."
        raise ValueError(msg)
    if len(parent_info.students) == 0:
        msg = "No students found."
        raise ValueError(msg)
    student_id = parent_info.students[0].student_id
    if student_id == "":
        msg = "student_id was blank."
        raise ValueError(msg)
    stops = await client.get_stop_info(
        school_id, parent_info.account_id, student_id, HcbSoapClient.PM_ID
    )
    if len(stops.student_stops) == 0:
        msg = "No stops found."
        raise ValueError(msg)
