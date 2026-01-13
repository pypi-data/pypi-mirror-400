"""
Base Pydantic models with standardized configuration.

This module provides a base model that all TradePose models should inherit from.
It includes standardized serialization rules, particularly for enum handling.
"""

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Base model with standardized configuration for all TradePose models.

    Configuration:
    - use_enum_values=False: Enums serialize to their NAME (uppercase string) instead of value
      Example: TaskStatus.PENDING → "PENDING" (not 0)
    - validate_assignment=True: Validate field assignments after model creation
    - arbitrary_types_allowed=True: Allow custom types (e.g., Redis connections)

    Internal Storage vs API Response:
    - PostgreSQL: Stores enums as SMALLINT (0, 1, 2, 3)
    - Python Code: Uses int Enum (TaskStatus.PENDING = 0)
    - Redis: Stores as integer in JSON ({"status": 0})
    - API JSON Output: Serializes as uppercase string ({"status": "PENDING"})

    This ensures:
    1. Efficient storage (integers in database)
    2. Type safety in code (enum objects)
    3. Readable API responses (uppercase strings)
    4. Backward compatibility (string format maintained)

    Example:
        ```python
        from tradepose_models.base import BaseModel
        from tradepose_models.enums import TaskStatus

        class MyModel(BaseModel):
            status: TaskStatus

        model = MyModel(status=TaskStatus.PENDING)
        print(model.model_dump())  # {'status': TaskStatus.PENDING}
        print(model.model_dump_json())  # '{"status":"PENDING"}'
        ```
    """

    model_config = ConfigDict(
        # Serialize enums to name (uppercase string) for API responses
        use_enum_values=False,
        # Validate assignments after model creation
        validate_assignment=True,
        # Allow arbitrary types (e.g., Redis connections, asyncpg pools)
        arbitrary_types_allowed=True,
        # Use attribute docstrings for schema descriptions
        use_attribute_docstrings=True,
    )
