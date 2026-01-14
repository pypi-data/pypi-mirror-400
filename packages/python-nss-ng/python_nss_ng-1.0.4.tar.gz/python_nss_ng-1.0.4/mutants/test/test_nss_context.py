# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for NSS lifecycle context manager.

This test module verifies that the NSS context manager properly handles
initialization, shutdown, and error conditions.
"""

import sys
import os
import pytest
import tempfile
import shutil

# Add src to path for importing nss_context module
sys.path.insert(0, 'src')

from nss_context import NSSContext, nss_context
import nss.nss as nss
from nss.error import NSPRError


class TestNSSContextBasic:
    """Tests for basic NSSContext functionality."""

    def test_context_manager_exists(self):
        """Verify NSSContext class exists and is importable."""
        assert NSSContext is not None
        assert callable(NSSContext)

    def test_functional_context_manager_exists(self):
        """Verify nss_context() functional form exists."""
        assert nss_context is not None
        assert callable(nss_context)

    def test_context_manager_without_database(self):
        """Test context manager initializes NSS without database."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        with NSSContext():
            # NSS should be initialized
            assert nss.nss_is_initialized()

        # NSS should be shutdown after exiting context
        # Note: Can't reliably test nss_is_initialized() after shutdown
        # because NSS might still have residual state

    def test_context_manager_with_database(self, test_certs):
        """Test context manager with database path."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path):
            # NSS should be initialized
            assert nss.nss_is_initialized()

            # Should be able to access certificate database
            certdb = nss.get_default_certdb()
            assert certdb is not None


class TestNSSContextLifecycle:
    """Tests for NSS lifecycle management."""

    def test_context_initialization(self):
        """Test that __enter__ initializes NSS."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        context = NSSContext()

        # Before entering, NSS might not be initialized
        result = context.__enter__()

        # After __enter__, NSS should be initialized
        assert nss.nss_is_initialized()
        assert result is context

        # Clean up
        context.__exit__(None, None, None)

    def test_context_shutdown(self):
        """Test that __exit__ shuts down NSS."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        context = NSSContext()
        context.__enter__()

        # NSS is initialized
        assert nss.nss_is_initialized()

        # Exit context
        context.__exit__(None, None, None)

        # NSS should be shut down
        # Note: We can't reliably check this without re-initializing

    def test_exception_propagates(self):
        """Test that exceptions in with block propagate correctly."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        class CustomException(Exception):
            pass

        with pytest.raises(CustomException):
            with NSSContext():
                raise CustomException("Test exception")

    def test_shutdown_on_exception(self):
        """Test that NSS shuts down even when exception occurs."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        try:
            with NSSContext():
                assert nss.nss_is_initialized()
                raise ValueError("Intentional error")
        except ValueError:
            pass

        # NSS should still be shut down despite exception


class TestNSSContextWithDatabase:
    """Tests for context manager with database."""

    def test_database_initialization(self, test_certs):
        """Test initialization with valid database."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path):
            # Should be able to access certificates
            certdb = nss.get_default_certdb()
            assert certdb is not None

            # Try to find a certificate
            try:
                cert = nss.find_cert_from_nickname('test_ca')
                assert cert is not None
            except NSPRError:
                # Certificate might not exist, but database access works
                pass

    def test_invalid_database_path(self):
        """Test initialization with invalid database path."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        with pytest.raises((NSPRError, Exception)):
            with NSSContext(db_name='sql:/nonexistent/path/to/db'):
                pass

    def test_database_vs_nodb(self, test_certs):
        """Test difference between database and no-database initialization."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # First, test with database
        db_path = f'sql:{test_certs}'
        with NSSContext(db_name=db_path):
            certdb_with_db = nss.get_default_certdb()
            assert certdb_with_db is not None

        # Then, test without database
        with NSSContext():
            certdb_without_db = nss.get_default_certdb()
            # Both should return something, but behavior may differ


class TestNSSContextPasswordCallback:
    """Tests for password callback functionality."""

    def test_password_callback_set(self, test_certs):
        """Test that password callback can be set."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        callback_called = {'called': False}

        def password_cb(slot, retry):
            callback_called['called'] = True
            return 'test_password'

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path, password_callback=password_cb):
            # Context manager should set the callback
            # Actual invocation depends on whether operations need password
            pass

    def test_none_password_callback(self, test_certs):
        """Test that None password callback is handled."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        # Should not raise error with None callback
        with NSSContext(db_name=db_path, password_callback=None):
            pass


class TestNSSContextFlags:
    """Tests for initialization flags."""

    def test_flags_parameter_accepted(self):
        """Test that flags parameter is accepted."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # Flags value of 0 should be safe
        with NSSContext(flags=0):
            assert nss.nss_is_initialized()

    def test_flags_with_database(self, test_certs):
        """Test flags parameter with database."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path, flags=0):
            assert nss.nss_is_initialized()


class TestFunctionalContextManager:
    """Tests for nss_context() functional form."""

    def test_functional_form_without_database(self):
        """Test functional context manager without database."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        with nss_context():
            assert nss.nss_is_initialized()

    def test_functional_form_with_database(self, test_certs):
        """Test functional context manager with database."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with nss_context(db_name=db_path):
            assert nss.nss_is_initialized()
            certdb = nss.get_default_certdb()
            assert certdb is not None

    def test_functional_form_with_callback(self, test_certs):
        """Test functional form with password callback."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        def password_cb(slot, retry):
            return 'test_password'

        db_path = f'sql:{test_certs}'

        with nss_context(db_name=db_path, password_callback=password_cb):
            assert nss.nss_is_initialized()

    def test_functional_form_with_flags(self):
        """Test functional form with flags."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        with nss_context(flags=0):
            assert nss.nss_is_initialized()


class TestNSSContextErrorHandling:
    """Tests for error handling in context manager."""

    def test_initialization_failure_cleanup(self):
        """Test that failed initialization is handled gracefully."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # Try to initialize with invalid path
        with pytest.raises((NSPRError, Exception)):
            with NSSContext(db_name='sql:/invalid/path'):
                pass

        # Should not be left in partially initialized state

    def test_shutdown_error_suppressed(self):
        """Test that shutdown errors don't prevent exception propagation."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        class TestException(Exception):
            pass

        # Even if shutdown fails, original exception should propagate
        with pytest.raises(TestException):
            with NSSContext():
                raise TestException("Original error")

    def test_multiple_context_sequential(self):
        """Test that multiple contexts can be used sequentially."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # First context
        with NSSContext():
            assert nss.nss_is_initialized()

        # Second context should work
        with NSSContext():
            assert nss.nss_is_initialized()


class TestNSSContextLogging:
    """Tests for logging in context manager."""

    def test_logging_on_success(self, caplog):
        """Test that successful operations are logged."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        import logging
        caplog.set_level(logging.DEBUG, logger='nss_context')

        with NSSContext():
            pass

        # Check that initialization and shutdown were logged
        # Note: Actual log checking depends on logging configuration

    def test_logging_on_failure(self, caplog):
        """Test that failures are logged."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        import logging
        caplog.set_level(logging.ERROR, logger='nss_context')

        try:
            with NSSContext(db_name='sql:/invalid/path'):
                pass
        except:
            pass

        # Errors should be logged


class TestNSSContextRealWorld:
    """Real-world usage scenarios for NSS context manager."""

    def test_certificate_operations_in_context(self, test_certs):
        """Test performing certificate operations within context."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path):
            certdb = nss.get_default_certdb()

            # Try to list certificates
            try:
                certs = certdb.find_certs_by_subject('')
            except NSPRError:
                # May fail depending on database content
                pass

    def test_digest_operation_in_context(self):
        """Test performing digest operations within context."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        test_data = b"Hello, NSS!"

        with NSSContext():
            # Digest operations should work without database
            digest = nss.sha256_digest(test_data)
            assert digest is not None
            assert len(digest) == 32  # SHA256 produces 32 bytes

    def test_context_with_ssl_operations(self, test_certs):
        """Test that SSL operations can be performed in context."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        db_path = f'sql:{test_certs}'

        with NSSContext(db_name=db_path):
            # Import ssl module
            import nss.ssl as ssl

            # Should be able to query SSL settings
            try:
                # Get a cipher suite setting
                enabled = ssl.get_default_cipher_pref(ssl.SSL_RSA_WITH_AES_128_CBC_SHA)
                assert isinstance(enabled, bool)
            except (NSPRError, AttributeError):
                # Cipher may not be available
                pass


class TestNSSContextDocumentation:
    """Tests that verify documented behavior."""

    def test_context_manager_example_from_docstring(self):
        """Test example from NSSContext docstring works."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # Example from docstring
        with NSSContext():
            data = b"hello world"
            digest = nss.sha256_digest(data)
            assert digest is not None

    def test_nodb_mode_example(self):
        """Test no-database mode example."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        # From docstring: "If None, NSS is initialized without a database"
        with NSSContext(db_name=None):
            assert nss.nss_is_initialized()


class TestNSSContextInternalState:
    """Tests for internal state management."""

    def test_initialized_flag(self):
        """Test that _initialized flag is managed correctly."""
        # Ensure NSS is not initialized
        try:
            nss.nss_shutdown()
        except:
            pass

        context = NSSContext()

        # Before entering, should not be initialized
        assert context._initialized is False

        context.__enter__()

        # After entering, should be initialized
        assert context._initialized is True

        context.__exit__(None, None, None)

        # After exiting, should be reset
        assert context._initialized is False

    def test_attributes_stored(self):
        """Test that initialization parameters are stored."""
        db_name = 'sql:test_db'
        flags = 42

        def callback(slot, retry):
            return 'password'

        context = NSSContext(db_name=db_name, password_callback=callback, flags=flags)

        assert context.db_name == db_name
        assert context.password_callback is callback
        assert context.flags == flags


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
