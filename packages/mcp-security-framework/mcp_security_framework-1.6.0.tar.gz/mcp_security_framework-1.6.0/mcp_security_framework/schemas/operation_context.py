"""
Operation Context Module

This module provides the OperationContext dataclass for passing operation
context information between security adapters and operations.

Key Features:
- Structured operation context with user and request information
- Serialization and deserialization support
- Metadata support for extensibility
- Parent operation tracking for operation chains

Classes:
    OperationContext: Dataclass for operation context information

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class OperationContext:
    """
    Operation Context Dataclass

    This dataclass provides a structured way to pass operation context
    information between security adapters and operations. It includes
    user information, request metadata, and operation tracking data.

    The context can be serialized to a dictionary for logging, storage,
    or transmission, and can be deserialized from a dictionary to
    restore the context.

    Attributes:
        user_id (Optional[str]): Unique identifier for the user performing
            the operation. Can be None if user is not authenticated.
        user_roles (List[str]): List of roles assigned to the user.
            Empty list if user has no roles.
        request_id (Optional[str]): Unique identifier for the request.
            Used for request tracking and correlation. Can be None if
            not available.
        parent_operation (Optional[str]): Identifier of the parent operation
            if this operation is part of a chain. Used for tracking operation
            hierarchies. Can be None if this is a top-level operation.
        metadata (Dict[str, Any]): Additional metadata for the operation.
            Can include IP address, user agent, session ID, or any other
            relevant information. Defaults to empty dictionary.
        timestamp (datetime): Timestamp when the context was created.
            Defaults to current UTC time if not provided.

    Methods:
        to_dict(): Serialize context to dictionary
        from_dict(data): Deserialize context from dictionary

    Example:
        >>> from mcp_security_framework.schemas.operation_context import (
        ...     OperationContext
        ... )
        >>> from datetime import datetime, timezone
        >>>
        >>> # Create operation context
        >>> context = OperationContext(
        ...     user_id="user123",
        ...     user_roles=["ftp:upload", "docker:pull"],
        ...     request_id="req456",
        ...     parent_operation="batch_upload",
        ...     metadata={
        ...         "ip": "192.168.1.1",
        ...         "user_agent": "Mozilla/5.0",
        ...         "session_id": "sess789"
        ...     },
        ...     timestamp=datetime.now(timezone.utc)
        ... )
        >>>
        >>> # Serialize to dictionary
        >>> context_dict = context.to_dict()
        >>> print(context_dict["user_id"])  # "user123"
        >>>
        >>> # Deserialize from dictionary
        >>> restored_context = OperationContext.from_dict(context_dict)
        >>> print(restored_context.user_id)  # "user123"

    Note:
        The timestamp is stored as a datetime object internally, but is
        serialized to ISO format string in the dictionary representation.
        When deserializing, ISO format strings are automatically converted
        back to datetime objects.
    """

    user_id: Optional[str] = None
    user_roles: List[str] = field(default_factory=list)
    request_id: Optional[str] = None
    parent_operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize operation context to dictionary.

        This method converts the OperationContext instance to a dictionary
        representation suitable for JSON serialization, logging, or storage.
        The timestamp is converted to ISO format string.

        Returns:
            Dict[str, Any]: Dictionary representation of the operation context.
                Contains all fields with timestamp as ISO format string.

        Example:
            >>> context = OperationContext(
            ...     user_id="user123",
            ...     user_roles=["admin"],
            ...     request_id="req456"
            ... )
            >>> context_dict = context.to_dict()
            >>> print(context_dict["user_id"])  # "user123"
            >>> print(context_dict["timestamp"])  # "2024-12-19T10:30:00+00:00"
        """
        return {
            "user_id": self.user_id,
            "user_roles": self.user_roles,
            "request_id": self.request_id,
            "parent_operation": self.parent_operation,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationContext":
        """
        Deserialize operation context from dictionary.

        This method creates an OperationContext instance from a dictionary
        representation. The timestamp is automatically converted from ISO
        format string to datetime object if present.

        Args:
            data (Dict[str, Any]): Dictionary containing operation context
                data. Must contain valid field values. Timestamp can be
                ISO format string or datetime object.

        Returns:
            OperationContext: OperationContext instance created from the
                dictionary data.

        Raises:
            ValueError: If timestamp string cannot be parsed.
            TypeError: If data types are incompatible.

        Example:
            >>> context_dict = {
            ...     "user_id": "user123",
            ...     "user_roles": ["admin"],
            ...     "request_id": "req456",
            ...     "timestamp": "2024-12-19T10:30:00+00:00"
            ... }
            >>> context = OperationContext.from_dict(context_dict)
            >>> print(context.user_id)  # "user123"
            >>> print(context.timestamp)  # datetime object
        """
        # Handle timestamp conversion
        timestamp = data.get("timestamp")
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        elif isinstance(timestamp, str):
            try:
                # Try parsing ISO format
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                # Fallback to current time if parsing fails
                timestamp = datetime.now(timezone.utc)
        elif not isinstance(timestamp, datetime):
            # If timestamp is not datetime or string, use current time
            timestamp = datetime.now(timezone.utc)

        return cls(
            user_id=data.get("user_id"),
            user_roles=data.get("user_roles", []),
            request_id=data.get("request_id"),
            parent_operation=data.get("parent_operation"),
            metadata=data.get("metadata", {}),
            timestamp=timestamp,
        )
