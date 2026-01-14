# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
Deprecation registry and utilities for python-nss-ng.

This module provides a centralized registry of deprecated functionality
and utilities for emitting deprecation warnings.
"""

import warnings
from typing import Dict, Optional

# Central registry of deprecated functionality
# Key: deprecated symbol name
# Value: replacement/migration guidance
DEPRECATED_REGISTRY: Dict[str, str] = {
    "io.NetworkAddress()": (
        "NetworkAddress initialization from a string parameter only works for IPv4. "
        "Use io.AddrInfo instead for proper IPv4/IPv6 support."
    ),
    "io.NetworkAddress.set_from_string()": (
        "NetworkAddress.set_from_string() only works for IPv4. "
        "Use io.AddrInfo instead for proper IPv4/IPv6 support."
    ),
    "io.NetworkAddress.hostentry": (
        "HostEntry objects only support IPv4. This property will be removed. "
        "Use io.AddrInfo instead for proper IPv4/IPv6 support."
    ),
    "io.HostEntry.get_network_addresses()": (
        "Use iteration instead (e.g., 'for net_addr in hostentry'). "
        "The port parameter is not respected; port will be the value when "
        "HostEntry object was created."
    ),
    "io.HostEntry.get_network_address()": (
        "Use indexing instead (e.g., 'hostentry[i]'). "
        "The port parameter is not respected; port will be the value when "
        "HostEntry object was created."
    ),
    "io.Socket() without family": (
        "Socket initialization without explicit family parameter is deprecated. "
        "The default family parameter of PR_AF_INET is deprecated because when "
        "iterating through NetworkAddress objects returned by AddrInfo, some "
        "addresses may be IPv6. Use the family property of the NetworkAddress "
        "object associated with the socket, e.g., Socket(net_addr.family)."
    ),
    "ssl.SSLSocket() without family": (
        "SSLSocket initialization without explicit family parameter is deprecated. "
        "The default family parameter of PR_AF_INET is deprecated because when "
        "iterating through NetworkAddress objects returned by AddrInfo, some "
        "addresses may be IPv6. Use the family property of the NetworkAddress "
        "object associated with the socket, e.g., SSLSocket(net_addr.family)."
    ),
}
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


def x_warn_deprecated__mutmut_orig(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_1(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 3
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_2(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is not None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_3(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = None

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_4(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(None, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_5(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, None)

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_6(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get("This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_7(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, )

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_8(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "XXThis functionality is deprecated.XX")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_9(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "this functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_10(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "THIS FUNCTIONALITY IS DEPRECATED.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_11(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = None

    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_12(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(None, category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_13(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=None, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_14(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, stacklevel=None)


def x_warn_deprecated__mutmut_15(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(category=DeprecationWarning, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_16(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, stacklevel=stacklevel)


def x_warn_deprecated__mutmut_17(
    symbol_name: str, alternative: Optional[str] = None, stacklevel: int = 2
) -> None:
    """
    Emit a deprecation warning for a deprecated symbol.

    Args:
        symbol_name: The name of the deprecated symbol (should be in DEPRECATED_REGISTRY)
        alternative: Optional alternative guidance (overrides registry if provided)
        stacklevel: Stack level for the warning (default: 2, caller of this function)
    """
    if alternative is None:
        alternative = DEPRECATED_REGISTRY.get(symbol_name, "This functionality is deprecated.")

    message = f"{symbol_name} is deprecated. {alternative}"

    warnings.warn(message, category=DeprecationWarning, )

x_warn_deprecated__mutmut_mutants : ClassVar[MutantDict] = {
'x_warn_deprecated__mutmut_1': x_warn_deprecated__mutmut_1,
    'x_warn_deprecated__mutmut_2': x_warn_deprecated__mutmut_2,
    'x_warn_deprecated__mutmut_3': x_warn_deprecated__mutmut_3,
    'x_warn_deprecated__mutmut_4': x_warn_deprecated__mutmut_4,
    'x_warn_deprecated__mutmut_5': x_warn_deprecated__mutmut_5,
    'x_warn_deprecated__mutmut_6': x_warn_deprecated__mutmut_6,
    'x_warn_deprecated__mutmut_7': x_warn_deprecated__mutmut_7,
    'x_warn_deprecated__mutmut_8': x_warn_deprecated__mutmut_8,
    'x_warn_deprecated__mutmut_9': x_warn_deprecated__mutmut_9,
    'x_warn_deprecated__mutmut_10': x_warn_deprecated__mutmut_10,
    'x_warn_deprecated__mutmut_11': x_warn_deprecated__mutmut_11,
    'x_warn_deprecated__mutmut_12': x_warn_deprecated__mutmut_12,
    'x_warn_deprecated__mutmut_13': x_warn_deprecated__mutmut_13,
    'x_warn_deprecated__mutmut_14': x_warn_deprecated__mutmut_14,
    'x_warn_deprecated__mutmut_15': x_warn_deprecated__mutmut_15,
    'x_warn_deprecated__mutmut_16': x_warn_deprecated__mutmut_16,
    'x_warn_deprecated__mutmut_17': x_warn_deprecated__mutmut_17
}

def warn_deprecated(*args, **kwargs):
    result = _mutmut_trampoline(x_warn_deprecated__mutmut_orig, x_warn_deprecated__mutmut_mutants, args, kwargs)
    return result

warn_deprecated.__signature__ = _mutmut_signature(x_warn_deprecated__mutmut_orig)
x_warn_deprecated__mutmut_orig.__name__ = 'x_warn_deprecated'


def x_is_deprecated__mutmut_orig(symbol_name: str) -> bool:
    """
    Check if a symbol is in the deprecation registry.

    Args:
        symbol_name: The name of the symbol to check

    Returns:
        True if the symbol is deprecated, False otherwise
    """
    return symbol_name in DEPRECATED_REGISTRY


def x_is_deprecated__mutmut_1(symbol_name: str) -> bool:
    """
    Check if a symbol is in the deprecation registry.

    Args:
        symbol_name: The name of the symbol to check

    Returns:
        True if the symbol is deprecated, False otherwise
    """
    return symbol_name not in DEPRECATED_REGISTRY

x_is_deprecated__mutmut_mutants : ClassVar[MutantDict] = {
'x_is_deprecated__mutmut_1': x_is_deprecated__mutmut_1
}

def is_deprecated(*args, **kwargs):
    result = _mutmut_trampoline(x_is_deprecated__mutmut_orig, x_is_deprecated__mutmut_mutants, args, kwargs)
    return result

is_deprecated.__signature__ = _mutmut_signature(x_is_deprecated__mutmut_orig)
x_is_deprecated__mutmut_orig.__name__ = 'x_is_deprecated'


def x_get_deprecation_message__mutmut_orig(symbol_name: str) -> Optional[str]:
    """
    Get the deprecation message for a symbol.

    Args:
        symbol_name: The name of the deprecated symbol

    Returns:
        The deprecation message, or None if the symbol is not deprecated
    """
    return DEPRECATED_REGISTRY.get(symbol_name)


def x_get_deprecation_message__mutmut_1(symbol_name: str) -> Optional[str]:
    """
    Get the deprecation message for a symbol.

    Args:
        symbol_name: The name of the deprecated symbol

    Returns:
        The deprecation message, or None if the symbol is not deprecated
    """
    return DEPRECATED_REGISTRY.get(None)

x_get_deprecation_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_deprecation_message__mutmut_1': x_get_deprecation_message__mutmut_1
}

def get_deprecation_message(*args, **kwargs):
    result = _mutmut_trampoline(x_get_deprecation_message__mutmut_orig, x_get_deprecation_message__mutmut_mutants, args, kwargs)
    return result

get_deprecation_message.__signature__ = _mutmut_signature(x_get_deprecation_message__mutmut_orig)
x_get_deprecation_message__mutmut_orig.__name__ = 'x_get_deprecation_message'


def list_deprecated() -> Dict[str, str]:
    """
    Get a copy of the entire deprecation registry.

    Returns:
        Dictionary mapping deprecated symbols to their deprecation messages
    """
    return DEPRECATED_REGISTRY.copy()
