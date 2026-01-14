"""Integration tests for Aster Futures API with mocked responses."""

import time
from decimal import Decimal

import pytest
import responses


@pytest.mark.integration
class TestAsterMarketData:
    """Test Aster market data endpoints with mocked responses."""

    def test_get_klines(self, mock_responses, aster_client):
        """Test fetching kline data."""
        symbol = "BTCUSDT"
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v1/klines",
            json=[
                [1704067200000, "42000.00", "42500.00", "41800.00", "42300.00", "1000.5", 1704067259999, "42300000.00", 5000],
                [1704067260000, "42300.00", "42600.00", "42200.00", "42400.00", "950.3", 1704067319999, "40280000.00", 4500],
            ],
            status=200,
        )

        klines = aster_client.get_klines(symbol, "1h", 2)

        assert len(klines) == 2
        assert klines[0]["open_time"] == 1704067200000
        assert klines[0]["open"] == 42000.00
        assert klines[0]["high"] == 42500.00
        assert klines[0]["low"] == 41800.00
        assert klines[0]["close"] == 42300.00
        assert klines[0]["volume"] == 1000.5
        assert klines[0]["trades"] == 5000

    def test_get_mark_price(self, mock_responses, aster_client):
        """Test fetching mark price."""
        symbol = "BTCUSDT"
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v1/premiumIndex",
            json={
                "symbol": "BTCUSDT",
                "markPrice": "42350.50",
                "indexPrice": "42340.20",
                "estimatedSettlePrice": "42345.80",
                "lastFundingRate": "0.0001",
                "nextFundingTime": 1704110400000,
                "interestRate": "0.05",
                "time": 1704067200000,
            },
            status=200,
        )

        result = aster_client.get_mark_price(symbol)

        assert result["symbol"] == symbol
        assert result["mark_price"] == 42350.50
        assert result["index_price"] == 42340.20
        assert result["funding_rate"] == 0.0001
        assert result["next_funding_time"] == 1704110400000


@pytest.mark.integration
class TestAsterAccount:
    """Test Aster account endpoints with mocked responses."""

    def test_get_account(self, mock_responses, aster_client):
        """Test fetching account information."""
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v2/account",
            json={
                "totalWalletBalance": "10000.50",
                "totalUnrealizedProfit": "50.25",
                "totalMarginBalance": "10050.75",
                "totalPositionInitialMargin": "500.00",
                "totalOpenOrderInitialMargin": "100.00",
                "availableBalance": "9450.75",
                "maxWithdrawAmount": "9450.75",
                "assets": [
                    {
                        "asset": "USDT",
                        "walletBalance": "10000.50",
                        "unrealizedProfit": "50.25",
                    }
                ],
                "positions": [],
            },
            status=200,
        )

        account = aster_client.get_account()

        assert account["total_wallet_balance"] == 10000.50
        assert account["total_unrealized_profit"] == 50.25
        assert account["available_balance"] == 9450.75
        assert len(account["assets"]) == 1

    def test_get_positions(self, mock_responses, aster_client):
        """Test fetching positions."""
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v2/positionRisk",
            json=[
                {
                    "symbol": "BTCUSDT",
                    "positionAmt": "0.5",
                    "entryPrice": "42000.00",
                    "markPrice": "42350.50",
                    "unRealizedProfit": "175.25",
                    "liquidationPrice": "40000.00",
                    "leverage": 10,
                    "marginType": "isolated",
                    "isolatedMargin": "500.00",
                    "positionSide": "LONG",
                },
                {
                    "symbol": "ETHUSDT",
                    "positionAmt": "0",
                    "entryPrice": "2200.00",
                    "markPrice": "2220.00",
                    "unRealizedProfit": "0",
                    "liquidationPrice": "0",
                    "leverage": 5,
                    "marginType": "cross",
                    "isolatedMargin": "0",
                    "positionSide": "BOTH",
                },
            ],
            status=200,
        )

        positions = aster_client.get_positions()

        assert len(positions) == 1  # Only non-zero positions
        assert positions[0]["symbol"] == "BTCUSDT"
        assert positions[0]["position_amt"] == 0.5
        assert positions[0]["entry_price"] == 42000.00
        assert positions[0]["unrealized_profit"] == 175.25

    def test_get_balance(self, mock_responses, aster_client):
        """Test fetching balance summary."""
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v2/account",
            json={
                "feeTier": 1,
                "canTrade": True,
                "canDeposit": True,
                "canWithdraw": True,
                "updateTime": 0,
                "totalInitialMargin": "0.00000000",
                "totalMaintMargin": "0.00000000",
                "totalWalletBalance": "10000.50",
                "totalUnrealizedProfit": "50.25",
                "totalMarginBalance": "10050.75",
                "totalPositionInitialMargin": "500.00",
                "totalOpenOrderInitialMargin": "100.00",
                "totalCrossWalletBalance": "10000.50",
                "totalCrossUnrealizedProfit": "50.25",
                "availableBalance": "9450.75",
                "maxWithdrawAmount": "9450.75",
                "assets": [],
                "positions": [],
            },
            status=200,
        )

        balance = aster_client.get_balance()

        assert balance["available_balance"] == 9450.75
        assert balance["total_margin_balance"] == 10050.75
        assert balance["total_unrealized_profit"] == 50.25


@pytest.mark.integration
class TestAsterTrading:
    """Test Aster trading endpoints with mocked responses."""

    def test_place_order_limit(self, mock_responses, aster_client):
        """Test placing a limit order."""
        # Mock exchangeInfo for symbol filters (called by place_order)
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v1/exchangeInfo",
            json={
                "symbols": [
                    {
                        "symbol": "BTCUSDT",
                        "status": "TRADING",
                        "contractType": "PERPETUAL",
                        "contractSize": "0.001",
                        "pricePrecision": 2,
                        "quantityPrecision": 3,
                        "baseAssetPrecision": 8,
                        "quotePrecision": 8,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "tickSize": "0.01",
                                "minPrice": "0.01",
                                "maxPrice": "1000000",
                            },
                            {
                                "filterType": "LOT_SIZE",
                                "stepSize": "0.001",
                                "minQty": "0.001",
                                "maxQty": "10000",
                            },
                            {
                                "filterType": "MIN_NOTIONAL",
                                "notional": "5",
                            },
                        ],
                    }
                ]
            },
            status=200,
        )

        mock_responses.add(
            responses.POST,
            "https://fapi.asterdex.com/fapi/v1/order",
            json={
                "orderId": 123456789,
                "symbol": "BTCUSDT",
                "status": "NEW",
                "clientOrderId": "client_order_001",
                "price": "42000.00",
                "origQty": "0.01",
                "executedQty": "0",
                "type": "LIMIT",
                "side": "BUY",
                "timeInForce": "GTC",
            },
            status=200,
        )

        result = aster_client.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=Decimal("0.01"),
            price=Decimal("42000"),
        )

        assert result["orderId"] == 123456789
        assert result["symbol"] == "BTCUSDT"
        assert result["status"] == "NEW"
        assert result["price"] == "42000.00"

    def test_place_order_market(self, mock_responses, aster_client):
        """Test placing a market order."""
        # Mock exchangeInfo for symbol filters
        mock_responses.add(
            responses.GET,
            "https://fapi.asterdex.com/fapi/v1/exchangeInfo",
            json={
                "symbols": [
                    {
                        "symbol": "BTCUSDT",
                        "status": "TRADING",
                        "contractType": "PERPETUAL",
                        "contractSize": "0.001",
                        "pricePrecision": 2,
                        "quantityPrecision": 3,
                        "baseAssetPrecision": 8,
                        "quotePrecision": 8,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "tickSize": "0.01",
                                "minPrice": "0.01",
                                "maxPrice": "1000000",
                            },
                            {
                                "filterType": "LOT_SIZE",
                                "stepSize": "0.001",
                                "minQty": "0.001",
                                "maxQty": "10000",
                            },
                            {
                                "filterType": "MIN_NOTIONAL",
                                "notional": "5",
                            },
                        ],
                    }
                ]
            },
            status=200,
        )

        mock_responses.add(
            responses.POST,
            "https://fapi.asterdex.com/fapi/v1/order",
            json={
                "orderId": 123456790,
                "symbol": "BTCUSDT",
                "status": "FILLED",
                "clientOrderId": "client_order_002",
                "origQty": "0.05",
                "executedQty": "0.05",
                "type": "MARKET",
                "side": "SELL",
                "avgPrice": "42350.00",
            },
            status=200,
        )

        result = aster_client.place_order(
            symbol="BTCUSDT",
            side="SELL",
            order_type="MARKET",
            quantity=Decimal("0.05"),
        )

        assert result["orderId"] == 123456790
        assert result["status"] == "FILLED"
        assert result["executedQty"] == "0.05"

    def test_cancel_order(self, mock_responses, aster_client):
        """Test canceling an order."""
        mock_responses.add(
            responses.DELETE,
            "https://fapi.asterdex.com/fapi/v1/order",
            json={
                "orderId": 123456789,
                "symbol": "BTCUSDT",
                "status": "CANCELED",
                "origQty": "0.01",
                "executedQty": "0",
            },
            status=200,
        )

        result = aster_client.cancel_order(symbol="BTCUSDT", order_id=123456789)

        assert result["status"] == "CANCELED"
        assert result["orderId"] == 123456789

    def test_set_leverage(self, mock_responses, aster_client):
        """Test setting leverage."""
        mock_responses.add(
            responses.POST,
            "https://fapi.asterdex.com/fapi/v1/leverage",
            json={
                "symbol": "BTCUSDT",
                "leverage": 20,
                "maxNotionalValue": "1000000",
            },
            status=200,
        )

        result = aster_client.set_leverage(symbol="BTCUSDT", leverage=20)

        assert result["leverage"] == 20
        assert result["symbol"] == "BTCUSDT"
