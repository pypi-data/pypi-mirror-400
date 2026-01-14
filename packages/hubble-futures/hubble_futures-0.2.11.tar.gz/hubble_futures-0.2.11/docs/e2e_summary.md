# hubble-futures E2E 测试覆盖率总结

**版本**: v1.0  
**更新日期**: 2026-01-05

---

## 📊 总体概览

| 交易所 | 测试数量 | 通过率 | 代码覆盖率 |
|--------|----------|--------|------------|
| **Aster DEX** | 21 | ✅ 100% | 80% |
| **WEEX** | 25 | ✅ 100% | 77% |
| **总计** | **46** | ✅ 100% | **77%** |

---

## 🏦 Aster DEX 测试覆盖 (21 个测试)

| 类别 | API 方法 | 测试状态 |
|------|----------|----------|
| **市场数据 (6)** | `get_klines`, `get_mark_price`, `get_ticker_24hr`, `get_depth`, `get_exchange_info`, `get_symbol_filters` | ✅ |
| **账户信息 (4)** | `get_account`, `get_balance`, `get_positions`, `get_open_orders` | ✅ |
| **辅助功能 (5)** | `validate_order_params`, `calculate_liquidation_price`, `get_funding_rate_history`, `get_open_interest`, `get_leverage_bracket` | ✅ |
| **交易功能 (6)** | `set_leverage`, `set_margin_type`, `place_order/cancel_order`, `get_order`, `cancel_all_orders`, `close_position` | ✅ |

### 测试文件

- `tests/e2e/test_aster_live.py`

---

## 🌐 WEEX 测试覆盖 (25 个测试)

| 类别 | API 方法 | 测试状态 |
|------|----------|----------|
| **市场数据 (7)** | `get_klines`, `get_mark_price`, `get_ticker_24hr`, `get_depth`, `get_exchange_info`, `get_symbol_filters`, `symbol_conversion` | ✅ |
| **账户信息 (4)** | `get_account`, `get_balance`, `get_positions`, `get_open_orders` | ✅ |
| **辅助功能 (5)** | `validate_order_params`, `calculate_liquidation_price`, `get_leverage_bracket`, `get_funding_rate_history`, `get_open_interest` | ✅ |
| **交易功能 (7)** | `set_leverage`, `set_margin_type`, `place_order/cancel_order`, `get_order`, `cancel_all_orders`, `place_sl_tp_orders`, `close_position` | ✅ |
| **参数映射 (2)** | `order_type_mapping`, `time_in_force_mapping` | ✅ |

### 测试文件

- `tests/e2e/test_weex_live.py`

---

## 📋 API 方法覆盖对比

| 功能分类 | Aster | WEEX | 备注 |
|----------|-------|------|------|
| K线数据 | ✅ | ✅ | |
| 标记价格 | ✅ | ✅ | |
| 24h行情 | ✅ | ✅ | |
| 深度数据 | ✅ | ✅ | |
| 交易规则 | ✅ | ✅ | |
| 账户信息 | ✅ | ✅ | |
| 持仓查询 | ✅ | ✅ | |
| 下单/撤单 | ✅ | ✅ | |
| 杠杆设置 | ✅ | ✅ | |
| 保证金模式 | ✅ | ✅ | WEEX 有仓位时受限 |
| 资金费率历史 | ✅ | ✅ | |
| 持仓量 | ✅ | ✅ | WEEX 从 ticker 提取 |
| 杠杆档位 | ✅ | ✅ | |
| 止盈止损单 | ❌ | ✅ | WEEX 特有 |
| Symbol转换 | ❌ | ✅ | WEEX 特有 (`cmt_` 前缀) |

---

## ⚠️ 已知限制

### WEEX 平台限制

1. **`set_margin_type`**: 有仓位或挂单时无法更改保证金模式
   - API 返回: `40015 - FAILED_PRECONDITION`
   - 测试处理: 检测并跳过，不标记为失败

2. **`place_sl_tp_orders`**: 需要 `client_oid` 参数
   - API 端点: `/capi/v2/order/plan_order`
   - 测试处理: 验证接口调用结构，允许 API 层错误

3. **`cancel_all_orders`**: 批量取消 API 不稳定
   - 解决方案: 改为逐个取消订单
   - 更可靠且行为一致

---

## 🔧 环境配置

### 必需的环境变量

```bash
# Aster DEX
ASTER_API_KEY=your_api_key
ASTER_API_SECRET=your_api_secret

# WEEX
WEEX_API_KEY=your_api_key
WEEX_API_SECRET=your_api_secret
WEEX_PASSPHRASE=your_passphrase

# 代理 (WEEX 需要 IP 白名单)
PROXY_URL=http://user:pass@host:port

# 启用 E2E 测试
RUN_E2E_TESTS=true
```

### 运行测试

```bash
cd docs/ref/hubble-futures

# 运行所有 E2E 测试
uv run pytest tests/e2e/ -v

# 仅 Aster 测试
uv run pytest tests/e2e/test_aster_live.py -v

# 仅 WEEX 测试
uv run pytest tests/e2e/test_weex_live.py -v

# 带覆盖率报告
uv run pytest tests/e2e/ -v --cov=hubble_futures
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `hubble_futures/aster.py` | Aster 客户端实现 |
| `hubble_futures/weex.py` | WEEX 客户端实现 |
| `tests/e2e/test_aster_live.py` | Aster E2E 测试 |
| `tests/e2e/test_weex_live.py` | WEEX E2E 测试 |
| `tests/e2e/conftest.py` | 测试配置和 fixtures |
