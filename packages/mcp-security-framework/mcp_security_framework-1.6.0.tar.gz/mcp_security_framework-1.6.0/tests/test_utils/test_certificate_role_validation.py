"""
Certificate Role Validation Test Module

This module provides comprehensive unit tests for certificate role validation
mechanisms in the MCP Security Framework, including allow/deny role lists,
priority handling, and integration with real certificates.

Test Classes:
    TestValidateCertificateRoles: Tests for validate_certificate_roles function
    TestValidateCertificateChainWithRoles: Tests for validate_certificate_chain with roles
    TestRealCertificatesWithRoles: Tests with real generated certificates

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import os
import tempfile
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
)
from mcp_security_framework.utils.cert_utils import (
    CertificateError,
    extract_roles_from_certificate,
    validate_certificate_chain,
    validate_certificate_roles,
)


class TestValidateCertificateRoles:
    """Test suite for validate_certificate_roles function."""

    def test_validate_roles_no_restrictions(self):
        """Test validation with no restrictions (both None)."""
        cert_roles = ["chunker", "embedder"]
        is_valid, error = validate_certificate_roles(cert_roles, None, None)

        assert is_valid is True
        assert error is None

    def test_validate_roles_allow_only_success(self):
        """Test validation with allow_roles only - success case."""
        cert_roles = ["chunker", "embedder"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=["chunker", "databaser"], deny_roles=None
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_allow_only_failure(self):
        """Test validation with allow_roles only - failure case."""
        cert_roles = ["chunker", "embedder"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=["databaser", "databasew"], deny_roles=None
        )

        assert is_valid is False
        assert error is not None
        assert "required roles" in error.lower()

    def test_validate_roles_deny_only_success(self):
        """Test validation with deny_roles only - success case."""
        cert_roles = ["chunker", "embedder"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["techsup", "databaser"]
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_deny_only_failure(self):
        """Test validation with deny_roles only - failure case."""
        cert_roles = ["chunker", "techsup"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["techsup"]
        )

        assert is_valid is False
        assert error is not None
        assert "denied roles" in error.lower()
        assert "techsup" in error.lower()

    def test_validate_roles_both_allow_and_deny_success(self):
        """Test validation with both allow and deny - success case."""
        cert_roles = ["chunker", "embedder"]
        is_valid, error = validate_certificate_roles(
            cert_roles,
            allow_roles=["chunker", "embedder", "databaser"],
            deny_roles=["techsup"],
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_deny_priority_over_allow(self):
        """Test that deny_roles has priority over allow_roles."""
        cert_roles = ["chunker", "techsup"]
        is_valid, error = validate_certificate_roles(
            cert_roles,
            allow_roles=["chunker", "techsup"],  # techsup is allowed
            deny_roles=["techsup"],  # but also denied - should fail
        )

        assert is_valid is False
        assert error is not None
        assert "denied roles" in error.lower()
        assert "techsup" in error.lower()

    def test_validate_roles_case_insensitive(self):
        """Test that role validation is case-insensitive."""
        cert_roles = ["Chunker", "EMBEDDER"]
        is_valid, error = validate_certificate_roles(
            cert_roles,
            allow_roles=["chunker", "embedder"],
            deny_roles=["TECHSUP"],
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_empty_cert_roles_with_allow(self):
        """Test validation with empty certificate roles but allow_roles required."""
        cert_roles = []
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=["chunker"], deny_roles=None
        )

        assert is_valid is False
        assert error is not None

    def test_validate_roles_empty_cert_roles_with_deny(self):
        """Test validation with empty certificate roles and deny_roles."""
        cert_roles = []
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["techsup"]
        )

        assert is_valid is True  # No denied roles found
        assert error is None

    def test_validate_roles_multiple_denied_roles(self):
        """Test validation with multiple denied roles."""
        cert_roles = ["chunker", "techsup", "databaser"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["techsup", "databaser"]
        )

        assert is_valid is False
        assert error is not None
        assert "techsup" in error.lower()
        assert "databaser" in error.lower()

    def test_validate_roles_whitespace_handling(self):
        """Test that whitespace in roles is handled correctly."""
        cert_roles = ["  chunker  ", " embedder "]
        is_valid, error = validate_certificate_roles(
            cert_roles,
            allow_roles=["chunker", "embedder"],
            deny_roles=None,
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_with_wildcard_allow(self):
        """Test that wildcard certificate roles satisfy allow lists."""
        cert_roles = ["*"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=["chunker"], deny_roles=None
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_with_wildcard_deny(self):
        """Test that wildcard certificate roles respect deny lists."""
        cert_roles = ["*"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["techsup"]
        )

        assert is_valid is False
        assert error is not None
        assert "techsup" in error.lower()

    def test_validate_roles_with_allow_wildcard_marker(self):
        """Test that wildcard allow list matches any certificate role."""
        cert_roles = ["chunker"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=["*"], deny_roles=None
        )

        assert is_valid is True
        assert error is None

    def test_validate_roles_with_deny_wildcard_marker(self):
        """Test that wildcard deny list blocks wildcard certificates."""
        cert_roles = ["*"]
        is_valid, error = validate_certificate_roles(
            cert_roles, allow_roles=None, deny_roles=["*"]
        )

        assert is_valid is False
        assert error is not None
        assert "wildcard" in error.lower()


class TestValidateCertificateChainWithRoles:
    """Test suite for validate_certificate_chain with role validation."""

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

    def create_ca_certificate(self) -> tuple:
        """Create a test CA certificate."""
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
        return ca_pair.certificate_path, ca_pair.private_key_path

    def create_client_certificate_with_roles(
        self, roles: list, ca_cert_path: str, ca_key_path: str
    ) -> str:
        """Create a client certificate with specified roles."""
        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )

        cert_manager = CertificateManager(cert_config)

        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=roles,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)
        return cert_pair.certificate_path

    def test_validate_chain_no_role_restrictions(self):
        """Test chain validation without role restrictions."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path, ca_cert_path, None, None, None
        )

        assert is_valid is True

    def test_validate_chain_with_allow_roles_success(self):
        """Test chain validation with allow_roles - success."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker", "embedder"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=["chunker", "databaser"],
            deny_roles=None,
        )

        assert is_valid is True

    def test_validate_chain_with_allow_roles_failure(self):
        """Test chain validation with allow_roles - failure."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=["databaser", "databasew"],
            deny_roles=None,
        )

        assert is_valid is False

    def test_validate_chain_with_deny_roles_success(self):
        """Test chain validation with deny_roles - success."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker", "embedder"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )

        assert is_valid is True

    def test_validate_chain_with_deny_roles_failure(self):
        """Test chain validation with deny_roles - failure."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker", "techsup"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )

        assert is_valid is False

    def test_validate_chain_deny_priority_over_allow(self):
        """Test that deny_roles has priority over allow_roles in chain validation."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker", "techsup"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=["chunker", "techsup"],  # techsup is allowed
            deny_roles=["techsup"],  # but also denied - should fail
        )

        assert is_valid is False

    def test_validate_chain_both_allow_and_deny_success(self):
        """Test chain validation with both allow and deny - success."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker", "embedder"], ca_cert_path, ca_key_path
        )

        is_valid = validate_certificate_chain(
            client_cert_path,
            ca_cert_path,
            None,
            allow_roles=["chunker", "embedder"],
            deny_roles=["techsup"],
        )

        assert is_valid is True

    def test_validate_chain_invalid_chain_with_roles(self):
        """Test that invalid chain fails even with valid roles."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

        # Create certificate with one CA
        client_cert_path = self.create_client_certificate_with_roles(
            ["chunker"], ca_cert_path, ca_key_path
        )

        # Create another CA (different from the one that signed the cert)
        wrong_ca_config = CAConfig(
            common_name="Wrong CA",
            organization="Wrong Org",
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
        wrong_ca_pair = cert_manager.create_root_ca(wrong_ca_config)

        # Try to validate with wrong CA - should fail even with valid roles
        is_valid = validate_certificate_chain(
            client_cert_path,
            wrong_ca_pair.certificate_path,  # Wrong CA
            None,
            allow_roles=["chunker"],  # Role is valid but chain is invalid
            deny_roles=None,
        )

        assert is_valid is False  # Chain validation fails first, before role check


class TestRealCertificatesWithRoles:
    """Test suite with real generated certificates and role validation."""

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
        """Create test CA and client certificates with various roles."""
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

        # Create certificates with different roles
        certificates = {
            "ca": ca_pair,
            "chunker_only": None,
            "embedder_only": None,
            "databaser_only": None,
            "techsup_only": None,
            "multiple_roles": None,
            "all_roles": None,
        }

        client_config_base = {
            "organization": "Test Org",
            "country": "US",
            "ca_cert_path": ca_pair.certificate_path,
            "ca_key_path": ca_pair.private_key_path,
        }

        cert_config_with_ca = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )

        cert_manager_with_ca = CertificateManager(cert_config_with_ca)

        # Create chunker certificate
        certificates["chunker_only"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="chunker_client", roles=["chunker"], **client_config_base
            )
        )

        # Create embedder certificate
        certificates["embedder_only"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="embedder_client", roles=["embedder"], **client_config_base
            )
        )

        # Create databaser certificate
        certificates["databaser_only"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="databaser_client",
                roles=["databaser"],
                **client_config_base,
            )
        )

        # Create techsup certificate
        certificates["techsup_only"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="techsup_client", roles=["techsup"], **client_config_base
            )
        )

        # Create certificate with multiple roles
        certificates["multiple_roles"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="multi_role_client",
                roles=["chunker", "embedder", "databaser"],
                **client_config_base,
            )
        )

        # Create certificate with all roles
        all_roles = [
            "other",
            "chunker",
            "embedder",
            "databaser",
            "databasew",
            "techsup",
        ]
        certificates["all_roles"] = cert_manager_with_ca.create_client_certificate(
            ClientCertConfig(
                common_name="all_roles_client", roles=all_roles, **client_config_base
            )
        )

        return certificates

    def test_real_cert_allow_chunker_only(self):
        """Test real certificate with allow_roles for chunker."""
        certs = self.create_test_certificates()

        # Chunker certificate should pass
        is_valid = validate_certificate_chain(
            certs["chunker_only"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["chunker"],
            deny_roles=None,
        )
        assert is_valid is True

        # Embedder certificate should fail
        is_valid = validate_certificate_chain(
            certs["embedder_only"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["chunker"],
            deny_roles=None,
        )
        assert is_valid is False

    def test_real_cert_deny_techsup(self):
        """Test real certificate with deny_roles for techsup."""
        certs = self.create_test_certificates()

        # Techsup certificate should fail
        is_valid = validate_certificate_chain(
            certs["techsup_only"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )
        assert is_valid is False

        # Chunker certificate should pass
        is_valid = validate_certificate_chain(
            certs["chunker_only"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )
        assert is_valid is True

    def test_real_cert_multiple_roles_allow(self):
        """Test real certificate with multiple roles and allow_roles."""
        certs = self.create_test_certificates()

        # Certificate with chunker, embedder, databaser
        is_valid = validate_certificate_chain(
            certs["multiple_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["chunker", "embedder"],
            deny_roles=None,
        )
        assert is_valid is True

        # Should also pass with databaser in allow list
        is_valid = validate_certificate_chain(
            certs["multiple_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["databaser"],
            deny_roles=None,
        )
        assert is_valid is True

    def test_real_cert_multiple_roles_deny(self):
        """Test real certificate with multiple roles and deny_roles."""
        certs = self.create_test_certificates()

        # Certificate with chunker, embedder, databaser - deny techsup (not present)
        is_valid = validate_certificate_chain(
            certs["multiple_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )
        assert is_valid is True

        # Deny one of the roles that is present
        is_valid = validate_certificate_chain(
            certs["multiple_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=None,
            deny_roles=["chunker"],
        )
        assert is_valid is False

    def test_real_cert_all_roles_validation(self):
        """Test certificate with all roles against various restrictions."""
        certs = self.create_test_certificates()

        # Should pass with allow for any role
        is_valid = validate_certificate_chain(
            certs["all_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["chunker"],
            deny_roles=None,
        )
        assert is_valid is True

        # Should fail if techsup is denied (it's in the cert)
        is_valid = validate_certificate_chain(
            certs["all_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=None,
            deny_roles=["techsup"],
        )
        assert is_valid is False

        # Should fail even if techsup is allowed but also denied (deny priority)
        is_valid = validate_certificate_chain(
            certs["all_roles"].certificate_path,
            certs["ca"].certificate_path,
            None,
            allow_roles=["techsup", "chunker"],
            deny_roles=["techsup"],
        )
        assert is_valid is False

    def test_real_cert_extract_and_validate_roles(self):
        """Test extracting roles from real certificate and validating."""
        certs = self.create_test_certificates()

        # Extract roles from multiple_roles certificate
        roles = extract_roles_from_certificate(
            certs["multiple_roles"].certificate_path, validate=True
        )

        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles

        # Validate extracted roles
        is_valid, error = validate_certificate_roles(
            roles, allow_roles=["chunker"], deny_roles=None
        )
        assert is_valid is True

        is_valid, error = validate_certificate_roles(
            roles, allow_roles=None, deny_roles=["chunker"]
        )
        assert is_valid is False

    def test_real_cert_comprehensive_positive_negative_pairs(self):
        """Comprehensive positive/negative test pairs on real certificates."""
        certs = self.create_test_certificates()

        # ========== POSITIVE TESTS ==========

        # Test 1: Single role cert with matching allow - POSITIVE
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is True
        )

        # Test 2: Single role cert with non-matching allow - NEGATIVE
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["embedder"],
                deny_roles=None,
            )
            is False
        )

        # Test 3: Single role cert with deny for different role - POSITIVE
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup"],
            )
            is True
        )

        # Test 4: Single role cert with deny for same role - NEGATIVE
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["chunker"],
            )
            is False
        )

        # Test 5: Multiple roles cert with allow matching one role - POSITIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is True
        )

        # Test 6: Multiple roles cert with allow not matching any - NEGATIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["techsup"],
                deny_roles=None,
            )
            is False
        )

        # Test 7: Multiple roles cert with deny for non-present role - POSITIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup"],
            )
            is True
        )

        # Test 8: Multiple roles cert with deny for present role - NEGATIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["embedder"],
            )
            is False
        )

        # Test 9: Both allow and deny, allow matches, deny doesn't - POSITIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=["techsup"],
            )
            is True
        )

        # Test 10: Both allow and deny, allow matches but deny also matches - NEGATIVE (deny priority)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker", "embedder"],
                deny_roles=["chunker"],  # Deny has priority
            )
            is False
        )

        # Test 11: Both allow and deny, allow doesn't match - NEGATIVE
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["techsup"],
                deny_roles=["databaser"],
            )
            is False
        )

    def test_real_cert_all_individual_roles_positive_negative(self):
        """Test each individual role certificate with positive and negative cases."""
        certs = self.create_test_certificates()

        # Chunker certificate
        # POSITIVE: allow chunker
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is True
        )
        # NEGATIVE: allow different role
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["embedder"],
                deny_roles=None,
            )
            is False
        )
        # POSITIVE: deny different role
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup"],
            )
            is True
        )
        # NEGATIVE: deny same role
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["chunker"],
            )
            is False
        )

        # Embedder certificate
        # POSITIVE: allow embedder
        assert (
            validate_certificate_chain(
                certs["embedder_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["embedder"],
                deny_roles=None,
            )
            is True
        )
        # NEGATIVE: allow different role
        assert (
            validate_certificate_chain(
                certs["embedder_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is False
        )
        # NEGATIVE: deny same role
        assert (
            validate_certificate_chain(
                certs["embedder_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["embedder"],
            )
            is False
        )

        # Databaser certificate
        # POSITIVE: allow databaser
        assert (
            validate_certificate_chain(
                certs["databaser_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["databaser"],
                deny_roles=None,
            )
            is True
        )
        # NEGATIVE: allow different role
        assert (
            validate_certificate_chain(
                certs["databaser_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is False
        )
        # NEGATIVE: deny same role
        assert (
            validate_certificate_chain(
                certs["databaser_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["databaser"],
            )
            is False
        )

        # Techsup certificate
        # POSITIVE: allow techsup
        assert (
            validate_certificate_chain(
                certs["techsup_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["techsup"],
                deny_roles=None,
            )
            is True
        )
        # NEGATIVE: allow different role
        assert (
            validate_certificate_chain(
                certs["techsup_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is False
        )
        # NEGATIVE: deny same role
        assert (
            validate_certificate_chain(
                certs["techsup_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup"],
            )
            is False
        )

    def test_real_cert_multiple_roles_all_combinations(self):
        """Test multiple roles certificate with all possible combinations."""
        certs = self.create_test_certificates()
        # Certificate has: chunker, embedder, databaser

        # POSITIVE: allow chunker (one of the roles)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=None,
            )
            is True
        )

        # POSITIVE: allow embedder (one of the roles)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["embedder"],
                deny_roles=None,
            )
            is True
        )

        # POSITIVE: allow databaser (one of the roles)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["databaser"],
                deny_roles=None,
            )
            is True
        )

        # POSITIVE: allow multiple roles from cert
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker", "embedder"],
                deny_roles=None,
            )
            is True
        )

        # NEGATIVE: allow role not in cert
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["techsup"],
                deny_roles=None,
            )
            is False
        )

        # NEGATIVE: allow role not in cert (databasew)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["databasew"],
                deny_roles=None,
            )
            is False
        )

        # POSITIVE: deny role not in cert
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup"],
            )
            is True
        )

        # NEGATIVE: deny chunker (present in cert)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["chunker"],
            )
            is False
        )

        # NEGATIVE: deny embedder (present in cert)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["embedder"],
            )
            is False
        )

        # NEGATIVE: deny databaser (present in cert)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["databaser"],
            )
            is False
        )

        # NEGATIVE: deny multiple roles, one present
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup", "chunker"],  # chunker is present
            )
            is False
        )

        # POSITIVE: allow matches, deny doesn't
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=["techsup"],
            )
            is True
        )

        # NEGATIVE: allow matches but deny also matches (deny priority)
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker", "embedder"],
                deny_roles=["chunker"],  # Deny has priority
            )
            is False
        )

        # NEGATIVE: allow doesn't match
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["techsup"],
                deny_roles=["techsup"],
            )
            is False
        )

    def test_real_cert_all_roles_comprehensive(self):
        """Comprehensive tests for certificate with all roles."""
        certs = self.create_test_certificates()
        # Certificate has: other, chunker, embedder, databaser, databasew, techsup

        # Test each role individually - POSITIVE
        for role in [
            "other",
            "chunker",
            "embedder",
            "databaser",
            "databasew",
            "techsup",
        ]:
            assert (
                validate_certificate_chain(
                    certs["all_roles"].certificate_path,
                    certs["ca"].certificate_path,
                    None,
                    allow_roles=[role],
                    deny_roles=None,
                )
                is True
            ), f"Should allow {role}"

        # Test denying each role individually - NEGATIVE
        for role in [
            "other",
            "chunker",
            "embedder",
            "databaser",
            "databasew",
            "techsup",
        ]:
            assert (
                validate_certificate_chain(
                    certs["all_roles"].certificate_path,
                    certs["ca"].certificate_path,
                    None,
                    allow_roles=None,
                    deny_roles=[role],
                )
                is False
            ), f"Should deny {role}"

        # POSITIVE: Allow multiple roles
        assert (
            validate_certificate_chain(
                certs["all_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker", "embedder", "databaser"],
                deny_roles=None,
            )
            is True
        )

        # NEGATIVE: Deny multiple roles (all present)
        assert (
            validate_certificate_chain(
                certs["all_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["chunker", "embedder"],
            )
            is False
        )

        # NEGATIVE: Allow matches but deny also matches (deny priority)
        assert (
            validate_certificate_chain(
                certs["all_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker", "techsup"],
                deny_roles=["techsup"],  # Deny has priority
            )
            is False
        )

        # POSITIVE: Allow matches, deny doesn't
        assert (
            validate_certificate_chain(
                certs["all_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=["invalid_role"],  # Not a valid role, but should still work
            )
            is True
        )

    def test_real_cert_edge_cases(self):
        """Test edge cases with real certificates."""
        certs = self.create_test_certificates()

        # Edge case 1: Empty allow list (should fail)
        # Note: This is technically invalid, but we test it
        # Actually, empty list means no roles allowed, so should fail
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=[],  # Empty list
                deny_roles=None,
            )
            is False
        )

        # Edge case 2: Empty deny list (should pass if allow matches)
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["chunker"],
                deny_roles=[],  # Empty list
            )
            is True
        )

        # Edge case 3: Both empty lists (should pass - no restrictions)
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=[],  # Empty
                deny_roles=[],  # Empty
            )
            is False
        )  # Empty allow means no roles allowed

        # Edge case 4: Case sensitivity - should be case-insensitive
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["CHUNKER"],  # Uppercase
                deny_roles=None,
            )
            is True
        )

        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["Chunker"],  # Mixed case
                deny_roles=None,
            )
            is True
        )

        # Edge case 5: Whitespace in roles
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["  chunker  "],  # With whitespace
                deny_roles=None,
            )
            is True
        )

        # Edge case 6: Multiple deny roles, one matches
        assert (
            validate_certificate_chain(
                certs["multiple_roles"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=None,
                deny_roles=["techsup", "invalid", "chunker"],  # chunker matches
            )
            is False
        )

        # Edge case 7: Multiple allow roles, none match
        assert (
            validate_certificate_chain(
                certs["chunker_only"].certificate_path,
                certs["ca"].certificate_path,
                None,
                allow_roles=["embedder", "databaser", "techsup"],  # None match
                deny_roles=None,
            )
            is False
        )
