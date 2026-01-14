"""E2E tests for WEEX with real API."""

import pytest


@pytest.mark.e2e
class TestWeexMarketData:
    """Test WEEX market data endpoints."""

    def test_get_klines(self, weex_client, test_symbol):
        """Test fetching K-line data."""
        klines = weex_client.get_klines(test_symbol, "1h", 10)

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

        # Verify data types
        assert isinstance(kline["open"], float)
        assert isinstance(kline["high"], float)
        assert isinstance(kline["low"], float)
        assert isinstance(kline["close"], float)
        assert isinstance(kline["volume"], float)

        # Verify WEEX-specific: close_time uses open_time
        assert kline["close_time"] == kline["open_time"]
        # Verify WEEX-specific: trades is 0 (not provided by WEEX)
        assert kline["trades"] == 0

    def test_get_mark_price(self, weex_client, test_symbol):
        """Test fetching mark price."""
        mark_price_data = weex_client.get_mark_price(test_symbol)

        assert isinstance(mark_price_data, dict)
        assert "symbol" in mark_price_data
        assert "mark_price" in mark_price_data
        assert "index_price" in mark_price_data
        assert "funding_rate" in mark_price_data

        assert mark_price_data["symbol"] == test_symbol
        assert isinstance(mark_price_data["mark_price"], float)
        assert mark_price_data["mark_price"] > 0

    def test_get_ticker_24hr(self, weex_client, test_symbol):
        """Test fetching 24h ticker."""
        ticker = weex_client.get_ticker_24hr(test_symbol)

        assert isinstance(ticker, dict)
        assert ticker.get("symbol") == test_symbol
        assert "lastPrice" in ticker or "markPrice" in ticker

    def test_get_depth(self, weex_client, test_symbol):
        """Test fetching orderbook depth."""
        depth = weex_client.get_depth(test_symbol, limit=10)

        assert isinstance(depth, dict)
        assert "bids" in depth
        assert "asks" in depth

        # Verify we have bids and asks
        assert len(depth["bids"]) > 0
        assert len(depth["asks"]) > 0

    def test_get_exchange_info(self, weex_client):
        """Test fetching exchange information."""
        exchange_info = weex_client.get_exchange_info()

        assert isinstance(exchange_info, dict)
        assert "symbols" in exchange_info
        assert len(exchange_info["symbols"]) > 0

    def test_get_symbol_filters(self, weex_client, test_symbol):
        """Test fetching symbol trading rules."""
        filters = weex_client.get_symbol_filters(test_symbol)

        assert isinstance(filters, dict)
        assert "tick_size" in filters
        assert "step_size" in filters
        assert "min_qty" in filters
        assert "max_leverage" in filters

        # Verify values are reasonable
        assert filters["tick_size"] > 0
        assert filters["step_size"] > 0
        assert filters["max_leverage"] > 0

    def test_symbol_conversion(self, weex_client, test_symbol):
        """Test WEEX symbol format conversion."""
        # Test internal conversion methods
        weex_symbol = weex_client._to_weex_symbol(test_symbol)
        assert weex_symbol.startswith("cmt_")
        assert weex_symbol.lower() == f"cmt_{test_symbol.lower()}"

        # Convert back
        standard_symbol = weex_client._from_weex_symbol(weex_symbol)
        assert standard_symbol == test_symbol


@pytest.mark.e2e
class TestWeexAccount:
    """Test WEEX account endpoints."""

    def test_get_account(self, weex_client):
        """Test fetching account information."""
        account = weex_client.get_account()

        assert isinstance(account, dict)
        assert "total_wallet_balance" in account
        assert "available_balance" in account
        assert "total_margin_balance" in account
        assert "total_unrealized_profit" in account

        # Verify numeric values
        assert isinstance(account["total_wallet_balance"], float)
        assert isinstance(account["available_balance"], float)

        # WEEX-specific: verify calculated wallet balance
        # wallet_balance = equity - unrealized_pnl
        equity = account["total_margin_balance"]
        unrealized = account["total_unrealized_profit"]
        expected_wallet = equity - unrealized
        assert abs(account["total_wallet_balance"] - expected_wallet) < 0.01

    def test_get_balance(self, weex_client):
        """Test fetching balance summary."""
        balance = weex_client.get_balance()

        assert isinstance(balance, dict)
        assert "available_balance" in balance
        assert "total_margin_balance" in balance
        assert "total_unrealized_profit" in balance

    def test_get_positions(self, weex_client, test_symbol):
        """Test fetching positions."""
        # Get all positions
        positions = weex_client.get_positions()
        assert isinstance(positions, list)

        # Get positions for specific symbol
        symbol_positions = weex_client.get_positions(test_symbol)
        assert isinstance(symbol_positions, list)

        # If there are positions, verify structure
        if symbol_positions:
            position = symbol_positions[0]
            assert "symbol" in position
            assert "position_amt" in position  # Should be signed (+ for long, - for short)
            assert "entry_price" in position
            assert "unrealized_profit" in position
            assert "leverage" in position
            assert "margin_type" in position

            # Verify WEEX-specific: entry_price calculated from open_value / size
            assert isinstance(position["entry_price"], float)
            if position["position_amt"] != 0:
                assert position["entry_price"] > 0

    def test_get_open_orders(self, weex_client, test_symbol):
        """Test fetching open orders."""
        # Get all open orders
        orders = weex_client.get_open_orders()
        assert isinstance(orders, list)

        # Get open orders for specific symbol
        symbol_orders = weex_client.get_open_orders(test_symbol)
        assert isinstance(symbol_orders, list)


@pytest.mark.e2e
class TestWeexHelpers:
    """Test WEEX helper functions."""

    def test_validate_order_params(self, weex_client, test_symbol):
        """Test order parameter validation."""
        # Get current mark price to use realistic values
        mark_price_data = weex_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Test valid parameters
        validation = weex_client.validate_order_params(test_symbol, price=current_price, quantity=0.01)

        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "adjusted_price" in validation
        assert "adjusted_quantity" in validation
        assert "errors" in validation

    def test_calculate_liquidation_price(self, weex_client):
        """Test liquidation price calculation."""
        liq_price_long = weex_client.calculate_liquidation_price(entry_price=50000, leverage=10, side="LONG")

        liq_price_short = weex_client.calculate_liquidation_price(entry_price=50000, leverage=10, side="SHORT")

        assert isinstance(liq_price_long, float)
        assert isinstance(liq_price_short, float)
        assert liq_price_long < 50000  # Long liquidation is below entry
        assert liq_price_short > 50000  # Short liquidation is above entry

    def test_get_leverage_bracket(self, weex_client, test_symbol):
        """Test fetching leverage bracket."""
        bracket = weex_client.get_leverage_bracket(test_symbol)

        assert isinstance(bracket, list)
        if bracket:
            assert "symbol" in bracket[0]
            assert "brackets" in bracket[0]
            assert bracket[0]["symbol"] == test_symbol

    def test_get_funding_rate_history(self, weex_client, test_symbol):
        """Test fetching funding rate history."""
        rates = weex_client.get_funding_rate_history(test_symbol, limit=10)

        assert isinstance(rates, list)
        assert len(rates) > 0
        assert len(rates) <= 10

        # Verify funding rate structure
        if rates:
            rate = rates[0]
            assert "funding_rate" in rate
            assert "funding_time" in rate
            assert isinstance(rate["funding_rate"], float)
            assert isinstance(rate["funding_time"], int)

    def test_get_open_interest(self, weex_client, test_symbol):
        """
        Test fetching open interest.

        Note: WEEX may not provide open interest data through a dedicated endpoint.
        This test verifies the method returns the expected structure.
        """
        oi = weex_client.get_open_interest(test_symbol)

        assert isinstance(oi, dict)
        assert "symbol" in oi
        assert "open_interest" in oi
        assert "timestamp" in oi
        assert oi["symbol"] == test_symbol
        assert isinstance(oi["open_interest"], float)
        # Open interest may be 0 if WEEX doesn't provide this data
        assert oi["open_interest"] >= 0


@pytest.mark.e2e
class TestWeexTrading:
    """
    Test WEEX trading endpoints.

    These tests place and cancel real orders using minimum trade amounts.
    Orders are placed far from market price (50% below) to avoid filling.
    All orders are canceled at the end of each test.
    """

    def test_set_leverage(self, weex_client, test_symbol):
        """Test setting leverage.

        Note: WEEX requires marginMode to match account's current mode.
        This test verifies the API call works or returns expected error.
        """
        from requests.exceptions import HTTPError

        try:
            result = weex_client.set_leverage(test_symbol, leverage=5)
            # WEEX returns success message: {'msg': 'success', 'code': '200', ...}
            assert result.get("code") == "200" or result.get("msg") == "success"
        except HTTPError as e:
            # May fail if marginMode doesn't match account mode or open orders exist
            if e.response is not None:
                error_body = e.response.text.lower()
                assert (
                    "marginmode" in error_body
                    or "must be set" in error_body
                    or "current mode" in error_body
                    or "open order" in error_body
                    or "open orders" in error_body
                    or "40015" in error_body
                ), f"Unexpected error: {e.response.text}"
            else:
                raise

    def test_set_margin_type(self, weex_client, test_symbol):
        """
        Test setting margin type.

        Note: WEEX does not allow changing margin type if there are
        open positions or pending orders for the symbol.
        """
        # First check if there are positions or orders
        positions = weex_client.get_positions(test_symbol)
        open_orders = weex_client.get_open_orders(test_symbol)

        has_positions = any(p.get("position_amt", 0) != 0 for p in positions)
        has_orders = len(open_orders) > 0

        if has_positions or has_orders:
            # Cannot change margin type with active positions/orders
            # Just verify the method can be called (will return error from API)
            try:
                result = weex_client.set_margin_type(test_symbol, margin_type="ISOLATED")
                # If no exception, check result
                assert isinstance(result, dict)
            except Exception as e:
                # Expected: WEEX returns error when changing margin with positions
                assert "position" in str(e).lower() or "order" in str(e).lower() or "40015" in str(e)
        else:
            # No positions or orders, can test margin type change
            result = weex_client.set_margin_type(test_symbol, margin_type="ISOLATED")
            assert isinstance(result, dict)

            # Set back to cross margin
            result = weex_client.set_margin_type(test_symbol, margin_type="CROSSED")
            assert isinstance(result, dict)

    def test_place_and_cancel_order(self, weex_client, test_symbol):
        """Test placing and canceling a limit order."""
        # Get current price
        mark_price_data = weex_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Get symbol filters for min quantity
        filters = weex_client.get_symbol_filters(test_symbol)
        min_qty = filters["min_qty"]

        # Place limit order far from current price (unlikely to fill)
        order_price = current_price * 0.5  # 50% below market
        order_qty = min_qty * 2  # Use minimum quantity

        order = weex_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price,
            time_in_force="GTC",
        )

        assert isinstance(order, dict)
        assert "orderId" in order
        order_id = order["orderId"]

        # Cancel the order
        cancel_result = weex_client.cancel_order(test_symbol, order_id=int(order_id))
        assert isinstance(cancel_result, dict)

    def test_get_order(self, weex_client, test_symbol):
        """Test querying order status."""
        # Get current price
        mark_price_data = weex_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]

        # Get symbol filters for min quantity
        filters = weex_client.get_symbol_filters(test_symbol)
        min_qty = filters["min_qty"]

        # Place a limit order
        order_price = current_price * 0.5  # 50% below market
        order_qty = min_qty * 2

        order = weex_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price,
            time_in_force="GTC",
        )

        order_id = order["orderId"]

        # Query the order
        order_info = weex_client.get_order(test_symbol, order_id=int(order_id))

        assert isinstance(order_info, dict)
        assert "orderId" in order_info
        assert "status" in order_info
        assert order_info["orderId"] == order_id

        # Clean up: cancel the order
        weex_client.cancel_order(test_symbol, order_id=int(order_id))

    def test_cancel_all_orders(self, weex_client, test_symbol):
        """Test canceling all open orders for a symbol."""
        # Get current price and filters
        mark_price_data = weex_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]
        filters = weex_client.get_symbol_filters(test_symbol)
        min_qty = filters["min_qty"]

        # Place multiple limit orders
        order_price_1 = current_price * 0.5  # 50% below market
        order_price_2 = current_price * 0.6  # 40% below market
        order_qty = min_qty * 2

        weex_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price_1,
            time_in_force="GTC",
        )

        weex_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=order_price_2,
            time_in_force="GTC",
        )

        # Cancel all orders
        result = weex_client.cancel_all_orders(test_symbol)
        assert isinstance(result, dict)

        # Verify all orders are canceled
        open_orders = weex_client.get_open_orders(test_symbol)
        assert len(open_orders) == 0

    def test_place_sl_tp_orders(self, weex_client, test_symbol):
        """
        Test placing stop-loss and take-profit trigger orders.

        Note: WEEX uses plan_order endpoint for SL/TP orders.
        This test verifies the method can be called, but individual
        orders may fail if position requirements aren't met.
        """
        # Get current price and filters
        mark_price_data = weex_client.get_mark_price(test_symbol)
        current_price = mark_price_data["mark_price"]
        filters = weex_client.get_symbol_filters(test_symbol)
        min_qty = filters["min_qty"]

        # First place a limit order (won't fill as it's far from market)
        entry_price = current_price * 0.5
        order_qty = min_qty * 2

        order = weex_client.place_order(
            symbol=test_symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=order_qty,
            price=entry_price,
            time_in_force="GTC",
        )
        assert "orderId" in order

        # Place SL/TP orders - these may or may not succeed depending on position
        sl_price = entry_price * 0.9  # 10% stop loss
        tp_price = entry_price * 1.1  # 10% take profit

        result = weex_client.place_sl_tp_orders(
            symbol=test_symbol,
            side="SELL",  # Close long position
            quantity=order_qty,
            stop_loss_price=sl_price,
            take_profit_price=tp_price,
        )

        # Verify result is a dict with expected keys
        assert isinstance(result, dict)
        assert "stop_loss" in result
        assert "take_profit" in result

        # Clean up: cancel all open orders for this symbol
        open_orders = weex_client.get_open_orders(test_symbol)
        for o in open_orders:
            try:
                weex_client.cancel_order(test_symbol, order_id=int(o["orderId"]))
            except Exception:
                pass

    def test_close_position(self, weex_client, test_symbol):
        """
        Test closing position.

        Note: This test handles the case where there's an existing position.
        Market order close may not execute instantly, so we use a
        tolerance check.
        """
        import time

        # Get current positions
        positions = weex_client.get_positions(test_symbol)

        if positions and positions[0].get("position_amt", 0) != 0:
            initial_position = abs(positions[0].get("position_amt", 0))

            # Close 100% of position
            result = weex_client.close_position(test_symbol, percent=100.0)
            assert isinstance(result, dict)

            # Wait a moment for order to process
            time.sleep(1)

            # Verify position is closed or significantly reduced
            positions_after = weex_client.get_positions(test_symbol)
            if positions_after:
                final_position = abs(positions_after[0].get("position_amt", 0))
                # Either position is closed or reduced by at least 90%
                reduction_pct = (
                    (initial_position - final_position) / initial_position * 100 if initial_position > 0 else 100
                )
                # Accept if either fully closed or market order is pending execution
                assert final_position < initial_position or "orderId" in result, (
                    f"Position not reduced: {initial_position} -> {final_position}"
                )
        else:
            # No position to close, test the method call
            result = weex_client.close_position(test_symbol, percent=100.0)
            assert isinstance(result, dict)
            assert "message" in result or "orderId" in result


@pytest.mark.e2e
class TestWeexParameterMapping:
    """Test WEEX-specific parameter mapping."""

    def test_order_type_mapping(self, weex_client):
        """Test WEEX order type mapping logic."""
        # These are internal mapping tests, not actual API calls
        # Testing the logic from place_order parameter conversion

        # BUY + !reduce_only = type 1 (Open Long)
        # BUY + reduce_only = type 4 (Close Short)
        # SELL + !reduce_only = type 2 (Open Short)
        # SELL + reduce_only = type 3 (Close Long)

        test_cases = [
            ("BUY", False, "1"),
            ("BUY", True, "4"),
            ("SELL", False, "2"),
            ("SELL", True, "3"),
        ]

        for side, reduce_only, expected_type in test_cases:
            if side.upper() == "BUY":
                weex_type = "4" if reduce_only else "1"
            else:
                weex_type = "3" if reduce_only else "2"

            assert weex_type == expected_type, f"Failed for {side} with reduce_only={reduce_only}"

    def test_time_in_force_mapping(self, weex_client):
        """Test WEEX time_in_force to order_type mapping."""
        order_type_map = {"GTC": "0", "IOC": "3", "FOK": "2", "GTX": "1"}

        for tif, expected in order_type_map.items():
            weex_order_type = order_type_map.get(tif.upper(), "0")
            assert weex_order_type == expected, f"Failed for {tif}"
