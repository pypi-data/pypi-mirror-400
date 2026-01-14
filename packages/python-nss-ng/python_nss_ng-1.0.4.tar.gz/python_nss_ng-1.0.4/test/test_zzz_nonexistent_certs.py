# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for nonexistent certificate lookups.

This module contains tests that look up non-existent certificates, which can
corrupt NSS internal state. These tests are named with zzz_ prefix to ensure
they run at the end of the test suite.
"""

import pytest
import nss.nss as nss
from nss.error import NSPRError

# Mark all tests in this module to run serially - they access certificate database
pytestmark = pytest.mark.xdist_group("cert_lookup_serial")


class TestNonexistentCertificateLookup:
    """Test that looking up nonexistent certificates raises appropriate errors."""

    def test_find_nonexistent_cert(self, nss_clean_state):
        """Test that finding nonexistent cert raises error."""
        with pytest.raises(NSPRError):
            nss.find_cert_from_nickname('definitely_does_not_exist_12345')

    def test_find_nonexistent_cert_various_names(self, nss_clean_state):
        """Test various nonexistent certificate names."""
        nonexistent_names = [
            'nonexistent_cert_12345',
            'invalid_nickname_xyz',
            'does_not_exist',
            'missing_certificate',
        ]

        for name in nonexistent_names:
            with pytest.raises(NSPRError):
                nss.find_cert_from_nickname(name)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
