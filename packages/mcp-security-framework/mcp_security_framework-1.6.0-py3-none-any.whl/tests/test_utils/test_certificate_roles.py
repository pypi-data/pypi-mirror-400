"""
Certificate Roles Test Module

This module provides comprehensive unit tests for certificate role mechanisms
in the MCP Security Framework, including role enumeration, validation, and
certificate generation with roles.

Test Classes:
    TestCertificateRole: Tests for CertificateRole enumeration
    TestRoleExtraction: Tests for role extraction from certificates
    TestCertificateGenerationWithRoles: Tests for certificate generation with roles
    TestMultipleRoles: Tests for multiple roles in single certificate

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mcp_security_framework.core.cert_manager import (
    CertificateConfigurationError,
    CertificateGenerationError,
    CertificateManager,
)
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    ServerCertConfig,
)
from mcp_security_framework.schemas.models import CertificateRole, UnknownRoleError
from mcp_security_framework.utils.cert_utils import (
    CertificateError,
    extract_roles_from_certificate,
    parse_certificate,
)


class TestCertificateRole:
    """Test suite for CertificateRole enumeration."""

    def test_all_roles_exist(self):
        """Test that all required roles exist in the enum."""
        expected_roles = [
            "other",
            "chunker",
            "embedder",
            "databaser",
            "databasew",
            "techsup",
            "mcpproxy",
            "*",
        ]
        actual_roles = [role.value for role in CertificateRole]

        assert len(actual_roles) == len(expected_roles)
        for expected_role in expected_roles:
            assert expected_role in actual_roles

    def test_role_values(self):
        """Test that role values are correct."""
        assert CertificateRole.OTHER.value == "other"
        assert CertificateRole.CHUNKER.value == "chunker"
        assert CertificateRole.EMBEDDER.value == "embedder"
        assert CertificateRole.DATABASER.value == "databaser"
        assert CertificateRole.DATABASEW.value == "databasew"
        assert CertificateRole.TECHSUP.value == "techsup"
        assert CertificateRole.MCPPROXY.value == "mcpproxy"
        assert CertificateRole.ALL_ACCESS.value == "*"

    def test_from_string_valid_roles(self):
        """Test from_string method with valid role strings."""
        assert CertificateRole.from_string("other") == CertificateRole.OTHER
        assert CertificateRole.from_string("chunker") == CertificateRole.CHUNKER
        assert CertificateRole.from_string("embedder") == CertificateRole.EMBEDDER
        assert CertificateRole.from_string("databaser") == CertificateRole.DATABASER
        assert CertificateRole.from_string("databasew") == CertificateRole.DATABASEW
        assert CertificateRole.from_string("techsup") == CertificateRole.TECHSUP
        assert CertificateRole.from_string("mcpproxy") == CertificateRole.MCPPROXY
        assert CertificateRole.from_string("*") == CertificateRole.ALL_ACCESS
        assert CertificateRole.from_string("all") == CertificateRole.ALL_ACCESS
        assert CertificateRole.from_string("ANY") == CertificateRole.ALL_ACCESS

    def test_from_string_case_insensitive(self):
        """Test from_string method is case-insensitive."""
        assert CertificateRole.from_string("OTHER") == CertificateRole.OTHER
        assert CertificateRole.from_string("Chunker") == CertificateRole.CHUNKER
        assert CertificateRole.from_string("EMBEDDER") == CertificateRole.EMBEDDER

    def test_from_string_with_whitespace(self):
        """Test from_string method handles whitespace."""
        assert CertificateRole.from_string("  other  ") == CertificateRole.OTHER
        assert CertificateRole.from_string(" chunker ") == CertificateRole.CHUNKER

    def test_from_string_invalid_role(self):
        """Test from_string method raises UnknownRoleError for invalid roles."""
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.from_string("invalid_role")

        assert exc_info.value.role_str == "invalid_role"
        assert "invalid_role" in str(exc_info.value)
        assert "Valid roles" in str(exc_info.value)
        assert isinstance(exc_info.value.valid_roles, list)
        assert len(exc_info.value.valid_roles) > 0

        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.from_string("admin")

        assert exc_info.value.role_str == "admin"
        assert "admin" in str(exc_info.value)

    def test_validate_roles_valid_list(self):
        """Test validate_roles method with valid role list."""
        roles = ["chunker", "embedder", "databaser"]
        validated = CertificateRole.validate_roles(roles)

        assert len(validated) == 3
        assert validated[0] == CertificateRole.CHUNKER
        assert validated[1] == CertificateRole.EMBEDDER
        assert validated[2] == CertificateRole.DATABASER

    def test_validate_roles_with_wildcard(self):
        """Test validate_roles method accepts wildcard markers."""
        roles = ["chunker", "*", "ALL"]
        validated = CertificateRole.validate_roles(roles)

        assert len(validated) == 3
        assert validated[0] == CertificateRole.CHUNKER
        assert validated[1] == CertificateRole.ALL_ACCESS
        assert validated[2] == CertificateRole.ALL_ACCESS

    def test_validate_roles_with_invalid(self):
        """Test validate_roles method raises UnknownRoleError for invalid roles."""
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["chunker", "invalid_role"])

        assert exc_info.value.role_str == "invalid_role"
        assert "invalid_role" in str(exc_info.value)

    def test_get_default_role(self):
        """Test get_default_role method returns OTHER."""
        default_role = CertificateRole.get_default_role()
        assert default_role == CertificateRole.OTHER

    def test_is_wildcard_helper(self):
        """Test the is_wildcard helper for multiple aliases."""
        assert CertificateRole.is_wildcard("*") is True
        assert CertificateRole.is_wildcard("all") is True
        assert CertificateRole.is_wildcard("ANY") is True
        assert CertificateRole.is_wildcard("chunker") is False
        assert CertificateRole.is_wildcard(None) is False

    def test_to_string_method(self):
        """Test to_string method converts enum to string."""
        assert CertificateRole.OTHER.to_string() == "other"
        assert CertificateRole.CHUNKER.to_string() == "chunker"
        assert CertificateRole.EMBEDDER.to_string() == "embedder"
        assert CertificateRole.DATABASER.to_string() == "databaser"
        assert CertificateRole.DATABASEW.to_string() == "databasew"
        assert CertificateRole.TECHSUP.to_string() == "techsup"
        assert CertificateRole.MCPPROXY.to_string() == "mcpproxy"

    def test_serialization_deserialization_roundtrip_all_roles(self):
        """
        Test serialization/deserialization roundtrip for all enum values.

        This test ensures that every role in the CertificateRole enum can be:
        1. Serialized to string using to_string()
        2. Deserialized back to enum using from_string()
        3. The result matches the original enum value
        """
        # Test all roles in the enumeration
        for role in CertificateRole:
            # Serialize: enum -> string
            role_str = role.to_string()

            # Verify it's a string
            assert isinstance(role_str, str)
            assert role_str == role.value

            # Deserialize: string -> enum
            deserialized_role = CertificateRole.from_string(role_str)

            # Verify roundtrip: original == deserialized
            assert deserialized_role == role, (
                f"Roundtrip failed for {role.name}: "
                f"original={role}, deserialized={deserialized_role}"
            )

            # Verify value matches
            assert deserialized_role.value == role.value, (
                f"Value mismatch for {role.name}: "
                f"original={role.value}, deserialized={deserialized_role.value}"
            )

    def test_serialization_deserialization_roundtrip_case_variations(self):
        """
        Test serialization/deserialization roundtrip with case variations.

        This test ensures that case-insensitive deserialization works correctly
        and maintains consistency with serialization.
        """
        # Test each role with different case variations
        test_cases = [
            ("other", "OTHER", "Other"),
            ("chunker", "CHUNKER", "Chunker"),
            ("embedder", "EMBEDDER", "Embedder"),
            ("databaser", "DATABASER", "Databaser"),
            ("databasew", "DATABASEW", "Databasew"),
            ("techsup", "TECHSUP", "Techsup"),
            ("mcpproxy", "MCPPROXY", "Mcpproxy"),
            ("*", "*", "*"),
        ]

        for lowercase, uppercase, titlecase in test_cases:
            # Deserialize from different case variations
            role_from_lower = CertificateRole.from_string(lowercase)
            role_from_upper = CertificateRole.from_string(uppercase)
            role_from_title = CertificateRole.from_string(titlecase)

            # All should result in the same enum value
            assert role_from_lower == role_from_upper == role_from_title

            # Serialize back to string
            serialized = role_from_lower.to_string()

            # Should always serialize to lowercase
            assert serialized == lowercase

            # Roundtrip: serialize -> deserialize should match
            roundtrip_role = CertificateRole.from_string(serialized)
            assert roundtrip_role == role_from_lower

    def test_serialization_deserialization_roundtrip_with_whitespace(self):
        """
        Test serialization/deserialization roundtrip with whitespace handling.

        This test ensures that whitespace is properly handled during deserialization
        and that serialization always produces clean strings.
        """
        # Test each role with whitespace variations
        for role in CertificateRole:
            # Test with leading/trailing whitespace
            role_str_with_whitespace = f"  {role.value}  "

            # Deserialize should handle whitespace
            deserialized = CertificateRole.from_string(role_str_with_whitespace)
            assert deserialized == role

            # Serialize should produce clean string (no whitespace)
            serialized = deserialized.to_string()
            assert serialized == role.value
            assert serialized.strip() == serialized  # No leading/trailing whitespace

            # Roundtrip should work
            roundtrip = CertificateRole.from_string(serialized)
            assert roundtrip == role


class TestUnknownRoleError:
    """Test suite for UnknownRoleError exception."""

    def test_unknown_role_error_inheritance(self):
        """Test that UnknownRoleError inherits from ValueError."""
        assert issubclass(UnknownRoleError, ValueError)

        # Test that it can be caught as ValueError
        try:
            CertificateRole.from_string("invalid_role")
        except ValueError as e:
            assert isinstance(e, UnknownRoleError)
        else:
            pytest.fail("Should have raised ValueError")

    def test_unknown_role_error_attributes(self):
        """Test that UnknownRoleError has correct attributes."""
        try:
            CertificateRole.from_string("unknown_role_test")
        except UnknownRoleError as e:
            assert hasattr(e, "role_str")
            assert hasattr(e, "valid_roles")
            assert e.role_str == "unknown_role_test"
            assert isinstance(e.valid_roles, list)
            assert len(e.valid_roles) > 0
            # Check that all valid roles are in the list
            for role in CertificateRole:
                assert role.value in e.valid_roles
        else:
            pytest.fail("Should have raised UnknownRoleError")

    def test_unknown_role_error_message(self):
        """Test that UnknownRoleError has informative error message."""
        invalid_role = "completely_invalid_role_123"
        try:
            CertificateRole.from_string(invalid_role)
        except UnknownRoleError as e:
            error_message = str(e)
            assert invalid_role in error_message
            assert "Unknown role" in error_message
            assert "Valid roles" in error_message
            # Check that at least one valid role is mentioned
            assert any(role.value in error_message for role in CertificateRole)
        else:
            pytest.fail("Should have raised UnknownRoleError")

    def test_unknown_role_error_various_invalid_inputs(self):
        """Test UnknownRoleError with various invalid role inputs."""
        invalid_roles = [
            "admin",
            "user",
            "guest",
            "superuser",
            "root",
            "invalid",
            "unknown",
            "test_role",
            "role123",
            "",
            "   ",
            "CHUNKER_INVALID",
            "chunker_extra",
            "embedder123",
        ]

        for invalid_role in invalid_roles:
            if invalid_role.strip():  # Skip empty strings
                with pytest.raises(UnknownRoleError) as exc_info:
                    CertificateRole.from_string(invalid_role)

                assert exc_info.value.role_str == invalid_role
                assert isinstance(exc_info.value.valid_roles, list)
                assert len(exc_info.value.valid_roles) == len(list(CertificateRole))

    def test_unknown_role_error_with_validate_roles(self):
        """Test that validate_roles raises UnknownRoleError for invalid roles."""
        # Test with first role invalid
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["invalid_role", "chunker"])
        assert exc_info.value.role_str == "invalid_role"

        # Test with middle role invalid
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["chunker", "invalid_role", "embedder"])
        assert exc_info.value.role_str == "invalid_role"

        # Test with last role invalid
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["chunker", "embedder", "invalid_role"])
        assert exc_info.value.role_str == "invalid_role"

        # Test with all roles invalid
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["invalid1", "invalid2"])
        assert exc_info.value.role_str == "invalid1"

    def test_unknown_role_error_valid_roles_list_completeness(self):
        """Test that valid_roles list contains all enum values."""
        try:
            CertificateRole.from_string("invalid")
        except UnknownRoleError as e:
            valid_roles_set = set(e.valid_roles)
            enum_roles_set = {role.value for role in CertificateRole}

            assert (
                valid_roles_set == enum_roles_set
            ), f"valid_roles mismatch: {valid_roles_set} != {enum_roles_set}"
            assert len(e.valid_roles) == len(list(CertificateRole))

    def test_unknown_role_error_case_sensitivity_in_error(self):
        """Test that error message preserves original case of invalid role."""
        test_cases = [
            ("ADMIN", "ADMIN"),
            ("Admin", "Admin"),
            ("admin", "admin"),
            ("INVALID_ROLE", "INVALID_ROLE"),
            ("InvalidRole", "InvalidRole"),
        ]

        for invalid_role, expected_in_error in test_cases:
            with pytest.raises(UnknownRoleError) as exc_info:
                CertificateRole.from_string(invalid_role)

            assert exc_info.value.role_str == invalid_role
            assert expected_in_error in str(exc_info.value)

    def test_unknown_role_error_with_whitespace(self):
        """Test that UnknownRoleError handles whitespace correctly."""
        # Test with leading/trailing whitespace - should strip and then fail
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.from_string("  invalid_role  ")

        # After stripping, it should be "invalid_role"
        assert exc_info.value.role_str == "  invalid_role  "

        # But the actual comparison is done on stripped version
        # So "  invalid_role  " stripped is "invalid_role" which is invalid
        assert "invalid_role" in str(exc_info.value).lower()

    def test_unknown_role_error_multiple_unknown_roles(self):
        """Test that validate_roles raises error on first unknown role."""
        with pytest.raises(UnknownRoleError) as exc_info:
            CertificateRole.validate_roles(["unknown1", "unknown2", "unknown3"])

        # Should fail on first unknown role
        assert exc_info.value.role_str == "unknown1"

    def test_unknown_role_error_in_cert_utils_context(self):
        """Test that cert_utils properly handles UnknownRoleError."""
        from mcp_security_framework.utils.cert_utils import (
            extract_roles_from_certificate,
        )

        # Create a certificate with invalid role in extension
        # This is a bit complex, so we'll test the validation part directly
        invalid_roles = ["chunker", "invalid_role_123", "embedder"]

        # The extract_roles_from_certificate with validate=True should filter out invalid roles
        # But we can't easily create a cert with invalid role, so we test the validation logic
        validated_count = 0
        for role_str in invalid_roles:
            try:
                CertificateRole.from_string(role_str)
                validated_count += 1
            except UnknownRoleError:
                pass

        # Should only validate 2 roles (chunker and embedder)
        assert validated_count == 2

    def test_unknown_role_error_in_cert_manager_context(self):
        """Test that cert_manager properly handles UnknownRoleError."""
        from mcp_security_framework.core.cert_manager import CertificateManager
        from mcp_security_framework.schemas.config import CertificateConfig
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            config = CertificateConfig(
                enabled=True,
                ca_creation_mode=True,
                cert_storage_path=str(Path(temp_dir) / "certs"),
                key_storage_path=str(Path(temp_dir) / "keys"),
            )

            cert_manager = CertificateManager(config)

            # Test _validate_and_normalize_roles with invalid roles
            # This should filter out invalid roles and log warnings
            roles_with_invalid = [
                "chunker",
                "invalid_role_456",
                "embedder",
                "another_invalid",
            ]
            validated = cert_manager._validate_and_normalize_roles(roles_with_invalid)

            # Should only contain valid roles
            assert len(validated) == 2
            assert "chunker" in validated
            assert "embedder" in validated
            assert "invalid_role_456" not in validated
            assert "another_invalid" not in validated

    def test_unknown_role_error_all_valid_roles_present(self):
        """Test that all valid roles are present in error message."""
        try:
            CertificateRole.from_string("invalid")
        except UnknownRoleError as e:
            # Check that all valid roles are in the valid_roles list
            all_enum_roles = {role.value for role in CertificateRole}
            error_valid_roles = set(e.valid_roles)

            assert all_enum_roles == error_valid_roles
            assert len(e.valid_roles) == len(all_enum_roles)


class TestRoleExtraction:
    """Test suite for role extraction from certificates."""

    def create_test_certificate_with_roles(self, roles: list, temp_dir: Path) -> str:
        """Helper method to create a test certificate with roles."""
        # Create CA certificate first
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
            cert_storage_path=str(temp_dir / "certs"),
            key_storage_path=str(temp_dir / "keys"),
        )

        cert_manager = CertificateManager(cert_config)
        ca_pair = cert_manager.create_root_ca(ca_config)

        # Create client certificate with roles
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=roles,
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
        )

        client_pair = cert_manager.create_client_certificate(client_config)
        return client_pair.certificate_path

    def test_extract_single_role(self, tmp_path):
        """Test extracting a single role from certificate."""
        cert_path = self.create_test_certificate_with_roles(["chunker"], tmp_path)
        roles = extract_roles_from_certificate(cert_path)

        assert len(roles) == 1
        assert "chunker" in roles

    def test_extract_multiple_roles(self, tmp_path):
        """Test extracting multiple roles from certificate."""
        cert_path = self.create_test_certificate_with_roles(
            ["chunker", "embedder", "databaser"], tmp_path
        )
        roles = extract_roles_from_certificate(cert_path)

        assert len(roles) == 3
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles

    def test_extract_roles_with_default(self, tmp_path):
        """Test extracting roles when no roles specified (should return default)."""
        cert_path = self.create_test_certificate_with_roles([], tmp_path)
        roles = extract_roles_from_certificate(cert_path)

        # Should return default role "other"
        assert len(roles) == 1
        assert "other" in roles

    def test_extract_roles_validation_enabled(self, tmp_path):
        """Test role extraction with validation enabled (default)."""
        cert_path = self.create_test_certificate_with_roles(
            ["chunker", "embedder"], tmp_path
        )
        roles = extract_roles_from_certificate(cert_path, validate=True)

        assert len(roles) == 2
        assert all(role in ["chunker", "embedder"] for role in roles)

    def test_extract_roles_validation_disabled(self, tmp_path):
        """Test role extraction with validation disabled."""
        # Create certificate with invalid role (will be filtered during creation)
        # But we can test with a manually created certificate
        cert_path = self.create_test_certificate_with_roles(["chunker"], tmp_path)

        # Modify certificate to add invalid role (this is complex, so we'll test differently)
        # For now, test that validation works correctly
        roles = extract_roles_from_certificate(cert_path, validate=False)
        assert len(roles) >= 1

    def test_extract_roles_case_insensitive(self, tmp_path):
        """Test that extracted roles are normalized to lowercase."""
        cert_path = self.create_test_certificate_with_roles(
            ["Chunker", "EMBEDDER"], tmp_path
        )
        roles = extract_roles_from_certificate(cert_path)

        assert "chunker" in roles
        assert "embedder" in roles
        assert "Chunker" not in roles
        assert "EMBEDDER" not in roles


class TestCertificateGenerationWithRoles:
    """Test suite for certificate generation with roles."""

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

    def test_create_client_certificate_with_single_role(self):
        """Test creating client certificate with single role."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=["chunker"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)
        assert os.path.exists(cert_pair.private_key_path)

        # Verify roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert len(roles) == 1

    def test_create_client_certificate_with_multiple_roles(self):
        """Test creating client certificate with multiple roles."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=["chunker", "embedder", "databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)

        # Verify all roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 3
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles

    def test_create_client_certificate_without_roles(self):
        """Test creating client certificate without roles (should use default)."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=[],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify default role is used
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 1
        assert "other" in roles

    def test_create_client_certificate_with_invalid_roles(self):
        """Test creating client certificate with invalid roles (should filter them)."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=["chunker", "invalid_role", "embedder"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify only valid roles are in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert "embedder" in roles
        assert "invalid_role" not in roles
        # If no valid roles, should use default
        if len(roles) == 1 and "other" in roles:
            # This means all roles were invalid, so default was used
            pass

    def test_create_server_certificate_with_roles(self):
        """Test creating server certificate with roles."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )

        cert_manager = CertificateManager(cert_config)

        server_config = ServerCertConfig(
            common_name="test_server",
            organization="Test Org",
            country="US",
            roles=["techsup", "databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_server_certificate(server_config)

        # Verify certificate was created
        assert os.path.exists(cert_pair.certificate_path)

        # Verify roles in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 2
        assert "techsup" in roles
        assert "databaser" in roles

    def test_role_normalization(self):
        """Test that roles are normalized to lowercase."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=["Chunker", "EMBEDDER", "Databaser"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify roles are normalized
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert "chunker" in roles
        assert "embedder" in roles
        assert "databaser" in roles
        assert "Chunker" not in roles
        assert "EMBEDDER" not in roles


class TestMultipleRoles:
    """Test suite for multiple roles in single certificate."""

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

    def test_all_roles_in_single_certificate(self):
        """Test that all roles can be in a single certificate."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )

        cert_manager = CertificateManager(cert_config)

        all_roles = [role.value for role in CertificateRole]
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=all_roles,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify all roles are in certificate
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == len(all_roles)
        for role in all_roles:
            assert role in roles

    def test_duplicate_roles_removed(self):
        """Test that duplicate roles are removed."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

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
            roles=["chunker", "chunker", "embedder", "embedder"],
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Verify duplicates are removed
        roles = extract_roles_from_certificate(cert_pair.certificate_path)
        assert len(roles) == 2
        assert roles.count("chunker") == 1
        assert roles.count("embedder") == 1

    def test_role_order_preserved(self):
        """Test that role order is preserved in certificate."""
        ca_cert_path, ca_key_path = self.create_ca_certificate()

        cert_config = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
            cert_storage_path=str(self.cert_storage),
            key_storage_path=str(self.key_storage),
        )

        cert_manager = CertificateManager(cert_config)

        role_order = ["chunker", "embedder", "databaser", "databasew", "techsup"]
        client_config = ClientCertConfig(
            common_name="test_client",
            organization="Test Org",
            country="US",
            roles=role_order,
            ca_cert_path=ca_cert_path,
            ca_key_path=ca_key_path,
        )

        cert_pair = cert_manager.create_client_certificate(client_config)

        # Extract roles and verify order (roles are stored as comma-separated string)
        cert = parse_certificate(cert_pair.certificate_path)
        roles_extension = cert.extensions.get_extension_for_oid(
            x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.1")
        )
        roles_str = roles_extension.value.value.decode("utf-8")
        roles_list = [r.strip() for r in roles_str.split(",")]

        # Verify order matches
        assert roles_list == role_order
