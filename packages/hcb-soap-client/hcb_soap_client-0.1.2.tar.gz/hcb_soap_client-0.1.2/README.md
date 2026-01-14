# hcb_soap_client

A Python async SOAP client for the "Here Comes the Bus" API, used to track school bus locations and schedules.

## Installation

```bash
pip install hcb_soap_client
```

Or install from source:

```bash
git clone https://github.com/pcartwright81/hcb_soap_client.git
cd hcb_soap_client
pip install -e .
```

## Usage

### Basic Usage (Context Manager - Recommended)

Using the async context manager is the most efficient approach as it reuses the HTTP session across multiple requests:

```python
import asyncio
from hcb_soap_client import HcbSoapClient

async def main():
    async with HcbSoapClient() as client:
        # Get school ID from school code
        school_id = await client.get_school_id("YOUR_SCHOOL_CODE")

        # Login and get parent/account info
        account = await client.get_parent_info(school_id, "username", "password")
        print(f"Account ID: {account.account_id}")
        print(f"Students: {[s.first_name for s in account.students]}")

        # Get bus stop info for a student
        for student in account.students:
            # Use AM_ID for morning routes, PM_ID for afternoon
            stops = await client.get_stop_info(
                school_id,
                account.account_id,
                student.student_id,
                HcbSoapClient.AM_ID  # or HcbSoapClient.PM_ID
            )

            if stops.vehicle_location:
                print(f"Bus location: {stops.vehicle_location.address}")
                print(f"Speed: {stops.vehicle_location.speed} mph")

asyncio.run(main())
```

### Simple Usage (Without Context Manager)

For one-off requests, you can use the client without a context manager. Note that this creates a new HTTP session for each request:

```python
async def simple_example():
    client = HcbSoapClient()
    school_id = await client.get_school_id("YOUR_SCHOOL_CODE")
```

### Using a Custom Session

You can provide your own `aiohttp.ClientSession` for advanced use cases:

```python
import aiohttp

async def custom_session_example():
    async with aiohttp.ClientSession() as session:
        client = HcbSoapClient(session=session)
        school_id = await client.get_school_id("YOUR_SCHOOL_CODE")
```

## API Reference

### `HcbSoapClient`

#### Constructor

```python
HcbSoapClient(url: str | None = None, session: aiohttp.ClientSession | None = None)
```

- `url`: Optional custom API endpoint (defaults to production URL)
- `session`: Optional aiohttp session to reuse

#### Class Attributes

- `AM_ID`: Time of day ID for morning routes
- `PM_ID`: Time of day ID for afternoon routes

#### Methods

##### `get_school_id(school_code: str) -> str`

Look up the school ID from a school code.

##### `get_parent_info(school_id: str, username: str, password: str) -> AccountResponse`

Authenticate and retrieve account information including students and time of day options.

##### `get_stop_info(school_id: str, parent_id: str, student_id: str, time_of_day_id: str) -> StopResponse`

Get bus stop information and current vehicle location for a student.

### Response Models

All response models are Pydantic `BaseModel` instances.

#### `AccountResponse`

- `account_id: str`
- `students: list[Student]`
- `times: list[TimeOfDay]`

#### `Student`

- `student_id: str`
- `first_name: str`
- `last_name: str`

#### `StopResponse`

- `vehicle_location: VehicleLocation | None`
- `student_stops: list[StudentStop]`

#### `VehicleLocation`

- `name: str` - Vehicle/bus name
- `latitude: float`
- `longitude: float`
- `log_time: datetime`
- `speed: int`
- `heading: str`
- `address: str`
- `ignition: bool`
- `display_on_map: bool`

## Development

### Install development dependencies

```bash
pip install -e ".[dev,test]"
```

### Run tests

```bash
pytest
```

### Run linter

```bash
ruff check .
```

## License

MIT License - see [LICENSE](LICENSE) for details.
