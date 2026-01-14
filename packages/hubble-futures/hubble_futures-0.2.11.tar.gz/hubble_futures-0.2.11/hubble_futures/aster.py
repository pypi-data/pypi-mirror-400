"""
Aster Futures API Client

Implementation for Aster DEX futures trading.
Uses /fapi/v1/ and /fapi/v2/ endpoints.
"""

import hashlib
import hmac
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from loguru import logger

from .base import BaseFuturesClient
from .config import ExchangeConfig


class AsterFuturesClient(BaseFuturesClient):
    """Aster Futures REST API Client"""

    DEFAULT_BASE_URL = "https://fapi.asterdex.com"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str | None = None,
        max_retries: int = 5,
        retry_delay: float = 1.0,
        timeout: float = 5.0,
        proxy_url: str | None = None
    ):
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url or self.DEFAULT_BASE_URL,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            proxy_url=proxy_url
        )

    def _setup_session_headers(self) -> None:
        """Setup Aster-specific headers."""
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-MBX-APIKEY": self.api_key
        })

    @classmethod
    def from_config(cls, config: ExchangeConfig) -> "AsterFuturesClient":
        """Create client from ExchangeConfig."""
        return cls(
            api_key=config.api_key,
            api_secret=config.api_secret,
            base_url=config.base_url or cls.DEFAULT_BASE_URL,
            proxy_url=config.proxy_url
        )

    def _generate_signature(self, params: dict) -> str:  # type: ignore[type-arg]
        """
        Generate request signature.

        Note: Aster DEX does NOT require sorted parameters.
        Uses insertion order (tested and confirmed).
        """
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    # ==================== Market Data ====================

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> list[dict]:  # type: ignore[type-arg]
        """Fetch candlestick (kline) data."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        data = self._request("GET", "/fapi/v1/klines", params=params)

        klines = []
        for k in data:
            klines.append({
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
                "quote_volume": float(k[7]),
                "trades": int(k[8]),
            })

        return klines

    def get_mark_price(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch mark price information."""
        params = {"symbol": symbol}
        data = self._request("GET", "/fapi/v1/premiumIndex", params=params)

        return {
            "symbol": data["symbol"],
            "mark_price": float(data["markPrice"]),
            "index_price": float(data["indexPrice"]),
            "funding_rate": float(data["lastFundingRate"]),
            "next_funding_time": data["nextFundingTime"],
        }

    def get_funding_rate_history(self, symbol: str, limit: int = 100) -> list[dict]:  # type: ignore[type-arg]
        """Fetch historical funding rates."""
        params = {
            "symbol": symbol,
            "limit": limit
        }
        return self._request("GET", "/fapi/v1/fundingRate", params=params)

    def get_open_interest(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch open interest statistics."""
        params = {"symbol": symbol}
        data = self._request("GET", "/fapi/v1/openInterest", params=params)

        return {
            "symbol": data["symbol"],
            "open_interest": float(data["openInterest"]),
            "timestamp": data["time"]
        }

    def get_ticker_24hr(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch 24-hour price change statistics."""
        params = {"symbol": symbol}
        return self._request("GET", "/fapi/v1/ticker/24hr", params=params)

    def get_depth(self, symbol: str, limit: int = 20) -> dict:  # type: ignore[type-arg]
        """Fetch orderbook depth."""
        params = {"symbol": symbol, "limit": limit}
        return self._request("GET", "/fapi/v1/depth", params=params)

    # ==================== Exchange Metadata ====================

    def get_exchange_info(self) -> dict:  # type: ignore[type-arg]
        """Fetch exchange information."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_symbol_filters(self, symbol: str, force_refresh: bool = False) -> dict:  # type: ignore[type-arg]
        """Fetch symbol filters (precision, min notional, etc.)."""
        if symbol in self._symbol_filters and not force_refresh:
            return self._symbol_filters[symbol]

        exchange_info = self.get_exchange_info()

        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                filters: dict = {}  # type: ignore[type-arg]

                # Contract specifications
                filters['contract_type'] = s.get('contractType', '')
                filters['contract_size'] = float(s.get('contractSize', 1.0))
                filters['contract_status'] = s.get('contractStatus', '')
                filters['underlying_type'] = s.get('underlyingType', '')

                # Precision settings
                filters['price_precision'] = int(s.get('pricePrecision', 0))
                filters['quantity_precision'] = int(s.get('quantityPrecision', 0))
                filters['base_asset_precision'] = int(s.get('baseAssetPrecision', 0))
                filters['quote_precision'] = int(s.get('quotePrecision', 0))

                # Extract filter rules
                for f in s['filters']:
                    filter_type = f['filterType']

                    if filter_type == 'PRICE_FILTER':
                        filters['tick_size'] = float(f['tickSize'])
                        filters['min_price'] = float(f['minPrice'])
                        filters['max_price'] = float(f['maxPrice'])
                    elif filter_type == 'LOT_SIZE':
                        filters['step_size'] = float(f['stepSize'])
                        filters['min_qty'] = float(f['minQty'])
                        filters['max_qty'] = float(f['maxQty'])
                    elif filter_type == 'NOTIONAL':
                        min_notional_val = (
                            f.get('minNotional') or
                            f.get('minNotionalValue') or
                            f.get('notional') or
                            f.get('notionalValue')
                        )
                        if min_notional_val:
                            filters['min_notional'] = float(min_notional_val)
                        else:
                            logger.warning(f"NOTIONAL filter found for {symbol} but no minNotional field")

                        max_notional_val = f.get('maxNotional') or f.get('maxNotionalValue')
                        if max_notional_val:
                            filters['max_notional'] = float(max_notional_val)
                    elif filter_type == 'MIN_NOTIONAL':
                        if 'min_notional' not in filters:
                            filters['min_notional'] = float(f.get('notional', f.get('notionalValue', 0)))
                    elif filter_type == 'MAX_NUM_ORDERS':
                        filters['max_num_orders'] = int(f.get('maxNumOrders', 0))
                    elif filter_type == 'MAX_NUM_ALGO_ORDERS':
                        filters['max_num_algo_orders'] = int(f.get('maxNumAlgoOrders', 0))
                    elif filter_type == 'PERCENT_PRICE':
                        filters['multiplier_up'] = float(f.get('multiplierUp', 0))
                        filters['multiplier_down'] = float(f.get('multiplierDown', 0))
                        filters['multiplier_decimal'] = float(f.get('multiplierDecimal', 0))

                self._symbol_filters[symbol] = filters
                return filters

        raise ValueError(f"Symbol {symbol} not found")

    def get_leverage_bracket(self, symbol: str | None = None, force_refresh: bool = False) -> dict:  # type: ignore[type-arg]
        """Fetch leverage bracket information."""
        cache_key = symbol or 'ALL'

        if cache_key in self._leverage_brackets and not force_refresh:
            return self._leverage_brackets[cache_key]

        params: dict = {}  # type: ignore[type-arg]
        if symbol:
            params['symbol'] = symbol

        try:
            data = self._request("GET", "/fapi/v1/leverageBracket", params=params)
            self._leverage_brackets[cache_key] = data
            return data
        except Exception as e:
            logger.debug(f"Leverage bracket endpoint not available: {e}")
            return {}

    # ==================== Account ====================

    def get_account(self) -> dict:  # type: ignore[type-arg]
        """Fetch account information."""
        data = self._request("GET", "/fapi/v2/account", signed=True)

        return {
            "total_wallet_balance": float(data["totalWalletBalance"]),
            "total_unrealized_profit": float(data["totalUnrealizedProfit"]),
            "total_margin_balance": float(data["totalMarginBalance"]),
            "total_position_initial_margin": float(data["totalPositionInitialMargin"]),
            "total_open_order_initial_margin": float(data["totalOpenOrderInitialMargin"]),
            "available_balance": float(data["availableBalance"]),
            "max_withdraw_amount": float(data["maxWithdrawAmount"]),
            "assets": data.get("assets", []),
            "positions": data.get("positions", [])
        }

    def get_positions(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Fetch current positions."""
        params: dict = {}  # type: ignore[type-arg]
        if symbol:
            params['symbol'] = symbol

        data = self._request("GET", "/fapi/v2/positionRisk", signed=True, params=params)

        positions = []
        for p in data:
            if float(p['positionAmt']) != 0:
                positions.append({
                    "symbol": p["symbol"],
                    "position_amt": float(p["positionAmt"]),
                    "entry_price": float(p["entryPrice"]),
                    "mark_price": float(p["markPrice"]),
                    "unrealized_profit": float(p["unRealizedProfit"]),
                    "liquidation_price": float(p["liquidationPrice"]),
                    "leverage": int(p["leverage"]),
                    "margin_type": p["marginType"],
                    "isolated_margin": float(p.get("isolatedMargin", 0)),
                    "position_side": p.get("positionSide", "BOTH")
                })

        return positions

    def get_balance(self) -> dict:  # type: ignore[type-arg]
        """Fetch account balance summary."""
        account = self.get_account()
        return {
            "available_balance": account["available_balance"],
            "total_margin_balance": account["total_margin_balance"],
            "total_unrealized_profit": account["total_unrealized_profit"]
        }

    # ==================== Trading ====================

    def set_leverage(self, symbol: str, leverage: int) -> dict:  # type: ignore[type-arg]
        """Configure leverage for a symbol."""
        params = {
            "symbol": symbol,
            "leverage": leverage
        }
        return self._request("POST", "/fapi/v1/leverage", signed=True, params=params)

    def set_margin_type(self, symbol: str, margin_type: str = "ISOLATED") -> dict:  # type: ignore[type-arg]
        """Configure margin mode."""
        params = {
            "symbol": symbol,
            "marginType": margin_type
        }
        return self._request("POST", "/fapi/v1/marginType", signed=True, params=params)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str = "LIMIT",
        quantity: float | None = None,
        price: float | None = None,
        stop_price: float | None = None,
        reduce_only: bool = False,
        time_in_force: str = "GTC",
        client_order_id: str | None = None,
        **kwargs: dict  # type: ignore[type-arg]
    ) -> dict:  # type: ignore[type-arg]
        """Place an order."""
        params: dict = {  # type: ignore[type-arg]
            "symbol": symbol,
            "side": side,
            "type": order_type,
        }

        filters: dict | None = None  # type: ignore[type-arg]

        if quantity is not None:
            filters = filters or self.get_symbol_filters(symbol)
            params["quantity"] = self._format_decimal(
                quantity,
                step=filters.get("step_size"),
                precision=filters.get("quantity_precision"),
                rounding=ROUND_DOWN
            )
        if price is not None:
            filters = filters or self.get_symbol_filters(symbol)
            params["price"] = self._format_decimal(
                price,
                step=filters.get("tick_size"),
                precision=filters.get("price_precision"),
                rounding=ROUND_HALF_UP
            )
        if stop_price is not None:
            filters = filters or self.get_symbol_filters(symbol)
            params["stopPrice"] = self._format_decimal(
                stop_price,
                step=filters.get("tick_size"),
                precision=filters.get("price_precision"),
                rounding=ROUND_HALF_UP
            )
        if reduce_only:
            params["reduceOnly"] = "true"
        if time_in_force and order_type == "LIMIT":
            params["timeInForce"] = time_in_force
        if client_order_id:
            params["newClientOrderId"] = client_order_id

        params.update(kwargs)

        return self._request("POST", "/fapi/v1/order", signed=True, params=params)

    def cancel_order(
        self,
        symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None
    ) -> dict:  # type: ignore[type-arg]
        """Cancel a specific order."""
        params = {"symbol": symbol}

        if order_id:
            params["orderId"] = order_id
        elif client_order_id:
            params["origClientOrderId"] = client_order_id
        else:
            raise ValueError("Must provide either order_id or client_order_id")

        return self._request("DELETE", "/fapi/v1/order", signed=True, params=params)

    def get_order(
        self,
        symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None
    ) -> dict:  # type: ignore[type-arg]
        """Query an order."""
        params = {"symbol": symbol}

        if order_id:
            params["orderId"] = order_id
        elif client_order_id:
            params["origClientOrderId"] = client_order_id
        else:
            raise ValueError("Must provide either order_id or client_order_id")

        return self._request("GET", "/fapi/v1/order", signed=True, params=params)

    def get_open_orders(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Fetch open orders."""
        params: dict = {}  # type: ignore[type-arg]
        if symbol:
            params["symbol"] = symbol

        return self._request("GET", "/fapi/v1/openOrders", signed=True, params=params)

    def cancel_all_orders(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Cancel all open orders for the symbol."""
        params = {"symbol": symbol}
        return self._request("DELETE", "/fapi/v1/allOpenOrders", signed=True, params=params)

    # ==================== Advanced Trading ====================

    def place_sl_tp_orders(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_loss_price: float | None = None,
        take_profit_price: float | None = None,
        trigger_type: str = "MARK_PRICE"
    ) -> dict:  # type: ignore[type-arg]
        """Submit stop-loss and take-profit orders."""
        filters = self.get_symbol_filters(symbol)
        tick_size = filters.get("tick_size")
        tick_decimal = Decimal(str(tick_size)) if tick_size else None

        def _align_price(price: float | None) -> float | None:
            if price is None or tick_decimal is None or tick_decimal <= 0:
                return price
            return float(Decimal(str(price)).quantize(tick_decimal, rounding=ROUND_HALF_UP))

        stop_loss_price = _align_price(stop_loss_price)
        take_profit_price = _align_price(take_profit_price)

        result: dict = {"stop_loss": None, "take_profit": None}  # type: ignore[type-arg]

        if stop_loss_price:
            sl_order = self.place_order(
                symbol=symbol,
                side=side,
                order_type="STOP_MARKET",
                quantity=quantity,
                stop_price=stop_loss_price,
                reduce_only=True,
                workingType=trigger_type
            )
            result["stop_loss"] = sl_order

        if take_profit_price:
            tp_order = self.place_order(
                symbol=symbol,
                side=side,
                order_type="TAKE_PROFIT_MARKET",
                quantity=quantity,
                stop_price=take_profit_price,
                reduce_only=True,
                workingType=trigger_type
            )
            result["take_profit"] = tp_order

        return result

    def close_position(self, symbol: str, percent: float = 100.0) -> dict:  # type: ignore[type-arg]
        """Close an existing position by percentage."""
        positions = self.get_positions(symbol)

        if not positions:
            return {"message": "No position to close"}

        position = positions[0]
        position_amt = position["position_amt"]

        close_qty = abs(position_amt) * (percent / 100.0)
        side = "SELL" if position_amt > 0 else "BUY"

        return self.place_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=close_qty,
            reduce_only=True
        )

    # ==================== Helpers ====================

    def validate_order_params(self, symbol: str, price: float, quantity: float) -> dict:  # type: ignore[type-arg]
        """Validate order parameters against exchange filters."""
        filters = self.get_symbol_filters(symbol)

        tick_size = filters['tick_size']
        adjusted_price = round(price / tick_size) * tick_size

        step_size = filters['step_size']
        adjusted_quantity = round(quantity / step_size) * step_size

        notional = adjusted_price * adjusted_quantity
        min_notional = filters.get('min_notional', 0)

        validation = {
            "valid": True,
            "adjusted_price": adjusted_price,
            "adjusted_quantity": adjusted_quantity,
            "notional": notional,
            "errors": []
        }

        if adjusted_price < filters['min_price']:
            validation["valid"] = False
            validation["errors"].append(f"Price {adjusted_price} below minimum {filters['min_price']}")

        if adjusted_quantity < filters['min_qty']:
            validation["valid"] = False
            validation["errors"].append(f"Quantity {adjusted_quantity} below minimum {filters['min_qty']}")

        if notional < min_notional:
            validation["valid"] = False
            validation["errors"].append(f"Notional {notional} below minimum {min_notional}")

        return validation

    def calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        side: str,
        maintenance_margin_rate: float = 0.005
    ) -> float:
        """Calculate approximate liquidation price."""
        if side == "LONG":
            liq_price = entry_price * (1 - (1 / leverage) + maintenance_margin_rate)
        else:
            liq_price = entry_price * (1 + (1 / leverage) - maintenance_margin_rate)

        return liq_price
