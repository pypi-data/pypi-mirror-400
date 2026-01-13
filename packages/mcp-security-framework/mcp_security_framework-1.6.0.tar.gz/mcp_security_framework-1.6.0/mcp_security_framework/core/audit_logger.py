"""
Audit Logger Module

This module provides structured audit logging capabilities for security
operations in the MCP Security Framework. It includes audit event models
and logger implementations with support for multiple backends.

Key Features:
- Structured audit event logging
- Multiple backend support (file, console, database, elasticsearch)
- Integration with operation context
- Comprehensive audit event information

Classes:
    AuditStatus: Audit status enumeration
    AuditEvent: Audit event dataclass
    AuditLogger: Audit logger with multiple backend support

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..schemas.operation_context import OperationContext


class AuditStatus(str, Enum):
    """
    Audit Status Enumeration

    This enumeration defines the possible status values for audit events.
    It is used to categorize the outcome of security operations.

    Values:
        SUCCESS: Operation completed successfully
        FAILED: Operation failed due to error
        DENIED: Operation was denied due to insufficient permissions
        PENDING: Operation is pending completion

    Example:
        >>> from mcp_security_framework.core.audit_logger import AuditStatus
        >>> status = AuditStatus.SUCCESS
        >>> print(status.value)  # "success"
    """

    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"
    PENDING = "pending"


@dataclass
class AuditEvent:
    """
    Audit Event Dataclass

    This dataclass represents a single audit event for security operations.
    It contains all relevant information about an operation including user
    information, operation details, status, and context.

    Attributes:
        operation (str): Name or identifier of the operation that was
            performed. Should be a descriptive string like "ftp:upload"
            or "docker:pull".
        operation_type (str): Type of operation enumeration class.
            Used to categorize operations by their type (e.g., "FtpOperation",
            "DockerOperation").
        user_roles (List[str]): List of roles assigned to the user who
            performed the operation. Empty list if user has no roles.
        params (Dict[str, Any]): Parameters passed to the operation.
            Can include operation-specific data like resource paths,
            file sizes, or other metadata. Defaults to empty dictionary.
        status (AuditStatus): Status of the operation. Indicates whether
            the operation succeeded, failed, was denied, or is pending.
        timestamp (datetime): Timestamp when the audit event was created.
            Defaults to current UTC time if not provided.
        error_message (Optional[str]): Error message if operation failed
            or was denied. None if operation succeeded.
        metadata (Dict[str, Any]): Additional metadata for the audit event.
            Can include IP address, user agent, session ID, or any other
            relevant information. Defaults to empty dictionary.
        context (Optional[OperationContext]): Optional operation context
            containing additional information about the operation, request,
            and user. Can include request ID, parent operation, and metadata.
            Defaults to None if no context is available.

    Methods:
        to_dict(): Serialize audit event to dictionary

    Example:
        >>> from mcp_security_framework.core.audit_logger import (
        ...     AuditEvent, AuditStatus
        ... )
        >>> from datetime import datetime, timezone
        >>>
        >>> event = AuditEvent(
        ...     operation="ftp:upload",
        ...     operation_type="FtpOperation",
        ...     user_roles=["ftp:upload"],
        ...     params={"remote_path": "/files/test.txt", "file_size": 1024},
        ...     status=AuditStatus.SUCCESS,
        ...     timestamp=datetime.now(timezone.utc),
        ...     error_message=None,
        ...     metadata={"ip": "192.168.1.1"},
        ...     context=None
        ... )
        >>>
        >>> # Serialize to dictionary
        >>> event_dict = event.to_dict()
        >>> print(event_dict["operation"])  # "ftp:upload"
    """

    operation: str
    operation_type: str
    user_roles: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    status: AuditStatus = AuditStatus.SUCCESS
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[OperationContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize audit event to dictionary.

        This method converts the AuditEvent instance to a dictionary
        representation suitable for JSON serialization, logging, or storage.
        The timestamp and context are converted to their dictionary
        representations.

        Returns:
            Dict[str, Any]: Dictionary representation of the audit event.
                Contains all fields with timestamp as ISO format string and
                context as dictionary if present.

        Example:
            >>> event = AuditEvent(
            ...     operation="ftp:upload",
            ...     operation_type="FtpOperation",
            ...     status=AuditStatus.SUCCESS
            ... )
            >>> event_dict = event.to_dict()
            >>> print(event_dict["operation"])  # "ftp:upload"
            >>> print(event_dict["status"])  # "success"
        """
        result = asdict(self)
        # Convert timestamp to ISO format
        result["timestamp"] = self.timestamp.isoformat() if self.timestamp else None
        # Convert status enum to string
        result["status"] = (
            self.status.value
            if isinstance(self.status, AuditStatus)
            else str(self.status)
        )
        # Convert context to dictionary if present
        if self.context is not None:
            result["context"] = self.context.to_dict()
        else:
            result["context"] = None
        return result


class AuditLogger:
    """
    Audit Logger Class

    This class provides structured audit logging capabilities for security
    operations. It supports multiple backends for logging audit events
    including file, console, database, and elasticsearch.

    The AuditLogger implements a unified interface for logging audit events
    across different backends, allowing for flexible deployment and integration
    with existing logging infrastructure.

    Attributes:
        backend (str): Backend type for audit logging. Supported values:
            "file", "console", "database", "elasticsearch".
        config (Dict[str, Any]): Configuration dictionary for the selected
            backend. Contains backend-specific settings like file paths,
            connection strings, or other configuration options.
        logger (Logger): Logger instance for audit operations. Used for
            console and file backends.

    Methods:
        log: Log an audit event
        log_operation: Convenient wrapper for logging operations

    Example:
        >>> from mcp_security_framework.core.audit_logger import (
        ...     AuditLogger, AuditEvent, AuditStatus
        ... )
        >>>
        >>> # Initialize file backend
        >>> audit_logger = AuditLogger(
        ...     backend="file",
        ...     config={"log_file": "/var/log/security_audit.log"}
        ... )
        >>>
        >>> # Log audit event
        >>> event = AuditEvent(
        ...     operation="ftp:upload",
        ...     operation_type="FtpOperation",
        ...     user_roles=["ftp:upload"],
        ...     status=AuditStatus.SUCCESS
        ... )
        >>> audit_logger.log(event)
        >>>
        >>> # Or use convenient wrapper
        >>> audit_logger.log_operation(
        ...     operation="ftp:download",
        ...     operation_type="FtpOperation",
        ...     user_roles=["ftp:download"],
        ...     status=AuditStatus.SUCCESS
        ... )

    Note:
        Database and elasticsearch backends are currently placeholders
        and will raise NotImplementedError if used. File and console
        backends are fully implemented.
    """

    def __init__(
        self,
        backend: str = "console",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Audit Logger.

        Args:
            backend (str): Backend type for audit logging. Supported values:
                "file", "console", "database", "elasticsearch". Defaults
                to "console" if not specified.
            config (Optional[Dict[str, Any]]): Configuration dictionary for
                the selected backend. For file backend, should contain
                "log_file" key with file path. For console backend, can
                be empty or None. Defaults to None.

        Raises:
            ValueError: If backend type is not supported.
            FileNotFoundError: If file backend is used and log file
                directory does not exist.

        Example:
            >>> # Console backend (default)
            >>> audit_logger = AuditLogger()
            >>>
            >>> # File backend
            >>> audit_logger = AuditLogger(
            ...     backend="file",
            ...     config={"log_file": "/var/log/security_audit.log"}
            ... )
        """
        self.backend = backend.lower()
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.backend}")

        # Validate backend type
        supported_backends = ["file", "console", "database", "elasticsearch"]
        if self.backend not in supported_backends:
            raise ValueError(
                f"Unsupported backend: {self.backend}. "
                f"Supported backends: {supported_backends}"
            )

        # Initialize backend-specific configuration
        if self.backend == "file":
            log_file = self.config.get("log_file")
            if not log_file:
                raise ValueError("File backend requires 'log_file' in config")
            # Ensure log file directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # Setup file handler if not already configured
            if not self.logger.handlers:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                )
                self.logger.addHandler(file_handler)
                self.logger.setLevel(logging.INFO)

        self.logger.info(
            "Audit logger initialized",
            extra={"backend": self.backend, "config_keys": list(self.config.keys())},
        )

    def log(self, event: AuditEvent) -> None:
        """
        Log an audit event.

        This method logs an audit event to the configured backend.
        The event is serialized and formatted according to the backend
        requirements.

        Args:
            event (AuditEvent): Audit event to log. Must be a valid
                AuditEvent instance with all required fields.

        Raises:
            NotImplementedError: If database or elasticsearch backend
                is used (not yet implemented).
            IOError: If file backend is used and log file cannot be written.

        Example:
            >>> from mcp_security_framework.core.audit_logger import (
            ...     AuditLogger, AuditEvent, AuditStatus
            ... )
            >>>
            >>> audit_logger = AuditLogger(backend="console")
            >>> event = AuditEvent(
            ...     operation="ftp:upload",
            ...     operation_type="FtpOperation",
            ...     user_roles=["ftp:upload"],
            ...     status=AuditStatus.SUCCESS
            ... )
            >>> audit_logger.log(event)
        """
        event_dict = event.to_dict()

        if self.backend == "console":
            # Log to console with structured format
            log_message = json.dumps(event_dict, indent=2, default=str)
            self.logger.info(f"Audit Event:\n{log_message}")

        elif self.backend == "file":
            # Log to file as JSON line
            log_message = json.dumps(event_dict, default=str)
            self.logger.info(log_message)

        elif self.backend == "database":
            # Placeholder for database backend
            raise NotImplementedError("Database backend not yet implemented")

        elif self.backend == "elasticsearch":
            # Placeholder for elasticsearch backend
            raise NotImplementedError("Elasticsearch backend not yet implemented")

    def log_operation(
        self,
        operation: str,
        operation_type: str,
        user_roles: List[str],
        params: Optional[Dict[str, Any]] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[OperationContext] = None,
    ) -> None:
        """
        Convenient wrapper for logging operations.

        This method creates an AuditEvent from the provided parameters
        and logs it using the log() method. It provides a more convenient
        interface for logging operations without explicitly creating
        AuditEvent instances.

        Args:
            operation (str): Name or identifier of the operation that was
                performed. Should be a descriptive string like "ftp:upload".
            operation_type (str): Type of operation enumeration class.
                Used to categorize operations (e.g., "FtpOperation").
            user_roles (List[str]): List of roles assigned to the user who
                performed the operation. Empty list if user has no roles.
            params (Optional[Dict[str, Any]]): Parameters passed to the
                operation. Can include operation-specific data. Defaults
                to None if no parameters.
            status (AuditStatus): Status of the operation. Defaults to
                AuditStatus.SUCCESS if not specified.
            error_message (Optional[str]): Error message if operation
                failed or was denied. None if operation succeeded.
            metadata (Optional[Dict[str, Any]]): Additional metadata for
                the audit event. Defaults to None if no metadata.
            context (Optional[OperationContext]): Optional operation context
                containing additional information. Defaults to None if no
                context is available.

        Example:
            >>> from mcp_security_framework.core.audit_logger import (
            ...     AuditLogger, AuditStatus
            ... )
            >>>
            >>> audit_logger = AuditLogger(backend="console")
            >>> audit_logger.log_operation(
            ...     operation="ftp:upload",
            ...     operation_type="FtpOperation",
            ...     user_roles=["ftp:upload"],
            ...     params={"remote_path": "/files/test.txt"},
            ...     status=AuditStatus.SUCCESS
            ... )
        """
        event = AuditEvent(
            operation=operation,
            operation_type=operation_type,
            user_roles=user_roles,
            params=params or {},
            status=status,
            timestamp=datetime.now(timezone.utc),
            error_message=error_message,
            metadata=metadata or {},
            context=context,
        )
        self.log(event)
