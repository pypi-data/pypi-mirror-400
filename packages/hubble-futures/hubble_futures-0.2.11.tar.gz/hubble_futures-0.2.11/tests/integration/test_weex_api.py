"""Integration tests for WEEX Futures API with mocked responses."""

import time

import pytest
import responses


@pytest.mark.integration
class TestWeexMarketData:
    """Test WEEX market data endpoints with mocked responses."""

    def test_get_klines(self, mock_responses, weex_client):
        """Test fetching kline data with symbol conversion."""
        symbol = "BTCUSDT"
        weex_symbol = "cmt_btcusdt"

        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/candles",
            json=[
                [1704067200000, "42000.00", "42500.00", "41800.00", "42300.00", "1000.5", "42300000.00"],
                [1704067260000, "42300.00", "42600.00", "42200.00", "42400.00", "950.3", "40280000.00"],
            ],
            status=200,
        )

        klines = weex_client.get_klines(symbol, "1h", 2)

        assert len(klines) == 2
        assert klines[0]["open_time"] == 1704067200000
        assert klines[0]["open"] == 42000.00
        assert klines[0]["high"] == 42500.00
        assert klines[0]["low"] == 41800.00
        assert klines[0]["close"] == 42300.00
        assert klines[0]["volume"] == 1000.5
        assert klines[0]["trades"] == 0  # WEEX doesn't provide trade count

    def test_get_mark_price(self, mock_responses, weex_client):
        """Test fetching mark price (requires two API calls)."""
        symbol = "BTCUSDT"
        weex_symbol = "cmt_btcusdt"

        # Mock ticker endpoint
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/ticker",
            json={
                "markPrice": "42350.50",
                "indexPrice": "42340.20",
            },
            status=200,
        )

        # Mock funding rate endpoint
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/currentFundRate",
            json={
                "fundingRate": "0.0001",
                "timestamp": 1704110400000,
            },
            status=200,
        )

        result = weex_client.get_mark_price(symbol)

        assert result["symbol"] == symbol
        assert result["mark_price"] == 42350.50
        assert result["index_price"] == 42340.20
        assert result["funding_rate"] == 0.0001
        assert result["next_funding_time"] == 1704110400000

    def test_symbol_conversion(self, weex_client):
        """Test symbol conversion between standard and WEEX format."""
        # Standard to WEEX
        assert weex_client._to_weex_symbol("BTCUSDT") == "cmt_btcusdt"
        assert weex_client._to_weex_symbol("ETHUSDT") == "cmt_ethusdt"

        # WEEX to standard
        assert weex_client._from_weex_symbol("cmt_btcusdt") == "BTCUSDT"
        assert weex_client._from_weex_symbol("cmt_ethusdt") == "ETHUSDT"

        # Already in WEEX format
        assert weex_client._to_weex_symbol("cmt_btcusdt") == "cmt_btcusdt"


@pytest.mark.integration
class TestWeexAccount:
    """Test WEEX account endpoints with mocked responses."""

    def test_get_account(self, mock_responses, weex_client):
        """Test fetching account information with USDT filtering."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/account/assets",
            json=[
                {
                    "coinName": "USDT",
                    "available": "9450.75",
                    "frozen": "500.00",
                    "equity": "10050.75",
                    "unrealizePnl": "50.25",
                },
                {
                    "coinName": "BTC",
                    "available": "0.5",
                    "frozen": "0",
                    "equity": "21000.00",
                    "unrealizePnl": "0",
                },
            ],
            status=200,
        )

        account = weex_client.get_account()

        # Should filter USDT asset
        assert account["total_wallet_balance"] == 10000.50  # equity - unrealizePnl
        assert account["total_unrealized_profit"] == 50.25
        assert account["total_margin_balance"] == 10050.75
        assert account["available_balance"] == 9450.75
        assert account["total_position_initial_margin"] == 500.00

    def test_get_positions(self, mock_responses, weex_client):
        """Test fetching positions with side conversion."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/account/position/allPosition",
            json=[
                {
                    "symbol": "cmt_btcusdt",
                    "size": "0.5",
                    "side": "LONG",
                    "open_value": "21000.00",
                    "unrealizePnl": "175.25",
                    "liquidatePrice": "40000.00",
                    "leverage": "10",
                    "margin_mode": "SHARED",
                    "marginSize": "500.00",
                },
                {
                    "symbol": "cmt_ethusdt",
                    "size": "1.0",
                    "side": "SHORT",
                    "open_value": "2200.00",
                    "unrealizePnl": "-50.00",
                    "liquidatePrice": "2500.00",
                    "leverage": "5",
                    "margin_mode": "1",
                    "marginSize": "200.00",
                },
                {
                    "symbol": "cmt_bchusdt",
                    "size": "0",  # Empty position
                    "side": "LONG",
                    "open_value": "0",
                    "unrealizePnl": "0",
                },
            ],
            status=200,
        )

        positions = weex_client.get_positions()

        # Should filter out empty positions and convert format
        assert len(positions) == 2

        # First position (LONG)
        assert positions[0]["symbol"] == "BTCUSDT"
        assert positions[0]["position_amt"] == 0.5  # Positive for LONG
        assert positions[0]["entry_price"] == 42000.00  # open_value / size
        assert positions[0]["unrealized_profit"] == 175.25

        # Second position (SHORT)
        assert positions[1]["symbol"] == "ETHUSDT"
        assert positions[1]["position_amt"] == -1.0  # Negative for SHORT
        assert positions[1]["entry_price"] == 2200.00
        assert positions[1]["unrealized_profit"] == -50.00

    def test_get_balance(self, mock_responses, weex_client):
        """Test fetching balance summary."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/account/assets",
            json=[
                {
                    "coinName": "USDT",
                    "available": "9450.75",
                    "equity": "10050.75",
                    "unrealizePnl": "50.25",
                },
            ],
            status=200,
        )

        balance = weex_client.get_balance()

        assert balance["available_balance"] == 9450.75
        assert balance["total_margin_balance"] == 10050.75
        assert balance["total_unrealized_profit"] == 50.25


@pytest.mark.integration
class TestWeexTrading:
    """Test WEEX trading endpoints with mocked responses."""

    def test_place_order_limit_long(self, mock_responses, weex_client):
        """Test placing a limit order to open long position."""
        # Mock symbol filters for formatting
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/contracts",
            json=[
                {
                    "tick_size": 1,
                    "size_increment": 5,
                    "minOrderSize": 0.0001,
                    "maxOrderSize": 100000,
                    "maxLeverage": 125,
                }
            ],
            status=200,
        )

        # Mock order placement
        mock_responses.add(
            responses.POST,
            "https://api-contract.weex.com/capi/v2/order/placeOrder",
            json={
                "order_id": "596471064624628269",
                "client_oid": "client_order_001",
            },
            status=200,
        )

        result = weex_client.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=0.01,
            price=42000,
        )

        assert result["orderId"] == "596471064624628269"
        assert result["symbol"] == "BTCUSDT"
        assert result["status"] == "NEW"
        assert result["side"] == "BUY"

    def test_place_order_market_short(self, mock_responses, weex_client):
        """Test placing a market order to open short position."""
        # Mock symbol filters
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/contracts",
            json=[
                {
                    "tick_size": 1,
                    "size_increment": 5,
                    "minOrderSize": 0.0001,
                }
            ],
            status=200,
        )

        # Mock order placement
        mock_responses.add(
            responses.POST,
            "https://api-contract.weex.com/capi/v2/order/placeOrder",
            json={
                "order_id": "596471064624628270",
                "client_oid": "client_order_002",
            },
            status=200,
        )

        result = weex_client.place_order(
            symbol="BTCUSDT",
            side="SELL",
            order_type="MARKET",
            quantity=0.05,
        )

        assert result["orderId"] == "596471064624628270"
        assert result["type"] == "MARKET"

    def test_place_order_reduce_only(self, mock_responses, weex_client):
        """Test placing a reduce-only order (close position)."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/contracts",
            json=[
                {
                    "tick_size": 1,
                    "size_increment": 5,
                    "minOrderSize": 0.0001,
                }
            ],
            status=200,
        )

        mock_responses.add(
            responses.POST,
            "https://api-contract.weex.com/capi/v2/order/placeOrder",
            json={
                "order_id": "596471064624628271",
                "client_oid": "client_order_003",
            },
            status=200,
        )

        # SELL with reduce_only=True should use type=3 (Close Long)
        result = weex_client.place_order(
            symbol="BTCUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=0.5,
            price=42500,
            reduce_only=True,
        )

        assert result["orderId"] == "596471064624628271"

    def test_cancel_order(self, mock_responses, weex_client):
        """Test canceling an order."""
        mock_responses.add(
            responses.POST,
            "https://api-contract.weex.com/capi/v2/order/cancel_order",
            json={
                "order_id": "596471064624628269",
                "client_oid": "client_order_001",
                "result": True,
            },
            status=200,
        )

        result = weex_client.cancel_order(symbol="BTCUSDT", order_id=596471064624628269)

        assert result["status"] == "CANCELED"
        assert result["orderId"] == "596471064624628269"

    def test_set_leverage(self, mock_responses, weex_client):
        """Test setting leverage."""
        mock_responses.add(
            responses.POST,
            "https://api-contract.weex.com/capi/v2/account/leverage",
            json={
                "symbol": "cmt_btcusdt",
                "longLeverage": "20",
                "shortLeverage": "20",
            },
            status=200,
        )

        result = weex_client.set_leverage(symbol="BTCUSDT", leverage=20)

        assert result["longLeverage"] == "20"
        assert result["shortLeverage"] == "20"


@pytest.mark.integration
class TestWeexParameterMapping:
    """Test WEEX-specific parameter mapping."""

    def test_time_in_force_mapping(self, mock_responses, weex_client):
        """Test timeInForce to order_type mapping."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/contracts",
            json=[
                {
                    "tick_size": 1,
                    "size_increment": 5,
                    "minOrderSize": 0.0001,
                }
            ],
            status=200,
        )

        # Test different timeInForce values
        for tif in ["GTC", "IOC", "FOK", "GTX"]:
            mock_responses.add(
                responses.POST,
                "https://api-contract.weex.com/capi/v2/order/placeOrder",
                json={"order_id": f"test_{tif}", "client_oid": tif},
                status=200,
            )

            result = weex_client.place_order(
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity=0.01,
                price=42000,
                time_in_force=tif,
            )

            assert result["orderId"] == f"test_{tif}"

    def test_side_and_reduce_only_mapping(self, mock_responses, weex_client):
        """Test side + reduce_only to WEEX type mapping."""
        mock_responses.add(
            responses.GET,
            "https://api-contract.weex.com/capi/v2/market/contracts",
            json=[
                {
                    "tick_size": 1,
                    "size_increment": 5,
                    "minOrderSize": 0.0001,
                }
            ],
            status=200,
        )

        test_cases = [
            ("BUY", False, "1"),   # Open Long
            ("SELL", False, "2"),  # Open Short
            ("SELL", True, "3"),   # Close Long
            ("BUY", True, "4"),    # Close Short
        ]

        for side, reduce_only, expected_type in test_cases:
            mock_responses.add(
                responses.POST,
                "https://api-contract.weex.com/capi/v2/order/placeOrder",
                json={"order_id": f"test_{side}_{reduce_only}", "client_oid": "test"},
                status=200,
            )

            weex_client.place_order(
                symbol="BTCUSDT",
                side=side,
                order_type="LIMIT",
                quantity=0.01,
                price=42000,
                reduce_only=reduce_only,
            )
