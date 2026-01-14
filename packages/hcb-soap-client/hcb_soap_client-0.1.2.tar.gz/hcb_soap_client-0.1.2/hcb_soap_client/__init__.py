"""Init file for the soap client."""

from datetime import time

from lxml import etree

# Public API exports - must be after utility functions are defined
# to avoid circular imports, so we import at module level but define
# utilities first inline

_MIN_PARTS_WITH_SECONDS = 3


def xpath_attr(root: etree._Element, expr: str) -> str:
    """Get first attribute result from XPath expression, or empty string."""
    result = root.xpath(expr)
    return result[0] if result else ""


def xpath_element(root: etree._Element, expr: str) -> etree._Element | None:
    """Get first element from XPath expression, or None."""
    result = root.xpath(expr)
    return result[0] if result else None


def xpath_elements(root: etree._Element, expr: str) -> list[etree._Element]:
    """Get elements from XPath expression."""
    return root.xpath(expr)


def parse_time_str(value: str | time) -> time:
    """Parse time string (HH:MM:SS) to time object."""
    if isinstance(value, time):
        return value
    parts = value.split(":")
    return time(
        hour=int(parts[0]),
        minute=int(parts[1]),
        second=int(parts[2]) if len(parts) >= _MIN_PARTS_WITH_SECONDS else 0,
    )


def parse_yn_bool(value: str) -> bool:
    """Parse Y/N or Yes/No string to bool."""
    return str(value).upper().startswith("Y")


# ruff: noqa: E402
# Public API exports - placed after utility definitions to avoid circular imports
from .account_response import AccountResponse
from .hcb_soap_client import HcbApiError, HcbSoapClient
from .stop_response import StopResponse

__all__ = [
    "AccountResponse",
    "HcbApiError",
    "HcbSoapClient",
    "StopResponse",
]
