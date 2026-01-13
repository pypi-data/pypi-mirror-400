"""TradePose shared models package.

This package contains Pydantic models, enums, schemas, and types shared
across the TradePose platform, including gateway, client SDK, and other
components.

Organization:
    - base: Base Pydantic model with standardized configuration
    - enums: Shared enumerations
    - events: Order and trading event models
    - schemas: Shared data schemas (Polars)
    - auth: Authentication and API key models
    - billing: Billing, subscription, and usage models
    - broker: Broker account and binding models
    - export: Export task and result models
    - gateway: Gateway API response models
    - indicators: Indicator specifications
    - strategy: Strategy configuration models
    - trading: Trading-related models (orders, positions, engagements)
    - utils: Utility modules (rate conversion, etc.)
    - validators: Shared validation utilities
    - types: Common type definitions

Example usage:
    from tradepose_models.base import BaseModel
    from tradepose_models.enums import TaskStatus, ExportType
    from tradepose_models.auth import APIKeyCreate
    from tradepose_models.billing import PlanResponse
    from tradepose_models.export import ExportTaskResponse
    from tradepose_models.utils import RateConverter, get_default_converter
"""

from .base import BaseModel
from .utils import DEFAULT_RATES, RateConverter, get_default_converter

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "BaseModel",
    "DEFAULT_RATES",
    "RateConverter",
    "get_default_converter",
]
