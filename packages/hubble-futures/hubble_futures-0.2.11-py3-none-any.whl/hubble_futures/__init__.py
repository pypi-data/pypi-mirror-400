"""
Exchange client factory and registry.

Usage:
    from hubble_futures import create_client, ExchangeConfig

    config = ExchangeConfig(
        name="asterdex",
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    client = create_client(config)
    klines = client.get_klines("BTCUSDT")

Function logging:
    from hubble_futures import start_function_log, record_function_call, finish_function_call, export_function_log

    start_function_log()
    record_function_call("open_position", {"symbol": "BTCUSDT", "side": "BUY"})
    finish_function_call("open_position", {"order_id": "12345", "status": "filled"})
    result = export_function_log(clear=True)
"""

from dataclasses import dataclass

from .aster import AsterFuturesClient
from .base import BaseFuturesClient
from .config import ExchangeConfig
from .function_log import (
    add_error,
    add_warning,
    clear_function_log,
    export_function_log,
    finish_function_call,
    get_function_log,
    record_function_call,
    set_trading_summary,
    start_function_log,
)
from .version import __version__
from .weex import WeexFuturesClient


@dataclass
class ExchangeInfo:
    """Exchange registration info - single source of truth."""
    client_class: type[BaseFuturesClient]
    default_url: str


# Single registry - add new exchanges here
# Each exchange only needs ONE entry (use primary name)
_EXCHANGE_REGISTRY: dict[str, ExchangeInfo] = {
    "asterdex": ExchangeInfo(AsterFuturesClient, "https://fapi.asterdex.com"),
    "weex": ExchangeInfo(WeexFuturesClient, "https://api-contract.weex.com"),
    # "binance": ExchangeInfo(BinanceFuturesClient, "https://fapi.binance.com"),
    # "okx": ExchangeInfo(OkxFuturesClient, "https://www.okx.com"),
}

# Aliases (alternative names that map to the same exchange)
_ALIASES: dict[str, str] = {
    "aster": "asterdex",
}


def _resolve_name(name: str) -> str:
    """Resolve alias to canonical name."""
    name = name.lower()
    return _ALIASES.get(name, name)


# Legacy compatibility - derived from registry
EXCHANGES: dict[str, type[BaseFuturesClient]] = {
    name: info.client_class for name, info in _EXCHANGE_REGISTRY.items()
}
EXCHANGES.update({alias: _EXCHANGE_REGISTRY[target].client_class for alias, target in _ALIASES.items()})

DEFAULT_BASE_URLS: dict[str, str] = {
    name: info.default_url for name, info in _EXCHANGE_REGISTRY.items()
}
DEFAULT_BASE_URLS.update({alias: _EXCHANGE_REGISTRY[target].default_url for alias, target in _ALIASES.items()})


def create_client(config: ExchangeConfig) -> BaseFuturesClient:
    """
    Factory function to create exchange client from config.

    Args:
        config: ExchangeConfig with exchange name and credentials

    Returns:
        Exchange client instance

    Raises:
        ValueError: If exchange is not supported

    Example:
        from hubble_futures import create_client, ExchangeConfig

        config = ExchangeConfig(
            name="asterdex",
            api_key="...",
            api_secret="..."
        )
        client = create_client(config)
    """
    canonical_name = _resolve_name(config.name)

    if canonical_name not in _EXCHANGE_REGISTRY:
        available = ", ".join(sorted(list(_EXCHANGE_REGISTRY.keys()) + list(_ALIASES.keys())))
        raise ValueError(
            f"Unknown exchange: '{config.name}'. "
            f"Available exchanges: {available}"
        )

    exchange_info = _EXCHANGE_REGISTRY[canonical_name]
    return exchange_info.client_class.from_config(config)


def list_exchanges() -> list:  # type: ignore[type-arg]
    """List all supported exchange names."""
    return sorted(set(EXCHANGES.keys()))


def get_default_base_url(exchange_name: str) -> str:
    """Get default base URL for an exchange."""
    return DEFAULT_BASE_URLS.get(exchange_name.lower(), "")


__all__ = [
    "create_client",
    "list_exchanges",
    "get_default_base_url",
    "ExchangeConfig",
    "BaseFuturesClient",
    "AsterFuturesClient",
    "WeexFuturesClient",
    "EXCHANGES",
    "DEFAULT_BASE_URLS",
    "__version__",
    # Function logging
    "start_function_log",
    "record_function_call",
    "finish_function_call",
    "set_trading_summary",
    "add_warning",
    "add_error",
    "export_function_log",
    "get_function_log",
    "clear_function_log",
]
