# Hubble Futures

Unified futures exchange client library for Hubble trading platform.

## Features

- **Unified Interface**: Single API for multiple exchanges
- **Exchange Support**: Aster DEX, WEEX (Binance, OKX coming soon)
- **Type Safe**: Full type hints and mypy strict mode
- **Adapter Pattern**: Exchange-specific differences handled internally
- **Retry Logic**: Automatic retry with exponential backoff for rate limits
- **Decimal Precision**: Proper decimal formatting for all exchanges

## Installation

```bash
pip install hubble-futures
```

## Quick Start

```python
from hubble_futures import create_client, ExchangeConfig

# Create exchange configuration
config = ExchangeConfig(
    name="asterdex",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Create client
client = create_client(config)

# Fetch market data
klines = client.get_klines("BTCUSDT", "1h", 200)
account = client.get_account()
positions = client.get_positions()

# Place order
order = client.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.01,
    price=50000
)
```

## Supported Exchanges

| Exchange | Name | Passphrase Required |
|----------|------|---------------------|
| Aster DEX | `asterdex` or `aster` | No |
| WEEX | `weex` | Yes |

### WEEX Configuration

WEEX requires an additional `passphrase` parameter:

```python
config = ExchangeConfig(
    name="weex",
    api_key="your_api_key",
    api_secret="your_api_secret",
    passphrase="your_passphrase"  # Required for WEEX
)
```

## API Reference

### Market Data

- `get_klines(symbol, interval, limit)` - Fetch candlestick data
- `get_mark_price(symbol)` - Fetch mark price and funding rate
- `get_depth(symbol, limit)` - Fetch orderbook
- `get_ticker_24hr(symbol)` - Fetch 24h statistics
- `get_exchange_info()` - Fetch exchange metadata
- `get_symbol_filters(symbol)` - Fetch trading rules

### Account & Trading

- `get_account()` - Fetch account information
- `get_positions(symbol)` - Fetch open positions
- `get_balance()` - Fetch balance summary
- `place_order(...)` - Place an order
- `cancel_order(symbol, order_id)` - Cancel an order
- `get_open_orders(symbol)` - Get open orders
- `set_leverage(symbol, leverage)` - Set leverage
- `close_position(symbol, percent)` - Close position

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/hubble/hubble-futures.git
cd hubble-futures

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Unit tests
pytest tests/unit -m unit

# Integration tests (mocked API)
pytest tests/integration -m integration

# E2E tests (requires .env with API credentials)
pytest tests/e2e -m e2e
```

### Code Quality

```bash
# Format check
ruff check hubble_futures tests

# Type check
mypy hubble_futures

# Coverage
pytest --cov=hubble_futures --cov-report=html
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  User Code                                  │
│  (Agent, Trading Bot, etc.)                 │
└─────────────────────────────────────────────┘
                 ↓ uses
┌─────────────────────────────────────────────┐
│  Factory: create_client(config)             │
└─────────────────────────────────────────────┘
                 ↓ creates
┌─────────────────────────────────────────────┐
│  BaseFuturesClient (Abstract)               │
│  - Unified interface                        │
│  - Common retry logic                       │
│  - Decimal formatting                       │
└─────────────────────────────────────────────┘
           ↓ implemented by
┌─────────────┬─────────────┬─────────────────┐
│  Aster      │  WEEX       │  Future         │
│  Adapter    │  Adapter    │  Adapters       │
│             │             │  (Binance, OKX) │
└─────────────┴─────────────┴─────────────────┘
```

### Adapter Responsibilities

Each exchange adapter handles:
- API authentication (different signing methods)
- Symbol format conversion (e.g., `BTCUSDT` ↔ `cmt_btcusdt`)
- Parameter mapping (e.g., `side` ↔ `type`)
- Response normalization (unified return format)

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/hubble/hubble-futures/issues
- Documentation: https://docs.hubble.com/futures-client
