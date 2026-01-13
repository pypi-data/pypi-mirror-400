# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-21

### Added

- `BatchOHLCVDownloadEvent.end_time`: 結束時間欄位（None = 自動填為 now + 30 天）
- `BatchOHLCVDownloadEvent.force_full`: 強制完整下載欄位（忽略 DB 現有資料）

### Fixed

- 使用 timezone-aware `datetime.now(timezone.utc)` 取代已棄用的 `datetime.utcnow()`

## [1.0.0] - 2025-11-29

### Breaking Changes

- First stable release with breaking changes from 0.1.x series

### Added

- Stable API for all models

## [0.1.0] - 2025-11-29 (deprecated)

### Added

- Initial release
- Pydantic models for strategy configuration (StrategyConfig, Blueprint, Trigger)
- Enums: Freq, IndicatorType, OrderStrategy, TradeDirection, TrendType
- Export models: ExportRequest, ExportResponse
- Billing models: DetailedUsageResponse
- Auth models: API key management (ApiKeyResponse, CreateApiKeyResponse)
- Indicator models and specifications
- Polars schema definitions for trades and performance data
