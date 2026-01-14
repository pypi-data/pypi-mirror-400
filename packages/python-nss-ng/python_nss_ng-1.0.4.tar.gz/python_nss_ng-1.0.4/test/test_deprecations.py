# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for deprecation warnings in python-nss-ng.

This test module verifies that deprecated functionality properly emits
DeprecationWarning messages to help users migrate to newer APIs.
"""

import sys
import warnings
import pytest


# Add src to path for importing deprecations module
sys.path.insert(0, 'src')

from deprecations import (
    DEPRECATED_REGISTRY,
    warn_deprecated,
    is_deprecated,
    get_deprecation_message,
    list_deprecated,
)


class TestDeprecationRegistry:
    """Tests for the deprecation registry and utilities."""

    def test_registry_not_empty(self):
        """Verify the deprecation registry contains known deprecated items."""
        assert len(DEPRECATED_REGISTRY) > 0
        assert "io.NetworkAddress()" in DEPRECATED_REGISTRY

    def test_is_deprecated(self):
        """Test deprecation checking."""
        assert is_deprecated("io.NetworkAddress()")
        assert is_deprecated("io.NetworkAddress.set_from_string()")
        assert not is_deprecated("io.AddrInfo")
        assert not is_deprecated("some_random_symbol")

    def test_get_deprecation_message(self):
        """Test retrieval of deprecation messages."""
        msg = get_deprecation_message("io.NetworkAddress()")
        assert msg is not None
        assert "IPv4" in msg
        assert "AddrInfo" in msg

        assert get_deprecation_message("nonexistent") is None

    def test_list_deprecated(self):
        """Test getting a copy of all deprecated symbols."""
        deprecated = list_deprecated()
        assert isinstance(deprecated, dict)
        assert len(deprecated) > 0

        # Verify it's a copy, not the original
        deprecated["test"] = "value"
        assert "test" not in DEPRECATED_REGISTRY


class TestDeprecationWarnings:
    """Tests for deprecation warning emission."""

    def test_warn_deprecated_emits_warning(self):
        """Verify warn_deprecated() emits a DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            warn_deprecated("io.NetworkAddress()")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "io.NetworkAddress()" in str(w[0].message)
            assert "deprecated" in str(w[0].message).lower()

    def test_warn_deprecated_with_alternative(self):
        """Test custom deprecation message."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            warn_deprecated("test.symbol", alternative="Use new.symbol instead")

            assert len(w) == 1
            assert "new.symbol" in str(w[0].message)

    def test_warn_deprecated_uses_registry(self):
        """Verify registry messages are used by default."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            warn_deprecated("io.NetworkAddress.hostentry")

            assert len(w) == 1
            msg = str(w[0].message)
            assert "HostEntry" in msg
            assert "IPv4" in msg

    def test_warn_deprecated_stacklevel(self):
        """Test stacklevel parameter for proper warning location."""
        def inner_function():
            warn_deprecated("test.symbol", stacklevel=3)

        def outer_function():
            inner_function()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            outer_function()

            assert len(w) == 1
            # Warning should point to appropriate stack level


class TestDeprecatedSymbols:
    """Test that documented deprecated symbols are in registry."""

    def test_network_address_deprecations(self):
        """Verify NetworkAddress related deprecations."""
        assert is_deprecated("io.NetworkAddress()")
        assert is_deprecated("io.NetworkAddress.set_from_string()")
        assert is_deprecated("io.NetworkAddress.hostentry")

    def test_host_entry_deprecations(self):
        """Verify HostEntry related deprecations."""
        assert is_deprecated("io.HostEntry.get_network_addresses()")
        assert is_deprecated("io.HostEntry.get_network_address()")

    def test_socket_deprecations(self):
        """Verify Socket initialization deprecations."""
        assert is_deprecated("io.Socket() without family")
        assert is_deprecated("ssl.SSLSocket() without family")

    def test_all_deprecations_have_messages(self):
        """Verify all registered deprecations have non-empty messages."""
        for symbol, message in DEPRECATED_REGISTRY.items():
            assert message, f"Symbol {symbol} has empty deprecation message"
            assert len(message) > 10, f"Symbol {symbol} has suspiciously short message"


class TestDeprecationGuidance:
    """Test that deprecation messages provide useful guidance."""

    def test_messages_suggest_alternatives(self):
        """Verify deprecation messages suggest alternatives."""
        for symbol, message in DEPRECATED_REGISTRY.items():
            msg_lower = message.lower()
            # Messages should contain guidance words
            has_guidance = any(
                word in msg_lower
                for word in ['use', 'instead', 'recommend', 'prefer', 'replace']
            )
            assert has_guidance, f"Message for {symbol} lacks guidance: {message}"

    def test_messages_explain_reason(self):
        """Verify messages explain why something is deprecated."""
        # Most deprecations are due to IPv4 limitations
        ipv4_related = [
            "io.NetworkAddress()",
            "io.NetworkAddress.set_from_string()",
            "io.NetworkAddress.hostentry",
        ]

        for symbol in ipv4_related:
            msg = get_deprecation_message(symbol)
            assert msg is not None
            assert "IPv4" in msg or "ipv4" in msg.lower()


class TestWarningBehavior:
    """Test warning behavior in different configurations."""

    def test_warnings_respect_filter(self):
        """Verify warnings respect Python's warning filters."""
        # Ignore all deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore", DeprecationWarning)

            warn_deprecated("test.symbol")

            # Warning should be filtered out
            assert len(w) == 0

    def test_warnings_can_be_errors(self):
        """Verify warnings can be turned into errors."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)

            with pytest.raises(DeprecationWarning):
                warn_deprecated("test.symbol")

    def test_multiple_warnings(self):
        """Test multiple deprecation warnings can be emitted."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            warn_deprecated("io.NetworkAddress()")
            warn_deprecated("io.Socket() without family")
            warn_deprecated("ssl.SSLSocket() without family")

            assert len(w) == 3
            assert all(issubclass(warning.category, DeprecationWarning) for warning in w)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
