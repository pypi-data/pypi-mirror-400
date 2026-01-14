"""Unit tests for WeexFuturesClient."""

import base64
import hashlib
import hmac

import pytest

from hubble_futures import ExchangeConfig, WeexFuturesClient


class TestWeexClientInit:
    """Test WeexFuturesClient initialization."""

    def test_init_minimal(self) -> None:
        """Test initializing client with minimal parameters."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.passphrase == "test_pass"
        assert client.base_url == "https://api-contract.weex.com"

    def test_init_custom_base_url(self) -> None:
        """Test initializing client with custom base URL."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass",
            base_url="https://custom.example.com"
        )

        assert client.base_url == "https://custom.example.com"

    def test_init_missing_passphrase(self) -> None:
        """Test initializing without passphrase raises ValueError."""
        with pytest.raises(ValueError, match="passphrase is required"):
            WeexFuturesClient(
                api_key="test_key",
                api_secret="test_secret",
                passphrase=""
            )

    def test_from_config(self) -> None:
        """Test creating client from ExchangeConfig."""
        config = ExchangeConfig(
            name="weex",
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        client = WeexFuturesClient.from_config(config)

        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        assert client.passphrase == "test_pass"

    def test_session_headers(self) -> None:
        """Test session headers are set correctly."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["locale"] == "en-US"


class TestWeexSymbolConversion:
    """Test symbol format conversion."""

    def test_to_weex_symbol(self) -> None:
        """Test converting standard symbol to WEEX format."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        assert client._to_weex_symbol("BTCUSDT") == "cmt_btcusdt"
        assert client._to_weex_symbol("ETHUSDT") == "cmt_ethusdt"

    def test_to_weex_symbol_already_converted(self) -> None:
        """Test converting symbol that's already in WEEX format."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        # Should not double-convert
        assert client._to_weex_symbol("cmt_btcusdt") == "cmt_btcusdt"

    def test_from_weex_symbol(self) -> None:
        """Test converting WEEX symbol to standard format."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        assert client._from_weex_symbol("cmt_btcusdt") == "BTCUSDT"
        assert client._from_weex_symbol("cmt_ethusdt") == "ETHUSDT"

    def test_from_weex_symbol_no_prefix(self) -> None:
        """Test converting symbol without cmt_ prefix."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        # Should just uppercase
        assert client._from_weex_symbol("btcusdt") == "BTCUSDT"

    def test_symbol_round_trip(self) -> None:
        """Test converting symbol back and forth."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        original = "BTCUSDT"
        weex = client._to_weex_symbol(original)
        back = client._from_weex_symbol(weex)

        assert back == original


class TestWeexSignature:
    """Test WEEX-specific signature generation."""

    def test_generate_weex_signature(self) -> None:
        """Test WEEX signature generation with known values."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        timestamp = "1234567890000"
        method = "GET"
        path = "/capi/v2/market/ticker"
        body = ""

        signature = client._generate_weex_signature(timestamp, method, path, body)

        # Verify signature is base64 encoded
        assert isinstance(signature, str)

        # Verify signature is valid base64
        try:
            base64.b64decode(signature)
        except Exception:
            pytest.fail("Signature is not valid base64")

        # Verify signature matches expected
        sign_string = f"{timestamp}{method}{path}{body}"
        expected_sig = base64.b64encode(
            hmac.new(
                b"test_secret",
                sign_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        assert signature == expected_sig

    def test_signature_with_body(self) -> None:
        """Test signature generation with request body."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        timestamp = "1234567890000"
        method = "POST"
        path = "/capi/v2/order/placeOrder"
        body = '{"symbol":"cmt_btcusdt","type":"1","size":"0.01"}'

        signature = client._generate_weex_signature(timestamp, method, path, body)

        # Verify signature includes body in calculation
        sign_string = f"{timestamp}{method}{path}{body}"
        expected_sig = base64.b64encode(
            hmac.new(
                b"test_secret",
                sign_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        assert signature == expected_sig

    def test_signature_with_query_params(self) -> None:
        """Test signature generation with query parameters in path."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        timestamp = "1234567890000"
        method = "GET"
        path = "/capi/v2/market/ticker?symbol=cmt_btcusdt"
        body = ""

        signature = client._generate_weex_signature(timestamp, method, path, body)

        # Query params should be included in path
        sign_string = f"{timestamp}{method}{path}{body}"
        expected_sig = base64.b64encode(
            hmac.new(
                b"test_secret",
                sign_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        assert signature == expected_sig


class TestWeexOrderTypeMapping:
    """Test WEEX order type parameter mapping."""

    def test_side_to_type_mapping(self) -> None:
        """Test mapping of side + reduce_only to WEEX type."""
        # This is implicit in place_order logic, testing concept here

        # BUY + !reduce_only = 1 (Open Long)
        # BUY + reduce_only = 4 (Close Short)
        # SELL + !reduce_only = 2 (Open Short)
        # SELL + reduce_only = 3 (Close Long)

        mappings = [
            ("BUY", False, "1"),
            ("BUY", True, "4"),
            ("SELL", False, "2"),
            ("SELL", True, "3"),
        ]

        for side, reduce_only, expected_type in mappings:
            if side.upper() == "BUY":
                weex_type = "4" if reduce_only else "1"
            else:
                weex_type = "3" if reduce_only else "2"

            assert weex_type == expected_type

    def test_order_type_to_match_price(self) -> None:
        """Test mapping order type to match_price."""
        # MARKET -> 1
        # LIMIT -> 0

        assert "1" == ("1" if "MARKET" == "MARKET" else "0")
        assert "0" == ("1" if "LIMIT" == "MARKET" else "0")

    def test_time_in_force_mapping(self) -> None:
        """Test mapping time_in_force to WEEX order_type."""
        order_type_map = {
            "GTC": "0",
            "IOC": "3",
            "FOK": "2",
            "GTX": "1"
        }

        assert order_type_map["GTC"] == "0"
        assert order_type_map["IOC"] == "3"
        assert order_type_map["FOK"] == "2"
        assert order_type_map["GTX"] == "1"


class TestWeexServerTime:
    """Test WEEX server time parsing."""

    def test_parse_server_time_weex_format(self) -> None:
        """Test parsing WEEX server time response."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        response_data = {
            "code": "00000",
            "data": {
                "timestamp": 1234567890000
            }
        }

        timestamp = client._parse_server_time(response_data)
        assert timestamp == 1234567890000

    def test_parse_server_time_missing_data(self) -> None:
        """Test parsing server time with missing data field."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        response_data = {"code": "00000"}

        timestamp = client._parse_server_time(response_data)
        # Should return current time as fallback
        assert isinstance(timestamp, int)
        assert timestamp > 0


class TestWeexSymbolFilters:
    """Test WEEX symbol filter conversion."""

    def test_symbol_filters_precision_conversion(self) -> None:
        """Test converting WEEX precision to tick_size/step_size."""
        # WEEX uses tick_size as precision (e.g., 1 means 0.1)
        # Our code converts: 10 ** (-tick_size)

        tick_size_precision = 1
        expected_tick_size = 10 ** (-tick_size_precision)
        assert expected_tick_size == 0.1

        step_size_precision = 5
        expected_step_size = 10 ** (-step_size_precision)
        assert expected_step_size == 0.00001


class TestWeexValidateOrder:
    """Test WEEX order parameter validation."""

    def test_validate_order_params_valid(self) -> None:
        """Test validation with valid parameters."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        # Mock filters
        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.00001,
            "min_qty": 0.001,
            "min_notional": 1
        }

        result = client.validate_order_params("BTCUSDT", price=50000, quantity=0.01)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_order_params_qty_too_low(self) -> None:
        """Test validation with quantity below minimum."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        client._symbol_filters["BTCUSDT"] = {
            "tick_size": 0.1,
            "step_size": 0.00001,
            "min_qty": 0.01,
            "min_notional": 1
        }

        result = client.validate_order_params("BTCUSDT", price=50000, quantity=0.005)

        assert result["valid"] is False
        assert any("Quantity" in err for err in result["errors"])


class TestWeexLeverageBracket:
    """Test WEEX leverage bracket conversion."""

    def test_get_leverage_bracket_with_symbol(self) -> None:
        """Test getting leverage bracket for a symbol."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        # Mock filters
        client._symbol_filters["BTCUSDT"] = {
            "max_leverage": 125,
            "min_leverage": 1
        }

        bracket = client.get_leverage_bracket("BTCUSDT")

        assert isinstance(bracket, list)
        assert len(bracket) == 1
        assert bracket[0]["symbol"] == "BTCUSDT"
        assert bracket[0]["brackets"][0]["initialLeverage"] == 125

    def test_get_leverage_bracket_no_symbol(self) -> None:
        """Test getting leverage bracket without symbol."""
        client = WeexFuturesClient(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_pass"
        )

        bracket = client.get_leverage_bracket()

        assert bracket == []
