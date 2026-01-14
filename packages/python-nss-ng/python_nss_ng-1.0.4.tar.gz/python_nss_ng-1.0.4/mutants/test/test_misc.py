# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

import sys
import os
import pytest

import nss.nss as nss


#-------------------------------------------------------------------------------
class TestVersion:
    """Test NSS version checking."""
    def test_version(self):

        version = nss.nss_get_version()
        assert nss.nss_version_check(version) is True

class TestShutdownCallback:
    """Test NSS shutdown callback functionality."""
    def test_shutdown_callback(self, nss_db_context):
        int_value = 43
        str_value = u"foobar"
        count = 0
        dict_value = {'count': count}

        def shutdown_callback(nss_data, i, s, d):
            assert isinstance(nss_data, dict)
            assert isinstance(i, int)
            assert i == int_value
            assert isinstance(s, str)
            assert s == str_value
            assert isinstance(d, dict)
            assert d is dict_value
            d['count'] += 1
            return True

        # NSS is already initialized by nss_db_context fixture
        # Test setting and clearing the shutdown callback
        nss.set_shutdown_callback(shutdown_callback, int_value, str_value, dict_value)

        # Clear the callback - it won't be invoked
        nss.set_shutdown_callback(None)

        # The callback count should still be at the initial value
        assert dict_value['count'] == count

#-------------------------------------------------------------------------------
