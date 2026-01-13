# Market Profile 開發者指南

> **其他文件**: 如需了解 Market Profile 的交易理論與策略應用，請參閱 [策略指南](./market_profile_trading.md)

## 目錄

- [概述](#概述)
- [核心概念](#核心概念)
- [API 參考](#api-參考)
- [配置指南](#配置指南)
  - [TPO 時間區間設定](#tpo-時間區間設定)
- [輸出欄位說明](#輸出欄位說明)
- [形狀識別 (實驗性功能)](#形狀識別-實驗性功能)
- [使用範例](#使用範例)
- [常見錯誤](#常見錯誤)
- [進階主題](#進階主題)
- [參考資料](#參考資料)

---

## 概述

Market Profile 是一種基於 **TPO (Time Price Opportunity)** 的價格分布分析工具，由 J. Peter Steidlmayer 於 1980 年代開發。它透過識別市場參與者的行為特徵和關鍵價格水平，幫助交易者理解市場結構。

### 核心價值

- **POC (Point of Control)**: 識別市場最認同的價格水平（最強的支撐/阻力）
- **Value Area**: 定義 70% TPO 集中的「公平價值區間」
- **Profile Shape**: 識別市場狀態（趨勢、反轉、區間）

### 快速開始

```python
from tradepose_models.indicators.market_profile import (
    MarketProfileIndicator,
    create_daily_anchor
)

# 1. 配置 24 小時滾動窗口（最常用）
anchor = create_daily_anchor(hour=9, minute=15, lookback_days=1)

# 2. 創建指標
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,      # ES 期貨最小跳動單位
    value_area_pct=0.7   # 標準 70% Value Area
)

# 3. 應用到策略（透過 strategy engine）
# 結果：包含所有欄位的 Struct 欄位 "market_profile"
```

---

## 核心概念

### TPO (Time Price Opportunity)

**定義**: 每個時間段（kbar）在其 `[low, high]` 價格範圍內按 `tick_size` 生成的價格層級計數。

**計算方式**:
```python
# 對於每根 K 線
low_level = round(low / tick_size)
high_level = round(high / tick_size)

# 每個價格層級獲得 +1 TPO
for level in range(low_level, high_level + 1):
    tpo_count[level] += 1
```

**範例**:
```
K 線: low=100.00, high=100.50, tick_size=0.10

生成的 TPO:
- level 1000 (100.00): +1
- level 1001 (100.10): +1
- level 1002 (100.20): +1
- level 1003 (100.30): +1
- level 1004 (100.40): +1
- level 1005 (100.50): +1

總共: 6 個 TPO
```

**視覺化**:
```
價格    TPO 分布
100.50  █
100.40  ██
100.30  ████       ← 更多 TPO = 更高市場接受度
100.20  █████      ← POC (最多 TPO)
100.10  ███
100.00  █
```

### POC (Point of Control)

**定義**: TPO 計數最多的價格層級，代表市場最認同的價格。

**交易意義**:
- **強支撐/阻力**: 市場參與者在此價格最活躍
- **磁吸效應**: 價格傾向回到 POC
- **突破信號**: 價格遠離 POC 表示趨勢形成

**確定性保證**: 當多個層級有相同最大 TPO 計數時，選擇**最低價格層級**（保守原則），確保相同輸入永遠產生相同結果（回測可重現）。

**範例**:
```python
# TPO 分布
tpo_count = {
    1000: 3,
    1001: 5,  # 最大
    1002: 5,  # 最大（tied）
    1003: 4
}

# POC = level 1001 (100.10) - 選擇最低的層級
```

### Value Area (VA)

**定義**: 包含 70%（預設）TPO 計數的價格範圍，由 VAH（上界）和 VAL（下界）定義。

**擴展算法**:
1. 從 POC 開始
2. 向上下兩側擴展
3. 每次優先選擇 TPO 較多的方向
4. 直到累積 TPO ≥ 目標百分比（70%）

**交易意義**:
- **VAH (Value Area High)**: 阻力，價格突破表示強勢
- **VAL (Value Area Low)**: 支撐，價格跌破表示弱勢
- **VA 內**: 公平價值區間，適合區間交易
- **VA 外**: 價格偏離，可能反轉或趨勢延續

**範例**:
```
總 TPO = 14, 目標 70% = 10

擴展過程:
1. 起始: va_levels=[1002], count=5
2. 上方 1003(4) vs 下方 1001(2) → 選上方
   va_levels=[1002,1003], count=9
3. 上方 1004(2) vs 下方 1001(2) → 選上方（相等時選上方）
   va_levels=[1002,1003,1004], count=11 ≥ 10 ✓

結果:
- VAH = 1004 * 0.10 = 100.40
- VAL = 1002 * 0.10 = 100.20
- Value Area = 0.20
```

### Anchor Segmentation (時間窗口分段)

**定義**: 將時間序列劃分為固定窗口，每個窗口計算獨立的 Market Profile。

**固定窗口語義** (ADR-052 v3.0):
- 每 `lookback_days` 個 anchor 創建一個 segment
- Segments 之間**無重疊數據**
- 確保 TPO 計算不會重複計算相同的 K 線

**範例**:
```python
# 每日 09:15 anchor, lookback=1
# - Wed 09:15 的 segment = [Tue 09:15, Wed 09:15)
# - Thu 09:15 的 segment = [Wed 09:15, Thu 09:15)
# 每個 segment 包含 24 小時的數據

anchor = create_daily_anchor(hour=9, minute=15, lookback_days=1)
```

#### Daily Anchor 的反直覺特性

**重要**: Daily anchor 並非「每天都會有值」，而是「每 N 天一次」。

```python
# 常見誤解: lookback_days=3 表示「過去 3 天」
anchor = create_daily_anchor(hour=9, minute=15, lookback_days=3)

# 實際行為: 每 3 天觸發一次計算
# - Mon 09:15: 計算 segment（包含 Fri 09:15 ~ Mon 09:15 數據）
# - Tue 09:15: 無值（不重疊）
# - Wed 09:15: 無值（不重疊）
# - Thu 09:15: 計算 segment（包含 Mon 09:15 ~ Thu 09:15 數據）
```

**如何實現「每天都有 Market Profile」？**

```python
# ✅ 方案 1: lookback_days=1（24 小時滾動窗口）
anchor = create_daily_anchor(hour=9, minute=15, lookback_days=1)
# - Mon 09:15: 計算 [Fri 09:15, Mon 09:15)
# - Tue 09:15: 計算 [Mon 09:15, Tue 09:15)
# - Wed 09:15: 計算 [Tue 09:15, Wed 09:15)
# 每天都有值 ✓

# ❌ 方案 2: lookback_days=3（每 3 天一次）
# 只有 Mon, Thu, Sun, ... 有值，中間 2 天為空
```

#### Weekly Anchor 解決多天窗口問題

如果想要「每天都有過去 5 天的 Market Profile」，需創建 5 個 weekly anchor 指標錯開觸發日。詳見 [使用範例 > 範例 7](#範例-7-每天都有-5-天窗口的-market-profile)。

---

## API 參考

### MarketProfileIndicator

```python
class MarketProfileIndicator(BaseModel):
    type: Literal["MarketProfile"] = "MarketProfile"
    anchor_config: Dict[str, Any]          # 必填
    tick_size: float                       # 必填，必須 > 0
    value_area_pct: float = 0.7            # 預設 70%
    fields: Optional[List[str]] = None     # 可選欄位選擇
    shape_config: Optional[Dict[str, Any]] = None  # 可選形狀識別
```

#### 參數說明

##### `anchor_config` (必填)

時間窗口配置，使用 helper functions 創建：

**選項 1: 每日 Anchor**
```python
from tradepose_models.indicators.market_profile import create_daily_anchor

# 24 小時滾動窗口（最常用）
anchor = create_daily_anchor(
    hour=9,           # 小時 (0-23)
    minute=15,        # 分鐘 (0-59)
    lookback_days=1   # 回溯天數
)
# 結果: 每日 09:15 的 segment = [前一日 09:15, 當日 09:15)
```

**選項 2: 每週 Anchor**
```python
from tradepose_models.indicators.market_profile import create_weekly_anchor
from tradepose_models.enums import Weekday

# 週線窗口
anchor = create_weekly_anchor(
    weekday=Weekday.MON,  # 或 0, 或 "Mon"
    hour=9,
    minute=0,
    lookback_days=5       # 約 1 週
)
```

**選項 3: Initial Balance 窗口**
```python
from tradepose_models.indicators.market_profile import create_initial_balance_anchor

# 交易日開盤後 60 分鐘（09:00 ~ 10:00）
anchor = create_initial_balance_anchor(
    start_hour=9,
    start_minute=0,
    end_hour=10,
    end_minute=0
)
# 結果: 每天 09:00-10:00 計算一次 Market Profile（IB 時段）

# 使用案例: RTH (Regular Trading Hours) 分析
# 美股 RTH = 09:30 ~ 16:00
anchor_rth = create_initial_balance_anchor(
    start_hour=9,
    start_minute=30,
    end_hour=16,
    end_minute=0
)
```

##### `tick_size` (必填)

最小價格單位，用於劃分價格層級。

**選擇指南**:

| 商品 | tick_size | 說明 |
|------|-----------|------|
| ES (E-mini S&P 500) | `0.25` | 最小變動 0.25 點 |
| NQ (E-mini Nasdaq) | `0.25` | 最小變動 0.25 點 |
| TXF (台指期) | `1.0` | 最小變動 1 點 |
| BTC (比特幣) | `1.0` ~ `10.0` | 根據價格範圍調整 |
| EUR/USD (外匯) | `0.0001` | 1 pip |
| 股票 | `0.01` | 1 分 |

**原則**:
- ✅ **使用商品的最小變動單位或其整數倍**
- ❌ **太小**: TPO 分布過於分散，難以識別集中區域
- ❌ **太大**: TPO 分布過於集中，失去價格細節

> **驗證標準**: 好的 tick_size 應使 Value Area 覆蓋 5-15 個價格層級，POC 清晰可辨

##### `value_area_pct` (可選，預設 0.7)

Value Area 百分比，表示要包含多少 TPO。

- **標準值**: `0.7` (70%) - 行業標準
- **範圍**: `(0, 1)` - 必須是小數，不是百分比數字
- **調整時機**:
  - 高波動市場: 可提高到 `0.8` 或 `0.85`
  - 低波動市場: 可降低到 `0.6` 或 `0.65`

**常見錯誤**:
```python
# ❌ 錯誤
value_area_pct = 70  # 應該是 0.7，不是 70

# ✅ 正確
value_area_pct = 0.7
```

##### `fields` (可選，預設 None)

選擇要保留的欄位，減少記憶體使用。

**可用欄位**:
- `"poc"`: Point of Control
- `"vah"`: Value Area High
- `"val"`: Value Area Low
- `"value_area"`: VAH - VAL 範圍
- `"tpo_distribution"`: TPO 分布詳情（List<Struct{price, count, periods}>）
- `"segment_id"`: 時間區段 ID（自動包含，用於 ffill）
- `"profile_shape"`: Profile 形狀類型（需啟用 `shape_config`）

**範例**:
```python
# 只保留 POC 和 VAH（記憶體優化）
# 注意: segment_id 會自動包含（用於 ffill），無需手動指定
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,
    fields=["poc", "vah"]  # segment_id 自動添加
)

# 或保留所有欄位（預設）
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,
    fields=None  # 包含所有 7 個欄位
)

# ⚠️ 記憶體提示:
# - tpo_distribution 是嵌套結構，佔用較多記憶體
# - 如果不需要進階分析（Single Prints、視覺化），可以不包含
```

##### `shape_config` (可選，實驗性功能)

Profile 形狀識別配置。詳見 [形狀識別](#形狀識別-實驗性功能) 章節。

### Helper Functions

#### `create_daily_anchor()`

```python
def create_daily_anchor(
    hour: int,
    minute: int,
    lookback_days: int = 1,
) -> Dict[str, Any]
```

創建每日 Anchor 配置。

**參數**:
- `hour`: 小時 (0-23)
- `minute`: 分鐘 (0-59)
- `lookback_days`: 回溯天數（預設 1）

**返回**: Anchor 配置 dict

**範例**:
```python
# 每日 09:15 結束，回溯 1 天
anchor = create_daily_anchor(9, 15, 1)

# 視覺化
# ├─────────────────────────┤ Segment 1
# Tue 09:15            Wed 09:15
#                      ├─────────────────────────┤ Segment 2
#                      Wed 09:15            Thu 09:15
```

#### `create_weekly_anchor()`

```python
def create_weekly_anchor(
    weekday: Union[int, str, Weekday],
    hour: int,
    minute: int,
    lookback_days: int = 5,
) -> Dict[str, Any]
```

創建每週 Anchor 配置。

**參數**:
- `weekday`: 星期幾
  - `int`: 0=週一, 1=週二, ..., 6=週日
  - `str`: "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
  - `Weekday` enum: `Weekday.MON`, `Weekday.TUE`, ...
- `hour`: 小時 (0-23)
- `minute`: 分鐘 (0-59)
- `lookback_days`: 回溯天數（預設 5）

**範例**:
```python
# 使用整數
anchor = create_weekly_anchor(0, 9, 15, 5)  # 週一

# 使用字串
anchor = create_weekly_anchor("Mon", 9, 15, 5)

# 使用 Weekday enum
from tradepose_models.enums import Weekday
anchor = create_weekly_anchor(Weekday.MON, 9, 15, 5)
```

#### `create_profile_shape_config()`

```python
def create_profile_shape_config(
    early_period_ratio: float = 0.15,
    late_period_ratio: float = 0.15,
    trend_ib_max_ratio: float = 0.20,
    trend_monotonic_threshold: float = 0.60,
    trend_imbalance_threshold: float = 0.70,
    pshape_concentration_threshold: float = 0.60,
    bshape_valley_threshold: float = 0.70,
    normal_symmetry_threshold: float = 0.30,
) -> Dict[str, Any]
```

創建 Profile 形狀識別配置。詳見 [形狀識別](#形狀識別-實驗性功能) 章節。

---

## 配置指南

### 常見使用場景

#### 場景 A: 24 小時滾動窗口（最常用）

```python
# 每日 09:15 為錨點，回溯 1 個交易日
anchor = create_daily_anchor(9, 15, 1)

# 範例:
# - Wed 09:15 的 segment = [Tue 09:15, Wed 09:15)
# - Thu 09:15 的 segment = [Wed 09:15, Thu 09:15)
```

**適用於**: 日內交易、隔夜持倉分析

#### 場景 B: Initial Balance (IB) 窗口

```python
# 交易日開盤後 60 分鐘（09:00 ~ 10:00）
anchor = {
    "start_rule": {"type": "DailyTime", "hour": 9, "minute": 0},
    "end_rule": {"type": "DailyTime", "hour": 10, "minute": 0},
    "lookback_days": 0
}
```

**適用於**: Initial Balance 交易策略、開盤區間突破

**重要**: 當 `lookback_days=0` 時，必須確保 `start_rule < end_rule`

#### 場景 C: 週線窗口

```python
# 每週一 09:00 為錨點，回溯 1 週
anchor = create_weekly_anchor(Weekday.MON, 9, 0, 5)
```

**適用於**: 波段交易、週線分析

> **驗證規則**: 詳見 [API 參考 > anchor_config](#anchor_config-必填) 的驗證說明

### TPO 時間區間設定

#### Bar 頻率選擇

**行業標準：30 分鐘 TPO**

J. Peter Steidlmayer 於 1980 年代在 CBOT 設計 Market Profile 時，選用 30 分鐘作為標準 TPO 區間。這個設計使得：
- **Initial Balance**（第一個小時）= 2 個 TPO 區間（A 和 B 時段）
- **標準 6.5 小時交易日** = 13 個 TPO 時段（A 到 M）

**為什麼是 30 分鐘？**

| 時間區間 | 優點 | 缺點 | 適用場景 |
|---------|------|------|---------
| **1-5 分鐘** | 極度精細、捕捉微觀結構 | 噪音多、Profile 過度破碎 | 極短線剝頭皮 |
| **15 分鐘** | 比 30m 更細緻 | IB = 4 期間（過多） | 短線交易者 |
| **30 分鐘** | 行業標準、IB = 2 期間、最多研究支持 | 對日內短線稍粗 | **大多數交易者（推薦）** |
| **60 分鐘** | 適合宏觀視角 | IB = 1 期間（失去意義） | 波段/長線交易者 |
| **Daily/Weekly** | 宏觀趨勢分析 | 失去日內結構 | Composite Profile |

**關鍵洞察**：
- 30 分鐘是「平衡點」：足夠細緻捕捉日內結構，又不會過度破碎
- Initial Balance 的定義依賴 30 分鐘：「前兩個 TPO 時段」= 1 小時
- 如果用 60 分鐘，IB 只有 1 個時段，無法形成有效範圍
- 如果用 15 分鐘，IB 有 4 個時段，定義變得模糊

**Volume Profile vs Market Profile**：
- **Market Profile**（TPO 為主）：建議用 30 分鐘
- **Volume Profile**（成交量為主）：可用更小區間（1m、5m、tick）因為不依賴 TPO 字母標記

#### Session 時間設定

**RTH vs ETH**:
- **RTH** (Regular Trading Hours): 正規交易時段，流動性最高，Value Area 最有意義
- **ETH** (Extended Trading Hours): 延長時段，噪音較多，可參考極值作為支撐/阻力
- **建議**: 日內交易優先使用 RTH，24 小時市場（外匯、加密）可自定義主要時段

#### Composite Profile 時間框架

**Daily Profile（每日）**：
- **計算時機**：每日 RTH 收盤後
- **重置時機**：每日 RTH 開盤時
- **用途**：識別當日日型、POC、Value Area

**Composite Profile（複合）**：
- **Weekly**：5-10 個交易日（約 1-2 週）
- **Monthly**：20-30 個交易日
- **計算時機**：滾動計算或固定週期結束時
- **用途**：識別更大的價值區、支撐/阻力

**Developing Profile（發展中）**：
- **計算時機**：實時，隨每根 K 線更新
- **用途**：日內交易決策

#### Session 配置範例

```python
# 美國股票/期貨（RTH）
anchor = create_daily_anchor(hour=9, minute=30, lookback_days=1)
# session: 9:30-16:00 ET
# IB: 9:30-10:30 ET (2 × 30分鐘)

# 外匯（倫敦時段）
anchor = create_daily_anchor(hour=8, minute=0, lookback_days=1)
# session: 8:00-17:00 London
# IB: 8:00-9:00 London

# 加密貨幣（自定義 24 小時）
anchor = create_daily_anchor(hour=0, minute=0, lookback_days=1)
# 或根據主要交易所活躍時段調整
```

---

## 輸出欄位說明

Market Profile 計算結果為 **Struct Series**，包含以下欄位：

### 欄位表格

| 欄位 | 類型 | 範圍 | 說明 | 交易用途 |
|------|------|------|------|----------|
| `poc` | `f64` | Price | Point of Control - TPO 計數最多的價格層級 | 強支撐/阻力，價格磁吸效應 |
| `vah` | `f64` | Price | Value Area High - 70% TPO 區間上界 | 阻力，突破表示強勢 |
| `val` | `f64` | Price | Value Area Low - 70% TPO 區間下界 | 支撐，跌破表示弱勢 |
| `value_area` | `f64` | ≥0 | VAH - VAL 範圍 | 公平價值寬度，波動度指標 |
| `tpo_distribution` | `List<Struct>` | - | TPO 分布詳情：每個價格層級的計數和時段列表 | Single Prints 識別、進階分析、視覺化 |
| `segment_id` | `u64` | - | 時間區段 ID（已 ffill） | Window 函數的 partition key |
| `profile_shape` | `str` | enum | Profile 形狀類型 | 市場狀態判斷，策略選擇 |

### 欄位關係

```
恆成立的不等式:
vah >= poc >= val

value_area = vah - val

profile_shape 可能值:
- "p_shaped": P型（看空反轉信號）
- "b_shaped": b型（看多反轉信號）
- "trend_day": 趨勢日（順勢交易）
- "normal": 正態分布（區間交易）
- "b_double_distribution": B型雙峰（區間交易）
- "undefined": 無法分類
```

### tpo_distribution 欄位詳解

`tpo_distribution` 是一個嵌套資料結構，包含完整的 TPO 分布資訊。

**資料結構**:
```python
List<Struct{
    price: f64,        # 價格層級（實際價格，已乘以 tick_size）
    count: u32,        # 該層級的 TPO 計數
    periods: List<u32> # 貢獻此層級的時段索引列表
}>
```

**範例資料**:
```python
# 假設 tick_size=0.10
[
    {price: 100.00, count: 3, periods: [0, 1, 2]},
    {price: 100.10, count: 5, periods: [1, 2, 3, 4, 5]},  # POC
    {price: 100.20, count: 4, periods: [2, 3, 4, 5]},
    {price: 100.30, count: 2, periods: [4, 5]},
    {price: 100.40, count: 1, periods: [5]},  # Single Print
]
```

**使用範例**:

```python
# 識別 Single Prints（72% 方向準確度指標）
df = df.with_column(
    pl.col("market_profile")
      .struct.field("tpo_distribution")
      .list.eval(pl.element().struct.field("count") == 1)
      .list.sum()
      .alias("single_print_count")
)

# 提取價格和計數用於視覺化
df = df.with_columns([
    pl.col("market_profile").struct.field("tpo_distribution")
      .list.eval(pl.element().struct.field("price")).alias("tpo_prices"),
    pl.col("market_profile").struct.field("tpo_distribution")
      .list.eval(pl.element().struct.field("count")).alias("tpo_counts")
])
```

**進階用途**:
- ✅ **識別 Single Prints**：72% 方向準確度指標（ManOverMarket 研究）
- ✅ **分析時段分布**：了解哪些時段對哪些價格貢獻最多
- ✅ **自定義形狀識別**：基於 TPO 分布實現自己的算法
- ✅ **視覺化 Market Profile**：繪製完整的 TPO Chart
- ✅ **TPO 密度分析**：檢測 Trend Day 特徵（≤5 TPOs/層級）

**記憶體注意**:
- `tpo_distribution` 是嵌套結構，包含多層資料
- 對於長時段（如 100+ K 線），可能包含 50-100 個價格層級
- 如果不需要進階分析，建議使用 `fields` 參數排除此欄位

### 展開 Struct 欄位

Market Profile 返回的是 Struct，需要展開才能使用各欄位：

```python
import polars as pl

# 批量展開多個欄位（推薦）
df = df.with_columns([
    pl.col("market_profile").struct.field("poc").alias("mp_poc"),
    pl.col("market_profile").struct.field("vah").alias("mp_vah"),
    pl.col("market_profile").struct.field("val").alias("mp_val"),
    pl.col("market_profile").struct.field("value_area").alias("mp_va"),
])

# 或使用 unnest 展開所有欄位
df = df.unnest("market_profile")
```

### 使用 segment_id 進行 Window 操作

`segment_id` 欄位已自動 ffill，非常適合作為 Polars window 函數的 partition key。

**為什麼使用 segment_id？**
- Market Profile 的其他欄位（poc, vah, val）是**稀疏的**（只在 anchor 點有值）
- `segment_id` 已 ffill，每個 segment 的所有行都有相同的 ID
- 輕量級（只有 8 bytes），ffill 成本低

```python
# 獲取當前 segment 的 POC（傳播到所有行）
df = df.with_column(
    pl.col("market_profile").struct.field("poc")
      .over([pl.col("market_profile").struct.field("segment_id")])
      .first()
      .alias("segment_poc")
)

# 判斷價格相對 Value Area 的位置
df = df.with_columns([
    pl.col("market_profile").struct.field("vah")
      .over([pl.col("market_profile").struct.field("segment_id")]).first().alias("segment_vah"),
    pl.col("market_profile").struct.field("val")
      .over([pl.col("market_profile").struct.field("segment_id")]).first().alias("segment_val"),
]).with_column(
    pl.when(pl.col("close") > pl.col("segment_vah")).then(pl.lit("above_va"))
      .when(pl.col("close") < pl.col("segment_val")).then(pl.lit("below_va"))
      .otherwise(pl.lit("inside_va")).alias("va_position")
)
```

> **提示**: 總是使用 `.first()` 聚合，因為 POC/VAH/VAL 在同一 segment 內的所有行都相同。

---

## 形狀識別 (實驗性功能)

### 實驗性功能警告

**狀態**: BETA - 算法可能在未來版本中變更

**準確度**: 尚未在大規模市場數據上驗證

**行業差距**: 無開源參考實現存在（根據 KB-006 研究）

**當前限制**:
1. ❌ **Single Prints 檢測**未實現（業界 72% 方向準確度特徵）
2. ❌ **TPO 密度分析**未實現（業界標準: ≤5 TPOs/層級）
3. ❌ **統計分布測試**未實現（偏度/峰度）

**建議**:
- ⚠️ 在生產交易中謹慎使用
- ✅ 根據您的特定市場數據驗證
- ✅ 將形狀視為**補充信號**，而非主要信號
- ✅ 預設參數基於行業標準，但可能需要調整

詳見 **ADR-060** 和 **KB-006** 了解詳細算法文件。

### Profile Shape 類型

Market Profile 形狀反映市場參與者的行為模式：

#### 1. P-Shaped (P型) - 看漲信號（Short Covering）

**結構**: 下窄上寬，像字母 "P"

**形成機制**: Short Covering（空頭回補）
- **本質**: Old Business（舊業務）- 既有空頭平倉，而非新買家進場
- **前置條件**: 通常跟隨一個或多個下跌日（市場過度做空）

**視覺特徵**:
```
價格    TPO 分布
1010    CDEFGH  ← 高位盤整區（bulge，寬）
1009    CDEFGH
1008    CDEFGH
1007    C
1006    C       ← 快速上漲區域
1005    B
1004    AB      ← 早期低位開盤（stem/tail，窄）
1003    AB
1002    A       ← 開盤在低位，空頭被迫回補
1001    A       ← Single Print Buying Tail
```

**時間序列特徵**:
- **開盤位置**: 開盤在低位（near the low）
- **早盤**: 價格從低位快速上漲（空頭被迫回補，形成 stem）
- **晚盤**: 上漲後在高位盤整/分配（distributing，形成 bulge）
- **結果**: 形成下窄上寬的 "P" 形狀

**交易含義**:
- **市場狀態**: 空頭回補，可能是下跌趨勢結束的信號
- **信號方向**: 看漲信號（Bullish signal）
- **語義解讀**:
  - 在下跌趨勢中出現 → 可能標誌趨勢結束/反轉
  - 在上漲趨勢中出現 → 趨勢延續信號
- **策略**: POC 是良好的支撐區域，回調到 POC 可考慮做多
- **注意**: 空頭回補是「暫時性強勢」，需要「新業務」（New Business）才能延續突破

**配置參數**:
- `pshape_concentration_threshold`: 預設 0.60（60% TPO 集中度）

**價格區域劃分**（實現細節）:

程式碼使用**硬編碼的 30% 閾值**劃分價格區域：

- **高位區**: 價格 > 70% 位置（`max_level - 30% * price_range`）
- **低位區**: 價格 < 30% 位置（`min_level + 30% * price_range`）
- **中間區**: 30%-70% 之間

**範例**:
```
假設價格範圍 100.00 - 110.00 (10 點範圍)

高位區: > 107.00 (110 - 30% * 10)
中間區: 103.00 - 107.00
低位區: < 103.00 (100 + 30% * 10)

P-Shaped 檢測邏輯:
- 早期 15% 時段的 60%+ TPO 必須在低位區 (< 103.00) ← 開盤在低位
- 晚期 15% 時段的 60%+ TPO 必須在高位區 (> 107.00) ← 收盤在高位盤整
```

**注意**: 30% 閾值目前為硬編碼，未來版本可能改為可配置參數。

#### 2. b-Shaped (b型) - 看跌信號（Long Liquidation）

**結構**: 上窄下寬，像小寫字母 "b"

**形成機制**: Long Liquidation（多頭平倉）
- **本質**: Old Business（舊業務）- 既有多頭離場，而非新賣家進場
- **前置條件**: 通常跟隨一個或多個上漲日（市場過度做多）

**視覺特徵**:
```
價格    TPO 分布
1010    A        ← Single Print Selling Tail
1009    A        ← 開盤在高位，多頭被迫平倉
1008    AB       ← 早期高位開盤（stem/tail，窄）
1007    AB
1006    B        ← 快速下跌區域
1005    C
1004    CDEFGH   ← 低位盤整區（bulge，寬）
1003    CDEFGH
1002    CDEFGH
1001    CDEFGH
```

**時間序列特徵**:
- **開盤位置**: 開盤在高位（near the high / top of the profile）
- **早盤**: 價格從高位快速下跌（多頭被迫平倉，形成 stem）
- **晚盤**: 下跌後在低位盤整/分配（distributing，形成 bulge）
- **結果**: 形成上窄下寬的 "b" 形狀

**交易含義**:
- **市場狀態**: 多頭平倉，可能是上漲趨勢結束的信號
- **信號方向**: 看跌信號（Bearish signal）
- **語義解讀**:
  - 在上漲趨勢中出現 → 可能標誌趨勢結束/反轉
  - 在下跌趨勢中出現 → 趨勢延續信號（consolidation before continuation）
- **策略**: POC 是良好的阻力區域，反彈到 POC 可考慮做空
- **注意**: 多頭平倉是「暫時性弱勢」，需要「新業務」（New Business）才能延續突破

**價格區域劃分**（與 P-Shaped 相同）:

程式碼使用**硬編碼的 30% 閾值**劃分價格區域：

- **高位區**: 價格 > 70% 位置（`max_level - 30% * price_range`）
- **低位區**: 價格 < 30% 位置（`min_level + 30% * price_range`）
- **中間區**: 30%-70% 之間

**b-Shaped 檢測邏輯**（與 P-Shaped 相反）:
- 早期 15% 時段的 60%+ TPO 必須在**高位區** ← 開盤在高位
- 晚期 15% 時段的 60%+ TPO 必須在**低位區** ← 收盤在低位盤整

**注意**: 30% 閾值目前為硬編碼，未來版本可能改為可配置參數。

#### 3. Trend Day (趨勢日) - 趨勢市場

**結構**: 持續單向移動

**視覺特徵**:
```
價格    TPO 分布
1010    FGHIJK   ← 晚期高位（上漲趨勢）
1009    EFGHIJK
1008    DEFGH
1007    CDE
1006    CD
1005    C
1004    B
1003    AB       ← 小 Initial Balance
1002    AB
1001    A        ← 早期低位
```

**檢測條件**（三者必須同時滿足）:

**條件 1: 小 Initial Balance (IB)**
```python
# IB = 前 2 個時段的價格範圍
ib_range = max_price_first_2_periods - min_price_first_2_periods
total_range = max_price_overall - min_price_overall
ib_ratio = ib_range / total_range

# 必須: IB < 20% 總範圍
if ib_ratio > 0.20:
    return False  # 不是 Trend Day
```

**條件 2: 單向移動**
```python
# 計算每個時段的價格中心
# 檢查價格是否單調遞增或遞減
monotonic_ratio = count_monotonic_movement / total_comparisons

# 必須: 60%+ 單向性
if monotonic_ratio < 0.60:
    return False  # 不是 Trend Day
```

**條件 3: TPO 不平衡**
```python
# 早期 15% 時段 vs 晚期 15% 時段
early_tpo_count = count_tpos_in_early_periods()
late_tpo_count = count_tpos_in_late_periods()

concentration = max(early_tpo, late_tpo) / (early_tpo + late_tpo)

# 必須: 70%+ 集中在一側
if concentration < 0.70:
    return False  # 不是 Trend Day

return True  # 所有 3 個條件滿足 = Trend Day
```

**行業標準特徵**（部分未實現）:
- ✅ 小 Initial Balance (< 20% 範圍)
- ✅ 單向價格擴展
- ✅ 早期/晚期 TPO 不平衡
- ❌ **TPO 密度**: 應 ≤5 TPOs/層級（未檢測）
- ❌ **85% 範圍在 IB 外**（未檢測）

**交易含義**:
- **市場狀態**: 強趨勢，單邊市場
- **策略**: 順勢交易，避免逆勢
- **特徵**: 不區分上漲/下跌（統一為 TrendDay）

**配置參數**:
- `trend_ib_max_ratio`: 預設 0.20（IB < 20%）
- `trend_monotonic_threshold`: 預設 0.60（60% 單向）
- `trend_imbalance_threshold`: 預設 0.70（70% 不平衡）

#### 4. B-Double Distribution (B型雙峰) - 區間市場

**結構**: 兩個獨立的 POC（雙峰分布）

**視覺特徵**:
```
價格    TPO 分布
1009    DEFGH    ← 峰 2
1008    DEFGH
1007    D
1006              ← 深谷
1005    A         ← 谷
1004              ← 深谷
1003    ABC       ← 峰 1
1002    ABC
1001    AB
```

**特徵**:
- 兩個明顯的局部最大值（POCs）
- 兩峰之間有深谷（< 70% 峰值 TPO 計數）
- 峰之間距離 > 20% 價格範圍

**交易含義**:
- **市場狀態**: 區間震蕩，兩個接受區域
- **策略**: 區間交易，在兩個 POC 之間操作

**配置參數**:
- `bshape_valley_threshold`: 預設 0.70（谷深度閾值）

#### 5. Normal (正態分布) - 平衡市場

**結構**: 對稱的鐘型分布

**視覺特徵**:
```
價格    TPO 分布
1007    C
1006    BCD
1005    ABCDEFGH  ← POC（中心）
1004    BCD
1003    C
```

**特徵**:
- POC 在價格範圍中間（30%-70%）
- 對稱的 TPO 分布
- 兩側差異 < 30%
- **行業標準**: 85% 範圍在 IB 內（未檢測）

**交易含義**:
- **市場狀態**: 平衡市場，供需均衡
- **策略**: 區間交易，VAH 做空、VAL 做多
- **特徵**: 50-60% 的交易日是 Normal 型

**配置參數**:
- `normal_symmetry_threshold`: 預設 0.30（<30% 不對稱）

#### 6. Undefined (無法分類)

不符合任何上述形狀的 profile。

### ProfileShapeConfig 配置

```python
class ProfileShapeConfig(BaseModel):
    # ========== 時段劃分（百分比方案）==========
    early_period_ratio: float = 0.15      # 前 15% 時段
    late_period_ratio: float = 0.15       # 後 15% 時段

    # ========== Trend Day 識別 ==========
    trend_ib_max_ratio: float = 0.20      # IB < 20% 總範圍
    trend_monotonic_threshold: float = 0.60  # 60%+ 單向移動
    trend_imbalance_threshold: float = 0.70  # 70%+ 集中度

    # ========== P/b 型識別 ==========
    pshape_concentration_threshold: float = 0.60  # 60% 集中度

    # ========== B-double 識別 ==========
    bshape_valley_threshold: float = 0.70  # 谷深度閾值

    # ========== Normal 型識別 ==========
    normal_symmetry_threshold: float = 0.30  # 對稱性閾值
```

### 參數來源與調整指南

**預設值來源** (基於行業標準):

| 參數 | 預設值 | 來源 | 市場類型 |
|------|--------|------|----------|
| `early_period_ratio` | 0.15 | 股票市場 IB 定義 (2/13 時段) | 股票 |
| `trend_ib_max_ratio` | 0.20 | 行業標準（ATAS, EMinimind） | 通用 |
| `trend_monotonic_threshold` | 0.60 | 允許適度回調 | 通用 |
| `trend_imbalance_threshold` | 0.70 | 強趨勢特徵 | 通用 |
| `pshape_concentration` | 0.60 | 業界共識 | 通用 |

**調整建議**:

| 市場類型 | 建議設置 | 理由 |
|----------|----------|------|
| **股票市場** | 使用預設值 (0.15, 0.20, 0.60, 0.70) | 符合 IB 定義 |
| **24h 期貨** | early=0.10, ib_max=0.15, monotonic=0.70, imbalance=0.75 | 更嚴格（IB 更小） |
| **高波動** | monotonic=0.50, imbalance=0.60 | 允許更多回調 |
| **低波動** | monotonic=0.70, imbalance=0.80 | 需要更強信號 |

**調整流程**:
1. 從預設值開始
2. 收集真實市場數據
3. 一次調整一個參數
4. 記錄準確度變化
5. 在測試集上驗證

### 形狀識別優先級

形狀檢測按以下順序進行（從最明顯到最不明顯）:

```
1. Trend Day      (最獨特)
   ↓ (不是)
2. B-Double       (雙峰明顯)
   ↓ (不是)
3. P-Shaped       (晚期集中)
   ↓ (不是)
4. b-Shaped       (早期集中)
   ↓ (不是)
5. Normal         (對稱)
   ↓ (不是)
6. Undefined      (fallback)
```

### 交易策略對照表

| Shape | 市場狀態 | 形成機制 | 交易策略 | 成功率 |
|-------|----------|----------|----------|--------|
| Trend Day | 強趨勢 | 新業務進場 | 順勢交易，避免逆勢 | N/A |
| P-Shaped | 空頭回補（Short Covering） | 舊業務平倉 | 看漲信號，回調到 POC 做多 | N/A |
| b-Shaped | 多頭平倉（Long Liquidation） | 舊業務平倉 | 看跌信號，反彈到 POC 做空 | N/A |
| Normal | 平衡 | 供需均衡 | 區間交易: VAH 做空、VAL 做多 | 50-60% 天數 |
| B-Double | 區間震蕩 | 雙峰分布 | 兩個 POC 之間交易 | N/A |

**注意**:
- P-shape 和 b-shape 代表「舊業務」（Old Business），需要「新業務」（New Business）才能延續突破
- 成功率數據尚未經過大規模回測驗證

### 使用形狀識別

```python
from tradepose_models.indicators.market_profile import (
    MarketProfileIndicator,
    create_daily_anchor,
    create_profile_shape_config
)

# 1. 創建形狀配置（使用預設值）
shape_config = create_profile_shape_config()

# 2. 或自訂參數（期貨市場）
shape_config = create_profile_shape_config(
    early_period_ratio=0.10,         # 期貨 IB 更小
    trend_ib_max_ratio=0.15,         # 更嚴格
    trend_monotonic_threshold=0.70,  # 更強單向性
    trend_imbalance_threshold=0.75   # 更強不平衡
)

# 3. 創建指標
mp = MarketProfileIndicator(
    anchor_config=create_daily_anchor(9, 15, 1),
    tick_size=0.25,
    shape_config=shape_config  # 啟用形狀識別
)

# 4. 應用後，profile_shape 欄位包含形狀類型
```

---

## 使用範例

### 範例 1: 基本 POC 支撐/阻力策略

```python
import polars as pl
from tradepose_models.indicators.market_profile import (
    MarketProfileIndicator,
    create_daily_anchor
)

# 1. 配置 Market Profile
anchor = create_daily_anchor(hour=9, minute=15, lookback_days=1)

mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,  # ES 期貨
    value_area_pct=0.7
)

# 2. 應用到 DataFrame（透過 strategy engine）
# 假設已經計算完成，結果在 "mp" 欄位

# 3. 展開 POC 欄位
df = df.with_column(
    pl.col("mp").struct.field("poc").alias("mp_poc")
)

# 4. 生成交易信號
df = df.with_column(
    pl.when(pl.col("close") > pl.col("mp_poc"))
      .then(pl.lit(1))   # 價格在 POC 上方 -> 多頭
      .otherwise(pl.lit(-1))  # 價格在 POC 下方 -> 空頭
      .alias("position")
)

# 5. 查看結果
print(df.select(["ts", "close", "mp_poc", "position"]))
```

### 範例 2: Value Area 突破策略

```python
# 1. 展開 VA 相關欄位
df = df.with_columns([
    pl.col("mp").struct.field("vah").alias("mp_vah"),
    pl.col("mp").struct.field("val").alias("mp_val"),
    pl.col("mp").struct.field("poc").alias("mp_poc"),
])

# 2. 判斷價格位置
df = df.with_column(
    pl.when(pl.col("close") > pl.col("mp_vah"))
      .then(pl.lit("above_va"))   # 突破 VAH -> 強勢
      .when(pl.col("close") < pl.col("mp_val"))
      .then(pl.lit("below_va"))   # 跌破 VAL -> 弱勢
      .otherwise(pl.lit("inside_va"))  # 在 VA 內 -> 盤整
      .alias("va_position")
)

# 3. 突破策略信號
df = df.with_column(
    pl.when(
        (pl.col("va_position") == "above_va") &
        (pl.col("va_position").shift(1) == "inside_va")
    ).then(pl.lit("LONG"))  # 突破 VAH -> 做多

    .when(
        (pl.col("va_position") == "below_va") &
        (pl.col("va_position").shift(1) == "inside_va")
    ).then(pl.lit("SHORT"))  # 跌破 VAL -> 做空

    .otherwise(pl.lit("NEUTRAL"))
    .alias("signal")
)

# 4. 篩選突破機會
breakouts = df.filter(pl.col("signal").is_in(["LONG", "SHORT"]))
print(breakouts.select(["ts", "close", "mp_vah", "mp_val", "signal"]))
```

### 範例 3: 使用 segment_id 計算距離 POC

```python
# 1. 使用 window 函數獲取 segment POC
df = df.with_column(
    pl.col("mp").struct.field("poc")
      .over([pl.col("mp").struct.field("segment_id")])
      .first()
      .alias("segment_poc")
)

# 2. 計算每根 K 線與 POC 的距離
df = df.with_columns([
    (pl.col("close") - pl.col("segment_poc")).alias("distance_from_poc"),
    ((pl.col("close") - pl.col("segment_poc")) / pl.col("segment_poc") * 100)
      .alias("distance_pct")
])

# 3. 篩選遠離 POC 的 K 線（可能反轉）
far_from_poc = df.filter(pl.col("distance_pct").abs() > 2.0)  # 距離 POC > 2%
print(far_from_poc.select(["ts", "close", "segment_poc", "distance_pct"]))
```

### 範例 4: 形狀基礎策略（實驗性）

```python
from tradepose_models.indicators.market_profile import create_profile_shape_config

# 1. 配置形狀識別
shape_config = create_profile_shape_config()

mp = MarketProfileIndicator(
    anchor_config=create_daily_anchor(9, 15, 1),
    tick_size=0.25,
    shape_config=shape_config  # 啟用形狀識別
)

# 2. 應用後展開形狀欄位
df = df.with_column(
    pl.col("mp").struct.field("profile_shape").alias("mp_shape")
)

# 3. 只在 Trend Day 使用趨勢跟隨策略
trend_days = df.filter(pl.col("mp_shape") == "trend_day")

trend_signals = trend_days.with_columns([
    pl.col("mp").struct.field("vah").alias("mp_vah"),
    pl.col("mp").struct.field("val").alias("mp_val"),
]).with_column(
    pl.when(pl.col("close") > pl.col("mp_vah"))
      .then(pl.lit("LONG"))   # 突破 VAH -> 順勢做多
      .when(pl.col("close") < pl.col("mp_val"))
      .then(pl.lit("SHORT"))  # 跌破 VAL -> 順勢做空
      .otherwise(pl.lit("NEUTRAL"))
      .alias("trend_signal")
)

print(trend_signals.select(["ts", "close", "mp_shape", "trend_signal"]))

# 4. 在 Normal 型使用區間策略
normal_days = df.filter(pl.col("mp_shape") == "normal")

range_signals = normal_days.with_columns([
    pl.col("mp").struct.field("vah").alias("mp_vah"),
    pl.col("mp").struct.field("val").alias("mp_val"),
]).with_column(
    pl.when(pl.col("close") > pl.col("mp_vah"))
      .then(pl.lit("SHORT"))  # 接近 VAH -> 做空
      .when(pl.col("close") < pl.col("mp_val"))
      .then(pl.lit("LONG"))   # 接近 VAL -> 做多
      .otherwise(pl.lit("NEUTRAL"))
      .alias("range_signal")
)

print(range_signals.select(["ts", "close", "mp_shape", "range_signal"]))
```

### 範例 5: 欄位選擇優化記憶體

```python
# 只需要 POC 和 VAH（減少記憶體使用）
# 注意: segment_id 會自動包含（用於 ffill），無需手動指定
mp = MarketProfileIndicator(
    anchor_config=create_daily_anchor(9, 15, 1),
    tick_size=0.25,
    fields=["poc", "vah"]  # segment_id 自動添加
)

# 應用後，Struct 包含 poc, vah, segment_id
df = df.with_columns([
    pl.col("mp").struct.field("poc").alias("mp_poc"),
    pl.col("mp").struct.field("vah").alias("mp_vah"),
    # val, value_area, tpo_distribution, profile_shape 不存在
])

# ⚠️ 記憶體提示:
# - 完整 Market Profile (7 個欄位): ~80 bytes/row
# - 只有 POC/VAH/VAL (3 個欄位): ~32 bytes/row
# - 只有 segment_id (1 個欄位): ~8 bytes/row
# - tpo_distribution 佔用最多記憶體（50-100 個價格層級）
```

### 範例 6: Initial Balance 突破策略

```python
from tradepose_models.indicators.market_profile import create_initial_balance_anchor

# 1. 配置 IB 窗口（09:00 ~ 10:00）
ib_anchor = create_initial_balance_anchor(
    start_hour=9,
    start_minute=0,
    end_hour=10,
    end_minute=0
)

mp = MarketProfileIndicator(
    anchor_config=ib_anchor,
    tick_size=0.25,
    fields=["vah", "val"]  # IB 突破只需要 VAH/VAL
)

# 2. 檢測突破
df = df.with_columns([
    pl.col("mp").struct.field("vah").alias("ib_high"),
    pl.col("mp").struct.field("val").alias("ib_low"),
]).with_column(
    pl.when(pl.col("close") > pl.col("ib_high"))
      .then(pl.lit("BREAKOUT_UP"))    # 突破 IB 上界
      .when(pl.col("close") < pl.col("ib_low"))
      .then(pl.lit("BREAKOUT_DOWN"))  # 突破 IB 下界
      .otherwise(pl.lit("INSIDE_IB"))
      .alias("ib_status")
)

# 3. 篩選突破信號
breakouts = df.filter(pl.col("ib_status").is_in(["BREAKOUT_UP", "BREAKOUT_DOWN"]))
```

### 範例 7: 每天都有 5 天窗口的 Market Profile

**問題**: 如果使用 `create_daily_anchor(hour=9, minute=15, lookback_days=5)`，會每 5 天才計算一次，無法實現「每天都有過去 5 天的數據」。

**解決方案**: 創建 5 個 weekly anchor 指標，錯開觸發日，然後合併結果。

```python
from tradepose_models.indicators.market_profile import create_weekly_anchor
from tradepose_models.enums import Weekday
import polars as pl

# 步驟 1: 在策略配置中定義 5 個 Market Profile 指標
strategy_config = {
    "indicators": [
        # 週一觸發（回溯 5 天）
        {
            "type": "MarketProfile",
            "anchor_config": create_weekly_anchor(Weekday.MON, 9, 15, lookback_days=5),
            "tick_size": 0.01,
            "fields": ["poc", "vah", "val"],
            "display_name": "mp_mon"
        },
        # 週二觸發
        {
            "type": "MarketProfile",
            "anchor_config": create_weekly_anchor(Weekday.TUE, 9, 15, lookback_days=5),
            "tick_size": 0.01,
            "fields": ["poc", "vah", "val"],
            "display_name": "mp_tue"
        },
        # 週三觸發
        {
            "type": "MarketProfile",
            "anchor_config": create_weekly_anchor(Weekday.WED, 9, 15, lookback_days=5),
            "tick_size": 0.01,
            "fields": ["poc", "vah", "val"],
            "display_name": "mp_wed"
        },
        # 週四觸發
        {
            "type": "MarketProfile",
            "anchor_config": create_weekly_anchor(Weekday.THU, 9, 15, lookback_days=5),
            "tick_size": 0.01,
            "fields": ["poc", "vah", "val"],
            "display_name": "mp_thu"
        },
        # 週五觸發
        {
            "type": "MarketProfile",
            "anchor_config": create_weekly_anchor(Weekday.FRI, 9, 15, lookback_days=5),
            "tick_size": 0.01,
            "fields": ["poc", "vah", "val"],
            "display_name": "mp_fri"
        },
    ]
}

# 步驟 2: 合併 5 個指標的結果（使用 coalesce 選擇非空值）
df = df.with_columns([
    # POC
    pl.coalesce([
        pl.col("mp_mon").struct.field("poc"),
        pl.col("mp_tue").struct.field("poc"),
        pl.col("mp_wed").struct.field("poc"),
        pl.col("mp_thu").struct.field("poc"),
        pl.col("mp_fri").struct.field("poc"),
    ]).alias("mp_5day_poc"),

    # VAH
    pl.coalesce([
        pl.col("mp_mon").struct.field("vah"),
        pl.col("mp_tue").struct.field("vah"),
        pl.col("mp_wed").struct.field("vah"),
        pl.col("mp_thu").struct.field("vah"),
        pl.col("mp_fri").struct.field("vah"),
    ]).alias("mp_5day_vah"),

    # VAL
    pl.coalesce([
        pl.col("mp_mon").struct.field("val"),
        pl.col("mp_tue").struct.field("val"),
        pl.col("mp_wed").struct.field("val"),
        pl.col("mp_thu").struct.field("val"),
        pl.col("mp_fri").struct.field("val"),
    ]).alias("mp_5day_val"),
])

# 步驟 3: 使用合併後的 Market Profile
# 現在 mp_5day_poc/vah/val 每天都有值（只要當週有 5 天交易數據）
df = df.with_column(
    pl.when(pl.col("close") > pl.col("mp_5day_vah"))
      .then(pl.lit("ABOVE_VA"))
      .when(pl.col("close") < pl.col("mp_5day_val"))
      .then(pl.lit("BELOW_VA"))
      .otherwise(pl.lit("INSIDE_VA"))
      .alias("position_vs_5day_va")
)

print(df.select(["ts", "close", "mp_5day_poc", "mp_5day_vah", "mp_5day_val", "position_vs_5day_va"]))
```

**結果說明**:
```
週一 09:15: mp_mon 觸發（包含 Wed上週 ~ Mon本週 數據）→ mp_5day_poc 有值
週二 09:15: mp_tue 觸發（包含 Thu上週 ~ Tue本週 數據）→ mp_5day_poc 有值
週三 09:15: mp_wed 觸發（包含 Fri上週 ~ Wed本週 數據）→ mp_5day_poc 有值
週四 09:15: mp_thu 觸發（包含 Mon本週 ~ Thu本週 數據）→ mp_5day_poc 有值
週五 09:15: mp_fri 觸發（包含 Tue本週 ~ Fri本週 數據）→ mp_5day_poc 有值
```

**為什麼這樣設計？**
- ✅ 避免數據重疊: 每個指標的 segment 不重疊，TPO 計算正確
- ✅ 每天都有值: 5 個指標輪流觸發，coalesce 確保每天都有一個非空值
- ✅ 計算效率: 每天只計算一次（而非每根 K 線都計算）

---

## 常見錯誤

### 錯誤 1: value_area_pct 使用整數

```python
# ❌ 錯誤
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,
    value_area_pct=70  # 應該是 0.7，不是 70
)
# 錯誤: ValidationError - value_area_pct must be between 0 and 1

# ✅ 正確
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,
    value_area_pct=0.7  # 小數格式
)
```

### 錯誤 2: tick_size 為 0 或負數

```python
# ❌ 錯誤
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.0  # tick_size 必須 > 0
)
# 錯誤: ValidationError - tick_size must be greater than 0

# ✅ 正確
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25  # 正數
)
```

### 錯誤 3: 誤解 lookback_days 的語義

```python
# ❌ lookback_days=3 ≠「每天都看過去 3 天」
# ✅ lookback_days=3 = 每 3 天計算一次（segments 不重疊）
# 詳見 [核心概念 > Anchor Segmentation](#anchor-segmentation-時間窗口分段)
```

### 錯誤 4: Anchor 配置驗證失敗

```python
# ❌ 錯誤: IB 窗口但 start >= end
anchor = create_initial_balance_anchor(
    start_hour=10, start_minute=0,
    end_hour=9, end_minute=0  # 10:00 > 09:00
)
# 錯誤: ValidationError - start_rule must be before end_rule

# ✅ 正確
anchor = create_initial_balance_anchor(
    start_hour=9, start_minute=0,
    end_hour=10, end_minute=0  # 09:00 < 10:00
)
```

### 錯誤 5: 結果全是 null

**可能原因**:
1. 數據時間範圍太短（無法找到回溯 anchor）
2. Anchor 時間不存在於數據中
3. `[start_rule, end_rule)` 窗口內沒有數據

**調試方法**:
```python
# 檢查 segmentation 結果
from tradepose_core import segment_by_anchor

df_test = segment_by_anchor(df, anchor_config)
segment_ids = df_test["segment_id"]

print(f"Total rows: {len(df_test)}")
print(f"Non-null segment_id: {len(df_test) - segment_ids.null_count()}")
print(f"Unique segments: {segment_ids.n_unique()}")

if segment_ids.null_count() == len(df_test):
    print("⚠️ Warning: No segments found!")
    print("Check:")
    print("  1. Anchor time exists in data")
    print("  2. Data time range is long enough")
    print("  3. lookback_days is appropriate")
```

### 錯誤 5: 期望 POC 只在 anchor 點出現

**現象**:
```
時間    segment_id  POC
09:00   6          16724.0  ← Anchor 點
09:15   7          16724.0  ← ❓ 為何相同？
09:30   8          null
```

**解釋**: 這是**正確行為**，不是 bug。

當基礎頻率 < Market Profile 計算頻率時，`asof_join` 會向前填充：

- **原因**: 09:15 時還沒有新的 30 分鐘 Market Profile
- **行為**: 使用最近可用的 Market Profile（09:00 的結果）
- **目的**: 確保策略使用「已知」的 Market Profile，避免 look-ahead bias

**如何只保留 anchor 點**:
```python
# 方法 1: 過濾 segment_id 變化點
df_anchor_only = df.filter(
    pl.col("mp").struct.field("segment_id") !=
    pl.col("mp").struct.field("segment_id").shift(1)
)

# 方法 2: 使用相同頻率
# 如果基礎頻率 = Market Profile 計算頻率，不會有 forward-fill
df_30min = resample_ohlcv(df, "30m")
df_mp = compute_market_profile(df_30min, anchor_config)
```

詳見 **ADR-050 Challenge 7** 了解完整解釋。

### 錯誤 6: 比較不同 tick_size 的形狀

```python
# ❌ 錯誤: 比較不同 tick_size 的 profile shape
df1 = compute_market_profile(..., tick_size=0.25)
df2 = compute_market_profile(..., tick_size=1.0)

# 形狀識別結果會不同！

# ✅ 正確: 使用相同 tick_size
df1 = compute_market_profile(..., tick_size=0.25)
df2 = compute_market_profile(..., tick_size=0.25)
```

**原因**: tick_size 影響 TPO 分布，進而影響形狀識別結果。

### 錯誤 7: 未驗證就使用形狀配置

```python
# ❌ 危險: 直接使用預設參數在生產環境
shape_config = create_profile_shape_config()
mp = MarketProfileIndicator(
    anchor_config=anchor,
    tick_size=0.25,
    shape_config=shape_config
)
# 部署到生產... 沒有回測驗證

# ✅ 正確: 先回測驗證
# 1. 收集歷史數據
# 2. 應用形狀識別
# 3. 記錄準確度
# 4. 調整參數
# 5. 驗證在測試集
# 6. 部署到生產
```

---

## 進階主題

### 跨頻率合併行為

當基礎數據頻率 < Market Profile 計算頻率時，會發生 **forward-fill**:

**範例**: 15 分鐘基礎數據 + 30 分鐘 Market Profile

```
┌─────────┬────────────┬──────┬─────────────────────────────┐
│ 時間    │ segment_id │ POC  │ 說明                        │
├─────────┼────────────┼──────┼─────────────────────────────┤
│ 09:00   │ 6          │ 16724│ ✅ Anchor 點                │
│ 09:15   │ 7          │ 16724│ ← 使用 09:00 的 MP（最新）   │
│ 09:30   │ 8          │ null │ ✅ 新 anchor（尚無數據）     │
│ 09:45   │ 8          │ null │ ← 使用 09:30 的 MP (null)   │
│ 10:00   │ 9          │ 16800│ ✅ 新 anchor                │
└─────────┴────────────┴──────┴─────────────────────────────┘
```

**為什麼這是正確的**:

1. **業務邏輯**: 策略在 09:15 做決策時，應該使用「最近可用」的 Market Profile
2. **避免 look-ahead bias**: 不能在 09:15 使用 09:30 的 MP（未來數據）
3. **與其他指標一致**: SuperTrend 等指標也有相同行為

**相關文件**: ADR-050 Challenge 7

### 使用 segment_id 的進階技巧

**技巧 1: 檢測 segment 邊界**
```python
# 標記 segment 開始
df = df.with_column(
    (pl.col("mp").struct.field("segment_id") !=
     pl.col("mp").struct.field("segment_id").shift(1))
    .alias("is_segment_start")
)

# 只在 segment 開始時執行操作
segment_starts = df.filter(pl.col("is_segment_start"))
```

**技巧 2: 計算 segment 內排名**
```python
# 每個 segment 內價格排名
df = df.with_column(
    pl.col("close")
      .rank()
      .over([pl.col("mp").struct.field("segment_id")])
      .alias("close_rank_in_segment")
)
```

**技巧 3: Segment 內標準化**
```python
# 計算 Z-score (segment 內標準化)
df = df.with_column(
    (
        (pl.col("close") - pl.col("close").mean()) /
        pl.col("close").std()
    ).over([pl.col("mp").struct.field("segment_id")])
    .alias("close_zscore")
)
```

### Performance 特性

**記憶體使用**:

| 配置 | 每行記憶體 | 說明 |
|------|-----------|------|
| 所有欄位 | ~80 bytes | 包含 7 個欄位 |
| 只 POC/VAH/VAL | ~32 bytes | 3 個 f64 欄位 |
| 只 segment_id | ~8 bytes | 1 個 u64 欄位 |

**計算時間** (10,000 bars):

| 操作 | 時間 | 說明 |
|------|------|------|
| TPO 計算 | ~100 ms | 核心計算 |
| 形狀識別 | ~7 ms | 可選功能 |
| 總計 | ~107 ms | 啟用形狀識別 |
| 總計 | ~100 ms | 不啟用形狀識別 |

**優化建議**:
1. ✅ 使用 `fields` 參數選擇需要的欄位
2. ✅ 不需要時不啟用 `shape_config`
3. ✅ 使用適當的 `tick_size`（不要太小）
4. ✅ 使用 `segment_id` 進行 window 操作而非 ffill 整個 struct

### 與 TradingView/Sierra Chart 對比

**共同點**:
- ✅ TPO 計算方式相同
- ✅ POC 定義相同
- ✅ Value Area 算法相同（70% TPO）

**差異**:
- ⚠️ 形狀識別: TradingView/Sierra Chart **不提供**自動形狀識別
- ⚠️ TPO Letters: 本實現不包含 TPO 字母標記（視覺化功能）
- ⚠️ Single Prints: TradingView 有，本實現未檢測

**驗證建議**:
```python
# 使用相同數據在 TradingView 和本系統計算
# 對比 POC, VAH, VAL 值
# 應該在誤差範圍內（<= 1 tick_size）
```

---

## 參考資料

### 內部文件

- **ADR-050**: Market Profile Stateful Implementation
  - 完整的 TPO 計算算法
  - 實現挑戰和解決方案
  - 使用指南

- **ADR-060**: Market Profile Shape Recognition 優化
  - 形狀識別算法詳細說明
  - 行業標準對比
  - 參數調整指南

- **KB-006**: Market Profile Shape Recognition 行業研究
  - 行業標準文獻回顧
  - 形狀類型定義
  - Single Prints 特徵研究

### 外部資源

- [TradingView TPO Indicator](https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/)
- [Sierra Chart TPO Charts](https://www.sierrachart.com/index.php?page=doc/StudiesReference/TimePriceOpportunityCharts.html)
- [Market Profile Guide - EMinimind](https://eminimind.com/the-ultimate-guide-to-market-profile/)
- [ATAS Platform - Market Profile](https://atas.net/volume-analysis-software/market-profile/)

### 學術文獻

- J. Peter Steidlmayer (1984). "Markets in Profile: Profiting from the Auction Process"
  - Market Profile 原創理論
  - Initial Balance 定義

- Dalton, Jones, Dalton (2007). "Mind Over Markets"
  - Market Profile 形狀分類
  - 交易策略應用

### 行業標準

- **Stock Market IB**: 前 2 個 30 分鐘時段 = 前 15% 時段（13 個時段/天）
- **Futures Market IB**: 前 2 個 30 分鐘時段 = 前 4% 時段（48 個時段/天）
- **Value Area**: 70% TPO 覆蓋率（業界共識）
- **Trend Day**: IB < 20% 總範圍（ATAS, EMinimind 標準）

---

## 版本資訊

**文件版本**: 1.0
**最後更新**: 2025-01-25
**對應實現版本**: tradepose-python 包
**對應 Rust 版本**: ADR-050 v2.1, ADR-060 v1.0

**變更歷史**:
- v1.0 (2025-01-25): 初始完整版本

---

## 聯繫與支援

如有問題或建議，請參考：
- 專案 README
- GitHub Issues
- 技術文件（ADR-050, ADR-060）

**重要提醒**:
- ⚠️ 形狀識別為實驗性功能，使用時請謹慎
- ✅ POC 和 Value Area 為穩定功能，可用於生產
- 📚 建議先閱讀 ADR-050 了解實現細節
