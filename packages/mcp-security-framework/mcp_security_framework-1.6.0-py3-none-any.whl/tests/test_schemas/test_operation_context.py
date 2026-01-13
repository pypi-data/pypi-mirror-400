"""
Operation Context Tests

This module provides comprehensive tests for the OperationContext dataclass.

Test Coverage:
- OperationContext creation with all fields
- OperationContext default values
- Serialization to dictionary (to_dict)
- Deserialization from dictionary (from_dict)
- Timestamp handling and conversion
- Metadata handling
- Edge cases and error handling

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timezone

from mcp_security_framework.schemas.operation_context import OperationContext


class TestOperationContext:
    """Test suite for OperationContext dataclass."""

    def test_operation_context_creation_with_all_fields(self):
        """Test creating OperationContext with all fields."""
        timestamp = datetime.now(timezone.utc)
        context = OperationContext(
            user_id="user123",
            user_roles=["admin", "user"],
            request_id="req456",
            parent_operation="batch_upload",
            metadata={"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"},
            timestamp=timestamp,
        )

        assert context.user_id == "user123"
        assert context.user_roles == ["admin", "user"]
        assert context.request_id == "req456"
        assert context.parent_operation == "batch_upload"
        assert context.metadata == {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        assert context.timestamp == timestamp

    def test_operation_context_default_values(self):
        """Test OperationContext with default values."""
        context = OperationContext()

        assert context.user_id is None
        assert context.user_roles == []
        assert context.request_id is None
        assert context.parent_operation is None
        assert context.metadata == {}
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_minimal_creation(self):
        """Test creating OperationContext with minimal fields."""
        context = OperationContext(
            user_id="user123",
            user_roles=["admin"],
        )

        assert context.user_id == "user123"
        assert context.user_roles == ["admin"]
        assert context.request_id is None
        assert context.parent_operation is None
        assert context.metadata == {}
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_to_dict(self):
        """Test serialization to dictionary."""
        timestamp = datetime(2024, 12, 19, 10, 30, 0, tzinfo=timezone.utc)
        context = OperationContext(
            user_id="user123",
            user_roles=["admin", "user"],
            request_id="req456",
            parent_operation="batch_upload",
            metadata={"ip": "192.168.1.1"},
            timestamp=timestamp,
        )

        context_dict = context.to_dict()

        assert context_dict["user_id"] == "user123"
        assert context_dict["user_roles"] == ["admin", "user"]
        assert context_dict["request_id"] == "req456"
        assert context_dict["parent_operation"] == "batch_upload"
        assert context_dict["metadata"] == {"ip": "192.168.1.1"}
        assert context_dict["timestamp"] == "2024-12-19T10:30:00+00:00"

    def test_operation_context_to_dict_with_none_timestamp(self):
        """Test to_dict with None timestamp."""
        context = OperationContext(
            user_id="user123",
            user_roles=["admin"],
        )
        context.timestamp = None

        context_dict = context.to_dict()

        assert context_dict["timestamp"] is None

    def test_operation_context_from_dict(self):
        """Test deserialization from dictionary."""
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin", "user"],
            "request_id": "req456",
            "parent_operation": "batch_upload",
            "metadata": {"ip": "192.168.1.1"},
            "timestamp": "2024-12-19T10:30:00+00:00",
        }

        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert context.user_roles == ["admin", "user"]
        assert context.request_id == "req456"
        assert context.parent_operation == "batch_upload"
        assert context.metadata == {"ip": "192.168.1.1"}
        assert isinstance(context.timestamp, datetime)
        assert context.timestamp.isoformat() == "2024-12-19T10:30:00+00:00"

    def test_operation_context_from_dict_with_datetime(self):
        """Test from_dict with datetime object instead of string."""
        timestamp = datetime(2024, 12, 19, 10, 30, 0, tzinfo=timezone.utc)
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin"],
            "timestamp": timestamp,
        }

        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert context.user_roles == ["admin"]
        assert context.timestamp == timestamp

    def test_operation_context_from_dict_without_timestamp(self):
        """Test from_dict without timestamp field."""
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin"],
        }

        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert context.user_roles == ["admin"]
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_from_dict_with_none_timestamp(self):
        """Test from_dict with None timestamp."""
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin"],
            "timestamp": None,
        }

        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_from_dict_with_invalid_timestamp(self):
        """Test from_dict with invalid timestamp string."""
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin"],
            "timestamp": "invalid-timestamp",
        }

        # Should not raise, but use current time as fallback
        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_from_dict_with_z_suffix(self):
        """Test from_dict with timestamp ending in Z."""
        context_dict = {
            "user_id": "user123",
            "user_roles": ["admin"],
            "timestamp": "2024-12-19T10:30:00Z",
        }

        context = OperationContext.from_dict(context_dict)

        assert isinstance(context.timestamp, datetime)
        # Check that Z was converted to +00:00
        assert context.timestamp.tzinfo == timezone.utc

    def test_operation_context_round_trip(self):
        """Test serialization and deserialization round trip."""
        original_context = OperationContext(
            user_id="user123",
            user_roles=["admin", "user"],
            request_id="req456",
            parent_operation="batch_upload",
            metadata={"ip": "192.168.1.1", "session_id": "sess789"},
            timestamp=datetime.now(timezone.utc),
        )

        # Serialize
        context_dict = original_context.to_dict()

        # Deserialize
        restored_context = OperationContext.from_dict(context_dict)

        assert restored_context.user_id == original_context.user_id
        assert restored_context.user_roles == original_context.user_roles
        assert restored_context.request_id == original_context.request_id
        assert restored_context.parent_operation == original_context.parent_operation
        assert restored_context.metadata == original_context.metadata
        # Timestamp might differ slightly due to serialization, so check it's close
        time_diff = abs(
            (restored_context.timestamp - original_context.timestamp).total_seconds()
        )
        assert time_diff < 1  # Within 1 second

    def test_operation_context_empty_metadata(self):
        """Test OperationContext with empty metadata."""
        context = OperationContext(
            user_id="user123",
            user_roles=["admin"],
            metadata={},
        )

        assert context.metadata == {}
        context_dict = context.to_dict()
        assert context_dict["metadata"] == {}

    def test_operation_context_complex_metadata(self):
        """Test OperationContext with complex metadata."""
        context = OperationContext(
            user_id="user123",
            user_roles=["admin"],
            metadata={
                "ip": "192.168.1.1",
                "user_agent": "Mozilla/5.0",
                "session_id": "sess789",
                "nested": {"key": "value"},
                "list": [1, 2, 3],
            },
        )

        assert context.metadata["ip"] == "192.168.1.1"
        assert context.metadata["nested"]["key"] == "value"
        assert context.metadata["list"] == [1, 2, 3]

        context_dict = context.to_dict()
        assert context_dict["metadata"]["nested"]["key"] == "value"

    def test_operation_context_empty_user_roles(self):
        """Test OperationContext with empty user_roles."""
        context = OperationContext(
            user_id="user123",
            user_roles=[],
        )

        assert context.user_roles == []
        context_dict = context.to_dict()
        assert context_dict["user_roles"] == []

    def test_operation_context_from_dict_missing_fields(self):
        """Test from_dict with missing optional fields."""
        context_dict = {
            "user_id": "user123",
        }

        context = OperationContext.from_dict(context_dict)

        assert context.user_id == "user123"
        assert context.user_roles == []
        assert context.request_id is None
        assert context.parent_operation is None
        assert context.metadata == {}
        assert isinstance(context.timestamp, datetime)

    def test_operation_context_from_dict_empty_dict(self):
        """Test from_dict with empty dictionary."""
        context = OperationContext.from_dict({})

        assert context.user_id is None
        assert context.user_roles == []
        assert context.request_id is None
        assert context.parent_operation is None
        assert context.metadata == {}
        assert isinstance(context.timestamp, datetime)
