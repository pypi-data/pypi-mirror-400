# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Tests for secure logging utilities in python-nss-ng.

This test module verifies that the secure logging system properly
prevents logging of sensitive cryptographic material.
"""

import sys
import logging
import pytest
from io import StringIO

# Add src to path for importing secure_logging module
sys.path.insert(0, 'src')

from secure_logging import (
    LogSensitivity,
    secure_log,
    redact_message,
    check_message_safety,
    SecureLogger,
    get_secure_logger,
    FORBIDDEN_LOG_PATTERNS,
)


class TestLogSensitivity:
    """Tests for LogSensitivity enumeration."""

    def test_sensitivity_values(self):
        """Verify LogSensitivity enum values."""
        assert LogSensitivity.PUBLIC.value == "public"
        assert LogSensitivity.SENSITIVE.value == "sensitive"
        assert LogSensitivity.REDACTED.value == "redacted"


class TestMessageSafetyChecking:
    """Tests for message safety checking."""

    def test_public_messages(self):
        """Test that normal messages are classified as public."""
        assert check_message_safety("Certificate loaded successfully") == LogSensitivity.PUBLIC
        assert check_message_safety("Connection established") == LogSensitivity.PUBLIC
        assert check_message_safety("Key size: 2048 bits") == LogSensitivity.PUBLIC

    def test_sensitive_keyword_detection(self):
        """Test detection of forbidden keywords."""
        for pattern in ['private key', 'password', 'secret', 'pin']:
            message = f"Processing {pattern} data"
            assert check_message_safety(message) == LogSensitivity.SENSITIVE

    def test_hex_key_detection(self):
        """Test detection of hex-encoded keys."""
        # Short hex is OK
        assert check_message_safety("Error code: 0x1234") == LogSensitivity.PUBLIC

        # Long hex should be redacted
        long_hex = "Key data: " + "a" * 64  # 64 hex chars
        assert check_message_safety(long_hex) == LogSensitivity.REDACTED

    def test_base64_detection(self):
        """Test detection of base64-encoded data."""
        # Short base64 is OK
        assert check_message_safety("ID: ABC123") == LogSensitivity.PUBLIC

        # Long base64 should be redacted
        long_b64 = "Data: " + "A" * 50 + "=="
        assert check_message_safety(long_b64) == LogSensitivity.REDACTED

    def test_case_insensitive_detection(self):
        """Test that keyword detection is case-insensitive."""
        assert check_message_safety("PRIVATE KEY loaded") == LogSensitivity.SENSITIVE
        assert check_message_safety("Password: secret") == LogSensitivity.SENSITIVE
        assert check_message_safety("Secret Token") == LogSensitivity.SENSITIVE


class TestMessageRedaction:
    """Tests for message redaction functionality."""

    def test_redact_hex_data(self):
        """Test redaction of hexadecimal data."""
        message = "Key: 1234567890abcdef1234567890abcdef1234567890abcdef"
        redacted = redact_message(message)
        assert "[REDACTED_HEX]" in redacted
        assert "1234567890abcdef" not in redacted

    def test_redact_base64_data(self):
        """Test redaction of base64 data."""
        message = "Token: " + "A" * 50 + "=="
        redacted = redact_message(message)
        assert "[REDACTED_BASE64]" in redacted
        assert "A" * 50 not in redacted

    def test_redact_passwords(self):
        """Test redaction of password-like patterns."""
        test_cases = [
            ("password: secret123", "password: [REDACTED]"),
            ("passwd=mypass", "passwd: [REDACTED]"),
            ("PIN: 1234", "PIN: [REDACTED]"),
        ]

        for original, expected_pattern in test_cases:
            redacted = redact_message(original)
            assert "[REDACTED]" in redacted
            assert "secret123" not in redacted
            assert "mypass" not in redacted

    def test_preserve_safe_content(self):
        """Test that safe content is not redacted."""
        safe_messages = [
            "Certificate validated successfully",
            "Connection to server established",
            "Key size is 2048 bits",
        ]

        for message in safe_messages:
            redacted = redact_message(message)
            assert redacted == message


class TestSecureLogFunction:
    """Tests for the secure_log function."""

    def setup_method(self):
        """Set up test logger."""
        self.log_stream = StringIO()
        self.logger = logging.getLogger('test_secure_log')
        self.logger.handlers.clear()
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def get_log_output(self):
        """Get captured log output."""
        return self.log_stream.getvalue()

    def test_log_public_message(self):
        """Test logging of public messages."""
        secure_log(self.logger.info, "Test message", sensitive=False)
        output = self.get_log_output()
        assert "Test message" in output

    def test_drop_sensitive_message(self):
        """Test that sensitive messages are not logged."""
        secure_log(self.logger.info, "Private key: ABC123", sensitive=True)
        output = self.get_log_output()
        assert "Private key" not in output
        assert "ABC123" not in output

    def test_redact_message(self):
        """Test automatic redaction."""
        hex_key = "1234567890abcdef" * 4
        secure_log(self.logger.info, f"Key: {hex_key}", redact=True)
        output = self.get_log_output()
        assert "[REDACTED" in output
        assert hex_key not in output


class TestSecureLogger:
    """Tests for SecureLogger class."""

    def setup_method(self):
        """Set up test logger."""
        self.log_stream = StringIO()
        base_logger = logging.getLogger('test_secure_logger')
        base_logger.handlers.clear()
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.DEBUG)
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.DEBUG)

        self.secure_logger = SecureLogger(base_logger, auto_redact=True, strict=False)

    def get_log_output(self):
        """Get captured log output."""
        return self.log_stream.getvalue()

    def test_log_levels(self):
        """Test all logging levels work."""
        self.secure_logger.debug("Debug message")
        self.secure_logger.info("Info message")
        self.secure_logger.warning("Warning message")
        self.secure_logger.error("Error message")
        self.secure_logger.critical("Critical message")

        output = self.get_log_output()
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
        assert "Critical message" in output

    def test_sensitive_not_logged(self):
        """Test sensitive messages are dropped."""
        self.secure_logger.info("Normal message")
        self.secure_logger.info("Sensitive data", sensitive=True)

        output = self.get_log_output()
        assert "Normal message" in output
        assert "Sensitive data" not in output

    def test_auto_redaction(self):
        """Test automatic redaction of suspicious content."""
        hex_data = "a" * 64
        self.secure_logger.info(f"Processing: {hex_data}")

        output = self.get_log_output()
        assert "[REDACTED" in output
        assert hex_data not in output

    def test_strict_mode_raises(self):
        """Test strict mode raises exceptions."""
        strict_logger = SecureLogger(
            logging.getLogger('strict_test'),
            auto_redact=True,
            strict=True
        )

        # Attempting to log sensitive data should raise
        with pytest.raises(ValueError):
            strict_logger.info("Private key data here", sensitive=True)

    def test_strict_mode_detects_patterns(self):
        """Test strict mode detects forbidden patterns."""
        strict_logger = SecureLogger(
            logging.getLogger('strict_test2'),
            auto_redact=True,
            strict=True
        )

        # Should raise when detecting forbidden pattern
        with pytest.raises(ValueError):
            strict_logger.info("The private key is: xyz")


class TestGetSecureLogger:
    """Tests for get_secure_logger factory function."""

    def test_creates_secure_logger(self):
        """Test that factory creates SecureLogger instance."""
        logger = get_secure_logger('test_factory')
        assert isinstance(logger, SecureLogger)

    def test_factory_parameters(self):
        """Test factory respects parameters."""
        logger = get_secure_logger('test_params', auto_redact=False, strict=True)
        assert isinstance(logger, SecureLogger)
        assert logger.auto_redact is False
        assert logger.strict is True


class TestRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    def setup_method(self):
        """Set up test logger."""
        self.log_stream = StringIO()
        base_logger = logging.getLogger('test_scenarios')
        base_logger.handlers.clear()
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.DEBUG)
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.DEBUG)

        self.logger = SecureLogger(base_logger)

    def get_log_output(self):
        """Get captured log output."""
        return self.log_stream.getvalue()

    def test_certificate_operations(self):
        """Test logging during certificate operations."""
        self.logger.info("Loading certificate from database")
        self.logger.debug("Certificate subject: CN=example.com")
        self.logger.info("Certificate validated successfully")

        output = self.get_log_output()
        assert "Loading certificate" in output
        assert "CN=example.com" in output
        assert "validated successfully" in output

    def test_key_generation(self):
        """Test logging during key generation."""
        self.logger.info("Generating RSA key pair")
        self.logger.debug("Key size: 2048 bits")
        self.logger.info("Key generation complete")

        # Should NOT log actual key material
        self.logger.debug("Private key material", sensitive=True)

        output = self.get_log_output()
        assert "Generating RSA" in output
        assert "2048 bits" in output
        assert "Private key material" not in output

    def test_ssl_connection(self):
        """Test logging during SSL operations."""
        self.logger.info("Establishing SSL connection")
        self.logger.debug("TLS version: 1.3")
        self.logger.debug("Cipher suite: TLS_AES_256_GCM_SHA384")
        self.logger.info("Handshake complete")

        output = self.get_log_output()
        assert "SSL connection" in output
        assert "TLS version" in output
        assert "Cipher suite" in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
