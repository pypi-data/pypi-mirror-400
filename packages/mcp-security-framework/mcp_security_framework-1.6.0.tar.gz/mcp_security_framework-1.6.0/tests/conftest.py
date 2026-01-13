"""
Pytest configuration and shared fixtures.

This module provides shared fixtures for all tests in the test suite.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from mcp_security_framework.core.cert_manager import CertificateManager
from mcp_security_framework.schemas.config import (
    CAConfig,
    CertificateConfig,
    ClientCertConfig,
    ServerCertConfig,
)


@pytest.fixture
def real_certificates():
    """
    Create real CA, client, and server certificates for testing.
    
    This fixture creates actual X.509 certificates using CertificateManager
    for use in tests that require real certificate files.
    
    Yields:
        dict: Dictionary containing:
            - ca_cert_path: Path to CA certificate
            - ca_key_path: Path to CA private key
            - client_cert_path: Path to client certificate
            - client_key_path: Path to client private key
            - server_cert_path: Path to server certificate
            - server_key_path: Path to server private key
            - temp_dir: Temporary directory path
    """
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

        # Create server certificate
        server_config = ServerCertConfig(
            common_name="test_server",
            organization="Test Org",
            country="US",
            roles=["chunker"],
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
        )

        server_pair = cert_manager_with_ca.create_server_certificate(server_config)

        yield {
            "ca_cert_path": ca_pair.certificate_path,
            "ca_key_path": ca_pair.private_key_path,
            "client_cert_path": client_pair.certificate_path,
            "client_key_path": client_pair.private_key_path,
            "server_cert_path": server_pair.certificate_path,
            "server_key_path": server_pair.private_key_path,
            "temp_dir": temp_dir,
        }

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def real_client_certificates():
    """
    Create real CA and client certificates for testing.
    
    Simplified fixture that only creates CA and client certificates.
    
    Yields:
        tuple: (client_cert_path, client_key_path, ca_cert_path)
    """
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


@pytest.fixture
def real_server_certificates():
    """
    Create real CA and server certificates for testing.
    
    Yields:
        tuple: (server_cert_path, server_key_path, ca_cert_path)
    """
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

        # Create server certificate
        cert_config_with_ca = CertificateConfig(
            enabled=True,
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
            cert_storage_path=str(cert_storage),
            key_storage_path=str(key_storage),
        )

        cert_manager_with_ca = CertificateManager(cert_config_with_ca)

        server_config = ServerCertConfig(
            common_name="test_server",
            organization="Test Org",
            country="US",
            roles=["chunker"],
            ca_cert_path=ca_pair.certificate_path,
            ca_key_path=ca_pair.private_key_path,
        )

        server_pair = cert_manager_with_ca.create_server_certificate(server_config)

        yield (
            server_pair.certificate_path,
            server_pair.private_key_path,
            ca_pair.certificate_path,
        )

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
