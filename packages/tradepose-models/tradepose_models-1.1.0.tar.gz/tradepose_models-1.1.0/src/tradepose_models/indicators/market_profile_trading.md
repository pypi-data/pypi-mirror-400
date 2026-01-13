# Market Profile 策略指南

> **其他文件**: 如需了解 Market Profile 的 API 使用與程式配置，請參閱 [開發者指南](./market_profile_developer.md)

## 目錄

- [概述](#概述)
- [核心概念](#核心概念)
- [日型分類 (Day Types)](#日型分類-day-types)
- [市場循環理論 (Market Cycle Theory)](#市場循環理論-market-cycle-theory)
- [Profile 形狀 (Profile Shapes)](#profile-形狀-profile-shapes)
- [形狀識別與交易策略](#形狀識別與交易策略)
- [參考資料](#參考資料)

---

## 概述

Market Profile 是一種基於 **TPO (Time Price Opportunity)** 的價格分布分析工具，由 J. Peter Steidlmayer 於 1980 年代開發。它透過識別市場參與者的行為特徵和關鍵價格水平，幫助交易者理解市場結構。

### 核心價值

- **POC (Point of Control)**: 識別市場最認同的價格水平（最強的支撐/阻力）
- **Value Area**: 定義 70% TPO 集中的「公平價值區間」
- **Profile Shape**: 識別市場狀態（趨勢、反轉、區間）

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

**問題**: 如果想要「每天都有過去 5 天的 Market Profile」，使用 daily anchor 無法實現（因為不重疊）。

**解決方案**: 創建 5 個 weekly anchor 指標，錯開觸發日。

```python
from tradepose_models.enums import Weekday

# 創建 5 個指標，分別在週一~週五觸發，每個回溯 5 天
indicators = [
    MarketProfileIndicator(
        anchor_config=create_weekly_anchor(Weekday.MON, 9, 15, lookback_days=5),
        tick_size=0.01
    ),
    MarketProfileIndicator(
        anchor_config=create_weekly_anchor(Weekday.TUE, 9, 15, lookback_days=5),
        tick_size=0.01
    ),
    MarketProfileIndicator(
        anchor_config=create_weekly_anchor(Weekday.WED, 9, 15, lookback_days=5),
        tick_size=0.01
    ),
    MarketProfileIndicator(
        anchor_config=create_weekly_anchor(Weekday.THU, 9, 15, lookback_days=5),
        tick_size=0.01
    ),
    MarketProfileIndicator(
        anchor_config=create_weekly_anchor(Weekday.FRI, 9, 15, lookback_days=5),
        tick_size=0.01
    ),
]

# 結果:
# - 週一 09:15: 第 1 個指標觸發（Wed 上週 ~ Mon 本週，5 天數據）
# - 週二 09:15: 第 2 個指標觸發（Thu 上週 ~ Tue 本週，5 天數據）
# - 週三 09:15: 第 3 個指標觸發（Fri 上週 ~ Wed 本週，5 天數據）
# - 週四 09:15: 第 4 個指標觸發（Mon 本週 ~ Thu 本週，5 天數據）
# - 週五 09:15: 第 5 個指標觸發（Tue 本週 ~ Fri 本週，5 天數據）

# 合併 5 個結果到同一個 DataFrame，使用 coalesce 選擇非空值
df = df.with_columns([
    pl.coalesce([
        pl.col("mp_mon"),
        pl.col("mp_tue"),
        pl.col("mp_wed"),
        pl.col("mp_thu"),
        pl.col("mp_fri"),
    ]).alias("mp_5day")
])
```

**為什麼需要這樣設計？**
- 避免數據重疊: 如果允許重疊，TPO 計算會重複計算同一根 K 線，結果不正確
- 計算效率: 只在需要時計算，避免每根 K 線都計算導致性能問題
- 語義清晰: 每個 segment 代表獨立的時間窗口，不會混淆

---

## 日型分類 (Day Types)

### 概述

Market Profile 日型分類基於 **Initial Balance (IB)** 和 **Range Extension** 的關係，幫助交易者識別當日市場結構並調整策略。

**Initial Balance (IB)** 定義：交易日第一小時（前兩個 30 分鐘時段）的價格範圍，為當日交易設定基準。

**核心邏輯**：
- **寬 IB** → 傾向於 Range-Bound Day（區間日）
- **窄 IB** → 傾向於 Trending Day（趨勢日）
- **Range Extension** 的方向和幅度決定具體日型

### 非趨勢日型（約 80-90% 的交易日）

#### 1. Normal Day（常規日）

**定義**：85%+ 的日波幅在 Initial Balance 內形成。

**特徵**：
- **IB 寬度**：寬（Wide IB）
- **Range Extension**：極少或無
- **出現頻率**：~2.43%（罕見，名稱具誤導性）
- **市場含義**：短線交易者主導，買賣雙方早盤即達成價值共識

**視覺特徵**：
```
價格    TPO 分布
105     A
104     AB
103     ABCDEF    ← IB 範圍內集中
102     ABCDEFGH  ← POC
101     ABCDEF
100     AB
99      A
```

**交易策略**：區間交易，在 IB High 做空、IB Low 做多。

---

#### 2. Normal Variation Day（常規變異日）

**定義**：IB 被單向突破，但 Range Extension < 2 倍 IB。

**特徵**：
- **IB 寬度**：中等
- **Range Extension**：有，但 < 2x IB
- **出現頻率**：~30-40%（高）
- **市場含義**：大時間框架交易者（OTF）在 IB 建立後進場，單向推動

**視覺特徵**：
```
價格    TPO 分布
108     EF        ← Range Extension
107     DEF
106     CDEF
105     BCDEF
104     ABCDE     ← IB High
103     ABCD      ← IB 範圍
102     ABC       ← IB Low
101     AB
```

**交易策略**：跟隨 Range Extension 方向，在突破 IB 後進場。

---

#### 3. Neutral Day（中立日）

**定義**：IB High 和 IB Low 都被突破，收盤在區間中間。

**特徵**：
- **IB 寬度**：中等
- **Range Extension**：雙向都有
- **出現頻率**：~30.21%
- **市場含義**：買賣雙方都活躍但無勝者，雙向拉鋸

**視覺特徵**：
```
價格    TPO 分布
107     EF        ← 上方 Range Extension
106     DEF
105     CDEF      ← IB High
104     ABCDEFGH  ← IB 範圍（收盤區域）
103     ABCDEF    ← IB Low
102     CDE
101     D         ← 下方 Range Extension
```

**交易策略**：預期反轉；當極端被觸及時考慮逆向交易。

---

#### 4. Neutral Extreme Day（中立極端日）

**定義**：類似 Neutral Day，但收盤偏向一端。

**特徵**：
- **IB 寬度**：中等
- **Range Extension**：雙向都有
- **市場含義**：收盤方向那一方獲勝，預示次日延續

**與 Neutral Day 區別**：收盤位置。Neutral Day 收盤在中間，Neutral Extreme 收盤在極端。

**交易策略**：預期次日按收盤方向延續。

---

#### 5. Non-Trend Day（無趨勢日）

**定義**：窄波幅、寬 Profile、無明確方向。

**特徵**：
- **IB 寬度**：窄
- **Range Extension**：無或極少
- **出現頻率**：常見於重大新聞前
- **市場含義**：市場等待新信息，交易活動低迷

**視覺特徵**：
```
價格    TPO 分布
102     ABCDEFGHIJ  ← 扁平寬厚
101     ABCDEFGHIJ  ← 所有時段都在窄區間
100     ABCDEFGHIJ
```

**交易策略**：避免交易，等待突破或新信息。通常「預示大行情」。

---

### 趨勢日型（約 5-10% 的交易日）

#### 6. Trend Day（趨勢日）

**定義**：持續單向移動，開盤在一端、收盤在另一端。

**特徵**：
- **IB 寬度**：窄（Narrow IB）
- **Range Extension**：大，持續延伸
- **出現頻率**：~5-10%
- **市場含義**：大時間框架交易者從開盤即主導，強勢定向市場
- **識別特徵**：One-Timeframing（連續更高高/更低低）

**視覺特徵**：
```
價格    TPO 分布
110     IJ        ← 收盤區域
109     HIJ
108     GHI
107     FGH       ← 細長垂直
106     EFG
105     DEF
104     CDE
103     BCD
102     ABC
101     AB        ← IB（窄）
100     A         ← 開盤區域
```

**識別條件**：
- IB < 20% 日波幅
- 每層 TPO ≤ 5 個
- 連續 30 分鐘時段維持同一方向（One-Timeframing）

**交易策略**：
- 順勢交易，避免逆勢
- 在 11:30 前識別出 Trend Day 後跟隨方向
- 不要在 Trend Day 做區間交易

---

#### 7. Double Distribution Day（雙分佈日）

**定義**：形成兩個獨立的價值區域，中間由 Single Prints 分隔。

**特徵**：
- **IB 寬度**：窄
- **Range Extension**：大
- **出現頻率**：與 Trend Day 合計 ~9.54%
- **市場含義**：新聞/事件驅動價值突然轉移

**視覺特徵**：
```
價格    TPO 分布
112     GHIJ      ← 第二分佈區（新價值區）
111     GHIJ
110     GHI
109     G         ← Single Prints（分隔區）
108     F
107     EF
106     DEF       ← 第一分佈區（原價值區）
105     CDEF
104     BCDE
103     ABCD      ← IB
102     ABC
```

**形成過程**：
1. 開盤形成第一個分佈區（Initial Balance 附近）
2. 新聞或大單驅動價格快速轉移
3. 在新價格區域形成第二個分佈區
4. 兩個分佈區之間由 Single Prints 分隔

**交易策略**：
- 在狹窄 IB 突破後進場
- Single Prints 區域可作為支撐/阻力

---

### 日型統計頻率表

| 日型 | 出現頻率 | IB 寬度 | Range Extension | 市場狀態 |
|------|---------|--------|-----------------|----------|
| Normal Day | ~2.43% | 寬 | 無/極少 | 平衡 |
| Normal Variation | ~30-40% | 中等 | 有，<2x IB | 輕度不平衡 |
| Trend Day | ~5-10% | 窄 | 大，持續 | 強烈不平衡 |
| Double Distribution | ~4-5% | 窄 | 大 | 價值轉移 |
| Neutral Day | ~30.21% | 中等 | 雙向 | 雙向拉鋸 |
| Neutral Extreme | (含在 Neutral) | 中等 | 雙向 | 一方獲勝 |
| Non-Trend Day | 常見 | 窄 | 無 | 等待信息 |

**關鍵統計**：
- 平衡日（非趨勢）：~80-90%
- 趨勢日：~5-10%
- Normal + Trend + Normal Variation 合計：~81.52%

---

## 市場循環理論 (Market Cycle Theory)

### Balance vs Imbalance（平衡與不平衡）

市場永遠處於以下兩種狀態之一：

#### 平衡市場（Balanced Market）

**定義**：價格在特定範圍內輪動，買賣雙方對「公平價值」達成共識。

**特徵**：
- 鐘型 Profile 分佈
- 價格在 Value Area 內震盪
- 低波動，雙向拍賣
- 對應日型：Normal Day、Neutral Day

**視覺化**：
```
價格在 VA 內輪動：
       ┌─────────────────┐
       │    Value Area   │
       │  ← Price ←→ →   │
       └─────────────────┘
```

#### 不平衡市場（Imbalanced Market）

**定義**：買方或賣方主導，價格單向移動尋找新價值區域。

**特徵**：
- 細長垂直 Profile
- 單側 Range Extension
- 高波動，單向拍賣
- 對應日型：Trend Day、Double Distribution Day

**視覺化**：
```
價格搜尋新價值：
       ┌─────────────────┐
       │  Old Value Area │
       └────────┬────────┘
                │ Price Discovery
                ▼
       ┌─────────────────┐
       │  New Value Area │
       └─────────────────┘
```

---

### AMT（Auction Market Theory）循環

市場在平衡與不平衡之間不斷循環：

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Balance (平衡)                                        │
│   └─ 水平發展，買賣雙方價值共識                         │
│   └─ Profile: 鐘型                                      │
│   └─ Day Type: Normal, Neutral                          │
│                                                         │
│         │                                               │
│         │ 新信息 / 催化劑                               │
│         ▼                                               │
│                                                         │
│   Imbalance (不平衡)                                    │
│   └─ 垂直發展，價格搜尋新價值                           │
│   └─ Profile: 細長                                      │
│   └─ Day Type: Trend, Double Distribution               │
│                                                         │
│         │                                               │
│         │ 發現新價值 / 動能耗盡                         │
│         ▼                                               │
│                                                         │
│   New Balance (新平衡)                                  │
│   └─ 在新價格區域建立共識                               │
│   └─ 循環重複                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Steidlmayer 四步循環

J. Peter Steidlmayer 將市場運動分為四個階段：

#### 1. Trend Phase（趨勢階段）
- **特徵**：垂直發展，價格失衡
- **Profile**：細長，單向延伸
- **日型**：Trend Day、Double Distribution Day

#### 2. Stop Phase（停止階段）
- **特徵**：反向交易者出現，趨勢被阻止
- **Profile**：開始形成上下限
- **信號**：P-shape 或 b-shape 形成

#### 3. Sideways Phase（橫盤階段）
- **特徵**：水平發展，在新範圍內輪動
- **Profile**：鐘型分佈
- **日型**：Normal Day、Neutral Day

#### 4. Transition Phase（過渡階段）
- **特徵**：價格離開範圍，產生新失衡
- **可能結果**：趨勢延續或反轉
- **信號**：Range Extension 突破

---

### Wyckoff 四階段循環（宏觀視角）

Market Profile 形狀與 Wyckoff 市場循環的對應關係：

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   1. Accumulation (積累)                                 │
│      └─ 大戶在低位吸籌                                   │
│      └─ Profile: P-shape (空頭回補)                      │
│      └─ 信號: 看漲                                       │
│                     │                                    │
│                     ▼                                    │
│   2. Markup (上漲)                                       │
│      └─ 需求超過供給，價格上升                           │
│      └─ Profile: Trend Day (Up)                          │
│      └─ 特徵: 垂直發展                                   │
│                     │                                    │
│                     ▼                                    │
│   3. Distribution (分配)                                 │
│      └─ 大戶在高位派發                                   │
│      └─ Profile: b-shape (多頭平倉)                      │
│      └─ 信號: 看跌                                       │
│                     │                                    │
│                     ▼                                    │
│   4. Markdown (下跌)                                     │
│      └─ 供給超過需求，價格下降                           │
│      └─ Profile: Trend Day (Down)                        │
│      └─ 特徵: 垂直發展                                   │
│                     │                                    │
│                     ▼                                    │
│         [循環重複回到 Accumulation]                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 日型與循環的對應關係

| 循環階段 | Profile Shape | 日型 | 市場行為 |
|----------|---------------|------|----------|
| Accumulation | P-shape | Non-Trend → Normal Variation | 低位吸籌，準備上漲 |
| Markup | Trend (Up) | Trend Day | 強勢上漲 |
| Distribution | b-shape | Non-Trend → Normal Variation | 高位派發，準備下跌 |
| Markdown | Trend (Down) | Trend Day | 強勢下跌 |
| Consolidation | D-shape | Normal, Neutral | 橫盤整理 |

**關鍵洞察**：
- **P-shape 和 b-shape 是「舊業務」（Old Business）**：既有部位平倉
- **需要「新業務」（New Business）才能延續為 Trend Day**：新參與者進場
- **如果沒有新業務**：市場回歸 Balance（Normal/Neutral Day）

---

## Profile 形狀 (Profile Shapes)

### 四種基本形狀

#### D-Shape（D型）- 平衡

**視覺**：對稱鐘型，像字母 "D"

```
價格    TPO
105     AB
104     ABCD
103     ABCDEF    ← POC
102     ABCD
101     AB
```

**含義**：
- 平衡市場，價值被接受
- 買賣雙方力量均衡
- 對應日型：Normal Day

**交易策略**：等待突破，或在 VA 內做區間交易。

---

#### P-Shape（P型）- 空頭回補

**視覺**：下窄上寬，像字母 "P"

```
價格    TPO
105     DEFGH     ← bulge（寬）
104     DEFGH
103     CDE
102     BC        ← stem（窄）
101     AB
100     A
```

**含義**：
- Short Covering（空頭回補）
- Old Business（舊業務）
- 開盤在低位，早盤上漲，高位盤整

**信號**：看漲

---

#### b-Shape（b型）- 多頭平倉

**視覺**：上窄下寬，像字母 "b"

```
價格    TPO
105     A
104     AB        ← stem（窄）
103     BC
102     CDE
101     DEFGH     ← bulge（寬）
100     DEFGH
```

**含義**：
- Long Liquidation（多頭平倉）
- Old Business（舊業務）
- 開盤在高位，早盤下跌，低位盤整

**信號**：看跌

---

#### B-Shape（B型）- 雙分佈

**視覺**：兩個分佈區域，中間凹陷，像大寫 "B"

```
價格    TPO
108     GHIJ      ← 上方分佈
107     GHIJ
106     GH        ← 凹陷區（Single Prints）
105     F
104     CDEF      ← 下方分佈
103     BCDE
102     ABC
```

**含義**：
- Double Distribution（雙分佈）
- 價值突然轉移
- 對應日型：Double Distribution Day

**交易策略**：在兩個 POC 之間操作，Single Prints 區域作為支撐/阻力。

---

### 形狀與市場狀態對照

| 形狀 | 市場狀態 | 形成機制 | 交易信號 |
|------|----------|----------|----------|
| D-Shape | 平衡 | 供需均衡 | 等待突破 |
| P-Shape | 空頭回補 | 舊業務平倉 | 看漲 |
| b-Shape | 多頭平倉 | 舊業務平倉 | 看跌 |
| B-Shape | 價值轉移 | 新聞/事件驅動 | 區間操作 |

---

## 形狀識別與交易策略

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

### Profile Shape 類型詳解

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

**識別條件**（三者必須同時滿足）:

1. **小 Initial Balance (IB)**: IB < 20% 總範圍
2. **單向移動**: 60%+ 時段維持同一方向
3. **TPO 不平衡**: 70%+ TPO 集中在早期或晚期

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

#### 6. Undefined (無法分類)

不符合任何上述形狀的 profile。

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
