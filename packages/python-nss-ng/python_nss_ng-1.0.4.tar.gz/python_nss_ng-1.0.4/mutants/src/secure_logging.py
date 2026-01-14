# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Secure logging utilities for python-nss-ng.

This module provides security-conscious logging wrappers that help prevent
accidental logging of sensitive cryptographic material.

The intentional use of both print() and logging in python-nss-ng:
- print() is used for control flow and status messages in examples to avoid
  accidental capture by log handlers that might leak sensitive information
- logging is used for diagnostics and errors in library code with careful
  attention to what is logged

This module helps enforce these patterns and provides utilities for secure logging.
"""

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class LogSensitivity(Enum):
    """Classification of log message sensitivity."""

    PUBLIC = "public"
    """Safe for logging - contains no sensitive information."""

    SENSITIVE = "sensitive"
    """Contains sensitive information - should not be logged."""

    REDACTED = "redacted"
    """Should be logged in redacted form only."""


# Items that should NEVER be logged
FORBIDDEN_LOG_PATTERNS = {
    "private key",
    "priv_key",
    "private_key",
    "password",
    "passwd",
    "passphrase",
    "secret",
    "pin",
    "token",
    "key_material",
    "symmetric_key",
    "session_key",
    "master_secret",
}


def x_secure_log__mutmut_orig(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = False, redact: bool = False
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = redact_message(message)

    logger_fn(message)


def x_secure_log__mutmut_1(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = True, redact: bool = False
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = redact_message(message)

    logger_fn(message)


def x_secure_log__mutmut_2(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = False, redact: bool = True
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = redact_message(message)

    logger_fn(message)


def x_secure_log__mutmut_3(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = False, redact: bool = False
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = None

    logger_fn(message)


def x_secure_log__mutmut_4(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = False, redact: bool = False
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = redact_message(None)

    logger_fn(message)


def x_secure_log__mutmut_5(
    logger_fn: Callable[[str], None], message: str, *, sensitive: bool = False, redact: bool = False
) -> None:
    """
    Securely log a message with sensitivity awareness.

    Args:
        logger_fn: The logging function to call (e.g., logger.debug, logger.error)
        message: The message to log
        sensitive: If True, the message will not be logged at all
        redact: If True, attempt to redact sensitive parts of the message

    Examples:
        >>> logger = logging.getLogger(__name__)
        >>> secure_log(logger.info, "Operation successful", sensitive=False)
        >>> secure_log(logger.debug, "Private key loaded", sensitive=True)  # Not logged
        >>> secure_log(logger.info, "Key size: 2048", redact=True)
    """
    if sensitive:
        # Drop sensitive messages entirely
        return

    if redact:
        message = redact_message(message)

    logger_fn(None)

x_secure_log__mutmut_mutants : ClassVar[MutantDict] = {
'x_secure_log__mutmut_1': x_secure_log__mutmut_1,
    'x_secure_log__mutmut_2': x_secure_log__mutmut_2,
    'x_secure_log__mutmut_3': x_secure_log__mutmut_3,
    'x_secure_log__mutmut_4': x_secure_log__mutmut_4,
    'x_secure_log__mutmut_5': x_secure_log__mutmut_5
}

def secure_log(*args, **kwargs):
    result = _mutmut_trampoline(x_secure_log__mutmut_orig, x_secure_log__mutmut_mutants, args, kwargs)
    return result

secure_log.__signature__ = _mutmut_signature(x_secure_log__mutmut_orig)
x_secure_log__mutmut_orig.__name__ = 'x_secure_log'


def x_redact_message__mutmut_orig(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_1(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = None

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_2(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(None, "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_3(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", None, message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_4(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", None)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_5(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub("[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_6(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_7(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", )

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_8(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"XX\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)XX", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_9(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[a-za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_10(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-ZA-Z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_11(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "XX[REDACTED_BASE64]XX", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_12(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[redacted_base64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_13(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = None

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_14(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(None, "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_15(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", None, message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_16(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", None)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_17(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub("[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_18(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_19(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", )

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_20(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"XX\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\bXX", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_21(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zg-z+/])[a-za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_22(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[G-ZG-Z+/])[A-ZA-Z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_23(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "XX[REDACTED_BASE64]XX", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_24(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[redacted_base64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_25(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = None

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_26(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(None, "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_27(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", None, message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_28(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", None)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_29(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub("[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_30(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_31(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", )

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_32(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"XX\b[0-9a-fA-F]{32,}\bXX", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_33(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fa-f]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_34(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9A-FA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_35(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "XX[REDACTED_HEX]XX", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_36(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[redacted_hex]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_37(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        None, r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_38(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", None, message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_39(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", None, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_40(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=None
    )


def x_redact_message__mutmut_41(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_42(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_43(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", flags=re.IGNORECASE
    )


def x_redact_message__mutmut_44(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, )


def x_redact_message__mutmut_45(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"XX(password|passwd|pwd|pin)\s*[:=]\s*\S+XX", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_46(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(PASSWORD|PASSWD|PWD|PIN)\s*[:=]\s*\S+", r"\1: [REDACTED]", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_47(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"XX\1: [REDACTED]XX", message, flags=re.IGNORECASE
    )


def x_redact_message__mutmut_48(message: str) -> str:
    """
    Redact potentially sensitive information from a log message.

    This is a basic implementation that replaces common patterns.
    For production use, consider more sophisticated redaction.

    Args:
        message: The message to redact

    Returns:
        The redacted message
    """
    import re

    # Redact things that look like base64 encoded data (common for keys)
    # Base64 can end with = or == padding, which hex never has
    # Check for base64 with padding first (= is not a word char, so use lookahead)
    message = re.sub(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", "[REDACTED_BASE64]", message)

    # Then check for base64 without padding but with non-hex characters
    # Must contain at least one non-hex character (g-z, G-Z, +, /) to distinguish from hex
    message = re.sub(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", "[REDACTED_BASE64]", message)

    # Redact things that look like hex keys (long hex strings - only 0-9a-fA-F)
    # Must have at least 32 characters and ONLY hex characters
    message = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[REDACTED_HEX]", message)

    # Redact password-like patterns
    return re.sub(
        r"(password|passwd|pwd|pin)\s*[:=]\s*\S+", r"\1: [redacted]", message, flags=re.IGNORECASE
    )

x_redact_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_redact_message__mutmut_1': x_redact_message__mutmut_1,
    'x_redact_message__mutmut_2': x_redact_message__mutmut_2,
    'x_redact_message__mutmut_3': x_redact_message__mutmut_3,
    'x_redact_message__mutmut_4': x_redact_message__mutmut_4,
    'x_redact_message__mutmut_5': x_redact_message__mutmut_5,
    'x_redact_message__mutmut_6': x_redact_message__mutmut_6,
    'x_redact_message__mutmut_7': x_redact_message__mutmut_7,
    'x_redact_message__mutmut_8': x_redact_message__mutmut_8,
    'x_redact_message__mutmut_9': x_redact_message__mutmut_9,
    'x_redact_message__mutmut_10': x_redact_message__mutmut_10,
    'x_redact_message__mutmut_11': x_redact_message__mutmut_11,
    'x_redact_message__mutmut_12': x_redact_message__mutmut_12,
    'x_redact_message__mutmut_13': x_redact_message__mutmut_13,
    'x_redact_message__mutmut_14': x_redact_message__mutmut_14,
    'x_redact_message__mutmut_15': x_redact_message__mutmut_15,
    'x_redact_message__mutmut_16': x_redact_message__mutmut_16,
    'x_redact_message__mutmut_17': x_redact_message__mutmut_17,
    'x_redact_message__mutmut_18': x_redact_message__mutmut_18,
    'x_redact_message__mutmut_19': x_redact_message__mutmut_19,
    'x_redact_message__mutmut_20': x_redact_message__mutmut_20,
    'x_redact_message__mutmut_21': x_redact_message__mutmut_21,
    'x_redact_message__mutmut_22': x_redact_message__mutmut_22,
    'x_redact_message__mutmut_23': x_redact_message__mutmut_23,
    'x_redact_message__mutmut_24': x_redact_message__mutmut_24,
    'x_redact_message__mutmut_25': x_redact_message__mutmut_25,
    'x_redact_message__mutmut_26': x_redact_message__mutmut_26,
    'x_redact_message__mutmut_27': x_redact_message__mutmut_27,
    'x_redact_message__mutmut_28': x_redact_message__mutmut_28,
    'x_redact_message__mutmut_29': x_redact_message__mutmut_29,
    'x_redact_message__mutmut_30': x_redact_message__mutmut_30,
    'x_redact_message__mutmut_31': x_redact_message__mutmut_31,
    'x_redact_message__mutmut_32': x_redact_message__mutmut_32,
    'x_redact_message__mutmut_33': x_redact_message__mutmut_33,
    'x_redact_message__mutmut_34': x_redact_message__mutmut_34,
    'x_redact_message__mutmut_35': x_redact_message__mutmut_35,
    'x_redact_message__mutmut_36': x_redact_message__mutmut_36,
    'x_redact_message__mutmut_37': x_redact_message__mutmut_37,
    'x_redact_message__mutmut_38': x_redact_message__mutmut_38,
    'x_redact_message__mutmut_39': x_redact_message__mutmut_39,
    'x_redact_message__mutmut_40': x_redact_message__mutmut_40,
    'x_redact_message__mutmut_41': x_redact_message__mutmut_41,
    'x_redact_message__mutmut_42': x_redact_message__mutmut_42,
    'x_redact_message__mutmut_43': x_redact_message__mutmut_43,
    'x_redact_message__mutmut_44': x_redact_message__mutmut_44,
    'x_redact_message__mutmut_45': x_redact_message__mutmut_45,
    'x_redact_message__mutmut_46': x_redact_message__mutmut_46,
    'x_redact_message__mutmut_47': x_redact_message__mutmut_47,
    'x_redact_message__mutmut_48': x_redact_message__mutmut_48
}

def redact_message(*args, **kwargs):
    result = _mutmut_trampoline(x_redact_message__mutmut_orig, x_redact_message__mutmut_mutants, args, kwargs)
    return result

redact_message.__signature__ = _mutmut_signature(x_redact_message__mutmut_orig)
x_redact_message__mutmut_orig.__name__ = 'x_redact_message'


def x_check_message_safety__mutmut_orig(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_1(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = None

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_2(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.upper()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_3(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern not in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_4(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(None, message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_5(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", None):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_6(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_7(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", ):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_8(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"XX\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)XX", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_9(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[a-za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_10(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-ZA-Z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_11(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(None, message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_12(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", None):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_13(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_14(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", ):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_15(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"XX\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\bXX", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_16(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zg-z+/])[a-za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_17(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[G-ZG-Z+/])[A-ZA-Z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_18(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(None, message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_19(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", None):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_20(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_21(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fA-F]{32,}\b", ):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_22(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"XX\b[0-9a-fA-F]{32,}\bXX", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_23(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9a-fa-f]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC


def x_check_message_safety__mutmut_24(message: str) -> LogSensitivity:
    """
    Check if a message appears to contain sensitive information.

    Args:
        message: The message to check

    Returns:
        LogSensitivity classification
    """
    message_lower = message.lower()

    # Check for forbidden patterns
    for pattern in FORBIDDEN_LOG_PATTERNS:
        if pattern in message_lower:
            return LogSensitivity.SENSITIVE

    # Check for long base64 strings (likely encoded keys)
    # Base64 can end with = or == padding, which hex never has
    import re

    if re.search(r"\b[A-Za-z0-9+/]{40,}={1,2}(?!\w)", message):
        return LogSensitivity.REDACTED

    # Base64 without padding but with non-hex characters
    if re.search(r"\b(?=.*[g-zG-Z+/])[A-Za-z0-9+/]{40,}\b", message):
        return LogSensitivity.REDACTED

    # Check for long hex strings (likely keys)
    if re.search(r"\b[0-9A-FA-F]{32,}\b", message):
        return LogSensitivity.REDACTED

    return LogSensitivity.PUBLIC

x_check_message_safety__mutmut_mutants : ClassVar[MutantDict] = {
'x_check_message_safety__mutmut_1': x_check_message_safety__mutmut_1,
    'x_check_message_safety__mutmut_2': x_check_message_safety__mutmut_2,
    'x_check_message_safety__mutmut_3': x_check_message_safety__mutmut_3,
    'x_check_message_safety__mutmut_4': x_check_message_safety__mutmut_4,
    'x_check_message_safety__mutmut_5': x_check_message_safety__mutmut_5,
    'x_check_message_safety__mutmut_6': x_check_message_safety__mutmut_6,
    'x_check_message_safety__mutmut_7': x_check_message_safety__mutmut_7,
    'x_check_message_safety__mutmut_8': x_check_message_safety__mutmut_8,
    'x_check_message_safety__mutmut_9': x_check_message_safety__mutmut_9,
    'x_check_message_safety__mutmut_10': x_check_message_safety__mutmut_10,
    'x_check_message_safety__mutmut_11': x_check_message_safety__mutmut_11,
    'x_check_message_safety__mutmut_12': x_check_message_safety__mutmut_12,
    'x_check_message_safety__mutmut_13': x_check_message_safety__mutmut_13,
    'x_check_message_safety__mutmut_14': x_check_message_safety__mutmut_14,
    'x_check_message_safety__mutmut_15': x_check_message_safety__mutmut_15,
    'x_check_message_safety__mutmut_16': x_check_message_safety__mutmut_16,
    'x_check_message_safety__mutmut_17': x_check_message_safety__mutmut_17,
    'x_check_message_safety__mutmut_18': x_check_message_safety__mutmut_18,
    'x_check_message_safety__mutmut_19': x_check_message_safety__mutmut_19,
    'x_check_message_safety__mutmut_20': x_check_message_safety__mutmut_20,
    'x_check_message_safety__mutmut_21': x_check_message_safety__mutmut_21,
    'x_check_message_safety__mutmut_22': x_check_message_safety__mutmut_22,
    'x_check_message_safety__mutmut_23': x_check_message_safety__mutmut_23,
    'x_check_message_safety__mutmut_24': x_check_message_safety__mutmut_24
}

def check_message_safety(*args, **kwargs):
    result = _mutmut_trampoline(x_check_message_safety__mutmut_orig, x_check_message_safety__mutmut_mutants, args, kwargs)
    return result

check_message_safety.__signature__ = _mutmut_signature(x_check_message_safety__mutmut_orig)
x_check_message_safety__mutmut_orig.__name__ = 'x_check_message_safety'


class SecureLogger:
    """
    A wrapper around Python's logging.Logger that enforces secure logging practices.

    This logger automatically checks messages for sensitive content and handles
    them appropriately based on configuration.

    Example:
        >>> import logging
        >>> base_logger = logging.getLogger(__name__)
        >>> secure = SecureLogger(base_logger)
        >>> secure.info("Certificate loaded successfully")
        >>> secure.debug("Processing key data", sensitive=True)  # Not logged
    """

    def xǁSecureLoggerǁ__init____mutmut_orig(self, logger: logging.Logger, auto_redact: bool = True, strict: bool = False):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = logger
        self.auto_redact = auto_redact
        self.strict = strict

    def xǁSecureLoggerǁ__init____mutmut_1(self, logger: logging.Logger, auto_redact: bool = False, strict: bool = False):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = logger
        self.auto_redact = auto_redact
        self.strict = strict

    def xǁSecureLoggerǁ__init____mutmut_2(self, logger: logging.Logger, auto_redact: bool = True, strict: bool = True):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = logger
        self.auto_redact = auto_redact
        self.strict = strict

    def xǁSecureLoggerǁ__init____mutmut_3(self, logger: logging.Logger, auto_redact: bool = True, strict: bool = False):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = None
        self.auto_redact = auto_redact
        self.strict = strict

    def xǁSecureLoggerǁ__init____mutmut_4(self, logger: logging.Logger, auto_redact: bool = True, strict: bool = False):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = logger
        self.auto_redact = None
        self.strict = strict

    def xǁSecureLoggerǁ__init____mutmut_5(self, logger: logging.Logger, auto_redact: bool = True, strict: bool = False):
        """
        Initialize SecureLogger.

        Args:
            logger: The underlying Python logger to wrap
            auto_redact: If True, automatically redact suspicious content
            strict: If True, raise exception on attempt to log sensitive data
        """
        self.logger = logger
        self.auto_redact = auto_redact
        self.strict = None

    xǁSecureLoggerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁ__init____mutmut_1': xǁSecureLoggerǁ__init____mutmut_1,
        'xǁSecureLoggerǁ__init____mutmut_2': xǁSecureLoggerǁ__init____mutmut_2,
        'xǁSecureLoggerǁ__init____mutmut_3': xǁSecureLoggerǁ__init____mutmut_3,
        'xǁSecureLoggerǁ__init____mutmut_4': xǁSecureLoggerǁ__init____mutmut_4,
        'xǁSecureLoggerǁ__init____mutmut_5': xǁSecureLoggerǁ__init____mutmut_5
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result

    __init__.__signature__ = _mutmut_signature(xǁSecureLoggerǁ__init____mutmut_orig)
    xǁSecureLoggerǁ__init____mutmut_orig.__name__ = 'xǁSecureLoggerǁ__init__'

    def xǁSecureLoggerǁ_log__mutmut_orig(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_1(
        self, level: int, message: str, sensitive: bool = True, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_2(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(None)
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_3(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:51]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_4(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = None
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_5(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(None)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_6(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity != LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_7(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(None)
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_8(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:51]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_9(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity != LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_10(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = None

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_11(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(None)

        self.logger.log(level, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_12(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(None, message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_13(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, None, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_14(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(message, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_15(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, *args, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_16(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, **kwargs)

    def xǁSecureLoggerǁ_log__mutmut_17(
        self, level: int, message: str, sensitive: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Internal logging method with sensitivity checks."""
        if sensitive:
            if self.strict:
                raise ValueError(f"Attempt to log sensitive data: {message[:50]}...")
            return

        # Automatic sensitivity detection
        if self.auto_redact:
            sensitivity = check_message_safety(message)
            if sensitivity == LogSensitivity.SENSITIVE:
                if self.strict:
                    raise ValueError(f"Potentially sensitive data detected: {message[:50]}...")
                return
            if sensitivity == LogSensitivity.REDACTED:
                message = redact_message(message)

        self.logger.log(level, message, *args, )

    xǁSecureLoggerǁ_log__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁ_log__mutmut_1': xǁSecureLoggerǁ_log__mutmut_1,
        'xǁSecureLoggerǁ_log__mutmut_2': xǁSecureLoggerǁ_log__mutmut_2,
        'xǁSecureLoggerǁ_log__mutmut_3': xǁSecureLoggerǁ_log__mutmut_3,
        'xǁSecureLoggerǁ_log__mutmut_4': xǁSecureLoggerǁ_log__mutmut_4,
        'xǁSecureLoggerǁ_log__mutmut_5': xǁSecureLoggerǁ_log__mutmut_5,
        'xǁSecureLoggerǁ_log__mutmut_6': xǁSecureLoggerǁ_log__mutmut_6,
        'xǁSecureLoggerǁ_log__mutmut_7': xǁSecureLoggerǁ_log__mutmut_7,
        'xǁSecureLoggerǁ_log__mutmut_8': xǁSecureLoggerǁ_log__mutmut_8,
        'xǁSecureLoggerǁ_log__mutmut_9': xǁSecureLoggerǁ_log__mutmut_9,
        'xǁSecureLoggerǁ_log__mutmut_10': xǁSecureLoggerǁ_log__mutmut_10,
        'xǁSecureLoggerǁ_log__mutmut_11': xǁSecureLoggerǁ_log__mutmut_11,
        'xǁSecureLoggerǁ_log__mutmut_12': xǁSecureLoggerǁ_log__mutmut_12,
        'xǁSecureLoggerǁ_log__mutmut_13': xǁSecureLoggerǁ_log__mutmut_13,
        'xǁSecureLoggerǁ_log__mutmut_14': xǁSecureLoggerǁ_log__mutmut_14,
        'xǁSecureLoggerǁ_log__mutmut_15': xǁSecureLoggerǁ_log__mutmut_15,
        'xǁSecureLoggerǁ_log__mutmut_16': xǁSecureLoggerǁ_log__mutmut_16,
        'xǁSecureLoggerǁ_log__mutmut_17': xǁSecureLoggerǁ_log__mutmut_17
    }

    def _log(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁ_log__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁ_log__mutmut_mutants"), args, kwargs, self)
        return result

    _log.__signature__ = _mutmut_signature(xǁSecureLoggerǁ_log__mutmut_orig)
    xǁSecureLoggerǁ_log__mutmut_orig.__name__ = 'xǁSecureLoggerǁ_log'

    def xǁSecureLoggerǁdebug__mutmut_orig(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_1(self, message: str, sensitive: bool = True, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_2(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(None, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_3(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, None, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_4(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, None, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_5(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_6(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_7(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, *args, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_8(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, sensitive, **kwargs)

    def xǁSecureLoggerǁdebug__mutmut_9(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, sensitive, *args, )

    xǁSecureLoggerǁdebug__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁdebug__mutmut_1': xǁSecureLoggerǁdebug__mutmut_1,
        'xǁSecureLoggerǁdebug__mutmut_2': xǁSecureLoggerǁdebug__mutmut_2,
        'xǁSecureLoggerǁdebug__mutmut_3': xǁSecureLoggerǁdebug__mutmut_3,
        'xǁSecureLoggerǁdebug__mutmut_4': xǁSecureLoggerǁdebug__mutmut_4,
        'xǁSecureLoggerǁdebug__mutmut_5': xǁSecureLoggerǁdebug__mutmut_5,
        'xǁSecureLoggerǁdebug__mutmut_6': xǁSecureLoggerǁdebug__mutmut_6,
        'xǁSecureLoggerǁdebug__mutmut_7': xǁSecureLoggerǁdebug__mutmut_7,
        'xǁSecureLoggerǁdebug__mutmut_8': xǁSecureLoggerǁdebug__mutmut_8,
        'xǁSecureLoggerǁdebug__mutmut_9': xǁSecureLoggerǁdebug__mutmut_9
    }

    def debug(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁdebug__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁdebug__mutmut_mutants"), args, kwargs, self)
        return result

    debug.__signature__ = _mutmut_signature(xǁSecureLoggerǁdebug__mutmut_orig)
    xǁSecureLoggerǁdebug__mutmut_orig.__name__ = 'xǁSecureLoggerǁdebug'

    def xǁSecureLoggerǁinfo__mutmut_orig(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_1(self, message: str, sensitive: bool = True, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_2(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(None, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_3(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, None, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_4(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, None, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_5(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_6(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_7(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, *args, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_8(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, sensitive, **kwargs)

    def xǁSecureLoggerǁinfo__mutmut_9(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, sensitive, *args, )

    xǁSecureLoggerǁinfo__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁinfo__mutmut_1': xǁSecureLoggerǁinfo__mutmut_1,
        'xǁSecureLoggerǁinfo__mutmut_2': xǁSecureLoggerǁinfo__mutmut_2,
        'xǁSecureLoggerǁinfo__mutmut_3': xǁSecureLoggerǁinfo__mutmut_3,
        'xǁSecureLoggerǁinfo__mutmut_4': xǁSecureLoggerǁinfo__mutmut_4,
        'xǁSecureLoggerǁinfo__mutmut_5': xǁSecureLoggerǁinfo__mutmut_5,
        'xǁSecureLoggerǁinfo__mutmut_6': xǁSecureLoggerǁinfo__mutmut_6,
        'xǁSecureLoggerǁinfo__mutmut_7': xǁSecureLoggerǁinfo__mutmut_7,
        'xǁSecureLoggerǁinfo__mutmut_8': xǁSecureLoggerǁinfo__mutmut_8,
        'xǁSecureLoggerǁinfo__mutmut_9': xǁSecureLoggerǁinfo__mutmut_9
    }

    def info(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁinfo__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁinfo__mutmut_mutants"), args, kwargs, self)
        return result

    info.__signature__ = _mutmut_signature(xǁSecureLoggerǁinfo__mutmut_orig)
    xǁSecureLoggerǁinfo__mutmut_orig.__name__ = 'xǁSecureLoggerǁinfo'

    def xǁSecureLoggerǁwarning__mutmut_orig(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_1(self, message: str, sensitive: bool = True, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_2(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(None, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_3(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, None, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_4(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, None, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_5(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_6(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_7(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, *args, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_8(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, sensitive, **kwargs)

    def xǁSecureLoggerǁwarning__mutmut_9(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, sensitive, *args, )

    xǁSecureLoggerǁwarning__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁwarning__mutmut_1': xǁSecureLoggerǁwarning__mutmut_1,
        'xǁSecureLoggerǁwarning__mutmut_2': xǁSecureLoggerǁwarning__mutmut_2,
        'xǁSecureLoggerǁwarning__mutmut_3': xǁSecureLoggerǁwarning__mutmut_3,
        'xǁSecureLoggerǁwarning__mutmut_4': xǁSecureLoggerǁwarning__mutmut_4,
        'xǁSecureLoggerǁwarning__mutmut_5': xǁSecureLoggerǁwarning__mutmut_5,
        'xǁSecureLoggerǁwarning__mutmut_6': xǁSecureLoggerǁwarning__mutmut_6,
        'xǁSecureLoggerǁwarning__mutmut_7': xǁSecureLoggerǁwarning__mutmut_7,
        'xǁSecureLoggerǁwarning__mutmut_8': xǁSecureLoggerǁwarning__mutmut_8,
        'xǁSecureLoggerǁwarning__mutmut_9': xǁSecureLoggerǁwarning__mutmut_9
    }

    def warning(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁwarning__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁwarning__mutmut_mutants"), args, kwargs, self)
        return result

    warning.__signature__ = _mutmut_signature(xǁSecureLoggerǁwarning__mutmut_orig)
    xǁSecureLoggerǁwarning__mutmut_orig.__name__ = 'xǁSecureLoggerǁwarning'

    def xǁSecureLoggerǁerror__mutmut_orig(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_1(self, message: str, sensitive: bool = True, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_2(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(None, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_3(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, None, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_4(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, None, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_5(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_6(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_7(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, *args, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_8(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, sensitive, **kwargs)

    def xǁSecureLoggerǁerror__mutmut_9(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, sensitive, *args, )

    xǁSecureLoggerǁerror__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁerror__mutmut_1': xǁSecureLoggerǁerror__mutmut_1,
        'xǁSecureLoggerǁerror__mutmut_2': xǁSecureLoggerǁerror__mutmut_2,
        'xǁSecureLoggerǁerror__mutmut_3': xǁSecureLoggerǁerror__mutmut_3,
        'xǁSecureLoggerǁerror__mutmut_4': xǁSecureLoggerǁerror__mutmut_4,
        'xǁSecureLoggerǁerror__mutmut_5': xǁSecureLoggerǁerror__mutmut_5,
        'xǁSecureLoggerǁerror__mutmut_6': xǁSecureLoggerǁerror__mutmut_6,
        'xǁSecureLoggerǁerror__mutmut_7': xǁSecureLoggerǁerror__mutmut_7,
        'xǁSecureLoggerǁerror__mutmut_8': xǁSecureLoggerǁerror__mutmut_8,
        'xǁSecureLoggerǁerror__mutmut_9': xǁSecureLoggerǁerror__mutmut_9
    }

    def error(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁerror__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁerror__mutmut_mutants"), args, kwargs, self)
        return result

    error.__signature__ = _mutmut_signature(xǁSecureLoggerǁerror__mutmut_orig)
    xǁSecureLoggerǁerror__mutmut_orig.__name__ = 'xǁSecureLoggerǁerror'

    def xǁSecureLoggerǁcritical__mutmut_orig(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_1(self, message: str, sensitive: bool = True, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_2(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(None, message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_3(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, None, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_4(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, None, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_5(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(message, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_6(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, sensitive, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_7(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_8(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, sensitive, **kwargs)

    def xǁSecureLoggerǁcritical__mutmut_9(self, message: str, sensitive: bool = False, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, sensitive, *args, )

    xǁSecureLoggerǁcritical__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureLoggerǁcritical__mutmut_1': xǁSecureLoggerǁcritical__mutmut_1,
        'xǁSecureLoggerǁcritical__mutmut_2': xǁSecureLoggerǁcritical__mutmut_2,
        'xǁSecureLoggerǁcritical__mutmut_3': xǁSecureLoggerǁcritical__mutmut_3,
        'xǁSecureLoggerǁcritical__mutmut_4': xǁSecureLoggerǁcritical__mutmut_4,
        'xǁSecureLoggerǁcritical__mutmut_5': xǁSecureLoggerǁcritical__mutmut_5,
        'xǁSecureLoggerǁcritical__mutmut_6': xǁSecureLoggerǁcritical__mutmut_6,
        'xǁSecureLoggerǁcritical__mutmut_7': xǁSecureLoggerǁcritical__mutmut_7,
        'xǁSecureLoggerǁcritical__mutmut_8': xǁSecureLoggerǁcritical__mutmut_8,
        'xǁSecureLoggerǁcritical__mutmut_9': xǁSecureLoggerǁcritical__mutmut_9
    }

    def critical(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureLoggerǁcritical__mutmut_orig"), object.__getattribute__(self, "xǁSecureLoggerǁcritical__mutmut_mutants"), args, kwargs, self)
        return result

    critical.__signature__ = _mutmut_signature(xǁSecureLoggerǁcritical__mutmut_orig)
    xǁSecureLoggerǁcritical__mutmut_orig.__name__ = 'xǁSecureLoggerǁcritical'


def x_get_secure_logger__mutmut_orig(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_1(name: str, auto_redact: bool = False, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_2(name: str, auto_redact: bool = True, strict: bool = True) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_3(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = None
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_4(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(None)
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_5(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(None, auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_6(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=None, strict=strict)


def x_get_secure_logger__mutmut_7(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=auto_redact, strict=None)


def x_get_secure_logger__mutmut_8(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(auto_redact=auto_redact, strict=strict)


def x_get_secure_logger__mutmut_9(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, strict=strict)


def x_get_secure_logger__mutmut_10(name: str, auto_redact: bool = True, strict: bool = False) -> SecureLogger:
    """
    Get a SecureLogger instance.

    Args:
        name: Logger name (typically __name__)
        auto_redact: Enable automatic redaction
        strict: Enable strict mode (raises exceptions on sensitive data)

    Returns:
        A SecureLogger instance
    """
    base_logger = logging.getLogger(name)
    return SecureLogger(base_logger, auto_redact=auto_redact, )

x_get_secure_logger__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_secure_logger__mutmut_1': x_get_secure_logger__mutmut_1,
    'x_get_secure_logger__mutmut_2': x_get_secure_logger__mutmut_2,
    'x_get_secure_logger__mutmut_3': x_get_secure_logger__mutmut_3,
    'x_get_secure_logger__mutmut_4': x_get_secure_logger__mutmut_4,
    'x_get_secure_logger__mutmut_5': x_get_secure_logger__mutmut_5,
    'x_get_secure_logger__mutmut_6': x_get_secure_logger__mutmut_6,
    'x_get_secure_logger__mutmut_7': x_get_secure_logger__mutmut_7,
    'x_get_secure_logger__mutmut_8': x_get_secure_logger__mutmut_8,
    'x_get_secure_logger__mutmut_9': x_get_secure_logger__mutmut_9,
    'x_get_secure_logger__mutmut_10': x_get_secure_logger__mutmut_10
}

def get_secure_logger(*args, **kwargs):
    result = _mutmut_trampoline(x_get_secure_logger__mutmut_orig, x_get_secure_logger__mutmut_mutants, args, kwargs)
    return result

get_secure_logger.__signature__ = _mutmut_signature(x_get_secure_logger__mutmut_orig)
x_get_secure_logger__mutmut_orig.__name__ = 'x_get_secure_logger'


def x_log_exception_safely__mutmut_orig(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_1(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "XXXX",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_2(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = True,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_3(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = None
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_4(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(None).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_5(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = None

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_6(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(None)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_7(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = None

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_8(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(None)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_9(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity != LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_10(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = None
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_11(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity != LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_12(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = None
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_13(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(None)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_14(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = None

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_15(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(None)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_16(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = None
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_17(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(None, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_18(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=None)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_19(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_20(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, )
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_21(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=4)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(line.strip())}")


def x_log_exception_safely__mutmut_22(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(None)


def x_log_exception_safely__mutmut_23(
    logger_fn: Callable[[str], None],
    exc: Exception,
    context: str = "",
    *,
    include_traceback: bool = False,
) -> None:
    """
    Log an exception in a secure manner, avoiding sensitive data leakage.

    This function logs exception information while being careful not to
    expose sensitive data that might be in exception messages (e.g.,
    file paths containing key material, connection strings with passwords).

    Args:
        logger_fn: The logging function to call (e.g., logger.error)
        exc: The exception to log
        context: Additional context about where the exception occurred
        include_traceback: If True, include limited traceback info

    Example:
        >>> try:
        ...     nss.nss_init("invalid_path")
        ... except Exception as e:
        ...     log_exception_safely(logger.error, e, "NSS initialization")
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Check if exception message appears sensitive
    sensitivity = check_message_safety(exc_message)

    if sensitivity == LogSensitivity.SENSITIVE:
        # Log only the exception type and context
        msg = f"{context}: {exc_type} occurred (details redacted for security)"
    elif sensitivity == LogSensitivity.REDACTED:
        # Log with redaction
        msg = f"{context}: {exc_type}: {redact_message(exc_message)}"
    else:
        # Safe to log
        msg = f"{context}: {exc_type}: {exc_message}" if context else f"{exc_type}: {exc_message}"

    logger_fn(msg)

    if include_traceback:
        # Only include limited traceback info, not full stack
        import traceback

        tb_lines = traceback.format_tb(exc.__traceback__, limit=3)
        # Redact each line of traceback
        for line in tb_lines:
            logger_fn(f"  {redact_message(None)}")

x_log_exception_safely__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_exception_safely__mutmut_1': x_log_exception_safely__mutmut_1,
    'x_log_exception_safely__mutmut_2': x_log_exception_safely__mutmut_2,
    'x_log_exception_safely__mutmut_3': x_log_exception_safely__mutmut_3,
    'x_log_exception_safely__mutmut_4': x_log_exception_safely__mutmut_4,
    'x_log_exception_safely__mutmut_5': x_log_exception_safely__mutmut_5,
    'x_log_exception_safely__mutmut_6': x_log_exception_safely__mutmut_6,
    'x_log_exception_safely__mutmut_7': x_log_exception_safely__mutmut_7,
    'x_log_exception_safely__mutmut_8': x_log_exception_safely__mutmut_8,
    'x_log_exception_safely__mutmut_9': x_log_exception_safely__mutmut_9,
    'x_log_exception_safely__mutmut_10': x_log_exception_safely__mutmut_10,
    'x_log_exception_safely__mutmut_11': x_log_exception_safely__mutmut_11,
    'x_log_exception_safely__mutmut_12': x_log_exception_safely__mutmut_12,
    'x_log_exception_safely__mutmut_13': x_log_exception_safely__mutmut_13,
    'x_log_exception_safely__mutmut_14': x_log_exception_safely__mutmut_14,
    'x_log_exception_safely__mutmut_15': x_log_exception_safely__mutmut_15,
    'x_log_exception_safely__mutmut_16': x_log_exception_safely__mutmut_16,
    'x_log_exception_safely__mutmut_17': x_log_exception_safely__mutmut_17,
    'x_log_exception_safely__mutmut_18': x_log_exception_safely__mutmut_18,
    'x_log_exception_safely__mutmut_19': x_log_exception_safely__mutmut_19,
    'x_log_exception_safely__mutmut_20': x_log_exception_safely__mutmut_20,
    'x_log_exception_safely__mutmut_21': x_log_exception_safely__mutmut_21,
    'x_log_exception_safely__mutmut_22': x_log_exception_safely__mutmut_22,
    'x_log_exception_safely__mutmut_23': x_log_exception_safely__mutmut_23
}

def log_exception_safely(*args, **kwargs):
    result = _mutmut_trampoline(x_log_exception_safely__mutmut_orig, x_log_exception_safely__mutmut_mutants, args, kwargs)
    return result

log_exception_safely.__signature__ = _mutmut_signature(x_log_exception_safely__mutmut_orig)
x_log_exception_safely__mutmut_orig.__name__ = 'x_log_exception_safely'


class SecureExceptionHandler:
    """
    Context manager for secure exception handling with logging.

    Use this to wrap code blocks where you want automatic secure
    exception logging without exposing sensitive information.

    Example:
        >>> logger = logging.getLogger(__name__)
        >>> with SecureExceptionHandler(logger, "Certificate loading"):
        ...     cert = nss.Certificate(certdata)
    """

    def xǁSecureExceptionHandlerǁ__init____mutmut_orig(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = True,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = logger
        self.context = context
        self.reraise = reraise
        self.log_level = log_level

    def xǁSecureExceptionHandlerǁ__init____mutmut_1(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = False,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = logger
        self.context = context
        self.reraise = reraise
        self.log_level = log_level

    def xǁSecureExceptionHandlerǁ__init____mutmut_2(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = True,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = None
        self.context = context
        self.reraise = reraise
        self.log_level = log_level

    def xǁSecureExceptionHandlerǁ__init____mutmut_3(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = True,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = logger
        self.context = None
        self.reraise = reraise
        self.log_level = log_level

    def xǁSecureExceptionHandlerǁ__init____mutmut_4(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = True,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = logger
        self.context = context
        self.reraise = None
        self.log_level = log_level

    def xǁSecureExceptionHandlerǁ__init____mutmut_5(
        self,
        logger: logging.Logger,
        context: str,
        reraise: bool = True,
        log_level: int = logging.ERROR,
    ):
        """
        Initialize the exception handler.

        Args:
            logger: Logger to use for exception logging
            context: Context description for the operation
            reraise: If True, re-raise the exception after logging
            log_level: Logging level to use (default: ERROR)
        """
        self.logger = logger
        self.context = context
        self.reraise = reraise
        self.log_level = None

    xǁSecureExceptionHandlerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureExceptionHandlerǁ__init____mutmut_1': xǁSecureExceptionHandlerǁ__init____mutmut_1,
        'xǁSecureExceptionHandlerǁ__init____mutmut_2': xǁSecureExceptionHandlerǁ__init____mutmut_2,
        'xǁSecureExceptionHandlerǁ__init____mutmut_3': xǁSecureExceptionHandlerǁ__init____mutmut_3,
        'xǁSecureExceptionHandlerǁ__init____mutmut_4': xǁSecureExceptionHandlerǁ__init____mutmut_4,
        'xǁSecureExceptionHandlerǁ__init____mutmut_5': xǁSecureExceptionHandlerǁ__init____mutmut_5
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureExceptionHandlerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSecureExceptionHandlerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result

    __init__.__signature__ = _mutmut_signature(xǁSecureExceptionHandlerǁ__init____mutmut_orig)
    xǁSecureExceptionHandlerǁ__init____mutmut_orig.__name__ = 'xǁSecureExceptionHandlerǁ__init__'

    def __enter__(self):
        return self

    def xǁSecureExceptionHandlerǁ__exit____mutmut_orig(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_1(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_2(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(None, msg)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_3(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, None)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_4(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(msg)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_5(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, )

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_6(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(None, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_7(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, None, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_8(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, exc_val, None)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_9(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(exc_val, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_10(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, self.context)

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_11(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, exc_val, )

            # Return False to re-raise, True to suppress
            return not self.reraise
        return None

    def xǁSecureExceptionHandlerǁ__exit____mutmut_12(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception securely
            def logger_fn(msg: str) -> None:
                self.logger.log(self.log_level, msg)

            log_exception_safely(logger_fn, exc_val, self.context)

            # Return False to re-raise, True to suppress
            return self.reraise
        return None

    xǁSecureExceptionHandlerǁ__exit____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureExceptionHandlerǁ__exit____mutmut_1': xǁSecureExceptionHandlerǁ__exit____mutmut_1,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_2': xǁSecureExceptionHandlerǁ__exit____mutmut_2,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_3': xǁSecureExceptionHandlerǁ__exit____mutmut_3,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_4': xǁSecureExceptionHandlerǁ__exit____mutmut_4,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_5': xǁSecureExceptionHandlerǁ__exit____mutmut_5,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_6': xǁSecureExceptionHandlerǁ__exit____mutmut_6,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_7': xǁSecureExceptionHandlerǁ__exit____mutmut_7,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_8': xǁSecureExceptionHandlerǁ__exit____mutmut_8,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_9': xǁSecureExceptionHandlerǁ__exit____mutmut_9,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_10': xǁSecureExceptionHandlerǁ__exit____mutmut_10,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_11': xǁSecureExceptionHandlerǁ__exit____mutmut_11,
        'xǁSecureExceptionHandlerǁ__exit____mutmut_12': xǁSecureExceptionHandlerǁ__exit____mutmut_12
    }

    def __exit__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureExceptionHandlerǁ__exit____mutmut_orig"), object.__getattribute__(self, "xǁSecureExceptionHandlerǁ__exit____mutmut_mutants"), args, kwargs, self)
        return result

    __exit__.__signature__ = _mutmut_signature(xǁSecureExceptionHandlerǁ__exit____mutmut_orig)
    xǁSecureExceptionHandlerǁ__exit____mutmut_orig.__name__ = 'xǁSecureExceptionHandlerǁ__exit__'


# Example usage patterns
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Create secure logger
    logger = get_secure_logger(__name__)

    # Safe logging
    logger.info("Certificate validation successful")
    logger.debug("Key size: 2048 bits")

    # Sensitive data - not logged
    logger.debug("Private key: ABC123...", sensitive=True)

    # Auto-redacted
    logger.info("Token value: 1234567890abcdef1234567890abcdef1234567890abcdef")

    # Exception logging examples
    try:
        raise ValueError("Database path: /secret/path/to/keydb contains sensitive info")
    except ValueError as e:
        log_exception_safely(logger.error, e, "Test exception")

    # Context manager example
    base_logger = logging.getLogger("test")
    with SecureExceptionHandler(base_logger, "Demo operation", reraise=False):
        raise RuntimeError("password=secret123")

    print("\nSecure logging examples completed.")
