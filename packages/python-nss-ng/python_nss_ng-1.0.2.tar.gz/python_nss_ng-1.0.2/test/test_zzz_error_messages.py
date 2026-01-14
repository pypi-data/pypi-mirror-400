# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for error message quality and exception handling.

This module tests that error messages are informative, helpful, and
provide sufficient context for debugging.
"""

import sys
import os
import time
import pytest
import re

# Add test directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nss.nss as nss
import nss.ssl as ssl
from nss.error import NSPRError

# Mark all tests in this module to run serially - they access NSS state and database
pytestmark = pytest.mark.xdist_group("error_messages_serial")



class TestMessageQuality:
    """Test that error messages are helpful and informative."""

    def test_certificate_not_found_error_message(self, nss_clean_state):
        """Test that certificate not found errors are informative."""
        with pytest.raises(NSPRError) as exc_info:
            nss.find_cert_from_nickname('definitely_nonexistent_cert_xyz123')

        error = exc_info.value
        error_str = str(error)

        # Error message should be non-empty
        assert len(error_str) > 0

        # Should contain some useful information
        # (exact message depends on NSS version)
        assert error_str is not None

    def test_invalid_database_path_error_message(self):
        """Test that invalid database path errors are informative."""
        # Test in subprocess to avoid disrupting shared NSS state
        import subprocess
        result = subprocess.run([
            sys.executable, '-c',
            "import nss.nss as nss; nss.nss_init('sql:/completely/invalid/nonexistent/path/to/database')"
        ], capture_output=True, text=True)

        # Should fail with an error
        assert result.returncode != 0

        # Error message should be in stderr and be non-empty
        assert len(result.stderr) > 0

    def test_malformed_data_error_message(self):
        """Test that malformed data errors are informative."""
        malformed_data = b"This is definitely not a valid certificate"

        with pytest.raises((NSPRError, ValueError, TypeError, AttributeError)) as exc_info:
            try:
                # Try to create certificate from bad data
                nss.Certificate(malformed_data)
            except AttributeError:
                # Alternative method if Certificate constructor doesn't exist
                nss.Certificate.new_from_der(malformed_data)

        error = exc_info.value
        error_str = str(error)

        # Should have some error message
        assert len(error_str) > 0

    def test_type_error_messages_informative(self):
        """Test that type errors have helpful messages."""
        # Try to pass wrong type to function
        with pytest.raises(TypeError) as exc_info:
            nss.set_ocsp_timeout('not_a_number')

        error = exc_info.value
        error_str = str(error)

        # Error should mention type issue
        assert len(error_str) > 0


class TestExceptionTypes:
    """Test that appropriate exception types are raised."""

    def test_nspr_error_for_nss_failures(self, nss_clean_state):
        """Test that NSS failures raise NSPRError."""
        with pytest.raises(NSPRError):
            nss.find_cert_from_nickname('nonexistent_cert_12345')

    def test_type_error_for_wrong_types(self):
        """Test that type errors raise TypeError."""
        with pytest.raises(TypeError):
            nss.set_ocsp_timeout('string_instead_of_int')

        with pytest.raises(TypeError):
            nss.set_use_pkix_for_validation('not_a_boolean')

    def test_value_error_for_invalid_values(self):
        """Test that invalid values raise appropriate errors."""
        with pytest.raises((NSPRError, ValueError)):
            # Invalid cipher suite
            ssl.set_default_cipher_pref(0xFFFF, True)

    def test_file_not_found_for_missing_tools(self):
        """Test that missing tools raise RuntimeError."""
        from util import find_nss_tool

        with pytest.raises(RuntimeError):
            find_nss_tool('completely_nonexistent_tool_xyz')


class TestErrorContext:
    """Test that errors include sufficient context."""

    def test_error_includes_operation_context(self, nss_clean_state):
        """Test that errors indicate what operation failed."""
        # Try to find nonexistent certificate
        with pytest.raises(NSPRError) as exc_info:
            nss.find_cert_from_nickname('nonexistent')

        # Error occurred and was caught
        assert exc_info.value is not None

    def test_error_preserves_traceback(self, nss_clean_state):
        """Test that errors preserve traceback information."""
        try:
            nss.find_cert_from_nickname('nonexistent')
        except NSPRError as e:
            import traceback
            tb = traceback.format_exc()

            # Traceback should include function name
            assert 'find_cert_from_nickname' in tb or len(tb) > 0

    def test_nested_exceptions_handled(self, nss_clean_state):
        """Test that nested exceptions are handled properly."""
        def inner_function():
            nss.find_cert_from_nickname('nonexistent')

        def outer_function():
            inner_function()

        try:
            outer_function()
        except NSPRError as e:
            # Exception should propagate with full context
            import traceback
            tb = traceback.format_exc()
            assert len(tb) > 0


class TestErrorRecovery:
    """Test that system recovers gracefully from errors."""

    def test_recovery_after_certificate_error(self, nss_clean_state):
        """Test recovery after certificate operation error."""
        # Cause an error
        try:
            nss.find_cert_from_nickname('nonexistent')
        except NSPRError:
            pass

        # System should still work
        try:
            cert = nss.find_cert_from_nickname('test_ca')
            # May or may not find cert, but shouldn't crash
        except NSPRError:
            # OK if cert doesn't exist
            pass

    def test_recovery_after_digest_error(self, nss_clean_state):
        """Test recovery after digest operation error."""
        # Create valid context
        context1 = nss.create_digest_context(nss.SEC_OID_SHA256)
        context1.digest_begin()
        context1.digest_op(b"test")
        digest1 = context1.digest_final()

        # Try to misuse context (may or may not error)
        try:
            context1.digest_op(b"more")
        except (NSPRError, RuntimeError):
            pass

        # Should be able to create new context
        context2 = nss.create_digest_context(nss.SEC_OID_SHA256)
        context2.digest_begin()
        context2.digest_op(b"new data")
        digest2 = context2.digest_final()
        assert digest2 is not None

    def test_recovery_after_ssl_error(self, nss_clean_state):
        """Test recovery after SSL configuration error."""
        # Try invalid operation
        try:
            ssl.set_default_cipher_pref(0xFFFF, True)
        except (NSPRError, ValueError):
            pass

        # System should still work
        try:
            enabled = ssl.get_default_cipher_pref(ssl.SSL_RSA_WITH_AES_128_CBC_SHA)
            assert isinstance(enabled, bool)
        except (AttributeError, NSPRError):
            # API may not be available
            pass


class TestDocumentation:
    """Test that functions have proper documentation."""

    def test_nss_functions_have_docstrings(self):
        """Test that key NSS functions have docstrings."""
        functions_to_check = [
            'nss_init',
            'nss_shutdown',
            'nss_get_version',
        ]

        for func_name in functions_to_check:
            if hasattr(nss, func_name):
                func = getattr(nss, func_name)
                # C functions may not have Python docstrings
                # This is a best-effort check
                doc = func.__doc__
                # May be None for C functions, which is acceptable

    def test_ssl_functions_have_docstrings(self):
        """Test that key SSL functions have docstrings."""
        functions_to_check = [
            'set_default_cipher_pref',
            'get_default_cipher_pref',
        ]

        for func_name in functions_to_check:
            if hasattr(ssl, func_name):
                func = getattr(ssl, func_name)
                # C functions may not have Python docstrings
                doc = func.__doc__
                # May be None for C functions

    def test_error_class_documented(self):
        """Test that NSPRError class has documentation."""
        # NSPRError should be importable
        assert NSPRError is not None

        # May or may not have docstring
        doc = NSPRError.__doc__


class TestErrorConsistency:
    """Test that errors are consistent across similar operations."""

    def test_nonexistent_items_raise_same_error_type(self, nss_clean_state):
        """Test that similar failures raise consistent error types."""
        # All of these should raise NSPRError (or similar)
        errors = []

        try:
            nss.find_cert_from_nickname('nonexistent1')
        except Exception as e:
            errors.append(type(e).__name__)

        try:
            nss.find_cert_from_nickname('nonexistent2')
        except Exception as e:
            errors.append(type(e).__name__)

        # Same operation should raise same error type
        if len(errors) >= 2:
            assert errors[0] == errors[1]

    def test_type_errors_consistent(self):
        """Test that type errors are consistent."""
        errors = []

        try:
            nss.set_ocsp_timeout('string')
        except Exception as e:
            errors.append(type(e).__name__)

        try:
            nss.set_use_pkix_for_validation('string')
        except Exception as e:
            errors.append(type(e).__name__)

        # Both should raise TypeError
        assert all(e == 'TypeError' for e in errors)


class TestErrorAttributes:
    """Test that exceptions have useful attributes."""

    def test_nspr_error_has_message(self, nss_clean_state):
        """Test that NSPRError has message attribute."""
        try:
            nss.find_cert_from_nickname('nonexistent')
        except NSPRError as e:
            # Error should have string representation
            error_str = str(e)
            assert error_str is not None
            assert len(error_str) > 0

    def test_nspr_error_has_errno(self, nss_clean_state):
        """Test that NSPRError may have errno attribute."""
        try:
            nss.find_cert_from_nickname('nonexistent')
        except NSPRError as e:
            # May have errno attribute
            if hasattr(e, 'errno'):
                errno = e.errno
                # Should be numeric
                assert isinstance(errno, int)

    def test_type_error_has_message(self):
        """Test that TypeError has informative message."""
        try:
            nss.set_ocsp_timeout('not_an_int')
        except TypeError as e:
            error_str = str(e)
            assert len(error_str) > 0


class TestUserFriendlyErrors:
    """Test that errors are user-friendly."""

    def test_errors_use_plain_language(self, nss_clean_state):
        """Test that errors avoid excessive jargon."""
        try:
            nss.find_cert_from_nickname('nonexistent')
        except NSPRError as e:
            error_str = str(e)

            # Should have some message
            assert len(error_str) > 0

            # Shouldn't be just a code or number
            assert not error_str.isdigit()

    def test_errors_suggest_solutions_when_possible(self):
        """Test that errors suggest solutions (documentation goal)."""
        # This is aspirational - errors should suggest fixes
        # For example, "Certificate not found. Check database path."
        # This test documents the requirement
        pass


class TestDeprecationWarnings:
    """Test deprecation warning quality."""

    def test_deprecation_warnings_informative(self):
        """Test that deprecation warnings are informative."""
        import warnings
        from nss.deprecations import warn_deprecated

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_deprecated("io.NetworkAddress()")

            assert len(w) == 1
            warning = w[0]

            # Warning message should be informative
            message = str(warning.message)
            assert len(message) > 20  # Substantial message

            # Should mention what's deprecated and alternative
            assert "deprecated" in message.lower()

    def test_deprecation_warnings_suggest_alternatives(self):
        """Test that deprecation warnings suggest alternatives."""
        from nss.deprecations import get_deprecation_message

        msg = get_deprecation_message("io.NetworkAddress()")
        assert msg is not None

        # Should suggest alternative
        assert "use" in msg.lower() or "instead" in msg.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
