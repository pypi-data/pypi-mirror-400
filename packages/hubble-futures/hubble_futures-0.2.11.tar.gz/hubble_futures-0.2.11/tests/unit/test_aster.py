"""Unit tests for AsterFuturesClient."""

import hashlib
import hmac
from decimal import ROUND_DOWN, ROUND_HALF_UP

import pytest

from hubble_futures import AsterFuturesClient, ExchangeConfig


class TestAsterClientInit:
    """Test AsterFuturesClient initialization."""

    def test_init_minimal(self) -> None:
        """Test initializing client with minimal parameters."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.base_url == "https://fapi.asterdex.com"

    def test_init_custom_base_url(self) -> None:
        """Test initializing client with custom base URL."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://custom.example.com"
        )

        assert client.base_url == "https://custom.example.com"

    def test_init_missing_api_key(self) -> None:
        """Test initializing without API key raises ValueError."""
        with pytest.raises(ValueError, match="api_key is required"):
            AsterFuturesClient(api_key="", api_secret="secret")

    def test_init_missing_api_secret(self) -> None:
        """Test initializing without API secret raises ValueError."""
        with pytest.raises(ValueError, match="api_secret is required"):
            AsterFuturesClient(api_key="key", api_secret="")

    def test_from_config(self) -> None:
        """Test creating client from ExchangeConfig."""
        config = ExchangeConfig(
            name="asterdex",
            api_key="test_key",
            api_secret="test_secret"
        )

        client = AsterFuturesClient.from_config(config)

        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"

    def test_session_headers(self) -> None:
        """Test session headers are set correctly."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["X-MBX-APIKEY"] == "test_key"


class TestAsterSignature:
    """Test signature generation."""

    def test_generate_signature(self) -> None:
        """Test signature generation with known values."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "0.01",
            "price": "50000",
            "timestamp": "1234567890000",
            "recvWindow": "5000"
        }

        signature = client._generate_signature(params)

        # Verify signature is correct format (hex string)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex is 64 characters

        # Verify signature matches expected
        expected_query = "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=0.01&price=50000&timestamp=1234567890000&recvWindow=5000"
        expected_sig = hmac.new(
            b"test_secret",
            expected_query.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        assert signature == expected_sig

    def test_signature_order_matters(self) -> None:
        """Test that parameter order affects signature."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        params1 = {"a": "1", "b": "2", "c": "3"}
        params2 = {"c": "3", "a": "1", "b": "2"}

        sig1 = client._generate_signature(params1)
        sig2 = client._generate_signature(params2)

        # Aster DEX uses insertion order, so different order = different signature
        assert sig1 != sig2


class TestAsterDecimalFormatting:
    """Test decimal formatting for precision compliance."""

    def test_format_decimal_step_size(self) -> None:
        """Test formatting with step size."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        # Test quantity with step size 0.001
        result = client._format_decimal(0.0123, step=0.001, rounding=ROUND_DOWN)
        assert result == "0.012"

    def test_format_decimal_precision(self) -> None:
        """Test formatting with precision."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        # Test price with 2 decimal places
        result = client._format_decimal(50000.456, precision=2, rounding=ROUND_HALF_UP)
        assert result == "50000.46"

    def test_format_decimal_both(self) -> None:
        """Test formatting with both step size and precision."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        # Step size takes precedence
        result = client._format_decimal(0.0123, step=0.001, precision=4, rounding=ROUND_DOWN)
        assert result == "0.012"

    def test_format_decimal_none_value(self) -> None:
        """Test formatting None returns empty string."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        result = client._format_decimal(None)  # type: ignore[arg-type]
        assert result == ""

    def test_format_decimal_zero_step(self) -> None:
        """Test formatting with zero step size."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        result = client._format_decimal(0.0123, step=0, rounding=ROUND_DOWN)
        assert result == "0.0123"

    def test_format_decimal_rounding_modes(self) -> None:
        """Test different rounding modes."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        value = 0.0125

        # ROUND_DOWN
        result_down = client._format_decimal(value, step=0.001, rounding=ROUND_DOWN)
        assert result_down == "0.012"

        # ROUND_HALF_UP
        result_up = client._format_decimal(value, step=0.001, rounding=ROUND_HALF_UP)
        assert result_up == "0.013"  # 0.0125 rounds to 0.013


class TestAsterSymbolFilters:
    """Test symbol filter parsing (requires mocked exchange info)."""

    def test_symbol_filters_cache(self) -> None:
        """Test symbol filters are cached."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        # Set mock cache
        client._symbol_filters["BTCUSDT"] = {"tick_size": 0.1}

        # Should return cached value
        filters = client._symbol_filters.get("BTCUSDT")
        assert filters is not None
        assert filters["tick_size"] == 0.1


class TestAsterLiquidationPrice:
    """Test liquidation price calculation."""

    def test_calculate_liquidation_price_long(self) -> None:
        """Test liquidation price for long position."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        liq_price = client.calculate_liquidation_price(
            entry_price=50000,
            leverage=10,
            side="LONG",
            maintenance_margin_rate=0.005
        )

        # For 10x long: liquidation at entry * (1 - 0.1 + 0.005) = entry * 0.905
        expected = 50000 * 0.905
        assert abs(liq_price - expected) < 0.01

    def test_calculate_liquidation_price_short(self) -> None:
        """Test liquidation price for short position."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        liq_price = client.calculate_liquidation_price(
            entry_price=50000,
            leverage=10,
            side="SHORT",
            maintenance_margin_rate=0.005
        )

        # For 10x short: liquidation at entry * (1 + 0.1 - 0.005) = entry * 1.095
        expected = 50000 * 1.095
        assert abs(liq_price - expected) < 0.01


class TestAsterValidateOrder:
    """Test order parameter validation."""

    def test_validate_order_params_valid(self) -> None:
        """Test validation with valid parameters."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        # Mock filters
        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.001,
            "min_price": 1000,
            "min_qty": 0.001,
            "min_notional": 10
        }

        result = client.validate_order_params("BTCUSDT", price=50000, quantity=0.01)

        assert result["valid"] is True
        assert result["adjusted_price"] == 50000.0
        assert result["adjusted_quantity"] == 0.01
        assert result["notional"] == 500.0
        assert len(result["errors"]) == 0

    def test_validate_order_params_price_too_low(self) -> None:
        """Test validation with price below minimum."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.001,
            "min_price": 1000,
            "min_qty": 0.001,
            "min_notional": 10
        }

        result = client.validate_order_params("BTCUSDT", price=500, quantity=0.01)

        assert result["valid"] is False
        assert "below minimum" in result["errors"][0]

    def test_validate_order_params_qty_too_low(self) -> None:
        """Test validation with quantity below minimum."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.001,
            "min_price": 1000,
            "min_qty": 0.01,
            "min_notional": 10
        }

        result = client.validate_order_params("BTCUSDT", price=50000, quantity=0.005)

        assert result["valid"] is False
        assert any("Quantity" in err for err in result["errors"])

    def test_validate_order_params_notional_too_low(self) -> None:
        """Test validation with notional below minimum."""
        client = AsterFuturesClient(
            api_key="test_key",
            api_secret="test_secret"
        )

        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.001,
            "min_price": 1000,
            "min_qty": 0.001,
            "min_notional": 100
        }

        result = client.validate_order_params("BTCUSDT", price=5000, quantity=0.01)

        assert result["valid"] is False
        assert any("Notional" in err for err in result["errors"])
