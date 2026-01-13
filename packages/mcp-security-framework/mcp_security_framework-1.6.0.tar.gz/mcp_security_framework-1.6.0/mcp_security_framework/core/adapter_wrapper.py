"""
Security Adapter Wrapper Module

This module provides a wrapper class for legacy security adapters that
do not conform to the SecurityAdapter interface. It automatically detects
and wraps legacy adapter methods, providing backward compatibility.

Key Features:
- Automatic method detection for legacy adapters
- Fallback mechanisms for missing methods
- Support for adapters without context parameter
- Seamless integration with SecurityAdapter interface

Classes:
    SecurityAdapterWrapper: Wrapper class for legacy security adapters

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .security_adapter import OperationType, SecurityAdapter
from ..schemas.operation_context import OperationContext


class SecurityAdapterWrapper(SecurityAdapter):
    """
    Security Adapter Wrapper Class

    This class provides a wrapper for legacy security adapters that do
    not conform to the SecurityAdapter interface. It automatically detects
    and wraps legacy adapter methods, providing backward compatibility
    with existing adapter implementations.

    The wrapper supports:
    - Automatic method detection using common naming patterns
    - Fallback mechanisms for missing methods
    - Support for adapters without context parameter
    - Logging warnings when methods are not found

    Attributes:
        legacy_adapter (Any): The legacy adapter instance to wrap.
            Can be any object with methods for validation, permission
            checking, and auditing.
        operation_type (Type[OperationType]): Type of operation enumeration
            that this adapter handles. Must be a subclass of OperationType.
        _validate_method (Optional[Callable]): Method for operation validation.
            Automatically detected if not provided.
        _check_permissions_method (Optional[Callable]): Method for permission
            checking. Automatically detected if not provided.
        _audit_method (Optional[Callable]): Method for operation auditing.
            Automatically detected if not provided.
        logger (Logger): Logger instance for wrapper operations.

    Example:
        >>> from mcp_security_framework.core.adapter_wrapper import (
        ...     SecurityAdapterWrapper
        ... )
        >>> from mcp_security_framework.core.security_adapter import OperationType
        >>>
        >>> class LegacyAdapter:
        ...     def validate_k8s_operation(self, operation, user_roles, params):
        ...         return True, ""
        ...     def check_k8s_permissions(self, user_roles, required_permissions):
        ...         return True, []
        ...     def audit_k8s_operation(self, operation, user_roles, params, status):
        ...         pass
        >>>
        >>> legacy_adapter = LegacyAdapter()
        >>> wrapper = SecurityAdapterWrapper(
        ...     legacy_adapter=legacy_adapter,
        ...     operation_type=KubernetesOperation,
        ...     validate_method=legacy_adapter.validate_k8s_operation,
        ...     check_permissions_method=legacy_adapter.check_k8s_permissions,
        ...     audit_method=legacy_adapter.audit_k8s_operation
        ... )
        >>>
        >>> # Use wrapper as SecurityAdapter
        >>> is_valid, error = wrapper.validate_operation(
        ...     operation=KubernetesOperation.CREATE_POD,
        ...     user_roles=["k8s:admin"],
        ...     params={"namespace": "default"}
        ... )

    Note:
        The wrapper automatically detects methods if they are not explicitly
        provided. It searches for methods with common naming patterns like
        "validate_*", "check_*_permissions", and "audit_*".
    """

    def __init__(
        self,
        legacy_adapter: Any,
        operation_type: Type[OperationType],
        validate_method: Optional[Callable] = None,
        check_permissions_method: Optional[Callable] = None,
        audit_method: Optional[Callable] = None,
    ):
        """
        Initialize Security Adapter Wrapper.

        Args:
            legacy_adapter (Any): The legacy adapter instance to wrap.
                Can be any object with methods for validation, permission
                checking, and auditing.
            operation_type (Type[OperationType]): Type of operation enumeration
                that this adapter handles. Must be a subclass of OperationType.
            validate_method (Optional[Callable]): Method for operation validation.
                If None, automatically detected from legacy_adapter. Defaults to None.
            check_permissions_method (Optional[Callable]): Method for permission
                checking. If None, automatically detected from legacy_adapter.
                Defaults to None.
            audit_method (Optional[Callable]): Method for operation auditing.
                If None, automatically detected from legacy_adapter. Defaults to None.

        Raises:
            ValueError: If legacy_adapter is None or operation_type is invalid.
            AttributeError: If required methods cannot be found and no fallback
                is available.

        Example:
            >>> legacy_adapter = LegacyKubernetesAdapter()
            >>> wrapper = SecurityAdapterWrapper(
            ...     legacy_adapter=legacy_adapter,
            ...     operation_type=KubernetesOperation
            ... )
        """
        if legacy_adapter is None:
            raise ValueError("legacy_adapter cannot be None")

        if not issubclass(operation_type, OperationType):
            raise ValueError(
                f"operation_type must be a subclass of OperationType, "
                f"got {operation_type}"
            )

        self.legacy_adapter = legacy_adapter
        self._operation_type = operation_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Auto-detect methods if not provided
        self._validate_method = validate_method or self._find_method("validate")
        self._check_permissions_method = check_permissions_method or self._find_method(
            "check", "permissions"
        )
        self._audit_method = audit_method or self._find_method("audit")

        # Log detected methods
        self.logger.info(
            "Security adapter wrapper initialized",
            extra={
                "legacy_adapter_type": type(legacy_adapter).__name__,
                "operation_type": operation_type.__name__,
                "validate_method": (
                    self._validate_method.__name__ if self._validate_method else None
                ),
                "check_permissions_method": (
                    self._check_permissions_method.__name__
                    if self._check_permissions_method
                    else None
                ),
                "audit_method": (
                    self._audit_method.__name__ if self._audit_method else None
                ),
            },
        )

    @property
    def operation_type(self) -> Type[OperationType]:
        """
        Get the operation type enumeration class for this adapter.

        Returns:
            Type[OperationType]: The operation type enumeration class
                that this adapter handles.
        """
        return self._operation_type

    def _find_method(self, *prefixes: str) -> Optional[Callable]:
        """
        Automatically find method in legacy adapter by prefix.

        This method searches for methods in the legacy adapter that match
        common naming patterns. It looks for methods starting with the
        provided prefixes.

        Args:
            *prefixes (str): Prefixes to search for in method names.
                Multiple prefixes can be provided for compound searches.

        Returns:
            Optional[Callable]: Found method if available, None otherwise.

        Example:
            >>> wrapper._find_method("validate")
            >>> wrapper._find_method("check", "permissions")
        """
        if not prefixes:
            return None

        # Build search pattern
        search_pattern = "_".join(prefixes).lower()

        # Search for methods matching the pattern
        for attr_name in dir(self.legacy_adapter):
            if not attr_name.startswith("_"):
                attr = getattr(self.legacy_adapter, attr_name)
                if callable(attr) and search_pattern in attr_name.lower():
                    self.logger.debug(
                        f"Found method '{attr_name}' for prefix '{search_pattern}'"
                    )
                    return attr

        # Try alternative patterns
        alternative_patterns = [
            f"{prefixes[0]}_{prefixes[1]}" if len(prefixes) > 1 else prefixes[0],
            (
                f"{prefixes[0]}{prefixes[1].capitalize()}"
                if len(prefixes) > 1
                else prefixes[0]
            ),
        ]

        for pattern in alternative_patterns:
            for attr_name in dir(self.legacy_adapter):
                if not attr_name.startswith("_"):
                    attr = getattr(self.legacy_adapter, attr_name)
                    if callable(attr) and pattern.lower() in attr_name.lower():
                        self.logger.debug(
                            f"Found method '{attr_name}' "
                            f"for alternative pattern '{pattern}'"
                        )
                        return attr

        self.logger.warning(
            f"Could not find method with prefix '{search_pattern}' "
            "in legacy adapter"
        )
        return None

    def validate_operation(
        self,
        operation: OperationType,
        user_roles: List[str],
        params: Optional[Dict[str, Any]] = None,
        context: Optional[OperationContext] = None,
    ) -> Tuple[bool, str]:
        """
        Validate if a user can perform an operation.

        This method wraps the legacy adapter's validation method, providing
        fallback behavior if the method is not found or does not support
        context parameter.

        Args:
            operation (OperationType): The operation to validate.
            user_roles (List[str]): List of roles assigned to the user.
            params (Optional[Dict[str, Any]]): Optional parameters for the operation.
            context (Optional[OperationContext]): Optional operation context.

        Returns:
            Tuple[bool, str]: A tuple containing validation result and error message.

        Example:
            >>> is_valid, error = wrapper.validate_operation(
            ...     operation=KubernetesOperation.CREATE_POD,
            ...     user_roles=["k8s:admin"],
            ...     params={"namespace": "default"}
            ... )
        """
        if not self._validate_method:
            self.logger.warning(
                "No validation method found, returning default validation result"
            )
            return True, ""

        # Try calling with context first
        if context is not None:
            try:
                result = self._validate_method(
                    operation.value if hasattr(operation, "value") else str(operation),
                    user_roles,
                    params or {},
                    context,
                )
                return result if isinstance(result, tuple) else (result, "")
            except TypeError:
                # Method doesn't support context, try without
                pass

        # Call without context
        try:
            result = self._validate_method(
                operation.value if hasattr(operation, "value") else str(operation),
                user_roles,
                params or {},
            )
            return result if isinstance(result, tuple) else (result, "")
        except Exception as e:
            self.logger.error(
                f"Error calling validation method: {e}",
                exc_info=True,
            )
            return False, str(e)

    def check_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Check if user has required permissions.

        This method wraps the legacy adapter's permission checking method,
        providing fallback behavior if the method is not found.

        Args:
            user_roles (List[str]): List of roles assigned to the user.
            required_permissions (List[str]): List of permissions required.

        Returns:
            Tuple[bool, List[str]]: A tuple containing permission check result
                and list of denied permissions.

        Example:
            >>> has_perms, denied = wrapper.check_permissions(
            ...     user_roles=["k8s:admin"],
            ...     required_permissions=["k8s:create", "k8s:delete"]
            ... )
        """
        if not self._check_permissions_method:
            self.logger.warning(
                "No permission check method found, returning default result"
            )
            # Default: check if all required permissions are in user roles
            denied = [p for p in required_permissions if p not in user_roles]
            return len(denied) == 0, denied

        try:
            result = self._check_permissions_method(user_roles, required_permissions)
            if isinstance(result, tuple) and len(result) == 2:
                return result
            # If result is not a tuple, assume it's a boolean
            return (result, []) if result else (False, required_permissions)
        except Exception as e:
            self.logger.error(
                f"Error calling permission check method: {e}",
                exc_info=True,
            )
            return False, required_permissions

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

        This method wraps the legacy adapter's audit method, providing
        fallback behavior if the method is not found or does not support
        context parameter.

        Args:
            operation (OperationType): The operation that was performed.
            user_roles (List[str]): List of roles assigned to the user.
            params (Optional[Dict[str, Any]]): Optional parameters for the operation.
            status (str): Status of the operation.
            context (Optional[OperationContext]): Optional operation context.

        Example:
            >>> wrapper.audit_operation(
            ...     operation=KubernetesOperation.CREATE_POD,
            ...     user_roles=["k8s:admin"],
            ...     params={"namespace": "default"},
            ...     status="success"
            ... )
        """
        if not self._audit_method:
            self.logger.warning("No audit method found, skipping audit logging")
            return

        # Try calling with context first
        if context is not None:
            try:
                self._audit_method(
                    operation.value if hasattr(operation, "value") else str(operation),
                    user_roles,
                    params or {},
                    status,
                    context,
                )
                return
            except TypeError:
                # Method doesn't support context, try without
                pass

        # Call without context
        try:
            self._audit_method(
                operation.value if hasattr(operation, "value") else str(operation),
                user_roles,
                params or {},
                status,
            )
        except Exception as e:
            self.logger.error(
                f"Error calling audit method: {e}",
                exc_info=True,
            )
