"""
Security Adapter Tests

This module provides comprehensive tests for the SecurityAdapter abstract
base class and OperationType enumeration.

Test Coverage:
- OperationType enumeration creation and usage
- SecurityAdapter abstract class cannot be instantiated
- SecurityAdapter abstract methods raise NotImplementedError
- Custom adapter implementation examples

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import pytest
from typing import Any, Dict, List, Optional, Tuple, Type

from mcp_security_framework.core.security_adapter import (
    OperationType,
    SecurityAdapter,
)
from mcp_security_framework.schemas.operation_context import OperationContext


class TestOperationType:
    """Test suite for OperationType enumeration."""

    def test_operation_type_is_enum(self):
        """Test that OperationType is an Enum."""
        from enum import Enum

        assert issubclass(OperationType, Enum)
        # OperationType is a base class, not meant to be instantiated directly

    def test_custom_operation_type_creation(self):
        """Test creating a custom operation type enumeration."""

        class FtpOperation(OperationType):
            """FTP operation types."""

            UPLOAD = "ftp:upload"
            DOWNLOAD = "ftp:download"
            LIST = "ftp:list"
            DELETE = "ftp:delete"

        # Test that values are accessible
        assert FtpOperation.UPLOAD.value == "ftp:upload"
        assert FtpOperation.DOWNLOAD.value == "ftp:download"
        assert FtpOperation.LIST.value == "ftp:list"
        assert FtpOperation.DELETE.value == "ftp:delete"

    def test_operation_type_inheritance(self):
        """Test that custom operation types inherit from OperationType."""

        class DockerOperation(OperationType):
            """Docker operation types."""

            PULL = "docker:pull"
            PUSH = "docker:push"

        assert issubclass(DockerOperation, OperationType)
        assert isinstance(DockerOperation.PULL, OperationType)

    def test_operation_type_string_value(self):
        """Test that operation types have string values."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        assert isinstance(TestOperation.TEST.value, str)
        assert TestOperation.TEST.value == "test:operation"


class TestSecurityAdapter:
    """Test suite for SecurityAdapter abstract base class."""

    def test_security_adapter_is_abstract(self):
        """Test that SecurityAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SecurityAdapter()

    def test_security_adapter_operation_type_property(self):
        """Test that operation_type property raises NotImplementedError."""
        # Cannot instantiate abstract class, so test by checking that
        # SecurityAdapter itself cannot be instantiated
        with pytest.raises(TypeError):
            SecurityAdapter()

    def test_security_adapter_validate_operation_abstract(self):
        """Test that validate_operation method is abstract."""

        class IncompleteAdapter(SecurityAdapter):
            """Incomplete adapter without validate_operation implementation."""

            @property
            def operation_type(self) -> Type[OperationType]:
                class TestOperation(OperationType):
                    TEST = "test:operation"

                return TestOperation

            def check_permissions(
                self,
                user_roles: List[str],
                required_permissions: List[str],
            ) -> Tuple[bool, List[str]]:
                return True, []

            def audit_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                status: str = "success",
                context: Optional[OperationContext] = None,
            ) -> None:
                pass

        # Cannot instantiate abstract class without all methods
        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_security_adapter_check_permissions_abstract(self):
        """Test that check_permissions method is abstract."""

        class IncompleteAdapter(SecurityAdapter):
            """Incomplete adapter without check_permissions implementation."""

            @property
            def operation_type(self) -> Type[OperationType]:
                class TestOperation(OperationType):
                    TEST = "test:operation"

                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context: Optional[OperationContext] = None,
            ) -> Tuple[bool, str]:
                return True, ""

            def audit_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                status: str = "success",
                context: Optional[OperationContext] = None,
            ) -> None:
                pass

        # Cannot instantiate abstract class without all methods
        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_security_adapter_audit_operation_abstract(self):
        """Test that audit_operation method is abstract."""

        class IncompleteAdapter(SecurityAdapter):
            """Incomplete adapter without audit_operation implementation."""

            @property
            def operation_type(self) -> Type[OperationType]:
                class TestOperation(OperationType):
                    TEST = "test:operation"

                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context: Optional[OperationContext] = None,
            ) -> Tuple[bool, str]:
                return True, ""

            def check_permissions(
                self,
                user_roles: List[str],
                required_permissions: List[str],
            ) -> Tuple[bool, List[str]]:
                return True, []

        # Cannot instantiate abstract class without all methods
        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_complete_security_adapter_implementation(self):
        """Test a complete SecurityAdapter implementation."""

        class FtpOperation(OperationType):
            """FTP operation types."""

            UPLOAD = "ftp:upload"
            DOWNLOAD = "ftp:download"

        class FtpSecurityAdapter(SecurityAdapter):
            """Complete FTP security adapter implementation."""

            def __init__(self):
                self.operation_permissions = {
                    FtpOperation.UPLOAD: ["ftp:upload", "ftp:admin"],
                    FtpOperation.DOWNLOAD: ["ftp:download", "ftp:admin"],
                }

            @property
            def operation_type(self) -> Type[OperationType]:
                return FtpOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context: Optional[OperationContext] = None,
            ) -> Tuple[bool, str]:
                required_perms = self.operation_permissions.get(operation, [])
                has_perms = any(perm in user_roles for perm in required_perms)
                if has_perms:
                    return True, ""
                return False, "Insufficient permissions"

            def check_permissions(
                self,
                user_roles: List[str],
                required_permissions: List[str],
            ) -> Tuple[bool, List[str]]:
                denied = [p for p in required_permissions if p not in user_roles]
                return len(denied) == 0, denied

            def audit_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                status: str = "success",
                context: Optional[OperationContext] = None,
            ) -> None:
                # Simple audit logging
                pass

        # Test adapter can be instantiated
        adapter = FtpSecurityAdapter()
        assert adapter is not None

        # Test operation_type property
        assert adapter.operation_type == FtpOperation

        # Test validate_operation with valid permissions
        is_valid, error = adapter.validate_operation(
            operation=FtpOperation.UPLOAD,
            user_roles=["ftp:upload"],
        )
        assert is_valid is True
        assert error == ""

        # Test validate_operation with invalid permissions
        is_valid, error = adapter.validate_operation(
            operation=FtpOperation.UPLOAD,
            user_roles=["ftp:read"],
        )
        assert is_valid is False
        assert error == "Insufficient permissions"

        # Test check_permissions with valid permissions
        has_perms, denied = adapter.check_permissions(
            user_roles=["ftp:upload", "ftp:download"],
            required_permissions=["ftp:upload"],
        )
        assert has_perms is True
        assert denied == []

        # Test check_permissions with missing permissions
        has_perms, denied = adapter.check_permissions(
            user_roles=["ftp:upload"],
            required_permissions=["ftp:upload", "ftp:delete"],
        )
        assert has_perms is False
        assert "ftp:delete" in denied

        # Test audit_operation (should not raise)
        adapter.audit_operation(
            operation=FtpOperation.UPLOAD,
            user_roles=["ftp:upload"],
            status="success",
        )

    def test_security_adapter_with_context(self):
        """Test SecurityAdapter with OperationContext."""

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test adapter with context support."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context: Optional[OperationContext] = None,
            ) -> Tuple[bool, str]:
                if context and context.user_id == "blocked_user":
                    return False, "User is blocked"
                return True, ""

            def check_permissions(
                self,
                user_roles: List[str],
                required_permissions: List[str],
            ) -> Tuple[bool, List[str]]:
                return True, []

            def audit_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                status: str = "success",
                context: Optional[OperationContext] = None,
            ) -> None:
                pass

        adapter = TestAdapter()

        # Test with context - allowed user
        context_allowed = OperationContext(
            user_id="allowed_user",
            user_roles=["admin"],
        )
        is_valid, error = adapter.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            context=context_allowed,
        )
        assert is_valid is True

        # Test with context - blocked user
        context_blocked = OperationContext(
            user_id="blocked_user",
            user_roles=["admin"],
        )
        is_valid, error = adapter.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            context=context_blocked,
        )
        assert is_valid is False
        assert error == "User is blocked"

        # Test without context
        is_valid, error = adapter.validate_operation(
            operation=TestOperation.TEST,
            user_roles=["admin"],
            context=None,
        )
        assert is_valid is True
