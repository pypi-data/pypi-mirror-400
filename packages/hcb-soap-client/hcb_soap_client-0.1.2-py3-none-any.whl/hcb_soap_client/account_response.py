"""Class for the account info."""

from datetime import time
from typing import Annotated, Self

from lxml import etree
from pydantic import BaseModel, BeforeValidator

from . import parse_time_str, xpath_attr, xpath_elements

# Type aliases for cleaner field definitions
TimeStr = Annotated[time, BeforeValidator(parse_time_str)]


class Student(BaseModel):
    """Info for the student."""

    student_id: str
    first_name: str
    last_name: str

    @classmethod
    def from_element(cls, elem: etree._Element) -> "Student":
        """Create from lxml element."""
        return cls(
            student_id=elem.get("EntityID", ""),
            first_name=elem.get("FirstName", ""),
            last_name=elem.get("LastName", ""),
        )


class TimeOfDay(BaseModel):
    """The time of day list."""

    id: str
    name: str
    begin_time: TimeStr
    end_time: TimeStr

    @classmethod
    def from_element(cls, elem: etree._Element) -> "TimeOfDay":
        """Create from lxml element."""
        return cls(
            id=elem.get("ID", ""),
            name=elem.get("Name", ""),
            begin_time=elem.get("BeginTime", "00:00:00"),
            end_time=elem.get("EndTime", "00:00:00"),
        )


class AccountResponse(BaseModel):
    """Parent account info."""

    account_id: str
    students: list[Student]
    times: list[TimeOfDay]

    @classmethod
    def from_text(cls, response_text: str) -> Self:
        """Create a new instance from text."""
        root = etree.fromstring(response_text.encode())

        account_id = xpath_attr(root, "//*[local-name()='Account']/@ID")
        student_elements = xpath_elements(root, "//*[local-name()='Student']")
        students = [Student.from_element(e) for e in student_elements]
        time_elements = xpath_elements(root, "//*[local-name()='TimeOfDay']")
        times = [TimeOfDay.from_element(e) for e in time_elements]

        return cls(account_id=account_id, students=students, times=times)
