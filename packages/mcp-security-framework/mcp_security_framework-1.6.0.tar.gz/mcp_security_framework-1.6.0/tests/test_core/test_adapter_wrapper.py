"""
Security Adapter Wrapper Tests

This module provides comprehensive tests for the SecurityAdapterWrapper class,
which wraps legacy security adapters to provide SecurityAdapter interface.

Test Coverage:
- SecurityAdapterWrapper initialization
- Automatic method detection
- validate_operation method wrapping
- check_permissions method wrapping
- audit_operation method wrapping
- Support for adapters without context parameter
- Fallback mechanisms
- Error handling

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import pytest

from mcp_security_framework.core.adapter_wrapper import SecurityAdapterWrapper
from mcp_security_framework.core.security_adapter import OperationType
from mcp_security_framework.schemas.operation_context import OperationContext


class TestSecurityAdapterWrapper:
    """Test suite for SecurityAdapterWrapper class."""

    def test_wrapper_initialization_with_explicit_methods(self):
        """Test wrapper initialization with explicitly provided methods."""

        class KubernetesOperation(OperationType):
            """Kubernetes operation types."""

            CREATE_POD = "k8s:create_pod"
            DELETE_POD = "k8s:delete_pod"

        class LegacyKubernetesAdapter:
            """Legacy Kubernetes adapter."""

            def validate_k8s_operation(
                self, operation: str, user_roles: list, params: dict
            ) -> tuple:
                return True, ""

            def check_k8s_permissions(
                self, user_roles: list, required_permissions: list
            ) -> tuple:
                return True, []

            def audit_k8s_operation(
                self, operation: str, user_roles: list, params: dict, status: str
            ) -> None:
                pass

        legacy_adapter = LegacyKubernetesAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=KubernetesOperation,
            validate_method=legacy_adapter.validate_k8s_operation,
            check_permissions_method=legacy_adapter.check_k8s_permissions,
            audit_method=legacy_adapter.audit_k8s_operation,
        )

        assert wrapper.legacy_adapter == legacy_adapter
        assert wrapper.operation_type == KubernetesOperation

    def test_wrapper_initialization_with_auto_detection(self):
        """Test wrapper initialization with automatic method detection."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter with auto-detectable methods."""

            def validate_test_operation(
                self, operation: str, user_roles: list, params: dict
            ) -> tuple:
                return True, ""

            def check_test_permissions(
                self, user_roles: list, required_permissions: list
            ) -> tuple:
                return True, []

            def audit_test_operation(
                self, operation: str, user_roles: list, params: dict, status: str
            ) -> None:
                pass

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        assert wrapper.legacy_adapter == legacy_adapter
        assert wrapper.operation_type == TestOperation

    def test_wrapper_initialization_with_none_adapter(self):
        """Test wrapper initialization with None adapter raises ValueError."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        with pytest.raises(ValueError, match="legacy_adapter cannot be None"):
            SecurityAdapterWrapper(
                legacy_adapter=None,
                operation_type=TestOperation,
            )

    def test_wrapper_initialization_with_invalid_operation_type(self):
        """Test wrapper initialization with invalid operation type."""

        class LegacyAdapter:
            """Legacy adapter."""

            pass

        with pytest.raises(
            ValueError, match="operation_type must be a subclass of OperationType"
        ):
            SecurityAdapterWrapper(
                legacy_adapter=LegacyAdapter(),
                operation_type=str,  # Not a subclass of OperationType
            )

    def test_wrapper_validate_operation_with_context(self):
        """Test validate_operation with context support."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter with context support."""

            def validate_test_operation(
                self, operation: str, user_roles: list, params: dict, context
            ) -> tuple:
                if context and context.user_id == "blocked":
                    return False, "User blocked"
                return True, ""

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Test with context - allowed user
        context_allowed = OperationContext(user_id="allowed", user_roles=["admin"])
        is_valid, error = wrapper.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            params={},
            context=context_allowed,
        )
        assert is_valid is True

        # Test with context - blocked user
        context_blocked = OperationContext(user_id="blocked", user_roles=["admin"])
        is_valid, error = wrapper.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            params={},
            context=context_blocked,
        )
        assert is_valid is False
        assert error == "User blocked"

    def test_wrapper_validate_operation_without_context(self):
        """Test validate_operation without context parameter."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter without context support."""

            def validate_test_operation(
                self, operation: str, user_roles: list, params: dict
            ) -> tuple:
                return True, ""

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Should work without context
        is_valid, error = wrapper.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            params={},
            context=None,
        )
        assert is_valid is True

    def test_wrapper_validate_operation_fallback(self):
        """Test validate_operation fallback when method not found."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter without validation method."""

            pass

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Should return default (True, "") when method not found
        is_valid, error = wrapper.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
        )
        assert is_valid is True
        assert error == ""

    def test_wrapper_check_permissions(self):
        """Test check_permissions method."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter with permission checking."""

            def check_test_permissions(
                self, user_roles: list, required_permissions: list
            ) -> tuple:
                denied = [p for p in required_permissions if p not in user_roles]
                return len(denied) == 0, denied

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Test with all permissions
        has_perms, denied = wrapper.check_permissions(
            user_roles=["admin", "user"],
            required_permissions=["admin"],
        )
        assert has_perms is True
        assert denied == []

        # Test with missing permissions
        has_perms, denied = wrapper.check_permissions(
            user_roles=["user"],
            required_permissions=["admin", "user"],
        )
        assert has_perms is False
        assert "admin" in denied

    def test_wrapper_check_permissions_fallback(self):
        """Test check_permissions fallback when method not found."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter without permission checking method."""

            pass

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Should use default fallback logic
        has_perms, denied = wrapper.check_permissions(
            user_roles=["admin"],
            required_permissions=["admin", "user"],
        )
        assert has_perms is False
        assert "user" in denied

    def test_wrapper_audit_operation(self):
        """Test audit_operation method."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        audit_calls = []

        class LegacyAdapter:
            """Legacy adapter with audit method."""

            def audit_test_operation(
                self, operation: str, user_roles: list, params: dict, status: str
            ) -> None:
                audit_calls.append((operation, user_roles, params, status))

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Test audit operation
        wrapper.audit_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            params={"key": "value"},
            status="success",
        )

        assert len(audit_calls) == 1
        assert audit_calls[0][0] == "test:operation"
        assert audit_calls[0][1] == ["admin"]
        assert audit_calls[0][2] == {"key": "value"}
        assert audit_calls[0][3] == "success"

    def test_wrapper_audit_operation_with_context(self):
        """Test audit_operation with context support."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        audit_calls = []

        class LegacyAdapter:
            """Legacy adapter with context support."""

            def audit_test_operation(
                self,
                operation: str,
                user_roles: list,
                params: dict,
                status: str,
                context,
            ) -> None:
                audit_calls.append((operation, user_roles, params, status, context))

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        context = OperationContext(user_id="user123", user_roles=["admin"])
        wrapper.audit_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            params={},
            status="success",
            context=context,
        )

        assert len(audit_calls) == 1
        assert audit_calls[0][4] == context

    def test_wrapper_audit_operation_fallback(self):
        """Test audit_operation fallback when method not found."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter without audit method."""

            pass

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Should not raise, just skip audit
        wrapper.audit_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            status="success",
        )

    def test_wrapper_operation_type_property(self):
        """Test operation_type property."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter."""

            pass

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        assert wrapper.operation_type == TestOperation

    def test_wrapper_error_handling_in_validate_operation(self):
        """Test error handling in validate_operation."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter that raises exception."""

            def validate_test_operation(
                self, operation: str, user_roles: list, params: dict
            ) -> tuple:
                raise ValueError("Validation error")

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
        )

        # Should catch exception and return error
        is_valid, error = wrapper.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
        )
        assert is_valid is False
        assert "Validation error" in error

    def test_wrapper_error_handling_in_check_permissions(self):
        """Test error handling in check_permissions."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class LegacyAdapter:
            """Legacy adapter that raises exception."""

            def check_test_permissions(
                self, user_roles: list, required_permissions: list
            ) -> tuple:
                raise ValueError("Permission check error")

        legacy_adapter = LegacyAdapter()
        wrapper = SecurityAdapterWrapper(
            legacy_adapter=legacy_adapter,
            operation_type=TestOperation,
            check_permissions_method=legacy_adapter.check_test_permissions,
        )

        # Should catch exception and return error
        has_perms, denied = wrapper.check_permissions(
            user_roles=["admin"],
            required_permissions=["admin"],
        )
        assert has_perms is False
        assert len(denied) > 0
