# E2E Tests for Hubble Futures

端到端测试套件，用于验证与真实交易所 API 的集成。

## 设置步骤

### 1. 配置 API 凭证

```bash
# 从项目根目录复制配置文件
cd /path/to/hubble-futures
cp .env.example .env
```

编辑 `.env` 文件，填写真实的 API 凭证：

```bash
# Aster DEX
ASTER_API_KEY=your_actual_key
ASTER_API_SECRET=your_actual_secret

# WEEX
WEEX_API_KEY=your_actual_key
WEEX_API_SECRET=your_actual_secret
WEEX_PASSPHRASE=your_actual_passphrase

# 启用 E2E 测试
RUN_E2E_TESTS=true
```

### 2. 安装依赖

```bash
uv sync --all-extras
```

### 3. 运行测试

```bash
# 运行所有 E2E 测试
uv run pytest tests/e2e -m e2e -v

# 仅运行 WEEX 测试
uv run pytest tests/e2e/test_weex_live.py -m e2e -v

# 仅运行 Aster 测试
uv run pytest tests/e2e/test_aster_live.py -m e2e -v

# 运行特定测试类
uv run pytest tests/e2e/test_weex_live.py::TestWeexMarketData -m e2e -v
```

## 测试覆盖范围

### WEEX 测试 (`test_weex_live.py`)

#### ✅ TestWeexMarketData（市场数据 - 只读，安全）
- `test_get_klines` - 获取 K 线数据
- `test_get_mark_price` - 获取标记价格
- `test_get_ticker_24hr` - 获取 24 小时行情
- `test_get_depth` - 获取订单簿深度
- `test_get_exchange_info` - 获取交易所信息
- `test_get_symbol_filters` - 获取交易规则
- `test_symbol_conversion` - 符号转换测试

#### ✅ TestWeexAccount（账户信息 - 只读，安全）
- `test_get_account` - 获取账户信息
- `test_get_balance` - 获取余额摘要
- `test_get_positions` - 获取持仓信息
- `test_get_open_orders` - 获取未成交订单

#### ✅ TestWeexHelpers（辅助函数）
- `test_validate_order_params` - 订单参数验证
- `test_calculate_liquidation_price` - 清算价格计算
- `test_get_leverage_bracket` - 杠杆配置查询

#### ⏸️ TestWeexTrading（交易功能 - 默认跳过）
- `test_set_leverage` - 设置杠杆
- `test_place_and_cancel_order` - 下单和撤单

**警告**: 交易测试默认跳过，避免意外下单。

#### ✅ TestWeexParameterMapping（参数映射验证）
- `test_order_type_mapping` - 订单类型映射
- `test_time_in_force_mapping` - TIF 参数映射

### Aster 测试 (`test_aster_live.py`)

#### ✅ TestAsterMarketData（市场数据 - 只读，安全）
- `test_get_klines` - 获取 K 线数据
- `test_get_mark_price` - 获取标记价格
- `test_get_ticker_24hr` - 获取 24 小时行情
- `test_get_depth` - 获取订单簿深度
- `test_get_exchange_info` - 获取交易所信息
- `test_get_symbol_filters` - 获取交易规则

#### ✅ TestAsterAccount（账户信息 - 只读，安全）
- `test_get_account` - 获取账户信息
- `test_get_balance` - 获取余额摘要
- `test_get_positions` - 获取持仓信息
- `test_get_open_orders` - 获取未成交订单

#### ✅ TestAsterHelpers（辅助函数）
- `test_validate_order_params` - 订单参数验证
- `test_calculate_liquidation_price` - 清算价格计算

#### ⏸️ TestAsterTrading（交易功能 - 默认跳过）
- `test_set_leverage` - 设置杠杆
- `test_place_and_cancel_order` - 下单和撤单

**警告**: 交易测试默认跳过，避免意外下单。

## 安全说明

### ✅ 安全的测试（默认运行）
- **市场数据查询**: 只读操作，不会修改账户状态
- **账户信息查询**: 只读操作，不会产生费用
- **辅助函数**: 本地计算，不涉及 API 调用

### ⚠️ 需谨慎的测试（默认跳过）
- **交易测试**: 会实际下单，虽然会立即撤单，但仍有风险
- 如需运行，手动移除测试类上的 `@pytest.mark.skip` 装饰器

## WEEX 特殊说明

### IP 白名单限制
WEEX API 可能有 IP 白名单限制：
1. 登录 WEEX 账户
2. 进入 API 管理
3. 将 VPS IP 添加到白名单

### 测试环境
- 生产环境：`https://api-contract.weex.com`
- 测试网络：查看 WEEX 文档确认是否提供

### 符号格式
WEEX 使用特殊符号格式：
- 标准格式：`BTCUSDT`
- WEEX 格式：`cmt_btcusdt`
- 库会自动转换，无需手动处理

## 故障排查

### 问题：E2E 测试未运行
```
collected 0 items
```

**解决方案**:
1. 检查 `.env` 文件是否存在
2. 确认 `RUN_E2E_TESTS=true`
3. 确认 API 凭证已填写

### 问题：认证失败
```
API error: Invalid signature
```

**解决方案**:
1. 检查 API Key 和 Secret 是否正确
2. WEEX 需确认 Passphrase 是否正确
3. 检查 API 权限（需要读取权限）
4. WEEX 需检查 IP 白名单

### 问题：符号不存在
```
Symbol BTCUSDT not found
```

**解决方案**:
1. 确认交易所支持该交易对
2. 修改 `.env` 中的 `TEST_SYMBOL`
3. 使用交易所支持的符号（如 `ETHUSDT`）

### 问题：WEEX 连接超时
```
Connection timeout
```

**解决方案**:
1. 检查 VPS 网络连接
2. 确认 IP 在 WEEX 白名单中
3. 尝试使用代理（如需要）

## 测试数据验证

### K 线数据验证
```python
assert kline["open"] > 0
assert kline["high"] >= kline["low"]
assert kline["close"] > 0
assert kline["volume"] >= 0
```

### WEEX 特定验证
```python
# WEEX K 线特点
assert kline["close_time"] == kline["open_time"]  # WEEX 不提供 close_time
assert kline["trades"] == 0  # WEEX 不提供交易次数

# WEEX 账户计算
assert abs(wallet_balance - (equity - unrealized_pnl)) < 0.01

# WEEX 仓位数据
assert position_amt > 0  # 多仓
assert position_amt < 0  # 空仓
assert entry_price == open_value / size  # 入场价计算
```

## 持续集成

E2E 测试在 CI 中默认跳过，仅在手动触发时运行：

```yaml
# .github/workflows/test.yml
- name: Run E2E tests
  if: github.event_name == 'workflow_dispatch'
  run: pytest tests/e2e -m e2e
  env:
    ASTER_API_KEY: ${{ secrets.ASTER_API_KEY }}
    WEEX_API_KEY: ${{ secrets.WEEX_API_KEY }}
    RUN_E2E_TESTS: true
```

## 贡献指南

添加新的 E2E 测试时：
1. 使用 `@pytest.mark.e2e` 标记
2. 只读测试正常运行
3. 交易测试添加 `@pytest.mark.skip`
4. 添加详细的文档字符串
5. 验证返回数据结构
6. 添加异常处理测试

## 许可证

MIT License - 详见 LICENSE 文件
