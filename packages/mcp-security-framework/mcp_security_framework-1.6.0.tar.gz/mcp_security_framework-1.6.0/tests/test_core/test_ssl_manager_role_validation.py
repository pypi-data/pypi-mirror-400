"""
SSL Manager Role Validation Test Module

This module provides comprehensive unit tests for SSLManager role validation
with real certificates.

Test Classes:
    TestSSLManagerRoleValidation: Tests for SSLManager role validation

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import os
import tempfile
from pathlib import Path

import pytest

from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.core.ssl_manager import SSLManager
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    SSLConfig,
)


class TestSSLManagerRoleValidation:
    """Test suite for SSLManager role validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cert_storage = self.temp_dir / "certs"
        self.key_storage = self.temp_dir / "keys"
        self.cert_storage.mkdir()
        self.key_storage.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_certificates(self) -> dict:
        """Create test CA and client certificates."""
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
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager = CertificateManager(cert_config)
        ca_pair = cert_manager.create_root_ca(ca_config)
        
        # Create client certificates
        cert_config_with_ca = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager_with_ca = CertificateManager(cert_config_with_ca)
        
        client_config_base = {
            "organization": "Test Org",
            "country": "US",
            "ca_cert_path": ca_pair.certificate_path,
            "ca_key_path": ca_pair.private_key_path,
        }
        
        certificates = {
            "ca": ca_pair,
            "chunker": cert_manager_with_ca.create_client_certificate(
                ClientCertConfig(common_name="chunker_client", roles=["chunker"], **client_config_base)
            ),
            "embedder": cert_manager_with_ca.create_client_certificate(
                ClientCertConfig(common_name="embedder_client", roles=["embedder"], **client_config_base)
            ),
            "techsup": cert_manager_with_ca.create_client_certificate(
                ClientCertConfig(common_name="techsup_client", roles=["techsup"], **client_config_base)
            ),
            "multiple": cert_manager_with_ca.create_client_certificate(
                ClientCertConfig(
                    common_name="multi_client",
                    roles=["chunker", "embedder", "databaser"],
                    **client_config_base
                )
            ),
        }
        
        return certificates

    def test_validate_certificate_no_role_restrictions(self):
        """Test SSLManager.validate_certificate without role restrictions."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(certs["chunker"].certificate_path)
        
        assert is_valid is True

    def test_validate_certificate_with_allow_roles_success(self):
        """Test SSLManager.validate_certificate with allow_roles - success."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["chunker", "embedder"],
        )
        
        assert is_valid is True

    def test_validate_certificate_with_allow_roles_failure(self):
        """Test SSLManager.validate_certificate with allow_roles - failure."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["embedder", "databaser"],
        )
        
        assert is_valid is False

    def test_validate_certificate_with_deny_roles_success(self):
        """Test SSLManager.validate_certificate with deny_roles - success."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        )
        
        assert is_valid is True

    def test_validate_certificate_with_deny_roles_failure(self):
        """Test SSLManager.validate_certificate with deny_roles - failure."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(
            certs["techsup"].certificate_path,
            deny_roles=["techsup"],
        )
        
        assert is_valid is False

    def test_validate_certificate_chain_with_roles(self):
        """Test SSLManager.validate_certificate_chain with roles."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        # Success case
        is_valid = ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["chunker"],
        )
        assert is_valid is True
        
        # Failure case
        is_valid = ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["embedder"],
        )
        assert is_valid is False

    def test_validate_certificate_deny_priority(self):
        """Test that deny_roles has priority in SSLManager."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        is_valid = ssl_manager.validate_certificate(
            certs["techsup"].certificate_path,
            allow_roles=["techsup", "chunker"],
            deny_roles=["techsup"],
        )
        
        assert is_valid is False

    def test_validate_certificate_all_scenarios(self):
        """Test all validation scenarios with SSLManager."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)  # Disabled for validation-only tests
        ssl_manager = SSLManager(ssl_config)
        
        # Scenario 1: No restrictions (POSITIVE)
        assert ssl_manager.validate_certificate(certs["chunker"].certificate_path) is True
        
        # Scenario 2: Allow only - success (POSITIVE)
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Scenario 3: Allow only - failure (NEGATIVE)
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        
        # Scenario 4: Deny only - success (POSITIVE)
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Scenario 5: Deny only - failure (NEGATIVE)
        assert ssl_manager.validate_certificate(
            certs["techsup"].certificate_path,
            deny_roles=["techsup"],
        ) is False
        
        # Scenario 6: Both - success (POSITIVE)
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["techsup"],
        ) is True
        
        # Scenario 7: Both - failure (denied role) (NEGATIVE)
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["databaser"],
        ) is False

    def test_validate_certificate_comprehensive_real_certificates(self):
        """Comprehensive positive/negative tests with real certificates via SSLManager."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)
        ssl_manager = SSLManager(ssl_config)
        
        # ========== POSITIVE TESTS ==========
        
        # Test 1: Single role - allow matches
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Test 2: Single role - deny doesn't match
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Test 3: Multiple roles - allow matches one
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Test 4: Multiple roles - allow matches multiple
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker", "embedder"],
        ) is True
        
        # Test 5: Multiple roles - deny doesn't match
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Test 6: Both - allow matches, deny doesn't
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["techsup"],
        ) is True
        
        # ========== NEGATIVE TESTS ==========
        
        # Test 7: Single role - allow doesn't match
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        
        # Test 8: Single role - deny matches
        assert ssl_manager.validate_certificate(
            certs["chunker"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Test 9: Multiple roles - allow doesn't match
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["techsup"],
        ) is False
        
        # Test 10: Multiple roles - deny matches one
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Test 11: Multiple roles - deny matches multiple
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            deny_roles=["chunker", "embedder"],
        ) is False
        
        # Test 12: Both - allow doesn't match
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["techsup"],
            deny_roles=["techsup"],
        ) is False
        
        # Test 13: Both - deny matches (priority)
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["chunker", "embedder"],
            deny_roles=["chunker"],  # Deny has priority
        ) is False
        
        # Test 14: Both - allow matches but deny also matches
        assert ssl_manager.validate_certificate(
            certs["multiple"].certificate_path,
            allow_roles=["databaser"],
            deny_roles=["databaser"],  # Both match, deny wins
        ) is False

    def test_validate_certificate_chain_comprehensive(self):
        """Comprehensive tests for validate_certificate_chain with roles via SSLManager."""
        certs = self.create_test_certificates()
        
        ssl_config = SSLConfig(enabled=False)
        ssl_manager = SSLManager(ssl_config)
        
        # ========== POSITIVE TESTS ==========
        
        # Test 1: No role restrictions
        assert ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
        ) is True
        
        # Test 2: Allow matches
        assert ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Test 3: Deny doesn't match
        assert ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Test 4: Both - allow matches, deny doesn't
        assert ssl_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["techsup"],
        ) is True
        
        # ========== NEGATIVE TESTS ==========
        
        # Test 5: Allow doesn't match
        assert ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        
        # Test 6: Deny matches
        assert ssl_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            certs["ca"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Test 7: Both - allow doesn't match
        assert ssl_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["techsup"],
            deny_roles=["techsup"],
        ) is False
        
        # Test 8: Both - deny matches (priority)
        assert ssl_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            certs["ca"].certificate_path,
            allow_roles=["chunker", "embedder"],
            deny_roles=["chunker"],  # Deny has priority
        ) is False

