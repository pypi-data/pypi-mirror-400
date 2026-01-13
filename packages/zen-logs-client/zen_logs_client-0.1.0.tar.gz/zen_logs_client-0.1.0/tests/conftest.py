"""Pytest configuration and fixtures."""

import pytest
import respx
from httpx import Response


@pytest.fixture
def mock_server():
    """Create a mock server that returns 202 for batch requests."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://localhost:7777/api/v1/batch").mock(
            return_value=Response(202)
        )
        yield mock


@pytest.fixture
def mock_server_error():
    """Create a mock server that returns 500 errors."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://localhost:7777/api/v1/batch").mock(
            return_value=Response(500)
        )
        yield mock


@pytest.fixture
def mock_server_rate_limit():
    """Create a mock server that returns 429 rate limit."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://localhost:7777/api/v1/batch").mock(
            return_value=Response(429)
        )
        yield mock
