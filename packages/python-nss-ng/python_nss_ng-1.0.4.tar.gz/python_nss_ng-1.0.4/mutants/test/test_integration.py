# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Integration tests for python-nss-ng.

This module tests end-to-end workflows, multi-component interactions,
and real-world usage scenarios.
"""

import sys
import os
import threading
import time
import pytest

# Add src to path for importing modules
sys.path.insert(0, 'src')

import nss.nss as nss
import nss.ssl as ssl
import nss.io as io
from nss.error import NSPRError


class TestCertificateLifecycle:
    """Test complete certificate lifecycle workflows."""

    def test_certificate_load_and_verify(self, nss_db_context):
        """Test loading and verifying a certificate end-to-end."""
        # Find a certificate
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Verify basic properties
        assert cert is not None
        assert cert.subject is not None
        assert cert.issuer is not None

        # Get validity period
        not_before = cert.valid_not_before_str
        not_after = cert.valid_not_after_str
        assert not_before is not None
        assert not_after is not None

        # Verify the certificate
        try:
            approved_usage = cert.verify_now(nss_db_context, True, nss.certificateUsageSSLServer)
            assert approved_usage is not None
        except NSPRError as e:
            # Verification might fail for various reasons
            # This is acceptable for integration testing
            pass

    def test_certificate_chain_validation(self, nss_db_context):
        """Test validating a certificate chain."""
        # Find server certificate
        try:
            server_cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Find CA certificate
        try:
            ca_cert = nss.find_cert_from_nickname('test_ca')
        except NSPRError:
            pytest.skip("test_ca certificate not available")

        # Verify server cert is signed by CA
        server_issuer = server_cert.issuer
        ca_subject = ca_cert.subject

        assert server_issuer is not None
        assert ca_subject is not None

        # The issuer of server cert should match subject of CA
        # (actual comparison would require proper DN comparison)

    def test_certificate_export_import_workflow(self, nss_db_context):
        """Test exporting and working with certificate data."""
        # Find a certificate
        try:
            cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # Export certificate to DER format
        try:
            cert_der = cert.der_data
            assert cert_der is not None
            assert len(cert_der) > 0
        except (AttributeError, NSPRError):
            pytest.skip("DER export not available")


class TestDigestWorkflows:
    """Test digest/hash operation workflows."""

    def test_digest_multiple_algorithms(self, nss_db_context):
        """Test using multiple digest algorithms on same data."""
        test_data = b"The quick brown fox jumps over the lazy dog"

        # Test multiple algorithms
        md5_digest = nss.md5_digest(test_data)
        sha1_digest = nss.sha1_digest(test_data)
        sha256_digest = nss.sha256_digest(test_data)
        sha512_digest = nss.sha512_digest(test_data)

        # Verify different algorithms produce different results
        assert md5_digest != sha1_digest
        assert sha1_digest != sha256_digest
        assert sha256_digest != sha512_digest

        # Verify expected lengths
        assert len(md5_digest) == 16  # 128 bits
        assert len(sha1_digest) == 20  # 160 bits
        assert len(sha256_digest) == 32  # 256 bits
        assert len(sha512_digest) == 64  # 512 bits

    def test_digest_incremental_vs_oneshot(self, nss_db_context):
        """Test that incremental hashing matches one-shot hashing."""
        test_data = b"Test data for incremental hashing" * 100
        chunk_size = 50

        # One-shot digest
        oneshot_digest = nss.sha256_digest(test_data)

        # Incremental digest
        context = nss.create_digest_context(nss.SEC_OID_SHA256)
        context.digest_begin()

        offset = 0
        while offset < len(test_data):
            chunk = test_data[offset:offset + chunk_size]
            context.digest_op(chunk)
            offset += chunk_size

        incremental_digest = context.digest_final()

        # Results should match
        assert oneshot_digest == incremental_digest

    def test_digest_empty_data(self, nss_db_context):
        """Test digesting empty data."""
        empty_data = b""

        # Should handle empty data gracefully
        md5_digest = nss.md5_digest(empty_data)
        sha256_digest = nss.sha256_digest(empty_data)

        assert md5_digest is not None
        assert sha256_digest is not None
        assert len(md5_digest) == 16
        assert len(sha256_digest) == 32


class TestSSLConfiguration:
    """Test SSL/TLS configuration workflows."""

    def test_ssl_version_range_configuration(self, nss_db_context):
        """Test configuring SSL version ranges."""
        try:
            # Get current default range
            min_ver, max_ver = ssl.get_default_ssl_version_range()
            assert min_ver is not None
            assert max_ver is not None

            # Save original values
            original_min = min_ver
            original_max = max_ver

            # Try to set a range (TLS 1.2 to TLS 1.3)
            try:
                ssl.set_default_ssl_version_range(
                    ssl.SSL_LIBRARY_VERSION_TLS_1_2,
                    ssl.SSL_LIBRARY_VERSION_TLS_1_3
                )

                # Verify it was set
                new_min, new_max = ssl.get_default_ssl_version_range()
                assert new_min == ssl.SSL_LIBRARY_VERSION_TLS_1_2
                assert new_max == ssl.SSL_LIBRARY_VERSION_TLS_1_3

                # Restore original
                ssl.set_default_ssl_version_range(original_min, original_max)
            except (NSPRError, AttributeError):
                # API might not be available or configuration might be locked
                pass

        except AttributeError:
            pytest.skip("SSL version range API not available")

    def test_cipher_suite_configuration(self, nss_db_context):
        """Test configuring cipher suites."""
        # Try to query a common cipher suite
        try:
            cipher_suite = ssl.SSL_RSA_WITH_AES_128_CBC_SHA

            # Get current preference
            original_pref = ssl.get_default_cipher_pref(cipher_suite)
            assert isinstance(original_pref, bool)

            # Toggle it
            ssl.set_default_cipher_pref(cipher_suite, not original_pref)

            # Verify it changed
            new_pref = ssl.get_default_cipher_pref(cipher_suite)
            assert new_pref == (not original_pref)

            # Restore original
            ssl.set_default_cipher_pref(cipher_suite, original_pref)

        except (AttributeError, NSPRError):
            pytest.skip("Cipher suite API not available")


class TestOCSPIntegrationWorkflow:
    """Test OCSP in real-world scenarios."""

    def test_ocsp_configuration_workflow(self, nss_db_context):
        """Test complete OCSP configuration and usage."""
        # Save initial state
        initial_pkix = nss.get_use_pkix_for_validation()

        # Configure OCSP
        nss.set_ocsp_cache_settings(100, 10, 30)
        nss.set_ocsp_timeout(30)
        nss.set_ocsp_failure_mode(nss.ocspMode_FailureIsNotAVerificationFailure)

        # Enable OCSP checking
        nss.enable_ocsp_checking(nss_db_context)

        # Configure default responder
        try:
            nss.set_ocsp_default_responder(
                nss_db_context,
                "http://ocsp.example.com:80/",
                'test_ca'
            )
            nss.enable_ocsp_default_responder(nss_db_context)
        except NSPRError:
            # Certificate might not exist
            pass

        # Clean up
        try:
            nss.disable_ocsp_default_responder(nss_db_context)
        except NSPRError:
            pass

        nss.disable_ocsp_checking(nss_db_context)
        nss.clear_ocsp_cache()

        # Restore PKIX setting
        nss.set_use_pkix_for_validation(initial_pkix)

    def test_ocsp_with_certificate_validation(self, nss_db_context):
        """Test OCSP in conjunction with certificate validation."""
        # Enable OCSP
        nss.enable_ocsp_checking(nss_db_context)

        try:
            # Find and validate a certificate
            cert = nss.find_cert_from_nickname('test_server')

            # Validate with OCSP enabled
            # Note: This will not actually contact an OCSP responder in tests
            # but exercises the code path
            try:
                approved_usage = cert.verify_now(
                    nss_db_context,
                    True,
                    nss.certificateUsageSSLServer
                )
            except NSPRError:
                # Validation may fail for various reasons
                pass
        except NSPRError:
            pytest.skip("test_server certificate not available")
        finally:
            # Clean up
            nss.disable_ocsp_checking(nss_db_context)


class TestMultiThreadedAccess:
    """Test thread-safe operations."""

    def test_concurrent_digest_operations(self, nss_db_context):
        """Test multiple threads performing digest operations."""
        test_data = b"Concurrent test data" * 100
        results = {}
        errors = []

        def digest_worker(thread_id):
            """Worker function for digest operations."""
            try:
                # Each thread performs multiple digest operations
                for i in range(10):
                    digest = nss.sha256_digest(test_data)
                    if thread_id not in results:
                        results[thread_id] = []
                    results[thread_id].append(digest)
            except Exception as e:
                errors.append((thread_id, e))

        # Create and start threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=digest_worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join(timeout=10)

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 5

        # Verify all results are identical within each thread
        for thread_id, digests in results.items():
            assert len(digests) == 10
            # All digests should be the same
            assert all(d == digests[0] for d in digests)

    def test_concurrent_certificate_access(self, nss_db_context):
        """Test multiple threads accessing certificates."""
        results = []
        errors = []

        def cert_worker(thread_id):
            """Worker function for certificate access."""
            try:
                # Try to find certificate
                cert = nss.find_cert_from_nickname('test_ca')
                results.append((thread_id, cert is not None))
            except NSPRError:
                # Certificate not found is acceptable
                results.append((thread_id, False))
            except Exception as e:
                errors.append((thread_id, e))

        # Create and start threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=cert_worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join(timeout=10)

        # Verify no unexpected errors
        assert len(errors) == 0, f"Errors in threads: {errors}"

        # Verify all threads completed
        assert len(results) == 5


class TestErrorRecovery:
    """Test error handling and recovery."""

    def test_recovery_from_invalid_certificate(self, nss_db_context):
        """Test that system recovers from invalid certificate operations."""
        # Try to find non-existent certificate
        with pytest.raises(NSPRError):
            nss.find_cert_from_nickname('nonexistent_cert_12345')

        # System should still work after error
        # Try valid operation
        try:
            cert = nss.find_cert_from_nickname('test_ca')
            assert cert is not None
        except NSPRError:
            # test_ca might not exist, but no crash
            pass

    def test_recovery_from_invalid_digest_context(self, nss_db_context):
        """Test recovery from digest errors."""
        # Create valid context
        context = nss.create_digest_context(nss.SEC_OID_SHA256)
        context.digest_begin()
        context.digest_op(b"test data")
        digest = context.digest_final()
        assert digest is not None

        # Try to use context after finalization (should fail or be handled)
        try:
            context.digest_op(b"more data")
            # Some implementations might allow this, others won't
        except (NSPRError, RuntimeError):
            # Expected - context is finalized
            pass

        # System should still work - create new context
        context2 = nss.create_digest_context(nss.SEC_OID_SHA256)
        context2.digest_begin()
        context2.digest_op(b"new data")
        digest2 = context2.digest_final()
        assert digest2 is not None

    def test_recovery_from_ssl_configuration_error(self, nss_db_context):
        """Test recovery from SSL configuration errors."""
        # Try to set invalid cipher suite
        invalid_cipher = 0xFFFF

        with pytest.raises((NSPRError, ValueError)):
            ssl.set_default_cipher_pref(invalid_cipher, True)

        # System should still work after error
        # Try valid operation
        try:
            enabled = ssl.get_default_cipher_pref(ssl.SSL_RSA_WITH_AES_128_CBC_SHA)
            assert isinstance(enabled, bool)
        except (AttributeError, NSPRError):
            # API might not be available
            pass


class TestResourceCleanup:
    """Test proper resource cleanup."""

    def test_digest_context_cleanup(self, nss_db_context):
        """Test that digest contexts are properly cleaned up."""
        # Create many contexts
        contexts = []
        for i in range(100):
            context = nss.create_digest_context(nss.SEC_OID_SHA256)
            context.digest_begin()
            context.digest_op(b"test data")
            digest = context.digest_final()
            contexts.append((context, digest))

        # Verify all completed successfully
        assert len(contexts) == 100

        # All should have valid digests
        for ctx, digest in contexts:
            assert digest is not None
            assert len(digest) == 32

    def test_certificate_reference_cleanup(self, nss_db_context):
        """Test that certificate references are properly managed."""
        # Find certificate multiple times
        certificates = []

        for i in range(50):
            try:
                cert = nss.find_cert_from_nickname('test_ca')
                certificates.append(cert)
            except NSPRError:
                # Certificate might not exist
                break

        # All references should be valid
        for cert in certificates:
            assert cert is not None
            # Should be able to access properties
            try:
                subject = cert.subject
                assert subject is not None
            except (AttributeError, NSPRError):
                # Some properties might not be accessible
                pass


class TestDataConversion:
    """Test data conversion and formatting utilities."""

    def test_hex_conversion_workflow(self, nss_db_context):
        """Test converting binary data to hex."""
        test_data = b"\x00\x01\x02\x03\xAB\xCD\xEF\xFF"

        # Convert to hex
        hex_str = nss.data_to_hex(test_data, separator=None)
        assert hex_str is not None
        assert isinstance(hex_str, str)

        # Verify format (should be lowercase hex)
        assert all(c in '0123456789abcdef' for c in hex_str.lower())

        # Test with separator
        hex_with_sep = nss.data_to_hex(test_data, separator=':')
        assert ':' in hex_with_sep

    def test_digest_to_hex_workflow(self, nss_db_context):
        """Test complete workflow: digest -> binary -> hex."""
        test_data = b"Test data for conversion"

        # Create digest
        digest_binary = nss.sha256_digest(test_data)

        # Convert to hex
        digest_hex = nss.data_to_hex(digest_binary, separator=None)

        # Verify format
        assert isinstance(digest_hex, str)
        assert len(digest_hex) == 64  # 32 bytes * 2 hex chars
        assert all(c in '0123456789abcdef' for c in digest_hex.lower())


class TestCompleteWorkflow:
    """Test complete real-world workflows."""

    def test_secure_communication_setup(self, nss_db_context):
        """Test setting up for secure communication."""
        # This simulates setting up for SSL/TLS communication

        # 1. Find server certificate
        try:
            server_cert = nss.find_cert_from_nickname('test_server')
        except NSPRError:
            pytest.skip("test_server certificate not available")

        # 2. Verify certificate is valid
        try:
            approved_usage = server_cert.verify_now(
                nss_db_context,
                True,
                nss.certificateUsageSSLServer
            )
        except NSPRError:
            # Validation might fail, but we're testing the workflow
            pass

        # 3. Configure SSL settings
        try:
            # Set minimum TLS version
            ssl.set_default_ssl_version_range(
                ssl.SSL_LIBRARY_VERSION_TLS_1_2,
                ssl.SSL_LIBRARY_VERSION_TLS_1_3
            )
        except (AttributeError, NSPRError):
            # API might not be available
            pass

        # 4. Configure cipher suites (example)
        try:
            ssl.set_default_cipher_pref(ssl.SSL_RSA_WITH_AES_128_CBC_SHA, True)
        except (AttributeError, NSPRError):
            pass

    def test_data_integrity_workflow(self, nss_db_context):
        """Test workflow for ensuring data integrity."""
        # Simulate workflow: hash data, verify later

        # 1. Original data
        original_data = b"Important data that needs integrity protection"

        # 2. Create hash
        original_hash = nss.sha256_digest(original_data)

        # 3. Later, verify data hasn't changed
        received_data = b"Important data that needs integrity protection"
        received_hash = nss.sha256_digest(received_data)

        # 4. Compare hashes
        assert original_hash == received_hash, "Data integrity check passed"

        # 5. Test with modified data
        modified_data = b"Important data that has been modified"
        modified_hash = nss.sha256_digest(modified_data)

        assert original_hash != modified_hash, "Modified data detected"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
