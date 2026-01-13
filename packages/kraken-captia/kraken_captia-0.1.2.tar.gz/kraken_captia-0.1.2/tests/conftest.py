"""Pytest configuration and fixtures for Kraken SDK tests."""

import pytest

from kraken_sdk import AsyncKrakenClient, KrakenClient


@pytest.fixture
def base_url() -> str:
    """Base URL for testing."""
    return "https://api.kraken.test"


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "test_api_key_12345"


@pytest.fixture
def client(base_url: str, api_key: str) -> KrakenClient:
    """Create a sync Kraken client for testing."""
    return KrakenClient(base_url=base_url, api_key=api_key)


@pytest.fixture
def async_client(base_url: str, api_key: str) -> AsyncKrakenClient:
    """Create an async Kraken client for testing."""
    return AsyncKrakenClient(base_url=base_url, api_key=api_key)
