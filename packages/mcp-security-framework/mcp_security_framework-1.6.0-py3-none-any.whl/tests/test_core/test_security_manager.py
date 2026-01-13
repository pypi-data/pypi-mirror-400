"""
Security Manager Tests

This module provides comprehensive tests for the SecurityManager class,
which is the main security management class that integrates all core
security components.

Test Coverage:
- SecurityManager initialization and component setup
- Request validation with authentication and authorization
- User authentication with different methods
- Permission checking and validation
- Certificate management operations
- SSL context creation
- Rate limiting functionality
- Security status and monitoring
- Error handling and edge cases

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_security_framework.core.security_manager import (
    SecurityConfigurationError,
    SecurityManager,
    SecurityValidationError,
)
from mcp_security_framework.schemas.config import (
    AuthConfig,
    CertificateConfig,
    LoggingConfig,
    PermissionConfig,
    RateLimitConfig,
    SecurityConfig,
    SSLConfig,
)
from mcp_security_framework.schemas.models import (
    AuthMethod,
    AuthResult,
    AuthStatus,
    CertificateInfo,
    CertificatePair,
    ValidationResult,
    ValidationStatus,
)
from mcp_security_framework.schemas.responses import ResponseStatus, SecurityResponse


class TestSecurityManager:
    """Test suite for SecurityManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create basic configuration
        self.config = SecurityConfig(
            auth=AuthConfig(
                enabled=True,
                methods=["api_key", "jwt"],
                api_keys={"admin": "admin_key_123", "user": "user_key_456"},
                jwt_secret="test_jwt_secret_123",
            ),
            permissions=PermissionConfig(enabled=True, roles_file="test_roles.json"),
            ssl=SSLConfig(enabled=False),
            certificates=CertificateConfig(enabled=False),
            rate_limit=RateLimitConfig(
                enabled=True, max_requests=100, window_seconds=60
            ),
            logging=LoggingConfig(level="INFO"),
            debug=True,
            environment="test",
        )

        # Mock the component managers
        self.mock_auth_manager = Mock()
        self.mock_permission_manager = Mock()
        self.mock_ssl_manager = Mock()
        self.mock_cert_manager = Mock()
        self.mock_rate_limiter = Mock()

        # Set up mock return values
        self.mock_auth_manager.is_auth_enabled = True
        self.mock_ssl_manager.is_ssl_enabled = False
        self.mock_rate_limiter.is_rate_limiting_enabled = True

        # Mock successful authentication
        self.mock_auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="admin",
            roles=["admin"],
            auth_method=AuthMethod.API_KEY,
            error_code=None,
            error_message=None,
        )

        # Mock successful validation
        self.mock_validation_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            error_code=None,
            error_message=None,
        )

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_security_manager_initialization_success(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test successful SecurityManager initialization."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Verify all components were initialized
        assert security_manager.config == self.config
        assert security_manager.permission_manager == self.mock_permission_manager
        assert security_manager.auth_manager == self.mock_auth_manager
        assert security_manager.ssl_manager == self.mock_ssl_manager
        assert security_manager.cert_manager == self.mock_cert_manager
        assert security_manager.rate_limiter == self.mock_rate_limiter

        # Verify component status
        assert security_manager._component_status["permission_manager"] is True
        assert security_manager._component_status["auth_manager"] is True
        assert security_manager._component_status["ssl_manager"] is True
        assert security_manager._component_status["cert_manager"] is True
        assert security_manager._component_status["rate_limiter"] is True

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    def test_security_manager_initialization_failure(
        self, mock_permission_manager_class
    ):
        """Test SecurityManager initialization failure."""
        # Make PermissionManager raise an exception
        mock_permission_manager_class.side_effect = Exception(
            "Permission manager failed"
        )

        # Verify SecurityManager raises SecurityConfigurationError
        with pytest.raises(SecurityConfigurationError) as exc_info:
            SecurityManager(self.config)

        assert "Failed to initialize security components" in str(exc_info.value)
        assert exc_info.value.error_code == -32001

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_validate_request_success(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test successful request validation."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Set up mock return values
        self.mock_auth_manager.authenticate_api_key.return_value = self.mock_auth_result
        self.mock_permission_manager.validate_access.return_value = (
            self.mock_validation_result
        )
        self.mock_rate_limiter.check_rate_limit.return_value = True

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test request validation
        request_data = {
            "api_key": "admin_key_123",
            "required_permissions": ["read", "write"],
            "client_ip": "192.168.1.100",
        }

        result = security_manager.validate_request(request_data)

        # Verify result
        assert result.is_valid is True
        assert result.status == ValidationStatus.VALID

        # Verify mocks were called correctly
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "admin_key_123"
        )
        self.mock_permission_manager.validate_access.assert_called_once_with(
            ["admin"], ["read", "write"]
        )
        self.mock_rate_limiter.check_rate_limit.assert_called_once_with("192.168.1.100")
        self.mock_rate_limiter.increment_request_count.assert_called_once_with(
            "192.168.1.100"
        )

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_validate_request_authentication_failure(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test request validation with authentication failure."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Set up failed authentication
        failed_auth_result = AuthResult(
            is_valid=False,
            status=AuthStatus.FAILED,
            username=None,
            roles=[],
            auth_method=AuthMethod.API_KEY,
            error_code=-32002,
            error_message="Invalid API key",
        )
        self.mock_auth_manager.authenticate_api_key.return_value = failed_auth_result

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test request validation
        request_data = {
            "api_key": "invalid_key",
            "required_permissions": ["read", "write"],
            "client_ip": "192.168.1.100",
        }

        result = security_manager.validate_request(request_data)

        # Verify result
        assert result.is_valid is False
        assert "Authentication failed" in result.error_message
        assert result.error_code == -32002

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_validate_request_rate_limit_exceeded(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test request validation with rate limit exceeded."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Set up successful authentication but rate limit exceeded
        self.mock_auth_manager.authenticate_api_key.return_value = self.mock_auth_result
        self.mock_rate_limiter.check_rate_limit.return_value = False

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test request validation
        request_data = {
            "api_key": "admin_key_123",
            "required_permissions": ["read", "write"],
            "client_ip": "192.168.1.100",
        }

        result = security_manager.validate_request(request_data)

        # Verify result
        assert result.is_valid is False
        assert "Rate limit exceeded" in result.error_message
        assert result.error_code == -32003

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_validate_request_permission_denied(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test request validation with permission denied."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Set up successful authentication and rate limiting but permission denied
        self.mock_auth_manager.authenticate_api_key.return_value = self.mock_auth_result
        self.mock_rate_limiter.check_rate_limit.return_value = True

        failed_validation_result = ValidationResult(
            is_valid=False,
            status=ValidationStatus.INVALID,
            error_code=-32004,
            error_message="Insufficient permissions",
        )
        self.mock_permission_manager.validate_access.return_value = (
            failed_validation_result
        )

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test request validation
        request_data = {
            "api_key": "admin_key_123",
            "required_permissions": ["admin_only"],
            "client_ip": "192.168.1.100",
        }

        result = security_manager.validate_request(request_data)

        # Verify result
        assert result.is_valid is False
        assert "Permission denied" in result.error_message
        assert result.error_code == -32004

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_authenticate_user_api_key(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test user authentication with API key."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        self.mock_auth_manager.authenticate_api_key.return_value = self.mock_auth_result

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test API key authentication
        credentials = {"method": "api_key", "api_key": "admin_key_123"}

        result = security_manager.authenticate_user(credentials)

        # Verify result
        assert result.is_valid is True
        assert result.username == "admin"
        assert result.roles == ["admin"]

        # Verify mock was called
        self.mock_auth_manager.authenticate_api_key.assert_called_once_with(
            "admin_key_123"
        )

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_authenticate_user_jwt(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test user authentication with JWT token."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        jwt_auth_result = AuthResult(
            is_valid=True,
            status=AuthStatus.SUCCESS,
            username="user",
            roles=["user"],
            auth_method=AuthMethod.JWT,
            error_code=None,
            error_message=None,
        )
        self.mock_auth_manager.authenticate_jwt_token.return_value = jwt_auth_result

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test JWT authentication
        credentials = {
            "method": "jwt",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        }

        result = security_manager.authenticate_user(credentials)

        # Verify result
        assert result.is_valid is True
        assert result.username == "user"
        assert result.roles == ["user"]

        # Verify mock was called
        self.mock_auth_manager.authenticate_jwt_token.assert_called_once_with(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_authenticate_user_invalid_method(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test user authentication with invalid method."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test invalid authentication method
        credentials = {"method": "invalid_method", "data": "some_data"}

        with pytest.raises(SecurityValidationError) as exc_info:
            security_manager.authenticate_user(credentials)

        assert "Unsupported authentication method" in str(exc_info.value)

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_check_permissions(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test permission checking."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        self.mock_permission_manager.validate_access.return_value = (
            self.mock_validation_result
        )

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test permission checking
        user_roles = ["admin", "user"]
        required_permissions = ["read", "write"]

        result = security_manager.check_permissions(user_roles, required_permissions)

        # Verify result
        assert result.is_valid is True
        assert result.status == ValidationStatus.VALID

        # Verify mock was called
        self.mock_permission_manager.validate_access.assert_called_once_with(
            user_roles, required_permissions
        )

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_check_rate_limit(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test rate limit checking."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        self.mock_rate_limiter.check_rate_limit.return_value = True

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test rate limit checking
        identifier = "192.168.1.100"
        result = security_manager.check_rate_limit(identifier)

        # Verify result
        assert result is True

        # Verify mock was called
        self.mock_rate_limiter.check_rate_limit.assert_called_once_with(identifier)

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_get_security_status(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test security status retrieval."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test security status
        status = security_manager.get_security_status()

        # Verify result
        assert isinstance(status, SecurityResponse)
        assert status.status == ResponseStatus.SUCCESS
        assert status.message == "Security system healthy"
        assert status.version == "1.0.0"

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_extract_auth_credentials_api_key(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test authentication credentials extraction with API key."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test API key extraction
        request_data = {"api_key": "test_key_123"}
        credentials = security_manager._extract_auth_credentials(request_data)

        # Verify result
        assert credentials["method"] == "api_key"
        assert credentials["api_key"] == "test_key_123"

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_extract_auth_credentials_authorization_header(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test authentication credentials extraction with Authorization header."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test Bearer token extraction
        request_data = {
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        credentials = security_manager._extract_auth_credentials(request_data)

        # Verify result
        assert credentials["method"] == "jwt"
        assert credentials["token"] == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Test ApiKey extraction
        request_data = {"authorization": "ApiKey test_api_key_123"}
        credentials = security_manager._extract_auth_credentials(request_data)

        # Verify result
        assert credentials["method"] == "api_key"
        assert credentials["api_key"] == "test_api_key_123"

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_extract_auth_credentials_no_credentials(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test authentication credentials extraction with no credentials."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test no credentials
        request_data = {"some_other_data": "value"}

        with pytest.raises(SecurityValidationError) as exc_info:
            security_manager._extract_auth_credentials(request_data)

        assert "No authentication credentials found" in str(exc_info.value)

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_log_security_event(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test security event logging."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test security event logging
        event_type = "test_event"
        event_data = {"user": "admin", "action": "login"}

        security_manager._log_security_event(event_type, event_data)

        # Verify event was logged
        assert len(security_manager._security_events) == 1
        event = security_manager._security_events[0]
        assert event["event_type"] == event_type
        assert event["event_data"] == event_data
        assert event["environment"] == "test"
        assert "timestamp" in event

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_factory_methods_work(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test that factory methods work correctly."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test factory methods
        fastapi_middleware = security_manager.create_fastapi_middleware()
        assert fastapi_middleware is not None
        assert hasattr(fastapi_middleware, "__call__")

        flask_middleware = security_manager.create_flask_middleware()
        assert flask_middleware is not None
        assert hasattr(flask_middleware, "__call__")

        # Django middleware should raise ImportError since it's not implemented
        with pytest.raises((ImportError, SecurityConfigurationError)):
            security_manager.create_django_middleware()

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_certificate_operations_not_implemented(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test certificate operations with NotImplementedError."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test certificate operations (these will be implemented in future steps)
        # These methods are not yet implemented, so they should raise NotImplementedError
        # or work with disabled certificate management
        pass

    @patch("mcp_security_framework.core.security_manager.PermissionManager")
    @patch("mcp_security_framework.core.security_manager.AuthManager")
    @patch("mcp_security_framework.core.security_manager.SSLManager")
    @patch("mcp_security_framework.core.security_manager.CertificateManager")
    @patch("mcp_security_framework.core.security_manager.RateLimiter")
    def test_ssl_context_creation_not_implemented(
        self,
        mock_rate_limiter_class,
        mock_cert_manager_class,
        mock_ssl_manager_class,
        mock_auth_manager_class,
        mock_permission_manager_class,
    ):
        """Test SSL context creation with NotImplementedError."""
        # Set up mocks
        mock_permission_manager_class.return_value = self.mock_permission_manager
        mock_auth_manager_class.return_value = self.mock_auth_manager
        mock_ssl_manager_class.return_value = self.mock_ssl_manager
        mock_cert_manager_class.return_value = self.mock_cert_manager
        mock_rate_limiter_class.return_value = self.mock_rate_limiter

        # Create SecurityManager
        security_manager = SecurityManager(self.config)

        # Test SSL context creation (these will be implemented in future steps)
        # These methods are not yet implemented, so they should raise NotImplementedError
        # or work with disabled SSL management
        pass

    def test_register_adapter(self):
        """Test registering a security adapter."""
        security_manager = SecurityManager(self.config)

        # Create a test adapter
        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()
        security_manager.register_adapter("test", adapter)

        # Verify adapter is registered
        assert "test" in security_manager.list_adapters()
        assert security_manager.get_adapter("test") == adapter

    def test_register_adapter_duplicate_name(self):
        """Test registering adapter with duplicate name raises error."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()
        security_manager.register_adapter("test", adapter)

        # Try to register again with same name
        with pytest.raises(SecurityConfigurationError):
            security_manager.register_adapter("test", adapter)

    def test_register_adapter_invalid_name(self):
        """Test registering adapter with invalid name raises error."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()

        # Try with empty name
        with pytest.raises(ValueError):
            security_manager.register_adapter("", adapter)

        # Try with None name (will be converted to string, but should fail)
        with pytest.raises(ValueError):
            security_manager.register_adapter(None, adapter)  # type: ignore

    def test_register_adapter_invalid_type(self):
        """Test registering non-adapter object raises error."""
        security_manager = SecurityManager(self.config)

        # Try to register a non-adapter object
        with pytest.raises(ValueError, match="Adapter must be a SecurityAdapter instance"):
            security_manager.register_adapter("test", "not_an_adapter")  # type: ignore

    def test_get_adapter(self):
        """Test getting a registered adapter."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()
        security_manager.register_adapter("test", adapter)

        # Get adapter
        retrieved_adapter = security_manager.get_adapter("test")
        assert retrieved_adapter == adapter

        # Get non-existent adapter
        assert security_manager.get_adapter("nonexistent") is None

    def test_list_adapters(self):
        """Test listing all registered adapters."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation1(OperationType):
            """Test operation types 1."""

            TEST = "test1:operation"

        class TestOperation2(OperationType):
            """Test operation types 2."""

            TEST = "test2:operation"

        class TestAdapter1(SecurityAdapter):
            """Test security adapter 1."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation1

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        class TestAdapter2(SecurityAdapter):
            """Test security adapter 2."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation2

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
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
                context=None,
            ) -> None:
                pass

        adapter1 = TestAdapter1()
        adapter2 = TestAdapter2()

        # Initially empty
        assert security_manager.list_adapters() == []

        # Register adapters
        security_manager.register_adapter("adapter1", adapter1)
        security_manager.register_adapter("adapter2", adapter2)

        # List adapters (should be sorted)
        adapters = security_manager.list_adapters()
        assert "adapter1" in adapters
        assert "adapter2" in adapters
        assert len(adapters) == 2
        assert adapters == sorted(adapters)

    def test_validate_operation(self):
        """Test validating operation through adapter."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
                if "admin" in user_roles:
                    return True, ""
                return False, "Insufficient permissions"

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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()
        security_manager.register_adapter("test", adapter)

        # Test successful validation
        is_valid, error = security_manager.validate_operation(
            adapter_name="test",
            operation=TestOperation.TEST,
            user_roles=["admin"],
        )
        assert is_valid is True
        assert error == ""

        # Test failed validation
        is_valid, error = security_manager.validate_operation(
            adapter_name="test",
            operation=TestOperation.TEST,
            user_roles=["user"],
        )
        assert is_valid is False
        assert error == "Insufficient permissions"

    def test_validate_operation_adapter_not_found(self):
        """Test validating operation with non-existent adapter."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import OperationType

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        # Try to validate with non-existent adapter
        with pytest.raises(SecurityValidationError, match="Adapter 'nonexistent' not found"):
            security_manager.validate_operation(
                adapter_name="nonexistent",
                operation=TestOperation.TEST,
                user_roles=["admin"],
            )

    def test_validate_operation_with_context(self):
        """Test validating operation with OperationContext."""
        security_manager = SecurityManager(self.config)

        from mcp_security_framework.core.security_adapter import (
            OperationType,
            SecurityAdapter,
        )
        from mcp_security_framework.schemas.operation_context import OperationContext
        from typing import Any, Dict, List, Optional, Tuple, Type

        class TestOperation(OperationType):
            """Test operation types."""

            TEST = "test:operation"

        class TestAdapter(SecurityAdapter):
            """Test security adapter with context support."""

            @property
            def operation_type(self) -> Type[OperationType]:
                return TestOperation

            def validate_operation(
                self,
                operation: OperationType,
                user_roles: List[str],
                params: Optional[Dict[str, Any]] = None,
                context=None,
            ) -> Tuple[bool, str]:
                if context and context.user_id == "blocked":
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
                context=None,
            ) -> None:
                pass

        adapter = TestAdapter()
        security_manager.register_adapter("test", adapter)

        # Test with context - allowed user
        context_allowed = OperationContext(user_id="allowed", user_roles=["admin"])
        is_valid, error = security_manager.validate_operation(
            adapter_name="test",
            operation=TestOperation.TEST,
            user_roles=["admin"],
            context=context_allowed,
        )
        assert is_valid is True

        # Test with context - blocked user
        context_blocked = OperationContext(user_id="blocked", user_roles=["admin"])
        is_valid, error = security_manager.validate_operation(
            adapter_name="test",
            operation=TestOperation.TEST,
            user_roles=["admin"],
            context=context_blocked,
        )
        assert is_valid is False
        assert error == "User is blocked"
