"""Unit tests for PersistMode enum.

Tests for:
- PersistMode (int enum, Rust compatible)
- ExportRequest with persist_mode field
"""

import pytest
from tradepose_models.enums import PersistMode
from tradepose_models.enums.export_type import ExportType
from tradepose_models.export import ExportRequest


class TestPersistMode:
    """Tests for PersistMode enum."""

    def test_values(self):
        """Test enum values match expected integers."""
        assert PersistMode.REDIS == 0
        assert PersistMode.PSQL == 1

    def test_is_int_enum(self):
        """Test that PersistMode is an integer enum."""
        assert isinstance(PersistMode.REDIS, int)
        assert isinstance(PersistMode.PSQL, int)

    def test_arithmetic(self):
        """Test integer arithmetic works."""
        assert PersistMode.REDIS + 1 == PersistMode.PSQL

    def test_from_int(self):
        """Test creating enum from integer value."""
        assert PersistMode(0) == PersistMode.REDIS
        assert PersistMode(1) == PersistMode.PSQL

    def test_invalid_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            PersistMode(99)

    def test_json_serialization(self):
        """Test JSON serialization produces integer value."""
        import json

        data = {"mode": PersistMode.PSQL}
        # IntEnum should serialize as integer
        serialized = json.dumps(data)
        assert '"mode": 1' in serialized or '"mode":1' in serialized

    def test_default_is_redis(self):
        """Test that default behavior is REDIS (value 0)."""
        assert PersistMode.REDIS.value == 0
        assert PersistMode(0) == PersistMode.REDIS


class TestExportRequestWithPersistMode:
    """Tests for ExportRequest model with persist_mode field."""

    def test_default_persist_mode(self):
        """Test that persist_mode defaults to REDIS."""
        request = ExportRequest(
            export_type=ExportType.BACKTEST_RESULTS,
            strategy_configs=[{"name": "test", "blueprints": []}],
        )
        assert request.persist_mode == PersistMode.REDIS

    def test_explicit_redis_mode(self):
        """Test setting persist_mode to REDIS explicitly."""
        request = ExportRequest(
            export_type=ExportType.BACKTEST_RESULTS,
            strategy_configs=[{"name": "test", "blueprints": []}],
            persist_mode=PersistMode.REDIS,
        )
        assert request.persist_mode == PersistMode.REDIS

    def test_psql_mode(self):
        """Test setting persist_mode to PSQL."""
        request = ExportRequest(
            export_type=ExportType.BACKTEST_RESULTS,
            strategy_configs=[{"name": "test", "blueprints": []}],
            persist_mode=PersistMode.PSQL,
        )
        assert request.persist_mode == PersistMode.PSQL

    def test_persist_mode_from_int(self):
        """Test persist_mode can be set from integer."""
        request = ExportRequest(
            export_type=ExportType.BACKTEST_RESULTS,
            strategy_configs=[{"name": "test", "blueprints": []}],
            persist_mode=1,  # type: ignore - testing int coercion
        )
        assert request.persist_mode == PersistMode.PSQL

    def test_persist_mode_in_model_dump(self):
        """Test persist_mode appears correctly in model dump."""
        request = ExportRequest(
            export_type=ExportType.BACKTEST_RESULTS,
            strategy_configs=[{"name": "test", "blueprints": []}],
            persist_mode=PersistMode.PSQL,
        )
        data = request.model_dump()
        # Should serialize as integer
        assert data["persist_mode"] == 1 or data["persist_mode"] == PersistMode.PSQL

    def test_backward_compatibility(self):
        """Test that requests without persist_mode still work (defaults to REDIS)."""
        # Simulate a request from an older client that doesn't send persist_mode
        request_data = {
            "export_type": ExportType.BACKTEST_RESULTS,
            "strategy_configs": [{"name": "test", "blueprints": []}],
        }
        request = ExportRequest.model_validate(request_data)
        assert request.persist_mode == PersistMode.REDIS
