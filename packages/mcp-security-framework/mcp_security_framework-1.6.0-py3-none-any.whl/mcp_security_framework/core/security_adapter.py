"""
Security Adapter Module

This module provides the base classes and types for creating extensible
security adapters in the MCP Security Framework. It defines the abstract
interface for security adapters and operation type enumerations.

Key Features:
- Base OperationType enumeration for defining operation types
- Abstract SecurityAdapter class for custom security adapters
- Support for operation validation and permission checking
- Integration with audit logging and operation context

Classes:
    OperationType: Base enumeration for operation types
    SecurityAdapter: Abstract base class for security adapters

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type

from abc import ABC, abstractmethod

from ..schemas.operation_context import OperationContext


class OperationType(str, Enum):
    """
    Base Operation Type Enumeration

    This enumeration serves as the base class for all operation type
    enumerations used in security adapters. Custom adapters should create
    their own enumeration classes that inherit from this base class.

    Operation types are used to categorize and identify different types
    of operations that can be validated by security adapters. Each
    operation type is represented as a string value following the pattern:
    "{service}:{operation}" (e.g., "ftp:upload", "docker:pull").

    Usage:
        To create a custom operation type enumeration, inherit from
        OperationType and define operation values:

        >>> class FtpOperation(OperationType):
        ...     UPLOAD = "ftp:upload"
        ...     DOWNLOAD = "ftp:download"
        ...     LIST = "ftp:list"
        ...     DELETE = "ftp:delete"

        >>> # Usage in adapter
        >>> operation = FtpOperation.UPLOAD
        >>> print(operation.value)  # "ftp:upload"

    Note:
        This is a base enumeration class. It should not be instantiated
        directly. Instead, create specific operation type enumerations
        for each service or domain that inherits from this class.

    Example:
        >>> from mcp_security_framework.core.security_adapter import OperationType
        >>>
        >>> class DockerOperation(OperationType):
        ...     PULL = "docker:pull"
        ...     PUSH = "docker:push"
        ...     RUN = "docker:run"
        ...     STOP = "docker:stop"
        >>>
        >>> # Use in security adapter
        >>> operation = DockerOperation.PULL
        >>> print(operation.value)  # "docker:pull"
    """

    pass


class SecurityAdapter(ABC):
    """
    Abstract Security Adapter Base Class

    This abstract base class defines the interface that all security
    adapters must implement. Security adapters provide extensible
    security validation for different types of operations (e.g., FTP,
    Docker, Kubernetes).

    Security adapters are responsible for:
    - Validating operations based on user roles and permissions
    - Checking user permissions for specific operations
    - Auditing operations for security compliance
    - Supporting operation context for complex workflows

    Subclasses must implement all abstract methods to provide complete
    security adapter functionality. The adapter should be registered
    with SecurityManager to be used in the security framework.

    Attributes:
        operation_type (Type[OperationType]): Type of operation enumeration
            that this adapter handles. Must be a subclass of OperationType.

    Methods:
        validate_operation: Validate if a user can perform an operation
        check_permissions: Check if user has required permissions
        audit_operation: Audit an operation for security compliance

    Example:
        >>> from mcp_security_framework.core.security_adapter import (
        ...     SecurityAdapter, OperationType
        ... )
        >>> from mcp_security_framework.schemas.operation_context import (
        ...     OperationContext
        ... )
        >>>
        >>> class FtpOperation(OperationType):
        ...     UPLOAD = "ftp:upload"
        ...     DOWNLOAD = "ftp:download"
        >>>
        >>> class FtpSecurityAdapter(SecurityAdapter):
        ...     @property
        ...     def operation_type(self) -> Type[OperationType]:
        ...         return FtpOperation
        ...
        ...     def validate_operation(
        ...         self,
        ...         operation: FtpOperation,
        ...         user_roles: List[str],
        ...         params: Optional[Dict[str, Any]] = None,
        ...         context: Optional[OperationContext] = None
        ...     ) -> Tuple[bool, str]:
        ...         # Implementation here
        ...         return True, ""
        ...
        ...     def check_permissions(
        ...         self,
        ...         user_roles: List[str],
        ...         required_permissions: List[str]
        ...     ) -> Tuple[bool, List[str]]:
        ...         # Implementation here
        ...         return True, []
        ...
        ...     def audit_operation(
        ...         self,
        ...         operation: FtpOperation,
        ...         user_roles: List[str],
        ...         params: Optional[Dict[str, Any]] = None,
        ...         status: str = "success",
        ...         context: Optional[OperationContext] = None
        ...     ) -> None:
        ...         # Implementation here
        ...         pass

    Note:
        This is an abstract base class. It cannot be instantiated directly.
        Subclasses must implement all abstract methods. The adapter should
        be registered with SecurityManager using register_adapter() method.

    See Also:
        OperationType: Base enumeration for operation types
        OperationContext: Context dataclass for operation information
        SecurityManager: Main security manager for adapter registration
    """

    @property
    @abstractmethod
    def operation_type(self) -> Type[OperationType]:
        """
        Get the operation type enumeration class for this adapter.

        This property returns the type of operation enumeration that this
        adapter handles. Each adapter should handle a specific set of
        operation types defined by an enumeration class that inherits
        from OperationType.

        Returns:
            Type[OperationType]: The operation type enumeration class
                that this adapter handles. Must be a subclass of
                OperationType.

        Example:
            >>> class FtpOperation(OperationType):
            ...     UPLOAD = "ftp:upload"
            ...
            >>> class FtpSecurityAdapter(SecurityAdapter):
            ...     @property
            ...     def operation_type(self) -> Type[OperationType]:
            ...         return FtpOperation
        """
        raise NotImplementedError("Subclasses must implement operation_type property")

    @abstractmethod
    def validate_operation(
        self,
        operation: OperationType,
        user_roles: List[str],
        params: Optional[Dict[str, Any]] = None,
        context: Optional[OperationContext] = None,
    ) -> Tuple[bool, str]:
        """
        Validate if a user can perform an operation.

        This method validates whether a user with the given roles can
        perform the specified operation. It checks permissions, validates
        operation parameters, and considers operation context if provided.

        Args:
            operation (OperationType): The operation to validate. Must be
                an instance of the operation type enumeration handled by
                this adapter.
            user_roles (List[str]): List of roles assigned to the user
                performing the operation. Empty list if user has no roles.
            params (Optional[Dict[str, Any]]): Optional parameters for
                the operation. Can include operation-specific data like
                resource paths, file sizes, or other metadata. Defaults
                to None if no parameters are provided.
            context (Optional[OperationContext]): Optional operation context
                containing additional information about the operation,
                request, and user. Can include request ID, parent operation,
                and metadata. Defaults to None if no context is available.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if the operation is allowed, False otherwise
                - str: Error message if operation is not allowed, empty
                    string if operation is allowed

        Raises:
            ValueError: If operation is not a valid operation type for
                this adapter.
            TypeError: If operation type is incompatible.

        Example:
            >>> adapter = FtpSecurityAdapter()
            >>> is_valid, error = adapter.validate_operation(
            ...     operation=FtpOperation.UPLOAD,
            ...     user_roles=["ftp:upload", "admin"],
            ...     params={"remote_path": "/files/test.txt"},
            ...     context=operation_context
            ... )
            >>> if not is_valid:
            ...     print(f"Operation denied: {error}")
        """
        raise NotImplementedError("Subclasses must implement validate_operation method")

    @abstractmethod
    def check_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Check if user has required permissions.

        This method checks whether a user with the given roles has all
        required permissions. It returns a list of denied permissions
        if the user is missing any required permissions.

        Args:
            user_roles (List[str]): List of roles assigned to the user.
                Empty list if user has no roles.
            required_permissions (List[str]): List of permissions required
                for the operation. Empty list if no permissions are required.

        Returns:
            Tuple[bool, List[str]]: A tuple containing:
                - bool: True if user has all required permissions, False
                    otherwise
                - List[str]: List of denied permissions (permissions that
                    the user is missing). Empty list if user has all
                    required permissions

        Example:
            >>> adapter = FtpSecurityAdapter()
            >>> has_perms, denied = adapter.check_permissions(
            ...     user_roles=["ftp:upload", "admin"],
            ...     required_permissions=["ftp:upload", "ftp:delete"]
            ... )
            >>> if not has_perms:
            ...     print(f"Missing permissions: {denied}")
        """
        raise NotImplementedError("Subclasses must implement check_permissions method")

    @abstractmethod
    def audit_operation(
        self,
        operation: OperationType,
        user_roles: List[str],
        params: Optional[Dict[str, Any]] = None,
        status: str = "success",
        context: Optional[OperationContext] = None,
    ) -> None:
        """
        Audit an operation for security compliance.

        This method logs an operation for security auditing purposes.
        It records operation details, user information, operation status,
        and context for compliance and security monitoring.

        Args:
            operation (OperationType): The operation that was performed.
                Must be an instance of the operation type enumeration
                handled by this adapter.
            user_roles (List[str]): List of roles assigned to the user
                who performed the operation. Empty list if user has no roles.
            params (Optional[Dict[str, Any]]): Optional parameters for
                the operation. Can include operation-specific data like
                resource paths, file sizes, or other metadata. Defaults
                to None if no parameters are provided.
            status (str): Status of the operation. Common values include
                "success", "failed", "denied", "pending". Defaults to
                "success" if not specified.
            context (Optional[OperationContext]): Optional operation context
                containing additional information about the operation,
                request, and user. Can include request ID, parent operation,
                and metadata. Defaults to None if no context is available.

        Example:
            >>> adapter = FtpSecurityAdapter()
            >>> adapter.audit_operation(
            ...     operation=FtpOperation.UPLOAD,
            ...     user_roles=["ftp:upload"],
            ...     params={"remote_path": "/files/test.txt", "file_size": 1024},
            ...     status="success",
            ...     context=operation_context
            ... )

        Note:
            This method should not raise exceptions. Any errors during
            auditing should be handled internally and logged appropriately.
        """
        raise NotImplementedError("Subclasses must implement audit_operation method")
