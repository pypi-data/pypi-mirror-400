"""
Certificate Role Validation Test Module - Core Level

This module provides comprehensive unit tests for certificate role validation
at the core level (CertificateManager) with real certificates.

Test Classes:
    TestCertificateManagerRoleValidation: Tests for CertificateManager role validation

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
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
)


class TestCertificateManagerRoleValidation:
    """Test suite for CertificateManager role validation."""

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
        
        # Create client certificates with different roles
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
        
        return certificates, cert_manager_with_ca

    def test_validate_chain_no_role_restrictions(self):
        """Test CertificateManager.validate_certificate_chain without role restrictions."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path
        )
        
        assert is_valid is True

    def test_validate_chain_with_allow_roles_success(self):
        """Test CertificateManager.validate_certificate_chain with allow_roles - success."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["chunker", "embedder"],
        )
        
        assert is_valid is True

    def test_validate_chain_with_allow_roles_failure(self):
        """Test CertificateManager.validate_certificate_chain with allow_roles - failure."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["embedder", "databaser"],
        )
        
        assert is_valid is False

    def test_validate_chain_with_deny_roles_success(self):
        """Test CertificateManager.validate_certificate_chain with deny_roles - success."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        )
        
        assert is_valid is True

    def test_validate_chain_with_deny_roles_failure(self):
        """Test CertificateManager.validate_certificate_chain with deny_roles - failure."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            deny_roles=["techsup"],
        )
        
        assert is_valid is False

    def test_validate_chain_deny_priority_over_allow(self):
        """Test that deny_roles has priority over allow_roles."""
        certs, cert_manager = self.create_test_certificates()
        
        # Create certificate with both allowed and denied role
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=certs["ca"].certificate_path,
            ca_key_path=certs["ca"].private_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )
        
        cert_manager_new = CertificateManager(cert_config)
        mixed_cert = cert_manager_new.create_client_certificate(
            ClientCertConfig(
                common_name="mixed_client",
                organization="Test Org",
                country="US",
                roles=["chunker", "techsup"],
                ca_cert_path=certs["ca"].certificate_path,
                ca_key_path=certs["ca"].private_key_path,
            )
        )
        
        is_valid = cert_manager_new.validate_certificate_chain(
            mixed_cert.certificate_path,
            allow_roles=["chunker", "techsup"],  # techsup is allowed
            deny_roles=["techsup"],  # but also denied - should fail
        )
        
        assert is_valid is False

    def test_validate_chain_both_allow_and_deny_success(self):
        """Test CertificateManager.validate_certificate_chain with both - success."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker", "embedder"],
            deny_roles=["techsup"],
        )
        
        assert is_valid is True

    def test_validate_chain_both_allow_and_deny_failure(self):
        """Test CertificateManager.validate_certificate_chain with both - failure."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker", "embedder"],
            deny_roles=["databaser"],  # databaser is in the cert
        )
        
        assert is_valid is False

    def test_validate_chain_with_custom_ca_and_roles(self):
        """Test CertificateManager.validate_certificate_chain with custom CA and roles."""
        certs, cert_manager = self.create_test_certificates()
        
        is_valid = cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            ca_cert_path=certs["ca"].certificate_path,
            allow_roles=["chunker"],
        )
        
        assert is_valid is True

    def test_validate_chain_all_role_scenarios(self):
        """Test all role scenarios with real certificates."""
        certs, cert_manager = self.create_test_certificates()
        
        # Scenario 1: Only allow - chunker passes (POSITIVE)
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Scenario 2: Only allow - embedder fails (NEGATIVE)
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        
        # Scenario 3: Only deny - techsup fails (NEGATIVE)
        assert cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            deny_roles=["techsup"],
        ) is False
        
        # Scenario 4: Only deny - chunker passes (POSITIVE)
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Scenario 5: Both - multiple roles cert passes (POSITIVE)
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["techsup"],
        ) is True
        
        # Scenario 6: Both - multiple roles cert fails (denied role) (NEGATIVE)
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["databaser"],  # databaser is in cert
        ) is False

    def test_validate_chain_comprehensive_real_certificates(self):
        """Comprehensive positive/negative tests with real certificates via CertificateManager."""
        certs, cert_manager = self.create_test_certificates()
        
        # ========== POSITIVE TESTS ==========
        
        # Test 1: Single role - allow matches
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Test 2: Single role - deny doesn't match
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Test 3: Multiple roles - allow matches one
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        
        # Test 4: Multiple roles - deny doesn't match
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        
        # Test 5: Both - allow matches, deny doesn't
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
            deny_roles=["techsup"],
        ) is True
        
        # ========== NEGATIVE TESTS ==========
        
        # Test 6: Single role - allow doesn't match
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        
        # Test 7: Single role - deny matches
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Test 8: Multiple roles - allow doesn't match
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["techsup"],
        ) is False
        
        # Test 9: Multiple roles - deny matches
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Test 10: Both - allow doesn't match
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["techsup"],
            deny_roles=["techsup"],
        ) is False
        
        # Test 11: Both - deny matches (priority)
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker", "embedder"],
            deny_roles=["chunker"],  # Deny has priority
        ) is False
        
        # Test 12: Both - allow matches but deny also matches
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["databaser"],
            deny_roles=["databaser"],  # Both match, deny wins
        ) is False

    def test_validate_chain_each_role_positive_negative(self):
        """Test each role certificate with positive and negative cases via CertificateManager."""
        certs, cert_manager = self.create_test_certificates()
        
        # Chunker certificate
        # POSITIVE
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        # NEGATIVE
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            allow_roles=["embedder"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["chunker"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        
        # Embedder certificate
        # POSITIVE
        assert cert_manager.validate_certificate_chain(
            certs["embedder"].certificate_path,
            allow_roles=["embedder"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["embedder"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        # NEGATIVE
        assert cert_manager.validate_certificate_chain(
            certs["embedder"].certificate_path,
            allow_roles=["chunker"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["embedder"].certificate_path,
            deny_roles=["embedder"],
        ) is False
        
        # Techsup certificate
        # POSITIVE
        assert cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            allow_roles=["techsup"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            deny_roles=["chunker"],
        ) is True
        # NEGATIVE
        assert cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            allow_roles=["chunker"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["techsup"].certificate_path,
            deny_roles=["techsup"],
        ) is False
        
        # Multiple roles certificate
        # POSITIVE
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["chunker"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["embedder"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["databaser"],
        ) is True
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["techsup"],
        ) is True
        # NEGATIVE
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            allow_roles=["techsup"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["chunker"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["embedder"],
        ) is False
        assert cert_manager.validate_certificate_chain(
            certs["multiple"].certificate_path,
            deny_roles=["databaser"],
        ) is False

