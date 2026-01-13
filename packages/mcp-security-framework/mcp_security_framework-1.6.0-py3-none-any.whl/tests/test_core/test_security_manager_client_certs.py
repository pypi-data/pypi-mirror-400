"""
Test suite for SecurityManager client certificate loading.

This module tests the critical bug fix for SecurityManager.create_ssl_context()
to ensure client certificates are loaded for mTLS authentication.

Author: Vasiliy Zdanovskiy <vasilyvz@gmail.com>
"""

import os
import shutil
import ssl
import tempfile
from pathlib import Path

import pytest

from mcp_security_framework import (
    PermissionConfig,
    SecurityConfig,
    SecurityManager,
    SSLConfig,
)
from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
)


class TestSecurityManagerClientCerts:
    """Test suite for SecurityManager client certificate loading."""

    @pytest.fixture
    def temp_cert_files(self):
        """Create temporary certificate files for testing using real certificates."""
        temp_dir = Path(tempfile.mkdtemp())
        cert_storage = temp_dir / "certs"
        key_storage = temp_dir / "keys"
        cert_storage.mkdir()
        key_storage.mkdir()

        try:
            # Create CA
            ca_config = CAConfig(
                common_name="Test CA",
                organization="Test Org",
                country="US",
                validity_days=365,
                key_size=2048,
            )

            cert_config = CertificateConfig(
                enabled=True,
                ca_creation_mode=True,
                cert_storage_path=str(cert_storage),
                key_storage_path=str(key_storage),
            )

            cert_manager = CertificateManager(cert_config)
            ca_pair = cert_manager.create_root_ca(ca_config)

            # Create client certificate
            cert_config_with_ca = CertificateConfig(
                enabled=True,
                ca_cert_path=ca_pair.certificate_path,
                ca_key_path=ca_pair.private_key_path,
                cert_storage_path=str(cert_storage),
                key_storage_path=str(key_storage),
            )

            cert_manager_with_ca = CertificateManager(cert_config_with_ca)

            client_config = ClientCertConfig(
                common_name="test_client",
                organization="Test Org",
                country="US",
                roles=["chunker"],
                ca_cert_path=ca_pair.certificate_path,
                ca_key_path=ca_pair.private_key_path,
            )

            client_pair = cert_manager_with_ca.create_client_certificate(client_config)

            yield (
                client_pair.certificate_path,
                client_pair.private_key_path,
                ca_pair.certificate_path,
            )

        finally:
            # Cleanup
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_security_manager_creates_ssl_context_with_client_certs(self, temp_cert_files):
        """Test SecurityManager creates SSL context with client certificates."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context with client certificates
        ssl_context = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            ca_cert_file=ca_path,
            verify_mode='CERT_NONE'
        )
        
        # Verify SSL context is created
        assert ssl_context is not None
        assert isinstance(ssl_context, ssl.SSLContext)
        assert ssl_context.verify_mode == ssl.CERT_NONE
        assert ssl_context.check_hostname is False

    def test_security_manager_ssl_context_with_verify_none_and_client_certs(self, temp_cert_files):
        """Test SecurityManager SSL context with verify=False and client certificates."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration with verify=False
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context
        ssl_context = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            verify_mode='CERT_NONE'
        )
        
        # Verify SSL context properties
        assert ssl_context is not None
        assert ssl_context.verify_mode == ssl.CERT_NONE
        assert ssl_context.check_hostname is False

    def test_security_manager_ssl_context_with_verify_true_and_client_certs(self, temp_cert_files):
        """Test SecurityManager SSL context with verify=True and client certificates."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration with verify=True (need cert_file and key_file for enabled=True with verify)
        ssl_config = SSLConfig(
            enabled=True,
            verify=True,
            verify_mode="CERT_REQUIRED",
            check_hostname=True,
            cert_file=cert_path,  # Required when enabled=True with verify
            key_file=key_path
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context
        ssl_context = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            ca_cert_file=ca_path,
            verify_mode='CERT_REQUIRED'
        )
        
        # Verify SSL context properties
        assert ssl_context is not None
        assert ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert ssl_context.check_hostname is True

    def test_security_manager_ssl_context_without_client_certs(self, temp_cert_files):
        """Test SecurityManager SSL context without client certificates."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context without client certificates
        ssl_context = security_manager.create_ssl_context(
            context_type='client',
            verify_mode='CERT_NONE'
        )
        
        # Verify SSL context is created
        assert ssl_context is not None
        assert ssl_context.verify_mode == ssl.CERT_NONE
        assert ssl_context.check_hostname is False

    def test_security_manager_ssl_context_server_type(self, temp_cert_files):
        """Test SecurityManager SSL context for server type."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False,
            cert_file=cert_path,
            key_file=key_path
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context for server
        ssl_context = security_manager.create_ssl_context(
            context_type='server',
            cert_file=cert_path,
            key_file=key_path,
            verify_mode='CERT_NONE'
        )
        
        # Verify SSL context is created
        assert ssl_context is not None
        assert isinstance(ssl_context, ssl.SSLContext)

    def test_security_manager_ssl_context_invalid_type(self, temp_cert_files):
        """Test SecurityManager SSL context with invalid context type."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Test invalid context type
        with pytest.raises(Exception):  # Should raise SecurityValidationError
            security_manager.create_ssl_context(
                context_type='invalid',
                client_cert_file=cert_path,
                client_key_file=key_path
            )

    def test_security_manager_ssl_context_caching(self, temp_cert_files):
        """Test SecurityManager SSL context caching."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context first time
        ssl_context1 = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            verify_mode='CERT_NONE'
        )
        
        # Create SSL context second time (should use cache)
        ssl_context2 = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            verify_mode='CERT_NONE'
        )
        
        # Verify both contexts are the same (cached)
        assert ssl_context1 is ssl_context2

    def test_security_manager_ssl_context_different_params(self, temp_cert_files):
        """Test SecurityManager SSL context with different parameters."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Create SSL context with CERT_NONE
        ssl_context1 = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            verify_mode='CERT_NONE'
        )
        
        # Create SSL context with CERT_REQUIRED
        ssl_context2 = security_manager.create_ssl_context(
            context_type='client',
            client_cert_file=cert_path,
            client_key_file=key_path,
            verify_mode='CERT_REQUIRED'
        )
        
        # Verify contexts are different (different cache keys)
        assert ssl_context1 is not ssl_context2
        assert ssl_context1.verify_mode == ssl.CERT_NONE
        assert ssl_context2.verify_mode == ssl.CERT_REQUIRED

    def test_security_manager_ssl_context_error_handling(self, temp_cert_files):
        """Test SecurityManager SSL context error handling."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Test with non-existent certificate file
        with pytest.raises(Exception):  # Should raise SSLConfigurationError
            security_manager.create_ssl_context(
                context_type='client',
                client_cert_file='nonexistent.crt',
                client_key_file=key_path,
                verify_mode='CERT_NONE'
            )

    def test_security_manager_ssl_context_comprehensive(self, temp_cert_files):
        """Test SecurityManager SSL context comprehensive scenario."""
        cert_path, key_path, ca_path = temp_cert_files
        
        # Create configuration
        ssl_config = SSLConfig(
            enabled=True,
            verify=False,
            verify_mode="CERT_NONE",
            check_hostname=False,
            client_cert_file=cert_path,
            client_key_file=key_path,
            ca_cert_file=ca_path
        )
        permission_config = PermissionConfig(enabled=False)
        security_config = SecurityConfig(ssl=ssl_config, permissions=permission_config)
        
        # Create SecurityManager
        security_manager = SecurityManager(security_config)
        
        # Test various scenarios
        scenarios = [
            {
                'context_type': 'client',
                'client_cert_file': cert_path,
                'client_key_file': key_path,
                'ca_cert_file': ca_path,
                'verify_mode': 'CERT_NONE'
            },
            {
                'context_type': 'client',
                'client_cert_file': cert_path,
                'client_key_file': key_path,
                'verify_mode': 'CERT_REQUIRED'
            },
            {
                'context_type': 'client',
                'verify_mode': 'CERT_NONE'
            }
        ]
        
        for scenario in scenarios:
            ssl_context = security_manager.create_ssl_context(**scenario)
            assert ssl_context is not None
            assert isinstance(ssl_context, ssl.SSLContext)
