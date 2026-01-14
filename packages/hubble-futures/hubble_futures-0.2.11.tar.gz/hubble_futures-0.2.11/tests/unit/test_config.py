"""Unit tests for ExchangeConfig."""

from hubble_futures.config import ExchangeConfig


class TestExchangeConfig:
    """Test ExchangeConfig dataclass."""

    def test_minimal_config(self) -> None:
        """Test creating config with minimal required fields."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="test_key",
            api_secret="test_secret"
        )

        assert config.name == "asterdex"
        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.base_url == ""
        assert config.passphrase == ""
        assert config.proxy_url is None

    def test_full_config(self) -> None:
        """Test creating config with all fields."""
        config = ExchangeConfig(
            name="weex",
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://api-contract.weex.com",
            passphrase="test_passphrase",
            proxy_url="http://user:pass@proxy.example.com:8080"
        )

        assert config.name == "weex"
        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.base_url == "https://api-contract.weex.com"
        assert config.passphrase == "test_passphrase"
        assert config.proxy_url == "http://user:pass@proxy.example.com:8080"

    def test_config_defaults(self) -> None:
        """Test default values for optional fields."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="key",
            api_secret="secret"
        )

        assert config.base_url == ""
        assert config.passphrase == ""
        assert config.proxy_url is None

    def test_config_immutability(self) -> None:
        """Test that config is a frozen dataclass (if frozen)."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="key",
            api_secret="secret"
        )

        # Dataclass without frozen=True allows mutation
        # This test verifies current behavior
        config.name = "weex"
        assert config.name == "weex"

    def test_proxy_url_only(self) -> None:
        """Test config with only proxy_url set."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="key",
            api_secret="secret",
            proxy_url="http://proxy.example.com:8080"
        )

        assert config.proxy_url == "http://proxy.example.com:8080"
        assert config.base_url == ""
        assert config.passphrase == ""

    def test_proxy_url_format_with_auth(self) -> None:
        """Test proxy URL with authentication."""
        proxy = "http://hubble-weex:Ft***@43.133.168.184:8080"
        config = ExchangeConfig(
            name="weex",
            api_key="key",
            api_secret="secret",
            proxy_url=proxy
        )

        assert config.proxy_url == proxy

    def test_proxy_url_format_without_auth(self) -> None:
        """Test proxy URL without authentication."""
        proxy = "http://43.133.168.184:8080"
        config = ExchangeConfig(
            name="asterdex",
            api_key="key",
            api_secret="secret",
            proxy_url=proxy
        )

        assert config.proxy_url == proxy

