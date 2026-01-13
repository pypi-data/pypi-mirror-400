# Batch Testing Module

批量回測 API，簡化多策略、多時期的回測流程。

## 設計目標

提供 **Jupyter-first** 的使用體驗：
- 非阻塞提交：`submit()` 立即返回，背景自動輪詢狀態
- 懶載入結果：第一次存取 `trades` / `performance` 時自動下載並快取
- 原生 Jupyter 支援：自動偵測環境、HTML 進度顯示

## 資料層級結構

```
BatchResults                          # 整批回測結果
├── PeriodResult                      # 單一時期的結果 (對應一個 task_id)
│   ├── StrategyResult (view)         # 策略層級視圖
│   │   └── BlueprintResult (view)    # Blueprint 層級視圖
│   │       ├── trades: DataFrame
│   │       └── performance: DataFrame
```

**關鍵概念**：
- 一個 `PeriodResult` = 一個 server task = 包含 N 個策略的回測
- `StrategyResult` / `BlueprintResult` 是 **View 物件**，不複製資料，只過濾
- `trades` / `performance` 存在於 `PeriodResult`，View 物件用 filter 取得子集

## 使用流程

### 1. 建立 BatchTester

```python
from tradepose_client.batch import BatchTester, Period

tester = BatchTester(
    api_key="sk_xxx",
    server_url="https://api.tradepose.com",
    poll_interval=2.0,      # 狀態輪詢間隔（秒）
    auto_download=True,     # 自動下載完成的結果
)
```

### 2. 提交回測

```python
batch = tester.submit(
    strategies=[strategy1, strategy2],
    periods=[
        Period.Q1(2024),
        Period.Q2(2024),
        Period.from_year(2023),
    ],
)
# 立即返回 BatchResults，背景開始輪詢
```

### 3. 監控進度

```python
# 即時狀態
print(batch.status)      # {'pending': 2, 'processing': 1, 'completed': 0, 'failed': 0}
print(batch.progress)    # 0.33

# 阻塞等待
batch.wait()             # 等待所有任務完成
batch.wait(timeout=60)   # 最多等 60 秒
```

### 4. 存取結果

```python
# === Batch 層級 ===
batch.summary()          # 所有 periods 的 performance 合併
batch.all_trades()       # 所有 periods 的 trades 合併

# === Period 層級 ===
period = batch["2024-01-01_2024-03-31"]  # by period key
period = batch.get_task("uuid-xxx")       # by task_id (O(1))

period.trades            # DataFrame: 該 period 所有策略的交易
period.performance       # DataFrame: 該 period 所有策略的績效
period.metadata          # TaskMetadataResponse: 完整 server 回傳

# === Strategy 層級 ===
strategy = period["VA_Breakout"]
strategy.trades          # 該策略所有 blueprints 的交易
strategy.performance     # 該策略所有 blueprints 的績效

# === Blueprint 層級 ===
bp = strategy["va_breakout_long"]
bp.trades                # 該 blueprint 的交易
bp.performance           # 該 blueprint 的績效

# === 鏈式存取 ===
batch["2024-Q1"]["VA_Breakout"]["va_breakout_long"].trades
```

### 5. 錯誤處理

```python
# 失敗的任務
for failed in batch.failed_tasks:  # list[PeriodResult]
    print(f"Task {failed.task_id} failed: {failed.error}")
    if failed.metadata:
        print(f"  Started: {failed.metadata.started_at}")
        print(f"  Worker: {failed.metadata.worker_id}")
```

### 6. 儲存結果

```python
batch.save("./results")
# 產生：
#   results/
#   ├── summary.parquet
#   ├── trades.parquet
#   └── 2024-01-01_2024-03-31/
#       ├── trades.parquet
#       └── performance.parquet
```

### 7. OHLCV 資料匯出

使用 `submit_ohlcv()` 取得策略的 OHLCV 資料與指標，返回 `OHLCVPeriodResult`：

```python
# 從 StrategyConfig 自動提取 base_instrument, base_freq 和所有指標
result = tester.submit_ohlcv(
    strategy=my_strategy,
    period=Period.Q1(2024),
    timeout=60,  # 60 秒後停止輪詢（可選）
)

# 立即返回 OHLCVPeriodResult，背景自動輪詢與下載
print(result.status)      # 'pending' | 'processing' | 'completed' | 'failed'
print(result.task_id)     # 'uuid-xxx'
print(result.period_str)  # '2024-01-01_2024-03-31'

# === 存取結果 ===
print(result.df)          # 完成時返回 DataFrame，否則 None
print(result.error)       # 失敗時返回錯誤訊息
```

**與 `submit()` 的差異**：

| 特性 | `submit()` | `submit_ohlcv()` |
|------|------------|------------------|
| 返回類型 | `BatchResults` | `OHLCVPeriodResult` |
| 用途 | 回測交易與績效 | OHLCV 與指標資料 |
| 輸入 | 多個策略 + 多個 periods | 單一策略 + 單一 period |
| timeout | 無 | 有（停止輪詢秒數）|
| 結果下載 | 背景自動下載 | 背景自動下載 |
| 存取方式 | `batch[period][strategy]` | `result.df` |

### 8. Enhanced OHLCV 資料匯出

使用 `submit_enhanced_ohlcv()` 取得已註冊策略的 OHLCV 資料與完整交易信號，返回 `EnhancedOhlcvPeriodResult`：

```python
# 需要已註冊的策略，返回包含交易信號和 trading context 的 OHLCV
result = tester.submit_enhanced_ohlcv(
    strategy=my_strategy,
    period=Period.Q1(2024),
    strategy_name="VA_Breakout",      # 可選，預設使用 strategy.name
    blueprint_name="va_breakout_long", # 可選，預設 base blueprint
    timeout=60,
)

# 立即返回 EnhancedOhlcvPeriodResult，背景自動輪詢與下載
print(result.status)      # 'pending' | 'processing' | 'completed' | 'failed'
print(result.task_id)     # 'uuid-xxx'
print(result.period_str)  # '2024-01-01_2024-03-31'

# === 存取結果 ===
print(result.df)          # 完成時返回 DataFrame，包含交易信號和上下文
print(result.error)       # 失敗時返回錯誤訊息
```

**`submit_ohlcv()` vs `submit_enhanced_ohlcv()` 的差異**：

| 特性 | `submit_ohlcv()` | `submit_enhanced_ohlcv()` |
|------|------------------|---------------------------|
| export_type | ON_DEMAND_OHLCV (3) | ENHANCED_OHLCV (2) |
| 需要策略註冊 | 否 | 是 |
| 指標來源 | 從 strategy 自動提取 indicator_specs | 從策略配置提取 |
| 包含交易信號 | 否 | 是 (entry/exit signals) |
| 包含 trading context | 否 | 是 |
| 返回類型 | `OHLCVPeriodResult` | `EnhancedOhlcvPeriodResult` |

## Period 建構方式

```python
from tradepose_client.batch import Period

# 季度
Period.Q1(2024)  # 2024-01-01 ~ 2024-03-31
Period.Q2(2024)  # 2024-04-01 ~ 2024-06-30

# 年度
Period.from_year(2024)           # 2024 全年
Period.from_year(2024, n_years=3)  # 2024-01-01 ~ 2026-12-31

# 月份
Period.from_month(2024, 3)                 # 2024-03-01 ~ 2024-03-31
Period.from_month(2024, 3, n_months=6)     # 2024-03-01 ~ 2024-08-31

# 自訂
Period(start="2024-01-01", end="2024-06-30")
```

## 模組結構

| 檔案 | 職責 |
|------|------|
| `tester.py` | `BatchTester` - 主要入口點，處理提交與下載 |
| `models.py` | `Period`, `BacktestRequest` - 資料模型 |
| `results.py` | `BatchResults`, `PeriodResult`, `StrategyResult`, `BlueprintResult` - 結果容器 |
| `background.py` | `BackgroundPoller` - 背景狀態輪詢 |
| `cache.py` | `ResultCache` - 記憶體快取 |

## 內部運作流程

```
User                    BatchTester                 BackgroundPoller            Server
  │                          │                             │                       │
  │ submit(strategies,       │                             │                       │
  │        periods)          │                             │                       │
  │─────────────────────────>│                             │                       │
  │                          │ POST /export (per period)   │                       │
  │                          │────────────────────────────────────────────────────>│
  │                          │                             │       task_id         │
  │                          │<────────────────────────────────────────────────────│
  │                          │                             │                       │
  │      BatchResults        │ start()                     │                       │
  │<─────────────────────────│────────────────────────────>│                       │
  │                          │                             │ GET /tasks/{id}       │
  │                          │                             │──────────────────────>│
  │                          │                             │     status/error      │
  │                          │                             │<──────────────────────│
  │                          │  _update_period_status()    │                       │
  │                          │<────────────────────────────│                       │
  │                          │                             │                       │
  │ batch.trades             │                             │                       │
  │─────────────────────────>│ (lazy load)                 │                       │
  │                          │ GET /tasks/{id}/result      │                       │
  │                          │────────────────────────────────────────────────────>│
  │      DataFrame           │         parquet bytes       │                       │
  │<─────────────────────────│<────────────────────────────────────────────────────│
```

## API 查詢複雜度

| 操作 | 複雜度 | 說明 |
|------|--------|------|
| `batch[period_key]` | O(1) | dict lookup |
| `batch.get_task(task_id)` | O(1) | `_task_index` 索引 |
| `batch.failed_tasks` | O(n) | 遍歷所有 periods |
| `period[strategy_name]` | O(n) | 遍歷策略列表（通常 n < 10） |
| `strategy[blueprint_name]` | O(n) | 遍歷 blueprints（通常 n < 5） |

## 重構注意事項

1. **View 物件不持有資料** - `StrategyResult` / `BlueprintResult` 是 filter view，資料存在 `PeriodResult`

2. **`_task_index` 是關鍵索引** - 確保 task_id 查詢是 O(1)

3. **`_update_period_status` 由 BackgroundPoller 呼叫** - 傳入完整 `TaskMetadataResponse`

4. **Jupyter 相容性** - `_repr_html_` 方法提供 HTML 渲染

5. **執行緒安全** - `BatchResults` 使用 `threading.RLock` 保護共享狀態

## 效能考量

### BackgroundPoller Client 重用

`BackgroundPoller` 在整個 polling 期間共用同一個 `TradePoseClient`：

- **連線重用**：利用 HTTP/2 keep-alive，避免重複 TLS 握手
- **資源效率**：單一 connection pool，減少記憶體使用
- **Client 生命週期**：隨 poller 啟動建立，停止時關閉

```python
# _poll_loop 內部實作
client = TradePoseClient(**config)
await client.__aenter__()
try:
    while polling:
        await _update_all_statuses(client)  # 重用 client
        await _download_completed(client)   # 重用 client
finally:
    await client.__aexit__(None, None, None)
```

### 記憶體管理

- `StrategyResult` / `BlueprintResult` 是 **View 物件**，不複製 DataFrame
- trades/performance 資料只存在 `PeriodResult`，View 用 filter 取得子集
- 使用 `ResultCache` 避免重複下載
