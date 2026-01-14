"""Test the hcb soap client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hcb_soap_client.hcb_soap_client import HcbApiError, HcbSoapClient
from tests.test_data.const import (
    ACCOUNT_ID,
    PASSWORD,
    SCHOOL_CODE,
    SCHOOL_ID,
    STUDENT_ONE_ID,
    USER_NAME,
)

from . import read_file


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock aiohttp session with common setup."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.close = AsyncMock(return_value=None)
    return session


@pytest.fixture
def mock_session_with_response(mock_session: MagicMock) -> MagicMock:
    """Create a mock session factory that sets response text."""

    def _set_response(filename: str) -> MagicMock:
        mock_session.post.return_value.__aenter__.return_value.text.return_value = (
            read_file(filename)
        )
        return mock_session

    mock_session.set_response = _set_response
    return mock_session


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_school_id(
    mock_client: MagicMock, mock_session_with_response: MagicMock
) -> None:
    """Tests the get school id."""
    session = mock_session_with_response.set_response("s1100.xml")
    mock_client.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_school_id(SCHOOL_CODE)
    assert response == SCHOOL_ID


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_parent_info(
    mock_client: MagicMock, mock_session_with_response: MagicMock
) -> None:
    """Tests the account response."""
    session = mock_session_with_response.set_response("s1157.xml")
    mock_client.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_parent_info(SCHOOL_ID, USER_NAME, PASSWORD)
    assert response.account_id == ACCOUNT_ID
    expected_students = 2
    assert len(response.students) == expected_students


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_stop_info(
    mock_client: MagicMock, mock_session_with_response: MagicMock
) -> None:
    """Tests the stop info response."""
    session = mock_session_with_response.set_response("s1158_AM.xml")
    mock_client.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_stop_info(
        SCHOOL_ID, ACCOUNT_ID, STUDENT_ONE_ID, HcbSoapClient.AM_ID
    )
    assert response.vehicle_location is not None
    assert response.vehicle_location.address != ""
    expected_stops = 2
    assert len(response.student_stops) == expected_stops


def test_init() -> None:
    """Test the init."""
    client = HcbSoapClient()
    assert client._url == "https://api.synovia.com/SynoviaApi.svc"
    assert client._owns_session is True

    client = HcbSoapClient("http://test.url")
    assert client._url == "http://test.url"

    client = HcbSoapClient(None)
    assert client._url == "https://api.synovia.com/SynoviaApi.svc"

    # Test with provided session
    mock_session = MagicMock()
    client = HcbSoapClient(session=mock_session)
    assert client._session is mock_session
    assert client._owns_session is False


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_context_manager(mock_client: MagicMock) -> None:
    """Test the async context manager creates and closes session."""
    mock_session = MagicMock()
    mock_session.close = AsyncMock(return_value=None)
    mock_client.return_value = mock_session

    async with HcbSoapClient() as client:
        assert client._session is mock_session
        mock_client.assert_called_once()

    mock_session.close.assert_called_once()
    assert client._session is None


async def test_context_manager_with_provided_session() -> None:
    """Test context manager does not close a provided session."""
    mock_session = MagicMock()
    mock_session.close = AsyncMock(return_value=None)

    async with HcbSoapClient(session=mock_session) as client:
        # Session should not be replaced
        assert client._session is mock_session

    # Should not close provided session
    mock_session.close.assert_not_called()


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_school_id_with_session(
    mock_client: MagicMock, mock_session_with_response: MagicMock
) -> None:
    """Test API call using context manager with reused session."""
    session = mock_session_with_response.set_response("s1100.xml")
    mock_client.return_value = session

    async with HcbSoapClient() as client:
        response = await client.get_school_id(SCHOOL_CODE)
        assert response == SCHOOL_ID


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_api_error_handling(mock_client: MagicMock) -> None:
    """Test that API errors are raised properly."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")
    mock_session.post.return_value.__aenter__.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_session

    client = HcbSoapClient()
    with pytest.raises(HcbApiError) as exc_info:
        await client.get_school_id(SCHOOL_CODE)

    assert exc_info.value.status_code == 500
    assert "500" in str(exc_info.value)


def test_hcb_api_error() -> None:
    """Test HcbApiError exception."""
    error = HcbApiError("Test error", status_code=404)
    assert str(error) == "Test error"
    assert error.status_code == 404

    error_no_status = HcbApiError("Another error")
    assert error_no_status.status_code is None
