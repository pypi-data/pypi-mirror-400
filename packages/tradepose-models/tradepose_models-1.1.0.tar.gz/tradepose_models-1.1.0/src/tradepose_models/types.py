"""Common type definitions (通用類型定義).

This module contains type aliases and custom types used across the platform
to improve code clarity and type safety.

這個模組包含平台上使用的類型別名和自定義類型，以提高代碼清晰度和類型安全性。

Example usage:
    from tradepose_models.types import UserId, APIKeyHash, Timestamp

    def get_user(user_id: UserId) -> dict:
        # Type hints make the code more readable
        return {"id": user_id}

    def verify_key(key_hash: APIKeyHash) -> bool:
        # Custom types document intent
        return check_hash(key_hash)
"""


# Placeholder for shared type definitions
# Types will be added here as needed
# 共用類型定義將根據需要添加到這裡

# Example structure:
# UserId = NewType('UserId', str)
# """User identifier type (用戶標識符類型)."""
#
# APIKeyHash = NewType('APIKeyHash', str)
# """Hashed API key type (API 密鑰哈希類型)."""
#
# Timestamp = NewType('Timestamp', datetime)
# """Timestamp type for consistency (時間戳類型以保持一致性)."""

__all__ = []
