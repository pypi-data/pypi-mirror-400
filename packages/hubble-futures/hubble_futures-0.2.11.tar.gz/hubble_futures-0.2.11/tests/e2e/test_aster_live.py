"""E2E tests for Aster DEX with real API."""

import pytest


@pytest.mark.e2e
class TestAsterMarketData:
    """Test Aster market data endpoints."""

    def test_get_klines(self, aster_client, test_symbol):
        """Test fetching K-line data."""
        klines = aster_client.get_klines(test_symbol, "1h", 10)

        assert isinstance(klines, list)
        assert len(klines) > 0
        assert len(klines) <= 10

        # Verify kline structure
        kline = klines[0]
        assert "open_time" in kline
        assert "open" in kline
        assert "high" in kline
        assert "low" in kline
        assert "close" in kline
        assert "volume" in kline
        assert "close_time" in kline
        assert "quote_volume" in kline
        assert "trades" in kline

        # Verify data types
        assert isinstance(kline["open"], float)
        assert isinstance(kline["high"], float)
        assert isinstance(kline["low"], float)
        assert isinstance(kline["close"], float)
        assert isinstance(kline["volume"], float)

    def test_get_mark_price(self, aster_client, test_symbol):
        """Test fetching mark price."""
        mark_price_data = aster_client.get_mark_price(test_symbol)

        assert isinstance(mark_price_data, dict)
        assert "symbol" in mark_price_data
        assert "mark_price" in mark_price_data
        assert "index_price" in mark_price_data
        assert "funding_rate" in mark_price_data
        assert "next_funding_time" in mark_price_data

        assert mark_price_data["symbol"] == test_symbol
        assert isinstance(mark_price_data["mark_price"], float)
        assert mark_price_data["mark_price"] > 0

    def test_get_ticker_24hr(self, aster_client, test_symbol):
        """Test fetching 24h ticker."""
        ticker = aster_client.get_ticker_24hr(test_symbol)

        assert isinstance(ticker, dict)
        assert ticker.get("symbol") == test_symbol

    def test_get_depth(self, aster_client, test_symbol):
        """Test fetching orderbook depth."""
        depth = aster_client.get_depth(test_symbol, limit=10)

        assert isinstance(depth, dict)
        assert "bids" in depth
        assert "asks" in depth

        # Verify we have bids and asks
        assert len(depth["bids"]) > 0
        assert len(depth["asks"]) > 0

        # Verify structure of first bid
        bid = depth["bids"][0]
        assert len(bid) >= 2  # [price, quantity]

    def test_get_exchange_info(self, aster_client):
        """Test fetching exchange information."""
        exchange_info = aster_client.get_exchange_info()

        assert isinstance(exchange_info, dict)
        assert "symbols" in exchange_info
        assert len(exchange_info["symbols"]) > 0

    def test_get_symbol_filters(self, aster_client, test_symbol):
        """Test fetching symbol trading rules."""
        filters = aster_client.get_symbol_filters(test_symbol)

        assert isinstance(filters, dict)
        assert "tick_size" in filters
        assert "step_size" in filters
        assert "min_qty" in filters
        assert "min_notional" in filters

        # Verify values are reasonable
        assert filters["tick_size"] > 0
        assert filters["step_size"] > 0


@pytest.mark.e2e
class TestAsterAccount:
    """Test Aster account endpoints."""

    def test_get_account(self, aster_client):
        """Test fetching account information."""
        account = aster_client.get_account()

        assert isinstance(account, dict)
        assert "total_wallet_balance" in account
        assert "available_balance" in account
        assert "total_margin_balance" in account
        assert "total_unrealized_profit" in account

        # Verify numeric values
        assert isinstance(account["total_wallet_balance"], float)
        assert isinstance(account["available_balance"], float)

    def test_get_balance(self, aster_client):
        """Test fetching balance summary."""
        balance = aster_client.get_balance()

        assert isinstance(balance, dict)
        assert "available_balance" in balance
        assert "total_margin_balance" in balance
        assert "total_unrealized_profit" in balance

    def test_get_positions(self, aster_client, test_symbol):
        """Test fetching positions."""
        # Get all positions
        positions = aster_client.get_positions()
        assert isinstance(positions, list)

        # Get positions for specific symbol
        symbol_positions = aster_client.get_positions(test_symbol)
        assert isinstance(symbol_positions, list)

        # If there are positions, verify structure
        if symbol_positions:
            position = symbol_positions[0]
            assert "symbol" in position
            assert "position_amt" in position
            assert "entry_price" in position
            assert "unrealized_profit" in position
            assert "leverage" in position

    def test_get_open_orders(self, aster_client, test_symbol):
        """Test fetching open orders."""
        # Get all open orders
        orders = aster_client.get_open_orders()
        assert isinstance(orders, list)

        # Get open orders for specific symbol
        symbol_orders = aster_client.get_open_orders(test_symbol)
        assert isinstance(symbol_orders, list)


@pytest.mark.e2e
class TestAsterHelpers:
    """Test Aster helper functions."""

    def test_validate_order_params(self, aster_client, test_symbol):
        """Test order parameter validation."""
        # Get current mark price to use realistic values
        mark_price_data = aster_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Test valid parameters
        validation = aster_client.validate_order_params(
            test_symbol,
            price=current_price,
            quantity=0.01
        )

        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "adjusted_price" in validation
        assert "adjusted_quantity" in validation
        assert "errors" in validation

    def test_calculate_liquidation_price(self, aster_client):
        """Test liquidation price calculation."""
        liq_price_long = aster_client.calculate_liquidation_price(
            entry_price=50000,
            leverage=10,
            side="LONG"
        )

        liq_price_short = aster_client.calculate_liquidation_price(
            entry_price=50000,
            leverage=10,
            side="SHORT"
        )

        assert isinstance(liq_price_long, float)
        assert isinstance(liq_price_short, float)
        assert liq_price_long < 50000  # Long liquidation is below entry
        assert liq_price_short > 50000  # Short liquidation is above entry

    def test_get_funding_rate_history(self, aster_client, test_symbol):
        """Test fetching funding rate history."""
        rates = aster_client.get_funding_rate_history(test_symbol, limit=10)

        assert isinstance(rates, list)
        assert len(rates) > 0
        assert len(rates) <= 10

        # Verify funding rate structure
        if rates:
            rate = rates[0]
            assert "fundingRate" in rate or "funding_rate" in rate
            assert "fundingTime" in rate or "funding_time" in rate

    def test_get_open_interest(self, aster_client, test_symbol):
        """Test fetching open interest."""
        oi = aster_client.get_open_interest(test_symbol)

        assert isinstance(oi, dict)
        assert "symbol" in oi
        # API returns 'open_interest' (standardized format)
        assert "open_interest" in oi
        assert oi["symbol"] == test_symbol
        assert isinstance(oi["open_interest"], float)
        assert oi["open_interest"] >= 0

    def test_get_leverage_bracket(self, aster_client, test_symbol):
        """Test fetching leverage bracket."""
        bracket = aster_client.get_leverage_bracket(test_symbol)

        # May return list or empty dict depending on Aster API support
        assert bracket is not None
        if isinstance(bracket, list) and bracket:
            assert "symbol" in bracket[0]
            assert "brackets" in bracket[0]
            assert bracket[0]["symbol"] == test_symbol
        # If Aster doesn't support this endpoint, it may return empty dict


@pytest.mark.e2e
class TestAsterTrading:
    """
    Test Aster trading endpoints.

    These tests place and cancel real orders using minimum trade amounts.
    Orders are placed far from market price (50% below) to avoid filling.
    All orders are canceled at the end of each test.
    """

    def test_set_leverage(self, aster_client, test_symbol):
        """Test setting leverage."""
        result = aster_client.set_leverage(test_symbol, leverage=5)
        assert isinstance(result, dict)

    def test_set_margin_type(self, aster_client, test_symbol):
        """Test setting margin type."""
        import requests
        
        try:
            # Set to isolated margin
            result = aster_client.set_margin_type(test_symbol, margin_type="ISOLATED")
            assert isinstance(result, dict)

            # Set back to cross margin
            result = aster_client.set_margin_type(test_symbol, margin_type="CROSSED")
            assert isinstance(result, dict)
        except requests.exceptions.HTTPError as e:
            # Skip if Multi-Assets mode is enabled (cannot switch to isolated)
            if "-4168" in str(e) or "Multi-Assets" in str(e):
                pytest.skip("Cannot change margin type in Multi-Assets mode")

    def test_place_and_cancel_order(self, aster_client, test_symbol):
        """Test placing and canceling a limit order."""
        # Get current price
        mark_price_data = aster_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Get symbol filters for min quantity
        filters = aster_client.get_symbol_filters(test_symbol)
        min_qty = filters.get("min_qty", 0.001)

        # Place limit order far from current price (unlikely to fill)
        order_price = current_price * 0.5  # 50% below market
        order_qty = min_qty * 2  # Use minimum quantity

        order = aster_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price,
            time_in_force="GTC"
        )

        assert isinstance(order, dict)
        assert "orderId" in order
        order_id = order["orderId"]

        # Cancel the order
        cancel_result = aster_client.cancel_order(test_symbol, order_id=order_id)
        assert isinstance(cancel_result, dict)

    def test_get_order(self, aster_client, test_symbol):
        """Test querying order status."""
        # Get current price
        mark_price_data = aster_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Get symbol filters for min quantity
        filters = aster_client.get_symbol_filters(test_symbol)
        min_qty = filters.get("min_qty", 0.001)

        # Place a limit order
        order_price = current_price * 0.5  # 50% below market
        order_qty = min_qty * 2

        order = aster_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price,
            time_in_force="GTC"
        )

        order_id = order["orderId"]

        # Query the order
        order_info = aster_client.get_order(test_symbol, order_id=int(order_id))

        assert isinstance(order_info, dict)
        assert "orderId" in order_info
        assert "status" in order_info

        # Clean up: cancel the order
        aster_client.cancel_order(test_symbol, order_id=order_id)

    def test_cancel_all_orders(self, aster_client, test_symbol):
        """Test canceling all open orders for a symbol."""
        # Get current price and filters
        mark_price_data = aster_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]
        filters = aster_client.get_symbol_filters(test_symbol)
        min_qty = filters.get("min_qty", 0.001)

        # Place multiple limit orders
        order_price_1 = current_price * 0.5  # 50% below market
        order_price_2 = current_price * 0.6  # 40% below market
        order_qty = min_qty * 2

        aster_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price_1,
            time_in_force="GTC"
        )

        aster_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price_2,
            time_in_force="GTC"
        )

        # Cancel all orders
        result = aster_client.cancel_all_orders(test_symbol)
        assert isinstance(result, dict)

        # Verify all orders are canceled
        open_orders = aster_client.get_open_orders(test_symbol)
        assert len(open_orders) == 0

    def test_close_position(self, aster_client, test_symbol):
        """Test closing position."""
        # Get current positions
        positions = aster_client.get_positions(test_symbol)

        if positions and positions[0].get("position_amt", 0) != 0:
            # Close 100% of position
            result = aster_client.close_position(test_symbol, percent=100.0)
            assert isinstance(result, dict)

            # Verify position is closed
            positions_after = aster_client.get_positions(test_symbol)
            if positions_after:
                assert abs(positions_after[0].get("position_amt", 0)) < 0.0001
        else:
            # No position to close, test the method call returns gracefully
            result = aster_client.close_position(test_symbol, percent=100.0)
            # Should return something indicating no position or success
            assert result is not None

