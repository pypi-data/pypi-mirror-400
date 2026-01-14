"""Pytest fixtures for integration tests with mocked API responses."""

import responses
from typing import Generator
import pytest

from hubble_futures import create_client, ExchangeConfig
from hubble_futures.aster import AsterFuturesClient
from hubble_futures.weex import WeexFuturesClient


@pytest.fixture
def aster_config() -> ExchangeConfig:
    """Create Aster exchange config for testing."""
    return ExchangeConfig(
        name="asterdex",
        api_key="test_api_key",
        api_secret="test_api_secret",
        base_url="https://fapi.asterdex.com",
    )


@pytest.fixture
def weex_config() -> ExchangeConfig:
    """Create WEEX exchange config for testing."""
    return ExchangeConfig(
        name="weex",
        api_key="test_api_key",
        api_secret="test_api_secret",
        passphrase="test_passphrase",
        base_url="https://api-contract.weex.com",
    )


@pytest.fixture
def aster_client(aster_config: ExchangeConfig) -> AsterFuturesClient:
    """Create Aster futures client for testing."""
    return create_client(aster_config)


@pytest.fixture
def weex_client(weex_config: ExchangeConfig) -> WeexFuturesClient:
    """Create WEEX futures client for testing."""
    return create_client(weex_config)


@pytest.fixture
def mock_responses() -> Generator[responses.RequestsMock, None, None]:
    """Provide mocked HTTP responses for API calls."""
    with responses.RequestsMock() as rsps:
        yield rsps
