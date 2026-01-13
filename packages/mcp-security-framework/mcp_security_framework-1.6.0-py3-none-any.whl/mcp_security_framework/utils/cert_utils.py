"""
Certificate Utilities Module

This module provides comprehensive utilities for working with X.509
certificates in the MCP Security Framework. It includes functions for
parsing certificates, extracting information, validating formats,
and working with OIDs.

Key Features:
    - Certificate parsing and validation
    - Certificate information extraction
    - OID handling and extension parsing
    - Certificate chain validation
    - Certificate format conversion
    - Certificate metadata extraction

Functions:
    parse_certificate: Parse certificate from PEM/DER format
    extract_certificate_info: Extract detailed certificate information
    validate_certificate_format: Validate certificate format
    extract_roles_from_certificate: Extract roles from certificate
    extract_permissions_from_certificate: Extract permissions from certificate
    validate_certificate_roles: Validate certificate roles against allow/deny lists
    validate_certificate_chain:
        Validate certificate chain with optional CRL and role checks
    get_certificate_expiry: Get certificate expiry information
    convert_certificate_format: Convert between certificate formats
    extract_public_key: Extract public key from certificate
    parse_crl: Parse Certificate Revocation List from PEM/DER format
    is_certificate_revoked: Check if certificate is revoked according to CRL
    validate_certificate_against_crl: Validate certificate against CRL with details
    is_crl_valid: Check if CRL is valid and not expired
    get_crl_info: Get detailed information from CRL

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
Version: 1.0.0
License: MIT
"""

import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID, NameOID, CRLEntryExtensionOID

from mcp_security_framework.utils.datetime_compat import (
    get_not_valid_after_utc,
    get_not_valid_before_utc,
)
from mcp_security_framework.schemas.models import CertificateRole, UnknownRoleError

ROLE_WILDCARD_MARKERS = {"*", "all", "any"}


class CertificateError(Exception):
    """Raised when certificate operations fail."""

    def __init__(self, message: str, error_code: int = -32002):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def parse_certificate(cert_data: Union[str, bytes, Path]) -> x509.Certificate:
    """
    Parse certificate from PEM or DER format.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Parsed X.509 certificate object

    Raises:
        CertificateError: If certificate parsing fails
    """
    try:
        # Handle string input first (check if it's PEM data)
        if isinstance(cert_data, str):
            # Check if it looks like PEM data
            if "-----BEGIN CERTIFICATE-----" in cert_data:
                lines = cert_data.strip().split("\n")
                cert_data = "".join(
                    line for line in lines if not line.startswith("-----")
                )
                cert_data = base64.b64decode(cert_data)
            else:
                # Try to treat as file path
                try:
                    if Path(cert_data).exists():
                        with open(cert_data, "rb") as f:
                            cert_data = f.read()
                    else:
                        # Try to decode as base64
                        cert_data = base64.b64decode(cert_data)
                except (OSError, ValueError):
                    # If file doesn't exist and not base64, try to decode anyway
                    cert_data = base64.b64decode(cert_data)

        # Handle Path object
        elif isinstance(cert_data, Path):
            if cert_data.exists():
                with open(cert_data, "rb") as f:
                    cert_data = f.read()
            else:
                raise CertificateError(f"Certificate file not found: {cert_data}")

        # Try to parse as PEM first, then as DER
        try:
            return x509.load_pem_x509_certificate(cert_data)
        except Exception:
            return x509.load_der_x509_certificate(cert_data)
    except Exception as e:
        raise CertificateError(f"Certificate parsing failed: {str(e)}")


def extract_certificate_info(cert_data: Union[str, bytes, Path]) -> Dict:
    """
    Extract detailed information from certificate.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Dictionary containing certificate information

    Raises:
        CertificateError: If information extraction fails
    """
    try:
        cert = parse_certificate(cert_data)

        # Extract basic information
        info = {
            "subject": str(cert.subject),
            "issuer": str(cert.issuer),
            "serial_number": str(cert.serial_number),
            "version": cert.version.name,
            "not_before": get_not_valid_before_utc(cert),
            "not_after": get_not_valid_after_utc(cert),
            "signature_algorithm": cert.signature_algorithm_oid._name,
            "public_key_algorithm": cert.public_key_algorithm_oid._name,
            "key_size": _get_key_size(cert.public_key()),
            "extensions": _extract_extensions(cert),
            "fingerprint_sha1": cert.fingerprint(hashes.SHA1()).hex(),
            "fingerprint_sha256": cert.fingerprint(hashes.SHA256()).hex(),
        }

        # Extract common name
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if cn:
            info["common_name"] = cn[0].value

        # Extract organization
        org = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        if org:
            info["organization"] = org[0].value

        # Extract country
        country = cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)
        if country:
            info["country"] = country[0].value

        # Extract unitid
        try:
            unitid = extract_unitid_from_certificate(cert_data)
            if unitid:
                info["unitid"] = unitid
        except Exception:
            # If unitid extraction fails, continue without it
            pass

        return info
    except Exception as e:
        raise CertificateError(f"Certificate information extraction failed: {str(e)}")


def validate_certificate_roles(
    cert_roles: List[str],
    allow_roles: Optional[List[str]] = None,
    deny_roles: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate certificate roles against allow and deny lists.

    This function checks if certificate roles meet the requirements:
    - If deny_roles is provided and any certificate role is in deny_roles,
      validation fails (highest priority)
    - If allow_roles is provided, at least one certificate role must be in allow_roles
    - If both are None, validation passes (no role restrictions)

    Args:
        cert_roles: List of roles from certificate (normalized to lowercase)
        allow_roles: Optional list of allowed roles. If provided, certificate
            must have at least one role from this list. If None, no allow check.
        deny_roles: Optional list of denied roles. If provided and certificate
            has any role from this list, validation fails. If None, no deny check.
            Has priority over allow_roles.

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str]):
            - is_valid: True if roles meet requirements, False otherwise
            - error_message: Human-readable error message if validation failed,
              None if validation passed

    Example:
        >>> cert_roles = ["chunker", "embedder"]
        >>> is_valid, error = validate_certificate_roles(
        ...     cert_roles,
        ...     allow_roles=["chunker", "databaser"],
        ...     deny_roles=["techsup"]
        ... )
        >>> assert is_valid == True
        >>>
        >>> # Deny has priority
        >>> is_valid, error = validate_certificate_roles(
        ...     ["chunker", "techsup"],
        ...     allow_roles=["chunker"],
        ...     deny_roles=["techsup"]
        ... )
        >>> assert is_valid == False
        >>> assert "techsup" in error.lower()
    """
    # Normalize certificate roles to lowercase
    cert_roles_lower = [
        role.lower().strip() for role in cert_roles if role and role.strip()
    ]
    cert_has_wildcard = any(role in ROLE_WILDCARD_MARKERS for role in cert_roles_lower)

    # Normalize allow_roles to lowercase if provided
    if allow_roles is not None:
        allow_roles_lower = [
            role.lower().strip() for role in allow_roles if role and role.strip()
        ]
    else:
        allow_roles_lower = None

    # Normalize deny_roles to lowercase if provided
    if deny_roles is not None:
        deny_roles_lower = [
            role.lower().strip() for role in deny_roles if role and role.strip()
        ]
    else:
        deny_roles_lower = None

    deny_contains_wildcard = bool(
        deny_roles_lower
        and any(role in ROLE_WILDCARD_MARKERS for role in deny_roles_lower)
    )
    allow_contains_wildcard = bool(
        allow_roles_lower
        and any(role in ROLE_WILDCARD_MARKERS for role in allow_roles_lower)
    )

    # Priority 1: Check deny_roles (highest priority)
    if deny_roles_lower:
        if cert_has_wildcard:
            if deny_contains_wildcard:
                return (
                    False,
                    "Wildcard role usage is denied by configuration.",
                )
            denied_roles_found = [
                role for role in deny_roles_lower if role not in ROLE_WILDCARD_MARKERS
            ]
        else:
            denied_roles_found = [
                role for role in cert_roles_lower if role in deny_roles_lower
            ]
        if denied_roles_found:
            return (
                False,
                f"Certificate contains denied roles: {', '.join(denied_roles_found)}",
            )

    # Priority 2: Check allow_roles
    if (
        allow_roles_lower is not None
    ):  # Check if allow_roles was provided (even if empty)
        if not allow_roles_lower:  # Empty list means no roles allowed
            if cert_roles_lower:  # Certificate has roles but none are allowed
                return (
                    False,
                    f"Certificate has roles but no roles are allowed. "
                    f"Certificate roles: {', '.join(cert_roles_lower)}",
                )
        elif allow_contains_wildcard:
            # Wildcard in allow list means any certificate role is acceptable
            pass
        elif cert_has_wildcard:
            # Wildcard certificate role satisfies any explicit allow list entry
            pass
        else:  # Non-empty allow list
            allowed_roles_found = [
                role for role in cert_roles_lower if role in allow_roles_lower
            ]
            if not allowed_roles_found:
                cert_roles_display = (
                    ", ".join(cert_roles_lower) if cert_roles_lower else "none"
                )
                required_display = ", ".join(allow_roles_lower)
                message = (
                    "Certificate does not have any required roles. "
                    f"Certificate roles: {cert_roles_display}, "
                    f"Required roles: {required_display}"
                )
                return (False, message)

    # Validation passed
    return (True, None)


def validate_certificate_format(cert_data: Union[str, bytes]) -> bool:
    """
    Validate certificate format.

    Args:
        cert_data: Certificate data to validate

    Returns:
        True if format is valid, False otherwise
    """
    try:
        parse_certificate(cert_data)
        return True
    except Exception:
        return False


def extract_roles_from_certificate(
    cert_data: Union[str, bytes, Path], validate: bool = True
) -> List[str]:
    """
    Extract roles from certificate extensions.

    This method extracts roles from certificate extensions and optionally
    validates them against the CertificateRole enumeration. If no roles are
    found, returns a list with the default role (OTHER).

    Args:
        cert_data: Certificate data as string, bytes, or file path
        validate: Whether to validate roles against CertificateRole enum.
            If True, invalid roles are filtered out. If False, returns
            all roles as-is. Default is True.

    Returns:
        List of role strings found in certificate. If no roles found and
        validate=True, returns list with default role ["other"].
        If validate=True, only valid roles from CertificateRole enum are returned.

    Raises:
        CertificateError: If role extraction fails

    Example:
        >>> roles = extract_roles_from_certificate("cert.pem")
        >>> print(roles)  # ["chunker", "embedder"]
        >>> roles = extract_roles_from_certificate("cert.pem", validate=False)
        >>> print(roles)  # ["chunker", "embedder", "invalid_role"]
    """
    try:
        cert = parse_certificate(cert_data)
        roles = []

        # Check for custom extension with roles
        try:
            roles_extension = cert.extensions.get_extension_for_oid(
                x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.1")  # Custom roles OID
            )
            if roles_extension:
                roles_data = roles_extension.value.value
                if isinstance(roles_data, bytes):
                    roles_str = roles_data.decode("utf-8")
                    roles = [
                        role.strip() for role in roles_str.split(",") if role.strip()
                    ]
        except x509.extensions.ExtensionNotFound:
            pass

        # Check subject alternative names for roles
        try:
            san_extension = cert.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            if san_extension:
                san = san_extension.value
                for name in san:
                    if isinstance(name, x509.DNSName):
                        # Check if DNS name contains role information
                        if "role=" in name.value:
                            role = name.value.split("role=")[1].split(",")[0]
                            if role not in roles:
                                roles.append(role)
        except x509.extensions.ExtensionNotFound:
            pass

        # Validate roles if requested
        if validate:
            validated_roles = []
            for role_str in roles:
                try:
                    # Validate role against enum
                    CertificateRole.from_string(role_str)
                    validated_roles.append(role_str.lower())
                except UnknownRoleError:
                    # Skip invalid roles
                    continue

            # If no valid roles found, return default role
            if not validated_roles:
                return [CertificateRole.get_default_role().value]

            return validated_roles

        # If no roles found and not validating, return empty list
        # (caller can decide what to do)
        return roles if roles else []
    except Exception as e:
        raise CertificateError(f"Role extraction failed: {str(e)}")


def extract_permissions_from_certificate(
    cert_data: Union[str, bytes, Path],
) -> List[str]:
    """
    Extract permissions from certificate extensions.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        List of permissions found in certificate

    Raises:
        CertificateError: If permission extraction fails
    """
    try:
        cert = parse_certificate(cert_data)
        permissions = []

        # Check for custom extension with permissions
        try:
            perms_extension = cert.extensions.get_extension_for_oid(
                x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.2")  # Custom permissions OID
            )
            if perms_extension:
                perms_data = perms_extension.value.value
                if isinstance(perms_data, bytes):
                    perms_str = perms_data.decode("utf-8")
                    permissions = [
                        perm.strip() for perm in perms_str.split(",") if perm.strip()
                    ]
        except x509.extensions.ExtensionNotFound:
            pass

        return permissions
    except Exception as e:
        raise CertificateError(f"Permission extraction failed: {str(e)}")


def extract_unitid_from_certificate(
    cert_data: Union[str, bytes, Path],
) -> Optional[str]:
    """
    Extract unitid from certificate extensions.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Unit ID (UUID4) found in certificate, or None if not found

    Raises:
        CertificateError: If unitid extraction fails
    """
    try:
        cert = parse_certificate(cert_data)
        unitid = None

        # Check for custom extension with unitid
        try:
            unitid_extension = cert.extensions.get_extension_for_oid(
                x509.ObjectIdentifier("1.3.6.1.4.1.99999.1.3")  # Custom unitid OID
            )
            if unitid_extension:
                unitid_data = unitid_extension.value.value
                if isinstance(unitid_data, bytes):
                    unitid_str = unitid_data.decode("utf-8")
                    unitid = unitid_str.strip()

                    # Validate UUID4 format
                    try:
                        import uuid

                        uuid.UUID(unitid, version=4)
                    except ValueError:
                        # Invalid UUID4 format, return None
                        unitid = None
        except x509.extensions.ExtensionNotFound:
            pass

        return unitid
    except Exception as e:
        raise CertificateError(f"Unitid extraction failed: {str(e)}")


def validate_certificate_chain(
    cert_data: Union[str, bytes, Path],
    ca_cert_data: Union[str, bytes, Path, List[Union[str, bytes, Path]]],
    crl_data: Optional[Union[str, bytes, Path]] = None,
    allow_roles: Optional[List[str]] = None,
    deny_roles: Optional[List[str]] = None,
) -> bool:
    """
    Validate certificate chain against CA certificate(s) and optionally check
    CRL and roles.

    This method validates a certificate chain and optionally checks:
    - Certificate chain validity against CA certificate(s)
    - Certificate revocation status (if CRL provided)
    - Certificate roles against allow/deny lists (if provided)

    Args:
        cert_data: Certificate data to validate
        ca_cert_data: CA certificate data or list of CA certificates
        crl_data: Optional CRL data to check for certificate revocation
        allow_roles: Optional list of allowed roles. If provided, certificate
            must have at least one role from this list. If None, no role check.
        deny_roles: Optional list of denied roles. If provided and certificate
            has any role from this list, validation fails. If None, no deny check.
            Has priority over allow_roles.

    Returns:
        True if chain is valid, not revoked, and roles meet requirements. False
        otherwise.

    Raises:
        CertificateError: If validation fails

    Example:
        >>> # Basic chain validation
        >>> is_valid = validate_certificate_chain("client.crt", "ca.crt")
        >>>
        >>> # With role restrictions
        >>> is_valid = validate_certificate_chain(
        ...     "client.crt",
        ...     "ca.crt",
        ...     allow_roles=["chunker", "embedder"],
        ...     deny_roles=["techsup"]
        ... )
    """
    try:
        cert = parse_certificate(cert_data)

        # Handle single CA certificate or list of CA certificates
        if isinstance(ca_cert_data, list):
            ca_certs = [parse_certificate(ca_cert) for ca_cert in ca_cert_data]
        else:
            ca_certs = [parse_certificate(ca_cert_data)]

        # Check that the certificate was issued by one of the CA certificates
        # This is a simplified validation. In a real scenario, you would use
        # OpenSSL or a similar library.
        chain_valid = False
        for ca_cert in ca_certs:
            if cert.issuer == ca_cert.subject:
                chain_valid = True
                break

        if not chain_valid:
            return False

        # If CRL is provided, check if certificate is revoked
        if crl_data:
            try:
                if is_certificate_revoked(cert_data, crl_data):
                    return False
            except Exception as e:
                # If CRL check fails, we can choose to fail validation or continue
                # For security, we'll fail validation if CRL check fails
                raise CertificateError(f"CRL validation failed: {str(e)}")

        # Check roles if allow_roles or deny_roles are provided
        if allow_roles is not None or deny_roles is not None:
            cert_roles = extract_roles_from_certificate(cert_data, validate=True)
            is_valid, error_message = validate_certificate_roles(
                cert_roles, allow_roles, deny_roles
            )
            if not is_valid:
                return False

        return True
    except Exception:
        return False


def get_certificate_expiry(cert_data: Union[str, bytes, Path]) -> Dict:
    """
    Get certificate expiry information.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Dictionary containing expiry information

    Raises:
        CertificateError: If expiry information extraction fails
    """
    try:
        cert = parse_certificate(cert_data)
        now = datetime.now(timezone.utc)

        # Calculate time until expiry
        time_until_expiry = get_not_valid_after_utc(cert) - now
        days_until_expiry = time_until_expiry.days

        # Determine expiry status
        if time_until_expiry.total_seconds() < 0:
            status = "expired"
        elif days_until_expiry <= 30:
            status = "expires_soon"
        else:
            status = "valid"

        return {
            "not_after": get_not_valid_after_utc(cert),
            "not_before": get_not_valid_before_utc(cert),
            "days_until_expiry": days_until_expiry,
            "is_expired": time_until_expiry.total_seconds() < 0,
            "expires_soon": days_until_expiry <= 30,
            "status": status,
            "total_seconds_until_expiry": time_until_expiry.total_seconds(),
        }
    except Exception as e:
        raise CertificateError(
            f"Certificate expiry information extraction failed: {str(e)}"
        )


def convert_certificate_format(
    cert_data: Union[str, bytes, Path], output_format: str = "PEM"
) -> str:
    """
    Convert certificate between formats.

    Args:
        cert_data: Certificate data as string, bytes, or file path
        output_format: Output format (PEM, DER)

    Returns:
        Certificate in specified format

    Raises:
        CertificateError: If conversion fails
    """
    try:
        cert = parse_certificate(cert_data)

        if output_format.upper() == "PEM":
            return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        elif output_format.upper() == "DER":
            der_data = cert.public_bytes(serialization.Encoding.DER)
            return base64.b64encode(der_data).decode("utf-8")
        else:
            raise CertificateError(f"Unsupported output format: {output_format}")
    except Exception as e:
        raise CertificateError(f"Certificate format conversion failed: {str(e)}")


def extract_public_key(cert_data: Union[str, bytes, Path]) -> str:
    """
    Extract public key from certificate in PEM format.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Public key in PEM format

    Raises:
        CertificateError: If public key extraction fails
    """
    try:
        cert = parse_certificate(cert_data)
        public_key = cert.public_key()

        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
    except Exception as e:
        raise CertificateError(f"Public key extraction failed: {str(e)}")


def _get_key_size(public_key) -> int:
    """Get key size from public key."""
    try:
        if hasattr(public_key, "key_size"):
            return public_key.key_size
        elif isinstance(public_key, rsa.RSAPublicKey):
            return public_key.key_size
        else:
            return 0
    except Exception:
        return 0


def _extract_extensions(cert: x509.Certificate) -> Dict:
    """Extract certificate extensions."""
    extensions = {}

    for extension in cert.extensions:
        ext_name = extension.oid._name
        ext_value = str(extension.value)
        extensions[ext_name] = ext_value

    return extensions


def validate_certificate_purpose(
    cert_data: Union[str, bytes, Path], purpose: str
) -> bool:
    """
    Validate certificate purpose (server, client, code signing, etc.).

    Args:
        cert_data: Certificate data as string, bytes, or file path
        purpose: Purpose to validate (server, client, code_signing, email)

    Returns:
        True if certificate supports the purpose, False otherwise

    Raises:
        CertificateError: If validation fails
    """
    try:
        cert = parse_certificate(cert_data)

        # Check extended key usage extension
        try:
            eku_extension = cert.extensions.get_extension_for_oid(
                ExtensionOID.EXTENDED_KEY_USAGE
            )
            if eku_extension:
                eku = eku_extension.value

                if purpose == "server":
                    return x509.oid.ExtendedKeyUsageOID.SERVER_AUTH in eku
                elif purpose == "client":
                    return x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH in eku
                elif purpose == "code_signing":
                    return x509.oid.ExtendedKeyUsageOID.CODE_SIGNING in eku
                elif purpose == "email":
                    return x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION in eku
        except x509.extensions.ExtensionNotFound:
            pass

        # Check key usage extension
        try:
            ku_extension = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
            if ku_extension:
                ku = ku_extension.value

                if purpose == "server":
                    return ku.digital_signature and ku.key_encipherment
                elif purpose == "client":
                    return ku.digital_signature and ku.key_agreement
                elif purpose == "code_signing":
                    return ku.digital_signature
                elif purpose == "email":
                    return ku.digital_signature and ku.key_encipherment
        except x509.extensions.ExtensionNotFound:
            pass

        return False
    except Exception as e:
        raise CertificateError(f"Certificate purpose validation failed: {str(e)}")


def get_certificate_serial_number(cert_data: Union[str, bytes, Path]) -> str:
    """
    Get certificate serial number.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        Certificate serial number as string

    Raises:
        CertificateError: If serial number extraction fails
    """
    try:
        cert = parse_certificate(cert_data)
        return str(cert.serial_number)
    except Exception as e:
        raise CertificateError(f"Serial number extraction failed: {str(e)}")


def is_certificate_self_signed(cert_data: Union[str, bytes, Path]) -> bool:
    """
    Check if certificate is self-signed.

    Args:
        cert_data: Certificate data as string, bytes, or file path

    Returns:
        True if certificate is self-signed, False otherwise

    Raises:
        CertificateError: If check fails
    """
    try:
        cert = parse_certificate(cert_data)
        return cert.subject == cert.issuer
    except Exception as e:
        raise CertificateError(f"Self-signed check failed: {str(e)}")


def parse_crl(crl_data: Union[str, bytes, Path]) -> x509.CertificateRevocationList:
    """
    Parse Certificate Revocation List (CRL) from PEM or DER format.

    Args:
        crl_data: CRL data as string, bytes, or file path

    Returns:
        Parsed X.509 CRL object

    Raises:
        CertificateError: If CRL parsing fails
    """
    try:
        # Handle string input first (check if it's PEM data)
        if isinstance(crl_data, str):
            # Check if it looks like PEM data
            if "-----BEGIN X509 CRL-----" in crl_data:
                lines = crl_data.strip().split("\n")
                crl_data = "".join(
                    line for line in lines if not line.startswith("-----")
                )
                crl_data = base64.b64decode(crl_data)
            else:
                # Try to treat as file path
                try:
                    if Path(crl_data).exists():
                        with open(crl_data, "rb") as f:
                            crl_data = f.read()
                    else:
                        # Try to decode as base64
                        crl_data = base64.b64decode(crl_data)
                except (OSError, ValueError):
                    # If file doesn't exist and not base64, try to decode anyway
                    crl_data = base64.b64decode(crl_data)

        # Handle Path object
        elif isinstance(crl_data, Path):
            if crl_data.exists():
                with open(crl_data, "rb") as f:
                    crl_data = f.read()
            else:
                raise CertificateError(f"CRL file not found: {crl_data}")

        # Try to parse as PEM first, then as DER
        try:
            return x509.load_pem_x509_crl(crl_data)
        except Exception:
            return x509.load_der_x509_crl(crl_data)
    except Exception as e:
        raise CertificateError(f"CRL parsing failed: {str(e)}")


def is_certificate_revoked(
    cert_data: Union[str, bytes, Path], crl_data: Union[str, bytes, Path]
) -> bool:
    """
    Check if certificate is revoked according to CRL.

    Args:
        cert_data: Certificate data to check
        crl_data: CRL data to check against

    Returns:
        True if certificate is revoked, False otherwise

    Raises:
        CertificateError: If revocation check fails
    """
    try:
        cert = parse_certificate(cert_data)
        crl = parse_crl(crl_data)

        # Get certificate serial number
        cert_serial = cert.serial_number

        # Check if certificate serial number is in CRL
        for revoked_cert in crl:
            if revoked_cert.serial_number == cert_serial:
                return True

        return False
    except Exception as e:
        raise CertificateError(f"Certificate revocation check failed: {str(e)}")


def validate_certificate_against_crl(
    cert_data: Union[str, bytes, Path], crl_data: Union[str, bytes, Path]
) -> Dict[str, any]:
    """
    Validate certificate against CRL and return detailed revocation status.

    Args:
        cert_data: Certificate data to validate
        crl_data: CRL data to validate against

    Returns:
        Dictionary containing revocation status and details

    Raises:
        CertificateError: If validation fails
    """
    try:
        cert = parse_certificate(cert_data)
        crl = parse_crl(crl_data)

        # Get certificate serial number
        cert_serial = cert.serial_number

        # Check if certificate serial number is in CRL
        for revoked_cert in crl:
            if revoked_cert.serial_number == cert_serial:
                # Extract revocation reason if available
                revocation_reason = "unspecified"
                try:
                    reason_ext = revoked_cert.extensions.get_extension_for_oid(
                        CRLEntryExtensionOID.CRL_REASON
                    )
                    if reason_ext:
                        revocation_reason = reason_ext.value.reason.name
                except x509.extensions.ExtensionNotFound:
                    pass

                return {
                    "is_revoked": True,
                    "serial_number": str(cert_serial),
                    "revocation_date": revoked_cert.revocation_date_utc,
                    "revocation_reason": revocation_reason,
                    "crl_issuer": str(crl.issuer),
                    "crl_last_update": crl.last_update_utc,
                    "crl_next_update": crl.next_update_utc,
                }

        return {
            "is_revoked": False,
            "serial_number": str(cert_serial),
            "crl_issuer": str(crl.issuer),
            "crl_last_update": crl.last_update_utc,
            "crl_next_update": crl.next_update_utc,
        }
    except Exception as e:
        raise CertificateError(f"Certificate CRL validation failed: {str(e)}")


def is_crl_valid(crl_data: Union[str, bytes, Path]) -> bool:
    """
    Check if CRL is valid (not expired and properly formatted).

    Args:
        crl_data: CRL data to validate

    Returns:
        True if CRL is valid, False otherwise

    Raises:
        CertificateError: If CRL validation fails
    """
    try:
        crl = parse_crl(crl_data)
        now = datetime.now(timezone.utc)

        # Check if CRL is expired
        if crl.next_update_utc and crl.next_update_utc < now:
            return False

        # Check if CRL is not yet valid
        if crl.last_update_utc and crl.last_update_utc > now:
            return False

        return True
    except Exception as e:
        raise CertificateError(f"CRL validation failed: {str(e)}")


def get_crl_info(crl_data: Union[str, bytes, Path]) -> Dict:
    """
    Get detailed information from CRL.

    Args:
        crl_data: CRL data to analyze

    Returns:
        Dictionary containing CRL information

    Raises:
        CertificateError: If CRL information extraction fails
    """
    try:
        crl = parse_crl(crl_data)
        now = datetime.now(timezone.utc)

        # Calculate time until CRL expiry
        time_until_expiry = crl.next_update_utc - now if crl.next_update_utc else None
        days_until_expiry = time_until_expiry.days if time_until_expiry else None

        # Determine CRL status
        if crl.next_update_utc and crl.next_update_utc < now:
            status = "expired"
        elif days_until_expiry and days_until_expiry <= 7:
            status = "expires_soon"
        else:
            status = "valid"

        # Count revoked certificates
        revoked_count = len(list(crl))

        return {
            "issuer": str(crl.issuer),
            "last_update": crl.last_update_utc,
            "next_update": crl.next_update_utc,
            "revoked_certificates_count": revoked_count,
            "days_until_expiry": days_until_expiry,
            "is_expired": crl.next_update_utc < now if crl.next_update_utc else False,
            "expires_soon": days_until_expiry <= 7 if days_until_expiry else False,
            "status": status,
            "version": "v2",  # CRL version is typically v2
            "signature_algorithm": crl.signature_algorithm_oid._name,
            "signature": crl.signature.hex(),
        }
    except Exception as e:
        raise CertificateError(f"CRL information extraction failed: {str(e)}")
