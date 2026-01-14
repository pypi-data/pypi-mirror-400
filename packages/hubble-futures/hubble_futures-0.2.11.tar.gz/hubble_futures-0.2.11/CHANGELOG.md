# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.9] - 2026-01-07

### Added

- **WEEX Plan Order Management**: Added support for canceling plan orders (trigger orders like SL/TP):
  - `get_plan_orders(symbol)` - Fetch current plan orders for a symbol
  - `cancel_plan_order(symbol, order_id)` - Cancel a specific plan order
  - `cancel_all_plan_orders(symbol)` - Cancel all plan orders for a symbol
  - **Fixes FAILED_PRECONDITION error**: WEEX does not allow leverage adjustment when any orders (including plan orders) exist. This update ensures all order types are cancelled before setting leverage.

## [0.2.8] - 2026-01-06

### Fixed

- Version bump for dependency consistency

## [0.2.7] - 2026-01-06

### Fixed

- **WEEX marginMode hardcoded issue**: Fixed `place_sl_tp_orders()` to dynamically infer `marginMode` from current position instead of hardcoding to `"3"` (Isolated). This resolves the error `"The marginMode must be set to the account's current marginMode."` when account is in Cross margin mode.
  - Now queries position info to determine correct marginMode (1=Cross, 3=Isolated)
  - Falls back to Cross mode if position query fails
  - Adds debug logging for marginMode inference

## [0.2.0] - 2026-01-04

### Added

- **Proxy Server Support**: Add `proxy_url` parameter to `ExchangeConfig` for IP whitelist bypass
  - Configure proxy via `ExchangeConfig(proxy_url="http://user:pass@host:port")`
  - All HTTP/HTTPS requests automatically route through configured proxy
  - No proxy configured = direct connection (backward compatible)
  - Support for authenticated proxy URLs with username/password

### Changed

- Updated `BaseFuturesClient.__init__()` to accept optional `proxy_url` parameter
- Updated `AsterFuturesClient` to support proxy configuration
- Updated `WeexFuturesClient` to support proxy configuration
- All exchange clients now respect proxy settings from `ExchangeConfig`

### Testing

- Added 9 new integration tests for proxy configuration
- Added 4 new unit tests for `proxy_url` field in `ExchangeConfig`
- All existing tests pass (73 unit + integration tests)

[Unreleased]: https://github.com/hubble-ecosystem/hubble-futures/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/hubble-ecosystem/hubble-futures/releases/tag/v0.2.0
[0.1.0]: https://github.com/hubble-ecosystem/hubble-futures/releases/tag/v0.1.0

## [0.1.0] - 2026-01-04

### Added

- Initial release of hubble-futures library
- Unified `BaseFuturesClient` abstract interface for futures trading
- `AsterFuturesClient` implementation for Aster DEX
- `WeexFuturesClient` implementation for WEEX exchange
- `ExchangeConfig` dataclass for exchange configuration
- `create_client()` factory function for easy client instantiation
- `list_exchanges()` function to discover supported exchanges

#### Market Data
- `get_klines()` - Fetch candlestick/kline data
- `get_mark_price()` - Fetch mark price and funding rate
- `get_funding_rate_history()` - Fetch historical funding rates
- `get_open_interest()` - Fetch open interest statistics
- `get_ticker_24hr()` - Fetch 24-hour ticker statistics
- `get_depth()` - Fetch order book depth
- `get_exchange_info()` - Fetch exchange trading rules
- `get_symbol_filters()` - Fetch symbol-specific filters and precision

#### Account
- `get_account()` - Fetch account information
- `get_balance()` - Fetch account balance summary
- `get_positions()` - Fetch current positions
- `set_leverage()` - Configure leverage for a symbol
- `set_margin_type()` - Configure margin mode (cross/isolated)

#### Trading
- `place_order()` - Place limit/market orders
- `cancel_order()` - Cancel an order
- `get_order()` - Fetch order details
- `get_open_orders()` - Fetch all open orders
- `cancel_all_orders()` - Cancel all open orders
- `place_sl_tp_orders()` - Place stop-loss/take-profit orders
- `close_position()` - Close a position with market order

#### WEEX-Specific Features
- Automatic symbol conversion (BTCUSDT ↔ cmt_btcusdt)
- WEEX signature generation (Base64 encoded HMAC-SHA256)
- Parameter mapping (side+reduce_only → WEEX type, order_type → match_price)
- USDT asset filtering for account data
- Position side conversion (LONG/SHORT → signed position_amt)

### Testing

- 61 unit tests covering core functionality
- 22 integration tests with mocked API responses
- E2E test framework for live API testing (optional)

### Documentation

- Comprehensive README with usage examples
- API documentation for all public methods
- E2E testing guide with troubleshooting

[Unreleased]: https://github.com/hubble-ecosystem/hubble-futures/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hubble-ecosystem/hubble-futures/releases/tag/v0.1.0
