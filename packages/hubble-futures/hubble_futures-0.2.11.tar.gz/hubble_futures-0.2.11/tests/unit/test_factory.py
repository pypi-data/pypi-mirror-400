"""Unit tests for factory functions."""

import pytest

from hubble_futures import (
    AsterFuturesClient,
    ExchangeConfig,
    WeexFuturesClient,
    create_client,
    get_default_base_url,
    list_exchanges,
)


class TestCreateClient:
    """Test create_client factory function."""

    def test_create_aster_client(self) -> None:
        """Test creating Aster client."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="test_key",
            api_secret="test_secret"
        )

        client = create_client(config)

        assert isinstance(client, AsterFuturesClient)
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.base_url == "https://fapi.asterdex.com"

    def test_create_aster_client_with_alias(self) -> None:
        """Test creating Aster client using alias."""
        config = ExchangeConfig(
            name="aster",
            api_key="test_key",
            api_secret="test_secret"
        )

        client = create_client(config)

        assert isinstance(client, AsterFuturesClient)

    def test_create_weex_client(self) -> None:
        """Test creating WEEX client."""
        config = ExchangeConfig(
            name="weex",
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        client = create_client(config)

        assert isinstance(client, WeexFuturesClient)
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.passphrase == "test_pass"
        assert client.base_url == "https://api-contract.weex.com"

    def test_create_client_with_custom_base_url(self) -> None:
        """Test creating client with custom base URL."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://custom.example.com"
        )

        client = create_client(config)

        assert client.base_url == "https://custom.example.com"

    def test_create_client_unknown_exchange(self) -> None:
        """Test creating client with unknown exchange raises ValueError."""
        config = ExchangeConfig(
            name="unknown_exchange",
            api_key="test_key",
            api_secret="test_secret"
        )

        with pytest.raises(ValueError, match="Unknown exchange"):
            create_client(config)

    def test_create_client_case_insensitive(self) -> None:
        """Test exchange name is case-insensitive."""
        config = ExchangeConfig(
            name="ASTERDEX",
            api_key="test_key",
            api_secret="test_secret"
        )

        client = create_client(config)

        assert isinstance(client, AsterFuturesClient)


class TestListExchanges:
    """Test list_exchanges function."""

    def test_list_exchanges(self) -> None:
        """Test listing all supported exchanges."""
        exchanges = list_exchanges()

        assert isinstance(exchanges, list)
        assert "asterdex" in exchanges
        assert "weex" in exchanges
        assert "aster" in exchanges  # Alias
        assert len(exchanges) >= 3

    def test_list_exchanges_sorted(self) -> None:
        """Test exchanges are sorted."""
        exchanges = list_exchanges()

        assert exchanges == sorted(exchanges)


class TestGetDefaultBaseUrl:
    """Test get_default_base_url function."""

    def test_get_aster_base_url(self) -> None:
        """Test getting Aster base URL."""
        url = get_default_base_url("asterdex")

        assert url == "https://fapi.asterdex.com"

    def test_get_weex_base_url(self) -> None:
        """Test getting WEEX base URL."""
        url = get_default_base_url("weex")

        assert url == "https://api-contract.weex.com"

    def test_get_url_with_alias(self) -> None:
        """Test getting URL using alias."""
        url = get_default_base_url("aster")

        assert url == "https://fapi.asterdex.com"

    def test_get_url_case_insensitive(self) -> None:
        """Test URL retrieval is case-insensitive."""
        url = get_default_base_url("ASTERDEX")

        assert url == "https://fapi.asterdex.com"

    def test_get_url_unknown_exchange(self) -> None:
        """Test getting URL for unknown exchange returns empty string."""
        url = get_default_base_url("unknown")

        assert url == ""
