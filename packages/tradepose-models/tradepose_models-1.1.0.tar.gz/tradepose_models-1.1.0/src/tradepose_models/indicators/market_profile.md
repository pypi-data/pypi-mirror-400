# Market Profile 指標文件

Market Profile 是一種基於 **TPO (Time Price Opportunity)** 的價格分布分析工具，由 J. Peter Steidlmayer 於 1980 年代開發。

本文件已拆分為兩份，針對不同讀者群：

---

## 文件索引

### [開發者指南](./market_profile_developer.md)

適合需要使用 Market Profile API 的**程式開發者**。

**內容包含**:
- API 參考與配置（MarketProfileIndicator、Helper Functions）
- 輸出欄位說明（POC、VAH、VAL、tpo_distribution、segment_id）
- 程式碼範例（7 個完整範例）
- 常見錯誤與除錯方法
- 進階主題（跨頻率合併、Performance 特性）

---

### [策略指南](./market_profile_trading.md)

適合需要理解 Market Profile 交易理論的**策略開發者**。

**內容包含**:
- 日型分類（7 種日型：Normal、Trend、Neutral 等）
- 市場循環理論（AMT、Wyckoff、Steidlmayer 四步循環）
- Profile 形狀（D/P/b/B 型）與交易含義
- 形狀識別與交易策略對照表
- 行業標準與學術文獻參考

---

## 快速選擇

| 你的問題 | 建議閱讀 |
|---------|---------|
| 如何配置 MarketProfileIndicator？ | [開發者指南](./market_profile_developer.md#api-參考) |
| tick_size 應該設多少？ | [開發者指南](./market_profile_developer.md#tick_size-必填) |
| 什麼是 Trend Day？ | [策略指南](./market_profile_trading.md#6-trend-day趨勢日) |
| P-shape 代表什麼？ | [策略指南](./market_profile_trading.md#p-shape-p型-空頭回補) |
| 如何使用 segment_id 做 Window 操作？ | [開發者指南](./market_profile_developer.md#使用-segment_id-進行-window-操作) |
| 市場循環理論是什麼？ | [策略指南](./market_profile_trading.md#市場循環理論-market-cycle-theory) |

---

## 相關資源

### 內部文件
- **ADR-050**: Market Profile Stateful Implementation
- **ADR-060**: Market Profile Shape Recognition 優化
- **KB-006**: Market Profile Shape Recognition 行業研究

### 外部資源
- [TradingView TPO Indicator](https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/)
- [Sierra Chart TPO Charts](https://www.sierrachart.com/index.php?page=doc/StudiesReference/TimePriceOpportunityCharts.html)
- [Market Profile Guide - EMinimind](https://eminimind.com/the-ultimate-guide-to-market-profile/)
