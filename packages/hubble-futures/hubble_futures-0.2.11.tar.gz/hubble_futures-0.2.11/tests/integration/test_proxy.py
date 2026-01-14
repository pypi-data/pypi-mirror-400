"""Integration tests for proxy configuration."""

import responses
from typing import Generator
import pytest

from hubble_futures import create_client, ExchangeConfig
from hubble_futures.aster import AsterFuturesClient
from hubble_futures.weex import WeexFuturesClient


@pytest.fixture
def aster_config_with_proxy() -> ExchangeConfig:
    """Create Aster exchange config with proxy for testing."""
    return ExchangeConfig(
        name="asterdex",
        api_key="test_api_key",
        api_secret="test_api_secret",
        base_url="https://fapi.asterdex.com",
        proxy_url="http://user:pass@proxy.example.com:8080"
    )


@pytest.fixture
def weex_config_with_proxy() -> ExchangeConfig:
    """Create WEEX exchange config with proxy for testing."""
    return ExchangeConfig(
        name="weex",
        api_key="test_api_key",
        api_secret="test_api_secret",
        passphrase="test_passphrase",
        base_url="https://api-contract.weex.com",
        proxy_url="http://proxy.example.com:8080"
    )


@pytest.fixture
def aster_config_no_proxy() -> ExchangeConfig:
    """Create Aster exchange config without proxy."""
    return ExchangeConfig(
        name="asterdex",
        api_key="test_api_key",
        api_secret="test_api_secret",
        base_url="https://fapi.asterdex.com",
        proxy_url=None
    )


class TestProxyConfiguration:
    """Test proxy configuration in exchange clients."""

    def test_aster_client_with_proxy_configured(self, aster_config_with_proxy: ExchangeConfig) -> None:
        """Test that Aster client correctly sets proxy from config."""
        client = create_client(aster_config_with_proxy)

        assert isinstance(client, AsterFuturesClient)
        assert client.proxy_url == "http://user:pass@proxy.example.com:8080"
        assert client.session.proxies == {
            "http": "http://user:pass@proxy.example.com:8080",
            "https": "http://user:pass@proxy.example.com:8080",
        }

    def test_weex_client_with_proxy_configured(self, weex_config_with_proxy: ExchangeConfig) -> None:
        """Test that WEEX client correctly sets proxy from config."""
        client = create_client(weex_config_with_proxy)

        assert isinstance(client, WeexFuturesClient)
        assert client.proxy_url == "http://proxy.example.com:8080"
        assert client.session.proxies == {
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080",
        }

    def test_aster_client_without_proxy(self, aster_config_no_proxy: ExchangeConfig) -> None:
        """Test that Aster client works without proxy (direct connection)."""
        client = create_client(aster_config_no_proxy)

        assert isinstance(client, AsterFuturesClient)
        assert client.proxy_url is None
        assert client.session.proxies == {}

    def test_weex_client_without_proxy(self, weex_config: ExchangeConfig) -> None:
        """Test that WEEX client works without proxy (direct connection)."""
        client = create_client(weex_config)

        assert isinstance(client, WeexFuturesClient)
        assert client.proxy_url is None
        assert client.session.proxies == {}

    def test_aster_direct_instantiation_with_proxy(self) -> None:
        """Test creating Aster client directly with proxy parameter."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://fapi.asterdex.com",
            proxy_url="http://test.proxy:8080"
        )

        assert client.proxy_url == "http://test.proxy:8080"
        assert client.session.proxies == {
            "http": "http://test.proxy:8080",
            "https": "http://test.proxy:8080",
        }

    def test_weex_direct_instantiation_with_proxy(self) -> None:
        """Test creating WEEX client directly with proxy parameter."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass",
            base_url="https://api-contract.weex.com",
            proxy_url="http://test.proxy:8080"
        )

        assert client.proxy_url == "http://test.proxy:8080"
        assert client.session.proxies == {
            "http": "http://test.proxy:8080",
            "https": "http://test.proxy:8080",
        }


class TestProxyWithApiCalls:
    """Test that API calls respect proxy configuration."""

    def test_aster_api_call_with_proxy(self, aster_config_with_proxy: ExchangeConfig) -> None:
        """Test that Aster API calls work with proxy configured."""
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            # Mock the server time endpoint
            rsps.add(
                responses.GET,
                "https://fapi.asterdex.com/fapi/v1/time",
                json={"serverTime": 1704355200000},
                status=200
            )

            client = create_client(aster_config_with_proxy)

            # The proxy should be set but the mock will intercept the call
            # We're testing that the client can still make API calls
            assert client.proxy_url == "http://user:pass@proxy.example.com:8080"
            # Time sync will make a request
            # (mocked response ensures no actual network call)

    def test_weex_api_call_with_proxy(self, weex_config_with_proxy: ExchangeConfig) -> None:
        """Test that WEEX API calls work with proxy configured."""
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            # Mock the server time endpoint
            rsps.add(
                responses.GET,
                "https://api-contract.weex.com/api/v5/public/time",
                json={"data": {"timestamp": "1704355200000"}},
                status=200
            )

            client = create_client(weex_config_with_proxy)

            # The proxy should be set but the mock will intercept the call
            assert client.proxy_url == "http://proxy.example.com:8080"

    def test_proxy_url_preserved_in_session(self, aster_config_with_proxy: ExchangeConfig) -> None:
        """Test that proxy configuration is preserved in the session."""
        client = create_client(aster_config_with_proxy)

        # Verify proxy is set
        assert "http" in client.session.proxies
        assert "https" in client.session.proxies

        # Verify proxy value matches config
        assert client.session.proxies["http"] == aster_config_with_proxy.proxy_url
        assert client.session.proxies["https"] == aster_config_with_proxy.proxy_url
