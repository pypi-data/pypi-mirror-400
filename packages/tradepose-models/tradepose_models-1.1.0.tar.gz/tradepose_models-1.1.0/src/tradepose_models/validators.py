"""Shared validation utilities (共用驗證工具).

This module contains reusable Pydantic validators and validation functions
that are used across multiple packages.

這個模組包含跨多個包使用的可重用 Pydantic 驗證器和驗證函數。

Example usage:
    from pydantic import BaseModel, field_validator
    from tradepose_models.validators import validate_api_key_format

    class APIKeyModel(BaseModel):
        key: str

        @field_validator('key')
        @classmethod
        def validate_key(cls, v):
            return validate_api_key_format(v)
"""

# Placeholder for shared validators
# Validators will be added here as needed
# 共用驗證器將根據需要添加到這裡

# Example structure:
# def validate_api_key_format(value: str) -> str:
#     """Validate API key format."""
#     if not value.startswith('sk_'):
#         raise ValueError("API key must start with 'sk_'")
#     return value

__all__ = []
