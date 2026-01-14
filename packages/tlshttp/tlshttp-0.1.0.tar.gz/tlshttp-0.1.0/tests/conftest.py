"""Pytest configuration and fixtures."""

import pytest

import tlshttp


@pytest.fixture
def client():
    """Provide a Client instance with automatic cleanup."""
    with tlshttp.Client(profile="chrome_120", timeout=30.0) as client:
        yield client


@pytest.fixture
async def async_client():
    """Provide an AsyncClient instance with automatic cleanup."""
    async with tlshttp.AsyncClient(profile="chrome_120", timeout=30.0) as client:
        yield client


@pytest.fixture
def headers():
    """Provide a Headers instance."""
    return tlshttp.Headers({"Content-Type": "application/json", "X-Custom": "value"})


@pytest.fixture
def cookies():
    """Provide a Cookies instance."""
    return tlshttp.Cookies({"session": "abc123", "user": "john"})
