"""
WEEX Futures API Client

Implementation for WEEX futures trading.
Uses /capi/v2/ endpoints.

API Documentation: https://www.weex.com/api-doc/contract/
"""

import base64
import hashlib
import hmac
import json
import random
import time
from decimal import ROUND_DOWN, ROUND_HALF_UP
from uuid import uuid4

import requests
from loguru import logger

from .base import BaseFuturesClient
from .config import ExchangeConfig

# Optional function logging
try:
    from .function_log import finish_function_call, record_function_call
    _FUNCTION_LOG_AVAILABLE = True
except ImportError:
    _FUNCTION_LOG_AVAILABLE = False


class WeexFuturesClient(BaseFuturesClient):
    """WEEX Futures REST API Client"""

    DEFAULT_BASE_URL = "https://api-contract.weex.com"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        base_url: str | None = None,
        max_retries: int = 6,
        retry_delay: float = 1.5,
        timeout: float = 15.0,
        proxy_url: str | None = None,
    ):
        """
        Initialize WEEX Futures client.


        Args:
            api_key: API key
            api_secret: API secret
            passphrase: API passphrase (required for WEEX)
            base_url: API base URL
            max_retries: Max retry attempts
            retry_delay: Base delay for backoff
            timeout: Request timeout
            proxy_url: Optional proxy server URL for all requests
        """
        if not passphrase:
            raise ValueError("passphrase is required for WEEX")

        self.passphrase = passphrase

        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url or self.DEFAULT_BASE_URL,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            proxy_url=proxy_url,
        )

    def _setup_session_headers(self) -> None:
        """Setup WEEX-specific headers."""
        self.session.headers.update({"Content-Type": "application/json", "locale": "en-US"})

    def _get_server_time_endpoint(self) -> str:
        """WEEX server time endpoint."""
        return "/capi/v2/common/time"

    def _parse_server_time(self, response_data: dict) -> int:  # type: ignore[type-arg]
        """Parse WEEX server time response."""
        # WEEX returns {"code": "00000", "data": {"timestamp": 1234567890000}}
        if isinstance(response_data, dict) and "data" in response_data:
            return response_data["data"].get("timestamp", int(time.time() * 1000))
        return int(time.time() * 1000)

    @classmethod
    def from_config(cls, config: ExchangeConfig) -> "WeexFuturesClient":
        """Create client from ExchangeConfig."""
        return cls(
            api_key=config.api_key,
            api_secret=config.api_secret,
            passphrase=config.passphrase,
            base_url=config.base_url or cls.DEFAULT_BASE_URL,
            proxy_url=config.proxy_url,
        )

    # ==================== Symbol Conversion ====================

    def _to_weex_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol to WEEX format.
        BTCUSDT -> cmt_btcusdt
        """
        if symbol.startswith("cmt_"):
            return symbol
        return f"cmt_{symbol.lower()}"

    def _from_weex_symbol(self, weex_symbol: str) -> str:
        """
        Convert WEEX symbol to standard format.
        cmt_btcusdt -> BTCUSDT
        """
        if weex_symbol.startswith("cmt_"):
            return weex_symbol[4:].upper()
        return weex_symbol.upper()

    # ==================== Authentication ====================

    def _generate_signature(self, params: dict) -> str:  # type: ignore[type-arg]
        """
        Generate request signature for WEEX.

        WEEX signature: HMAC-SHA256(timestamp + method + path + body) -> Base64

        Note: This is called by _request but WEEX uses a different signing approach,
        so we override _request entirely.
        """
        # This method is not used directly for WEEX
        # Signature is generated in _request method
        return ""

    def _generate_weex_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """
        Generate WEEX-specific signature.

        Sign string: timestamp + method + path + body
        Algorithm: HMAC-SHA256 -> Base64
        """
        sign_string = f"{timestamp}{method.upper()}{path}{body}"
        signature = hmac.new(self.api_secret.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(signature).decode("utf-8")

    def _request(
        self,
        method: str,
        endpoint: str,
        signed: bool = False,
        params: dict | None = None,  # type: ignore[type-arg]
        data: dict | None = None,  # type: ignore[type-arg]
        **kwargs: dict,  # type: ignore[type-arg]
    ) -> dict:  # type: ignore[type-arg]
        """
        WEEX-specific request method.

        WEEX uses:
        - Headers for authentication (ACCESS-KEY, ACCESS-SIGN, etc.)
        - JSON body for POST requests
        - Query params for GET requests
        """
        url = f"{self.base_url}{endpoint}"

        # Record function call start (if logging is available)
        if _FUNCTION_LOG_AVAILABLE:
            function_name = f"{method.lower()}_{endpoint.replace('/', '_')}"
            record_params = {"endpoint": endpoint, "method": method}
            if params:
                record_params.update(params)
            if data:
                record_params["data"] = data
            record_function_call(function_name, record_params)

        # Build query string for GET requests
        query_string = ""
        if params and method.upper() == "GET":
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        # Build request body for POST requests
        body = ""
        if data:
            body = json.dumps(data)

        headers = dict(self.session.headers)

        if signed:
            timestamp = str(int(time.time() * 1000))
            sign_path = endpoint + query_string
            signature = self._generate_weex_signature(timestamp, method, sign_path, body)

            headers.update(
                {
                    "ACCESS-KEY": self.api_key,
                    "ACCESS-SIGN": signature,
                    "ACCESS-TIMESTAMP": timestamp,
                    "ACCESS-PASSPHRASE": self.passphrase,
                }
            )

        # Build proxies dict for explicit passing
        proxies = None
        if self.proxy_url:
            proxies = {"http": self.proxy_url, "https": self.proxy_url}

        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, params=params, headers=headers, timeout=self.timeout, proxies=proxies
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url, data=body if body else None, headers=headers, timeout=self.timeout, proxies=proxies
                    )
                elif method.upper() == "DELETE":
                    response = self.session.delete(
                        url, params=params, headers=headers, timeout=self.timeout, proxies=proxies
                    )
                else:
                    if _FUNCTION_LOG_AVAILABLE:
                        finish_function_call(function_name, error=f"Unsupported HTTP method: {method}")
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                result = response.json()

                # WEEX returns {code, msg, data} structure for some endpoints
                if isinstance(result, dict) and "code" in result:
                    if result.get("code") not in ["200", "00000", 200]:
                        error_msg = f"WEEX API error: {result.get('msg', 'Unknown error')}"
                        if _FUNCTION_LOG_AVAILABLE:
                            finish_function_call(function_name, error=error_msg)
                        raise Exception(error_msg)
                    if _FUNCTION_LOG_AVAILABLE:
                        finish_function_call(function_name, {"status": "succeeded", "data": result.get("data", result)})
                    return result.get("data", result)

                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, {"status": "succeeded", "data": result})
                return result

            except requests.exceptions.HTTPError as e:
                resp = e.response

                if resp.status_code == 429:
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2**attempt)
                        jitter = delay * 0.2 * (2 * random.random() - 1)
                        delay = delay + jitter
                        logger.warning(
                            f"Rate limit hit (429). Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {self.max_retries} retries")
                        if _FUNCTION_LOG_AVAILABLE:
                            finish_function_call(function_name, error="Rate limit exceeded")
                        raise

                logger.error(f"WEEX API request failed: {e}")
                logger.error(f"Response: {resp.text}")
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, error=str(e))
                raise

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                err_type = "timeout" if isinstance(e, requests.exceptions.Timeout) else "connection error"
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2**attempt)
                    jitter = delay * 0.2 * (2 * random.random() - 1)
                    delay = delay + jitter
                    logger.warning(
                        f"{err_type.capitalize()}: {method} {endpoint}. Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s"
                    )
                    time.sleep(delay)
                    continue
                if isinstance(e, requests.exceptions.Timeout):
                    if _FUNCTION_LOG_AVAILABLE:
                        finish_function_call(function_name, error=f"Timeout after {self.timeout}s")
                    raise Exception(f"API request timeout after {self.timeout}s") from e
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, error=f"Connection error: {e}")
                raise Exception(f"API connection failed: {e}") from e

            except Exception as e:
                logger.error(f"Request exception: {method} {endpoint} - {e}")
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, error=str(e))
                raise

        if _FUNCTION_LOG_AVAILABLE:
            finish_function_call(function_name, error="Exhausted all retry attempts")
        raise Exception(f"Exhausted all retry attempts for {method} {endpoint}")

    # ==================== Market Data ====================

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> list[dict]:  # type: ignore[type-arg]
        """
        Fetch candlestick data.

        Converts WEEX response to Aster-compatible format.
        """
        weex_symbol = self._to_weex_symbol(symbol)

        # WEEX uses 'granularity' instead of 'interval'
        params = {
            "symbol": weex_symbol,
            "granularity": interval,
            "limit": min(limit, 1000),  # WEEX max is 1000
        }

        data = self._request("GET", "/capi/v2/market/candles", params=params)

        # WEEX returns: [[timestamp, open, high, low, close, base_vol, quote_vol], ...]
        klines = []
        for k in data:
            klines.append(
                {
                    "open_time": int(k[0]),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": int(k[0]),  # WEEX doesn't have close_time, use open_time
                    "quote_volume": float(k[6]) if len(k) > 6 else 0,
                    "trades": 0,  # WEEX doesn't provide trade count
                }
            )

        return klines

    def get_mark_price(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """
        Fetch mark price information.

        WEEX: Mark price is in ticker, funding rate needs separate call.
        """
        weex_symbol = self._to_weex_symbol(symbol)

        # Get ticker for mark price and index price
        ticker = self._request("GET", "/capi/v2/market/ticker", params={"symbol": weex_symbol})

        # Get current funding rate
        try:
            funding = self._request("GET", "/capi/v2/market/currentFundRate", params={"symbol": weex_symbol})
            funding_rate = float(funding.get("fundingRate", 0))
            next_funding_time = funding.get("timestamp", 0)
        except Exception:
            funding_rate = 0
            next_funding_time = 0

        return {
            "symbol": symbol,
            "mark_price": float(ticker.get("markPrice", 0)),
            "index_price": float(ticker.get("indexPrice", 0)),
            "funding_rate": funding_rate,
            "next_funding_time": next_funding_time,
        }

    def get_funding_rate_history(self, symbol: str, limit: int = 100) -> list[dict]:  # type: ignore[type-arg]
        """Fetch historical funding rates."""
        weex_symbol = self._to_weex_symbol(symbol)

        params = {
            "symbol": weex_symbol,
            "limit": min(limit, 100),  # WEEX max is 100
        }

        data = self._request("GET", "/capi/v2/market/getHistoryFundRate", params=params)

        # Convert to standardized format
        result = []
        for item in data:
            result.append(
                {
                    "symbol": symbol,
                    "funding_rate": float(item.get("fundingRate", 0)),
                    "funding_time": int(item.get("fundingTime", 0)),
                }
            )

        return result

    def get_open_interest(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """
        Fetch open interest statistics.

        Note: WEEX does not have a dedicated open interest endpoint.
        This method attempts to extract open interest from ticker data.
        """
        weex_symbol = self._to_weex_symbol(symbol)

        # Try to get from ticker endpoint (WEEX may include open interest here)
        try:
            data = self._request("GET", "/capi/v2/market/ticker", params={"symbol": weex_symbol})
            open_interest = float(data.get("openInterest", 0))
            if open_interest == 0:
                logger.debug(f"WEEX ticker for {symbol} has no openInterest field, using default 0")
        except Exception as e:
            logger.warning(f"Failed to fetch open interest for {symbol}: {e}, returning 0")
            open_interest = 0.0

        return {"symbol": symbol, "open_interest": open_interest, "timestamp": int(time.time() * 1000)}

    def get_ticker_24hr(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch 24-hour price change statistics."""
        weex_symbol = self._to_weex_symbol(symbol)

        data = self._request("GET", "/capi/v2/market/ticker", params={"symbol": weex_symbol})

        return {
            "symbol": symbol,
            "lastPrice": data.get("last"),
            "priceChange": data.get("priceChangePercent"),
            "highPrice": data.get("high_24h"),
            "lowPrice": data.get("low_24h"),
            "volume": data.get("base_volume"),
            "quoteVolume": data.get("volume_24h"),
            "markPrice": data.get("markPrice"),
            "indexPrice": data.get("indexPrice"),
        }

    def get_depth(self, symbol: str, limit: int = 20) -> dict:  # type: ignore[type-arg]
        """Fetch orderbook depth."""
        weex_symbol = self._to_weex_symbol(symbol)

        # WEEX only supports limit 15 or 200
        weex_limit = 200 if limit > 15 else 15

        data = self._request("GET", "/capi/v2/market/depth", params={"symbol": weex_symbol, "limit": weex_limit})

        return {"bids": data.get("bids", []), "asks": data.get("asks", []), "timestamp": data.get("timestamp")}

    # ==================== Exchange Metadata ====================

    def get_exchange_info(self) -> dict:  # type: ignore[type-arg]
        """Fetch exchange information."""
        data = self._request("GET", "/capi/v2/market/contracts")
        return {"symbols": data}

    def get_symbol_filters(self, symbol: str, force_refresh: bool = False) -> dict:  # type: ignore[type-arg]
        """Fetch symbol filters."""
        if symbol in self._symbol_filters and not force_refresh:
            return self._symbol_filters[symbol]

        weex_symbol = self._to_weex_symbol(symbol)
        contracts = self._request("GET", "/capi/v2/market/contracts", params={"symbol": weex_symbol})

        if not contracts:
            raise ValueError(f"Symbol {symbol} not found")

        contract = contracts[0] if isinstance(contracts, list) else contracts

        # Convert WEEX format to Aster-compatible format
        filters = {
            "contract_type": "PERPETUAL",
            "contract_size": float(contract.get("contract_val", 1)),
            "contract_status": "TRADING",
            # Precision: WEEX uses tick_size and size_increment differently
            "price_precision": int(contract.get("tick_size", 1)),
            "quantity_precision": int(contract.get("size_increment", 5)),
            # Calculate tick_size and step_size from precision
            "tick_size": 10 ** (-int(contract.get("tick_size", 1))),
            "step_size": 10 ** (-int(contract.get("size_increment", 5))),
            "min_qty": float(contract.get("minOrderSize", 0.0001)),
            "max_qty": float(contract.get("maxOrderSize", 100000)),
            "min_price": 0,
            "max_price": float("inf"),
            # WEEX doesn't have min_notional in contract info
            "min_notional": 1,  # Default minimum
            "min_leverage": int(contract.get("minLeverage", 1)),
            "max_leverage": int(contract.get("maxLeverage", 125)),
        }

        self._symbol_filters[symbol] = filters
        return filters

    def get_leverage_bracket(self, symbol: str | None = None, force_refresh: bool = False) -> list[dict]:  # type: ignore[type-arg]
        """Fetch leverage bracket information."""
        # WEEX includes leverage info in contracts endpoint
        if symbol:
            filters = self.get_symbol_filters(symbol, force_refresh)
            return [
                {
                    "symbol": symbol,
                    "brackets": [
                        {
                            "bracket": 1,
                            "initialLeverage": filters.get("max_leverage", 125),
                            "notionalCap": float("inf"),
                            "notionalFloor": 0,
                            "maintMarginRatio": 0.005,
                        }
                    ],
                }
            ]
        return []

    # ==================== Account ====================

    def get_account(self) -> dict:  # type: ignore[type-arg]
        """Fetch account information."""
        data = self._request("GET", "/capi/v2/account/assets", signed=True)

        # WEEX returns array of assets, find USDT
        usdt_asset = None
        for asset in data:
            if asset.get("coinName") == "USDT":
                usdt_asset = asset
                break

        if not usdt_asset:
            usdt_asset = data[0] if data else {}

        available = float(usdt_asset.get("available", 0))
        equity = float(usdt_asset.get("equity", 0))
        frozen = float(usdt_asset.get("frozen", 0))
        unrealized_pnl = float(usdt_asset.get("unrealizePnl", 0))

        # Calculate wallet balance (equity - unrealized PnL)
        wallet_balance = equity - unrealized_pnl

        return {
            "total_wallet_balance": wallet_balance,
            "total_unrealized_profit": unrealized_pnl,
            "total_margin_balance": equity,
            "total_position_initial_margin": frozen,
            "total_open_order_initial_margin": 0,
            "available_balance": available,
            "max_withdraw_amount": available,
            "assets": data,
            "positions": [],  # Positions need separate call
        }

    def get_positions(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Fetch current positions."""
        data = self._request("GET", "/capi/v2/account/position/allPosition", signed=True)

        positions = []
        for p in data:
            # Skip empty positions
            size = float(p.get("size", 0))
            if size == 0:
                continue

            pos_symbol = self._from_weex_symbol(p.get("symbol", ""))

            # Filter by symbol if provided
            if symbol and pos_symbol != symbol:
                continue

            # Convert side to position_amt (positive for LONG, negative for SHORT)
            side = p.get("side", "").upper()
            position_amt = size if side == "LONG" else -size

            # Calculate entry price from open_value / size
            open_value = float(p.get("open_value", 0))
            entry_price = open_value / size if size > 0 else 0

            # Get mark price from separate call if needed
            # For now, estimate from unrealized PnL
            unrealized_pnl = float(p.get("unrealizePnl", 0))

            positions.append(
                {
                    "symbol": pos_symbol,
                    "position_amt": position_amt,
                    "entry_price": entry_price,
                    "mark_price": 0,  # Would need separate ticker call
                    "unrealized_profit": unrealized_pnl,
                    "liquidation_price": float(p.get("liquidatePrice", 0)),
                    "leverage": int(float(p.get("leverage", 1))),
                    "margin_type": "cross" if p.get("margin_mode") == "SHARED" else "isolated",
                    "isolated_margin": float(p.get("marginSize", 0)),
                    "position_side": side,
                }
            )

        return positions

    def get_balance(self) -> dict:  # type: ignore[type-arg]
        """Fetch account balance summary."""
        account = self.get_account()
        return {
            "available_balance": account["available_balance"],
            "total_margin_balance": account["total_margin_balance"],
            "total_unrealized_profit": account["total_unrealized_profit"],
        }

    # ==================== Trading ====================

    def set_leverage(self, symbol: str, leverage: int) -> dict:  # type: ignore[type-arg]
        """Configure leverage for a symbol."""
        weex_symbol = self._to_weex_symbol(symbol)

        # WEEX requires marginMode and separate long/short leverage
        data = {
            "symbol": weex_symbol,
            "marginMode": 1,  # 1=Cross, 3=Isolated
            "longLeverage": str(leverage),
            "shortLeverage": str(leverage),
        }

        return self._request("POST", "/capi/v2/account/leverage", signed=True, data=data)

    def set_margin_type(self, symbol: str, margin_type: str = "ISOLATED") -> dict:  # type: ignore[type-arg]
        """Configure margin mode."""
        weex_symbol = self._to_weex_symbol(symbol)

        # Convert Aster margin type to WEEX
        weex_margin_mode = 3 if margin_type.upper() == "ISOLATED" else 1

        data = {"symbol": weex_symbol, "marginMode": weex_margin_mode}

        return self._request("POST", "/capi/v2/account/position/changeHoldModel", signed=True, data=data)

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
        **kwargs: dict,  # type: ignore[type-arg]
    ) -> dict:  # type: ignore[type-arg]
        """
        Place an order.

        Converts Aster-style parameters to WEEX format:
        - side (BUY/SELL) + reduce_only -> type (1/2/3/4)
        - order_type (LIMIT/MARKET) -> match_price (0/1)

        Args:
            margin_mode (str, optional): Margin mode - "cross" or "isolated".
                Defaults to "cross". WEEX requires this to match account's
                current margin mode setting.
        """
        weex_symbol = self._to_weex_symbol(symbol)

        # Convert side + reduce_only to WEEX type
        # 1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short
        if side.upper() == "BUY":
            weex_type = "4" if reduce_only else "1"  # Close Short or Open Long
        else:  # SELL
            weex_type = "3" if reduce_only else "2"  # Close Long or Open Short

        # Convert order type to match_price
        # 0=Limit, 1=Market
        match_price = "1" if order_type.upper() == "MARKET" else "0"

        # Convert time_in_force to order_type
        # 0=Normal(GTC), 1=PostOnly, 2=FOK, 3=IOC
        order_type_map = {
            "GTC": "0",
            "IOC": "3",
            "FOK": "2",
            "GTX": "1",  # PostOnly
        }
        weex_order_type = order_type_map.get(time_in_force.upper(), "0")

        # Determine marginMode from kwargs or default to Cross (1)
        # WEEX: 1=Cross, 3=Isolated
        margin_mode = kwargs.get("margin_mode", "cross")
        if isinstance(margin_mode, str):
            weex_margin_mode = "3" if margin_mode.lower() == "isolated" else "1"
        else:
            weex_margin_mode = str(margin_mode) if margin_mode in [1, 3] else "1"

        # Build order data
        data: dict = {  # type: ignore[type-arg]
            "symbol": weex_symbol,
            "type": weex_type,
            "match_price": match_price,
            "order_type": weex_order_type,
            "marginMode": weex_margin_mode,
            "client_oid": client_order_id or str(int(time.time() * 1000)),
        }

        # Add quantity
        if quantity is not None:
            filters = self.get_symbol_filters(symbol)
            data["size"] = self._format_decimal(
                quantity,
                step=filters.get("step_size"),
                precision=filters.get("quantity_precision"),
                rounding=ROUND_DOWN,
            )

        # Add price for limit orders
        if price is not None and match_price == "0":
            filters = self.get_symbol_filters(symbol)
            data["price"] = self._format_decimal(
                price, step=filters.get("tick_size"), precision=filters.get("price_precision"), rounding=ROUND_HALF_UP
            )

        # Add stop loss/take profit if provided in kwargs
        if kwargs.get("presetStopLossPrice") or kwargs.get("presetTakeProfitPrice"):
            # Ensure we have filters for price formatting
            if "filters" not in dir() or filters is None:
                filters = self.get_symbol_filters(symbol)
            if kwargs.get("presetStopLossPrice"):
                data["presetStopLossPrice"] = self._format_decimal(
                    kwargs["presetStopLossPrice"],
                    step=filters.get("tick_size"),
                    precision=filters.get("price_precision"),
                    rounding=ROUND_HALF_UP,
                )
            if kwargs.get("presetTakeProfitPrice"):
                data["presetTakeProfitPrice"] = self._format_decimal(
                    kwargs["presetTakeProfitPrice"],
                    step=filters.get("tick_size"),
                    precision=filters.get("price_precision"),
                    rounding=ROUND_HALF_UP,
                )

        result = self._request("POST", "/capi/v2/order/placeOrder", signed=True, data=data)

        # Convert response to Aster-compatible format
        return {
            "orderId": result.get("order_id"),
            "symbol": symbol,
            "status": "NEW",
            "clientOrderId": result.get("client_oid"),
            "price": price,
            "origQty": quantity,
            "executedQty": 0,
            "type": order_type,
            "side": side,
        }

    def cancel_order(self, symbol: str, order_id: int | None = None, client_order_id: str | None = None) -> dict:  # type: ignore[type-arg]
        """Cancel a specific order."""
        data: dict = {}  # type: ignore[type-arg]

        if order_id:
            data["orderId"] = str(order_id)
        elif client_order_id:
            data["clientOid"] = client_order_id
        else:
            raise ValueError("Must provide either order_id or client_order_id")

        result = self._request("POST", "/capi/v2/order/cancel_order", signed=True, data=data)

        return {
            "orderId": result.get("order_id"),
            "symbol": symbol,
            "status": "CANCELED" if result.get("result") else "FAILED",
            "clientOrderId": result.get("client_oid"),
        }

    def get_order(self, symbol: str, order_id: int | None = None, client_order_id: str | None = None) -> dict:  # type: ignore[type-arg]
        """Query an order."""
        if not order_id:
            raise ValueError("order_id is required for WEEX")

        params = {"orderId": str(order_id)}

        data = self._request("GET", "/capi/v2/order/detail", signed=True, params=params)

        # Convert WEEX status to Aster status
        status_map = {"open": "NEW", "filled": "FILLED", "partial_filled": "PARTIALLY_FILLED", "canceled": "CANCELED"}

        return {
            "orderId": data.get("order_id"),
            "symbol": self._from_weex_symbol(data.get("symbol", "")),
            "status": status_map.get(data.get("status", ""), data.get("status")),
            "clientOrderId": data.get("client_oid"),
            "price": data.get("price"),
            "origQty": data.get("size"),
            "executedQty": data.get("filled_qty"),
            "type": "MARKET" if data.get("order_type") == "ioc" else "LIMIT",
            "side": "BUY" if "long" in data.get("type", "") else "SELL",
        }

    def get_open_orders(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Fetch open orders."""
        params: dict = {}  # type: ignore[type-arg]
        if symbol:
            params["symbol"] = self._to_weex_symbol(symbol)

        data = self._request("GET", "/capi/v2/order/current", signed=True, params=params)

        orders = []
        for order in data:
            weex_type = order.get("type", "")

            # Determine side from WEEX type
            if "long" in weex_type:
                side = "BUY" if "open" in weex_type else "SELL"
            else:
                side = "SELL" if "open" in weex_type else "BUY"

            orders.append(
                {
                    "orderId": order.get("order_id"),
                    "symbol": self._from_weex_symbol(order.get("symbol", "")),
                    "status": "NEW" if order.get("status") == "open" else order.get("status"),
                    "clientOrderId": order.get("client_oid"),
                    "price": order.get("price"),
                    "origQty": order.get("size"),
                    "executedQty": order.get("filled_qty"),
                    "type": "LIMIT",  # Simplified
                    "side": side,
                    "time": order.get("createTime"),
                }
            )

        return orders

    def cancel_all_orders(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """
        Cancel all open orders for the symbol.

        WEEX doesn't have a direct "cancel all by symbol" endpoint,
        so we query open orders first, then cancel individually.
        Batch cancel may not work reliably on WEEX.
        """
        # Get all open orders for this symbol
        open_orders = self.get_open_orders(symbol)

        if not open_orders:
            return {"message": "No orders to cancel"}

        # Cancel orders individually (more reliable than batch)
        successful = []
        failed = []

        for order in open_orders:
            order_id = order.get("orderId")
            if not order_id:
                continue

            try:
                result = self.cancel_order(symbol, order_id=int(order_id))
                successful.append(order_id)
            except Exception as e:
                logger.warning(f"Failed to cancel order {order_id}: {e}")
                failed.append({"orderId": order_id, "error": str(e)})

        return {
            "success": True,
            "cancelled": successful,
            "failed": failed,
            "message": f"Cancelled {len(successful)} orders, {len(failed)} failed",
        }

    def get_plan_orders(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """
        Fetch current plan orders (trigger orders like SL/TP).
        
        Args:
            symbol: Trading pair (optional, if None returns all).
            
        Returns:
            List of plan orders.
        """
        params: dict = {}  # type: ignore[type-arg]
        if symbol:
            params["symbol"] = self._to_weex_symbol(symbol)
        
        try:
            data = self._request("GET", "/capi/v2/order/currentPlan", signed=True, params=params)
        except Exception as e:
            logger.warning(f"Failed to get plan orders: {e}")
            return []
        
        if not data:
            return []
        
        orders = []
        for order in data:
            orders.append({
                "orderId": order.get("order_id"),
                "symbol": self._from_weex_symbol(order.get("symbol", "")),
                "status": order.get("status"),
                "triggerPrice": order.get("trigger_price"),
                "executePrice": order.get("execute_price"),
                "size": order.get("size"),
                "type": order.get("type"),
                "clientOrderId": order.get("client_oid"),
                "createTime": order.get("createTime"),
            })
        
        return orders

    def cancel_plan_order(self, symbol: str, order_id: str | int) -> dict:  # type: ignore[type-arg]
        """
        Cancel a specific plan order (trigger order).
        
        Args:
            symbol: Trading pair.
            order_id: Plan order ID.
            
        Returns:
            Cancellation result.
        """
        data = {"orderId": str(order_id)}
        
        result = self._request("POST", "/capi/v2/order/cancel_plan", signed=True, data=data)
        
        return {
            "orderId": str(order_id),
            "symbol": symbol,
            "status": "CANCELED" if result.get("result") else "FAILED",
        }

    def cancel_all_plan_orders(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """
        Cancel all plan orders (trigger orders like SL/TP) for the symbol.
        
        WEEX stores SL/TP as trigger orders in /capi/v2/order/plan_order.
        These must be cancelled separately from normal orders before
        adjusting leverage.
        
        Args:
            symbol: Trading pair.
            
        Returns:
            Cancellation result with success/failed counts.
        """
        # Get all plan orders for this symbol
        plan_orders = self.get_plan_orders(symbol)
        
        if not plan_orders:
            logger.debug(f"No plan orders to cancel for {symbol}")
            return {"message": "No plan orders to cancel", "cancelled": [], "failed": []}
        
        logger.info(f"Found {len(plan_orders)} plan orders to cancel for {symbol}")
        
        # Cancel orders individually
        successful = []
        failed = []
        
        for order in plan_orders:
            order_id = order.get("orderId")
            if not order_id:
                continue
            
            try:
                result = self.cancel_plan_order(symbol, order_id)
                successful.append(order_id)
                logger.debug(f"Cancelled plan order {order_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel plan order {order_id}: {e}")
                failed.append({"orderId": order_id, "error": str(e)})
        
        logger.info(f"Cancelled {len(successful)} plan orders, {len(failed)} failed for {symbol}")
        
        return {
            "success": True,
            "cancelled": successful,
            "failed": failed,
            "message": f"Cancelled {len(successful)} plan orders, {len(failed)} failed",
        }

    # ==================== Advanced Trading ====================


    def place_sl_tp_orders(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_loss_price: float | None = None,
        take_profit_price: float | None = None,
        trigger_type: str = "MARK_PRICE",
    ) -> dict:  # type: ignore[type-arg]
        """
        Submit stop-loss and take-profit orders.

        WEEX supports preset SL/TP in the order itself,
        but for existing positions, we use trigger orders.

        Note: marginMode is dynamically inferred from current position to match
        the account's actual margin mode setting.
        """
        result: dict = {"stop_loss": None, "take_profit": None}  # type: ignore[type-arg]
        weex_symbol = self._to_weex_symbol(symbol)

        # Get symbol filters for price precision formatting
        filters = self.get_symbol_filters(symbol)
        tick_size = filters.get("tick_size")
        price_precision = filters.get("price_precision")

        # Dynamically determine marginMode from current position
        # WEEX API requires marginMode to match account's current setting
        # 1 = Cross (全仓), 3 = Isolated (逐仓)
        weex_margin_mode = "1"  # Default to Cross
        try:
            positions = self.get_positions(symbol)
            if positions:
                margin_type = positions[0].get("margin_type", "cross")
                weex_margin_mode = "3" if margin_type == "isolated" else "1"
                logger.debug(f"Inferred marginMode from position: {margin_type} -> {weex_margin_mode}")
        except Exception as e:
            logger.warning(f"Could not get position for marginMode inference, using default Cross: {e}")

        # Determine close type based on side
        # If side is SELL (closing long), use type 3
        # If side is BUY (closing short), use type 4
        close_type = "3" if side.upper() == "SELL" else "4"

        if stop_loss_price:
            # WEEX uses plan_order endpoint for trigger orders
            sl_data = {
                "symbol": weex_symbol,
                "type": close_type,
                "trigger_price": self._format_decimal(
                    stop_loss_price, step=tick_size, precision=price_precision, rounding=ROUND_HALF_UP
                ),
                "execute_price": "0",  # Market price (match_type=1)
                "size": str(quantity),
                "match_type": "1",  # 1=Market price execution
                "marginMode": weex_margin_mode,
                "client_oid": f"sl-{uuid4().hex}",
            }
            try:
                result["stop_loss"] = self._request("POST", "/capi/v2/order/plan_order", signed=True, data=sl_data)
            except Exception as e:
                logger.error(f"Failed to place SL order: {e}")

        if take_profit_price:
            # WEEX uses plan_order endpoint for trigger orders
            tp_data = {
                "symbol": weex_symbol,
                "type": close_type,
                "trigger_price": self._format_decimal(
                    take_profit_price, step=tick_size, precision=price_precision, rounding=ROUND_HALF_UP
                ),
                "execute_price": "0",  # Market price (match_type=1)
                "size": str(quantity),
                "match_type": "1",  # 1=Market price execution
                "marginMode": weex_margin_mode,
                "client_oid": f"tp-{uuid4().hex}",
            }
            try:
                result["take_profit"] = self._request("POST", "/capi/v2/order/plan_order", signed=True, data=tp_data)
            except Exception as e:
                logger.error(f"Failed to place TP order: {e}")

        return result

    def close_position(self, symbol: str, percent: float = 100.0) -> dict:  # type: ignore[type-arg]
        """Close an existing position by percentage."""
        positions = self.get_positions(symbol)

        if not positions:
            return {"message": "No position to close"}

        position = positions[0]
        position_amt = position["position_amt"]

        if position_amt == 0:
            return {"message": "No position to close"}

        # Calculate close quantity
        close_qty = abs(position_amt) * (percent / 100.0)

        # Determine close direction
        # If position_amt > 0 (LONG), close with type 3 (close long)
        # If position_amt < 0 (SHORT), close with type 4 (close short)
        side = "SELL" if position_amt > 0 else "BUY"

        return self.place_order(symbol=symbol, side=side, order_type="MARKET", quantity=close_qty, reduce_only=True)

    # ==================== Helpers ====================

    def validate_order_params(self, symbol: str, price: float, quantity: float) -> dict:  # type: ignore[type-arg]
        """Validate order parameters against exchange filters."""
        filters = self.get_symbol_filters(symbol)

        tick_size = filters.get("tick_size", 0.1)
        adjusted_price = round(price / tick_size) * tick_size

        step_size = filters.get("step_size", 0.00001)
        adjusted_quantity = round(quantity / step_size) * step_size

        notional = adjusted_price * adjusted_quantity
        min_notional = filters.get("min_notional", 1)

        validation = {
            "valid": True,
            "adjusted_price": adjusted_price,
            "adjusted_quantity": adjusted_quantity,
            "notional": notional,
            "errors": [],
        }

        if adjusted_quantity < filters.get("min_qty", 0):
            validation["valid"] = False
            validation["errors"].append(f"Quantity {adjusted_quantity} below minimum {filters['min_qty']}")

        if notional < min_notional:
            validation["valid"] = False
            validation["errors"].append(f"Notional {notional} below minimum {min_notional}")

        return validation

    def calculate_liquidation_price(
        self, entry_price: float, leverage: int, side: str, maintenance_margin_rate: float = 0.005
    ) -> float:
        """Calculate approximate liquidation price."""
        if side.upper() in ["LONG", "BUY"]:
            liq_price = entry_price * (1 - (1 / leverage) + maintenance_margin_rate)
        else:
            liq_price = entry_price * (1 + (1 / leverage) - maintenance_margin_rate)

        return liq_price
