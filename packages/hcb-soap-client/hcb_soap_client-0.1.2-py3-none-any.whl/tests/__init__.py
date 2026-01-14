"""Init file for tests."""

from pathlib import Path


def read_file(file_name: str) -> str:
    """Read a text file."""
    with Path(f"tests/test_data/{file_name}").open() as file:
        return file.read()
