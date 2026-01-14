"""
Exchange configuration model.

Provides type-safe configuration for exchange clients.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExchangeConfig:
    """
    Exchange configuration.

    Supported exchanges: asterdex, weex, binance, okx (more to come)

    Attributes:
        name: Exchange name ("asterdex", "weex", etc.)
        api_key: API key
        api_secret: API secret
        base_url: API base URL (auto-detected if empty)
        passphrase: API passphrase (required for WEEX, OKX)
        proxy_url: Proxy server URL for API requests (optional).
            Required for exchanges with IP whitelist restrictions.
            Format: http://user:pass@host:port or http://host:port
            If not provided, connects directly to exchange.
    """
    name: str
    api_key: str
    api_secret: str
    base_url: str = ""
    passphrase: str = ""
    proxy_url: Optional[str] = None
