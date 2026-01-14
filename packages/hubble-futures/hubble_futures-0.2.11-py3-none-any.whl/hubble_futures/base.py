"""
Base class for futures exchange clients.

Provides common functionality shared across all exchange implementations:
- HTTP session management
- Request retry logic for rate limits
- Decimal formatting for prices/quantities
- Time synchronization
"""

import random
import time
from abc import ABC, abstractmethod
from decimal import ROUND_DOWN, Decimal

import requests
from loguru import logger

# Optional function logging (may not be available in all environments)
try:
    from .function_log import finish_function_call, record_function_call
    _FUNCTION_LOG_AVAILABLE = True
except ImportError:
    _FUNCTION_LOG_AVAILABLE = False


class BaseFuturesClient(ABC):
    """
    Abstract base class for futures exchange clients.

    All exchange implementations should inherit from this class
    and implement the abstract methods.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        max_retries: int = 5,
        retry_delay: float = 1.0,
        timeout: float = 5.0,
        proxy_url: str | None = None
    ):
        """
        Initialize base client.

        Args:
            api_key: API key
            api_secret: API secret
            base_url: API base URL
            max_retries: Max retry attempts for rate limit errors
            retry_delay: Base delay for exponential backoff
            timeout: Request timeout in seconds
            proxy_url: Optional proxy server URL for all requests.
                Required for exchanges with IP whitelist restrictions.
                Format: http://user:pass@host:port or http://host:port
        """
        if not api_key:
            raise ValueError("api_key is required")
        if not api_secret:
            raise ValueError("api_secret is required")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.proxy_url = proxy_url

        self.session = requests.Session()
        self._setup_session_headers()
        self._setup_session_proxy()

        # Caches
        self._symbol_filters: dict = {}
        self._leverage_brackets: dict = {}
        self._last_sync_time: float = 0
        self.time_offset: int = 0

    def _setup_session_headers(self) -> None:
        """Setup default session headers. Override in subclass if needed."""
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def _setup_session_proxy(self) -> None:
        """Setup proxy for session if proxy_url is configured."""
        if self.proxy_url:
            self.session.proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url,
            }
            # Mask sensitive parts of proxy URL for logging
            masked_proxy = self._mask_proxy_url(self.proxy_url)
            logger.info(f"Using proxy: {masked_proxy}")
        else:
            self.session.proxies = {}
            logger.debug("No proxy configured, using direct connection")

    def _mask_proxy_url(self, proxy_url: str) -> str:
        """Mask sensitive parts of proxy URL for logging.

        Args:
            proxy_url: Full proxy URL like "http://user:pass@host:port" or "http://host:port"

        Returns:
            Masked URL with credentials hidden and IP partially masked
        """
        try:
            # Parse proxy URL
            if "@" in proxy_url:
                # Format: http://user:pass@host:port
                auth_part, endpoint = proxy_url.split("@", 1)
                protocol = auth_part.split("://")[0]
                # Mask credentials completely
                return f"{protocol}://***@{self._mask_host(endpoint)}"
            else:
                # Format: http://host:port
                protocol, endpoint = proxy_url.split("://", 1)
                return f"{protocol}://{self._mask_host(endpoint)}"
        except Exception:
            # If parsing fails, return completely masked
            return "***"

    def _mask_host(self, endpoint: str) -> str:
        """Mask IP address or hostname in endpoint.

        Args:
            endpoint: Endpoint like "192.168.1.1:8080" or "example.com:8080"

        Returns:
            Masked endpoint with IP partially hidden
        """
        # Split host and port
        if ":" in endpoint:
            host, port = endpoint.rsplit(":", 1)
            # Mask IP address (show first and last octet)
            parts = host.split(".")
            if len(parts) == 4:  # IPv4
                return f"{parts[0]}.***.{parts[3]}:{port}"
            else:  # Domain or other format
                return f"***:{port}"
        else:
            # No port, just mask host
            parts = endpoint.split(".")
            if len(parts) == 4:  # IPv4
                return f"{parts[0]}.***.{parts[3]}"
            else:
                return "***"

    @abstractmethod
    def _generate_signature(self, params: dict) -> str:  # type: ignore[type-arg]
        """Generate request signature. Must be implemented by subclass."""
        pass

    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds with offset correction."""
        if time.time() - self._last_sync_time > 3600:
            self._sync_server_time()
        return int(time.time() * 1000) + self.time_offset

    def _get_server_time_endpoint(self) -> str:
        """
        Get server time endpoint. Override in subclass for different exchanges.
        Return empty string to disable time sync.
        """
        return "/fapi/v1/time"

    def _parse_server_time(self, response_data: dict) -> int:  # type: ignore[type-arg]
        """Parse server time from response. Override if response format differs."""
        return response_data.get('serverTime', int(time.time() * 1000))

    def _sync_server_time(self) -> None:
        """Sync with server time."""
        endpoint = self._get_server_time_endpoint()
        if not endpoint:
            # Time sync disabled for this exchange
            return

        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                timeout=self.timeout
            )
            if response.status_code == 200:
                server_time = self._parse_server_time(response.json())
                local_time = int(time.time() * 1000)
                self.time_offset = server_time - local_time
                self._last_sync_time = time.time()
        except Exception as e:
            logger.warning(f"Clock sync failed: {e}")
            self.time_offset = 0

    def _request(
        self,
        method: str,
        endpoint: str,
        signed: bool = False,
        **kwargs: dict  # type: ignore[type-arg]
    ) -> dict:  # type: ignore[type-arg]
        """
        Generic request method with retry logic for rate limits.

        Args:
            method: HTTP method (GET/POST/DELETE)
            endpoint: API endpoint
            signed: Whether signature is required
            **kwargs: Additional request parameters

        Returns:
            Response data as dict

        Raises:
            requests.exceptions.HTTPError: For non-retryable HTTP errors
        """
        url = f"{self.base_url}{endpoint}"

        # Record function call start (if logging is available)
        if _FUNCTION_LOG_AVAILABLE:
            function_name = f"{method.lower()}_{endpoint.replace('/', '_')}"
            record_params = {"endpoint": endpoint, "method": method}
            if 'params' in kwargs:
                record_params.update(kwargs['params'])
            record_function_call(function_name, record_params)

        for attempt in range(self.max_retries + 1):
            if signed:
                params = kwargs.get('params', {})
                if 'signature' in params:
                    del params['signature']
                params['timestamp'] = self._get_timestamp()
                params['recvWindow'] = 5000
                params['signature'] = self._generate_signature(params)
                kwargs['params'] = params

            try:
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout

                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                result = response.json()

                # Record successful function call
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, {"status": "succeeded", "data": result})

                return result

            except requests.exceptions.HTTPError as e:
                resp = e.response

                if resp.status_code == 429:
                    if attempt < self.max_retries:
                        retry_after = resp.headers.get('Retry-After')
                        if retry_after:
                            try:
                                delay = float(retry_after)
                            except ValueError:
                                delay = self.retry_delay * (2 ** attempt)
                        else:
                            delay = self.retry_delay * (2 ** attempt)

                        jitter = delay * 0.2 * (2 * random.random() - 1)
                        delay = delay + jitter

                        logger.warning(
                            f"Rate limit hit (429) on {method} {endpoint}. "
                            f"Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(
                            f"Rate limit exceeded after {self.max_retries} retries"
                        )
                        logger.error(f"Response: {resp.text}")
                        if _FUNCTION_LOG_AVAILABLE:
                            finish_function_call(function_name, error=f"Rate limit exceeded")
                        raise

                logger.error(f"API request failed: {e}")
                logger.error(f"Response: {resp.text}")
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, error=str(e))
                raise

            except requests.exceptions.Timeout as e:
                logger.error(f"Request timeout: {method} {endpoint}")
                if _FUNCTION_LOG_AVAILABLE:
                    finish_function_call(function_name, error=f"Timeout after {self.timeout}s")
                raise Exception(f"API request timeout after {self.timeout}s") from e

            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {method} {endpoint} - {e}")
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

    def _format_decimal(
        self,
        value: float,
        step: float | None = None,
        precision: int | None = None,
        rounding: str = ROUND_DOWN
    ) -> str:
        """Format numeric values to comply with exchange precision rules."""
        if value is None:
            return ""
        decimal_value = Decimal(str(value))

        if step:
            step_decimal = Decimal(str(step))
            if step_decimal > 0:
                multiple = (decimal_value / step_decimal).to_integral_value(rounding=rounding)
                decimal_value = (multiple * step_decimal).quantize(step_decimal, rounding=rounding)

        if precision is not None and precision >= 0:
            quant = Decimal('1').scaleb(-precision)
            decimal_value = decimal_value.quantize(quant, rounding=rounding)

        normalized = decimal_value.normalize()
        return format(normalized, 'f')

    # ==================== Abstract Methods ====================
    # Subclasses must implement these methods

    @classmethod
    @abstractmethod
    def from_config(cls, config: "ExchangeConfig") -> "BaseFuturesClient":  # type: ignore[name-defined] # noqa: F821
        """Create client instance from ExchangeConfig."""
        pass

    # Market Data
    @abstractmethod
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> list[dict]:  # type: ignore[type-arg]
        """Fetch candlestick data."""
        pass

    @abstractmethod
    def get_mark_price(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch mark price info."""
        pass

    @abstractmethod
    def get_depth(self, symbol: str, limit: int = 20) -> dict:  # type: ignore[type-arg]
        """Fetch orderbook."""
        pass

    @abstractmethod
    def get_ticker_24hr(self, symbol: str) -> dict:  # type: ignore[type-arg]
        """Fetch 24h statistics."""
        pass

    # Account
    @abstractmethod
    def get_account(self) -> dict:  # type: ignore[type-arg]
        """Fetch account info."""
        pass

    @abstractmethod
    def get_positions(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Fetch open positions."""
        pass

    @abstractmethod
    def get_balance(self) -> dict:  # type: ignore[type-arg]
        """Fetch balance summary."""
        pass

    # Trading
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> dict:  # type: ignore[type-arg]
        """Set leverage for symbol."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def cancel_order(
        self,
        symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None
    ) -> dict:  # type: ignore[type-arg]
        """Cancel an order."""
        pass

    @abstractmethod
    def get_open_orders(self, symbol: str | None = None) -> list[dict]:  # type: ignore[type-arg]
        """Get open orders."""
        pass

    # Helpers
    @abstractmethod
    def get_symbol_filters(self, symbol: str, force_refresh: bool = False) -> dict:  # type: ignore[type-arg]
        """Get trading rules for symbol."""
        pass

    @abstractmethod
    def close_position(self, symbol: str, percent: float = 100.0) -> dict:  # type: ignore[type-arg]
        """Close position by percentage."""
        pass
