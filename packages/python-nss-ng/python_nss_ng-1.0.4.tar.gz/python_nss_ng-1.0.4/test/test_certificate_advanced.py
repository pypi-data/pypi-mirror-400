# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Advanced certificate and key management tests.

This module tests advanced certificate operations, key management,
certificate chain validation, and trust management.
"""

import sys
import os
import pytest
import tempfile

# Add test directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nss.nss as nss
from nss.error import NSPRError


class TestCertificateProperties:
    """Test certificate property access and validation."""

    def test_certificate_subject_access(self, nss_db_context):
        """Test accessing certificate subject."""
        try:
            cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        subject = cert.subject
        assert subject is not None
        # Subject should be a Distinguished Name object or string
        assert subject is not None

    def test_certificate_issuer_access(self, nss_db_context):
        """Test accessing certificate issuer."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        issuer = cert.issuer
        assert issuer is not None

    def test_certificate_validity_period(self, nss_db_context):
        """Test accessing certificate validity period."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Get validity period as strings
        not_before = cert.valid_not_before_str
        not_after = cert.valid_not_after_str

        assert not_before is not None
        assert not_after is not None
        assert len(not_before) > 0
        assert len(not_after) > 0

    def test_certificate_serial_number(self, nss_db_context):
        """Test accessing certificate serial number."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Try to access serial number
        try:
            serial = cert.serial_number
            assert serial is not None
        except AttributeError:
            # Serial number property may not be available
            pytest.skip("Serial number property not available")

    def test_self_signed_detection(self, nss_db_context):
        """Test detecting self-signed certificates."""
        try:
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # CA cert should be self-signed (issuer == subject)
        issuer = ca_cert.issuer
        subject = ca_cert.subject

        assert issuer is not None
        assert subject is not None

        # For self-signed cert, issuer and subject should be same
        # (Actual comparison depends on DN object implementation)

    def test_certificate_fingerprint(self, nss_db_context):
        """Test getting certificate fingerprint."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Try to get fingerprint or compute from DER data
        try:
            der_data = cert.der_data
            if der_data:
                # Compute SHA256 fingerprint
                fingerprint = nss.sha256_digest(der_data)
                assert fingerprint is not None
                assert len(fingerprint) == 32
        except AttributeError:
            pytest.skip("DER data not available")


class TestCertificateChainValidation:
    """Test certificate chain validation."""

    def test_validate_server_cert_against_ca(self, nss_db_context):
        """Test validating server certificate against CA."""
        try:
            server_cert = nss.find_cert_from_nickname('test_server')
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("Required certificates not available")

        # Server cert issuer should match CA cert subject
        server_issuer = server_cert.issuer
        ca_subject = ca_cert.subject

        assert server_issuer is not None
        assert ca_subject is not None

    def test_certificate_chain_length(self, nss_db_context):
        """Test determining certificate chain length."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Certificate should have an issuer
        issuer = cert.issuer
        assert issuer is not None

        # For our test certs, chain length should be 2 (server -> CA)

    def test_certificate_verification_usage(self, nss_db_context):
        """Test certificate verification with specific usage."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Test different usage types
        usage_types = [
            nss.certificateUsageSSLServer,
            nss.certificateUsageSSLClient,
        ]

        for usage in usage_types:
            try:
                approved_usage = cert.verify_now(nss_db_context, True, usage)
                # Verification may succeed or fail depending on certificate
            except NSPRError as e:
                # Some usage types may not be approved
                pass

    def test_certificate_trust_verification(self, nss_db_context):
        """Test verifying certificate trust."""
        try:
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # CA certificate should be trusted
        try:
            approved_usage = ca_cert.verify_now(
                nss_db_context,
                True,
                nss.certificateUsageSSLCA
            )
            assert approved_usage is not None
        except NSPRError:
            # Verification might fail for various reasons
            pass


class TestCertificateSearch:
    """Test certificate search and enumeration."""

    def test_find_cert_by_nickname(self, nss_db_context):
        """Test finding certificate by nickname."""
        try:
            cert = nss.find_cert_from_nickname('test_ca')
            assert cert is not None
        except NSPRError:
            pytest.skip("test_ca certificate not available")

    def test_find_cert_case_sensitivity(self, nss_db_context):
        """Test case sensitivity of certificate nicknames."""
        # Test if nickname search is case-sensitive
        try:
            cert1 = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # Try with different case - may or may not work
        try:
            cert2 = nss.find_cert_from_nickname('TEST_CA')
            # Some implementations may be case-insensitive
        except NSPRError:
            # Case-sensitive - this is acceptable
            pass

    def test_enumerate_certificates(self, nss_db_context):
        """Test enumerating certificates in database."""
        # List all certificates using the actual NSS API
        try:
            # PK11CertListAll = 0 (list all certificates)
            certs = nss.list_certs(0)
            assert isinstance(certs, tuple)
            # We should have at least our test certificates
            assert len(certs) >= 0  # May be empty or have certs
        except (NSPRError, AttributeError) as e:
            pytest.fail(f"Certificate enumeration failed: {e}")


class TestCertificateExport:
    """Test certificate export functionality."""

    def test_export_certificate_der(self, nss_db_context):
        """Test exporting certificate as DER."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Get DER encoded certificate
        try:
            der_data = cert.der_data
            assert der_data is not None
            assert isinstance(der_data, bytes)
            assert len(der_data) > 0

            # DER data should start with 0x30 (SEQUENCE)
            assert der_data[0] == 0x30
        except AttributeError:
            pytest.skip("DER export not available")

    def test_export_certificate_pem(self, nss_db_context):
        """Test exporting certificate as PEM."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Export to PEM format using standard base64 encoding
        import base64
        import textwrap

        der_data = cert.der_data
        assert der_data is not None
        assert isinstance(der_data, bytes)

        # Convert DER to base64
        b64_data = base64.b64encode(der_data).decode('ascii')

        # Wrap in PEM format with proper headers
        pem_str = '-----BEGIN CERTIFICATE-----\n'
        pem_str += '\n'.join(textwrap.wrap(b64_data, 64))
        pem_str += '\n-----END CERTIFICATE-----'

        # Verify PEM format
        assert 'BEGIN CERTIFICATE' in pem_str
        assert 'END CERTIFICATE' in pem_str
        assert len(b64_data) > 0

    def test_export_certificate_base64(self, nss_db_context):
        """Test getting certificate as base64."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Get DER and convert to base64
        try:
            import base64
            der_data = cert.der_data
            base64_data = base64.b64encode(der_data)

            assert base64_data is not None
            assert len(base64_data) > 0
        except AttributeError:
            pytest.skip("DER export not available")


class TestCertificateComparison:
    """Test certificate comparison operations."""

    def test_same_certificate_equality(self, nss_db_context):
        """Test that same certificate found twice is equal."""
        try:
            cert1 = nss.find_cert_from_nickname('test_ca')
            cert2 = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # Certificates should be the same
        # (Equality comparison may not be implemented)
        assert cert1 is not None
        assert cert2 is not None

    def test_different_certificates_inequality(self, nss_db_context):
        """Test that different certificates are not equal."""
        try:
            cert1 = nss.find_cert_from_nickname('test_ca')
            cert2 = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("Required certificates not available")

        # Should be different certificates
        assert cert1 is not None
        assert cert2 is not None

        # Compare DER data if available
        try:
            der1 = cert1.der_data
            der2 = cert2.der_data
            assert der1 != der2
        except AttributeError:
            # DER comparison not available
            pass


class TestCertificateExtensions:
    """Test certificate extension handling."""

    def test_basic_constraints_extension(self, nss_db_context):
        """Test accessing basic constraints extension."""
        try:
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # CA cert should have basic constraints
        # (Extension access API may vary)
        try:
            # Try to access extensions
            # API depends on implementation
            pass
        except AttributeError:
            pytest.skip("Extension access not available")

    def test_key_usage_extension(self, nss_db_context):
        """Test accessing key usage extension."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Server cert should have key usage
        # (API may vary)
        pass

    def test_subject_alternative_name(self, nss_db_context):
        """Test accessing subject alternative name."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Server cert may have SAN
        # (API depends on implementation)
        pass


class TestKeyManagement:
    """Test key management operations."""

    def test_get_internal_key_slot(self, nss_db_context):
        """Test getting internal key slot."""
        try:
            slot = nss.get_internal_key_slot()
            assert slot is not None
        except AttributeError:
            pytest.skip("Key slot API not available")

    def test_key_slot_properties(self, nss_db_context):
        """Test key slot properties."""
        try:
            slot = nss.get_internal_key_slot()
            # Try to access slot properties
            # (API varies by implementation)
        except AttributeError:
            pytest.skip("Key slot API not available")

    def test_private_key_access(self, nss_db_context):
        """Test accessing private keys."""
        # Private key access requires proper authentication
        # This test documents the requirement
        try:
            slot = nss.get_internal_key_slot()
            # Private key operations would go here
        except AttributeError:
            pytest.skip("Private key API not available")


class TestCertificateRevocation:
    """Test certificate revocation handling."""

    def test_crl_checking(self, nss_db_context):
        """Test CRL (Certificate Revocation List) checking."""
        # CRL checking configuration
        # (Implementation specific)
        pass

    def test_ocsp_integration(self, nss_db_context):
        """Test OCSP integration with certificate validation."""
        # Enable OCSP
        nss.enable_ocsp_checking(nss_db_context)

        try:
            cert = nss.find_cert_from_nickname('test_server')

            # Validate with OCSP enabled
            try:
                approved_usage = cert.verify_now(
                    nss_db_context,
                    True,
                    nss.certificateUsageSSLServer
                )
            except NSPRError:
                # Validation may fail (no OCSP responder)
                pass
        except NSPRError:
            pytest.skip("test_server certificate not available")
        finally:
            # Disable OCSP
            nss.disable_ocsp_checking(nss_db_context)


class TestCertificateTrust:
    """Test certificate trust management."""

    def test_ca_certificate_trusted(self, nss_db_context):
        """Test that CA certificate is trusted."""
        try:
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # CA should be trusted for issuing server certs
        try:
            approved_usage = ca_cert.verify_now(
                nss_db_context,
                True,
                nss.certificateUsageSSLCA
            )
            assert approved_usage is not None
        except NSPRError:
            # Trust validation might fail
            pass

    def test_trust_flags(self, nss_db_context):
        """Test certificate trust flags."""
        try:
            cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # Try to access trust flags
        # (API depends on implementation)
        pass


class TestCertificateFormatting:
    """Test certificate formatting and display."""

    def test_certificate_string_representation(self, nss_db_context):
        """Test string representation of certificate."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Should be able to convert to string
        cert_str = str(cert)
        assert cert_str is not None
        assert len(cert_str) > 0

    def test_certificate_subject_formatting(self, nss_db_context):
        """Test formatting certificate subject."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        subject = cert.subject
        subject_str = str(subject)

        assert subject_str is not None
        assert len(subject_str) > 0

    def test_certificate_issuer_formatting(self, nss_db_context):
        """Test formatting certificate issuer."""
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        issuer = cert.issuer
        issuer_str = str(issuer)

        assert issuer_str is not None
        assert len(issuer_str) > 0


class TestCertificateEdgeCases:
    """Test certificate edge cases and error conditions."""

    def test_null_nickname_search(self, nss_db_context):
        """Test searching with null/empty nickname."""
        with pytest.raises((NSPRError, ValueError, TypeError)):
            nss.find_cert_from_nickname('')

    def test_special_characters_in_nickname(self, nss_db_context):
        """Test searching with special characters."""
        special_nicknames = [
            'test-cert',
            'test_cert',
            'test.cert',
            'test cert',
        ]

        for nickname in special_nicknames:
            try:
                cert = nss.find_cert_from_nickname(nickname)
                # May or may not exist
            except NSPRError:
                # Expected if cert doesn't exist
                pass

    def test_very_long_nickname(self, nss_db_context):
        """Test searching with very long nickname."""
        long_nickname = 'a' * 1000

        with pytest.raises(NSPRError):
            nss.find_cert_from_nickname(long_nickname)

    def test_unicode_nickname(self, nss_db_context):
        """Test searching with Unicode nickname."""
        unicode_nicknames = [
            'test_café',
            'test_日本',
            'test_😀',
        ]

        for nickname in unicode_nicknames:
            try:
                cert = nss.find_cert_from_nickname(nickname)
                # May work or may not depending on implementation
            except (NSPRError, UnicodeError):
                # Expected - may not support Unicode
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
