# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
NSS lifecycle context manager for python-nss-ng.

This module provides context managers for proper NSS initialization and shutdown,
helping to avoid common lifecycle management issues.

NSS initialization and shutdown rules:
- nss_init() or nss_init_nodb() should be called exactly once per process
- nss_shutdown() should be called exactly once per process, not per thread
- Repeated init/shutdown in high-frequency loops should be avoided
- All NSS operations must occur after initialization and before shutdown

Example usage:
    >>> with NSSContext(db_name='sql:pki'):
    ...     # NSS is initialized, perform operations
    ...     cert = nss.find_cert_from_nickname('server_cert')
    ...     # NSS will be shut down on exit

    >>> with NSSContext():  # No database
    ...     # NSS initialized without database
    ...     digest = nss.sha256_digest(b"data")
"""

import contextlib
import logging
from collections.abc import Callable, Generator
from typing import Any, Optional

logger = logging.getLogger(__name__)
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


class NSSContext:
    """
    Context manager for NSS initialization and shutdown.

    This ensures proper NSS lifecycle management with automatic cleanup.

    Args:
        db_name: Path to NSS certificate database (e.g., 'sql:pki').
                 If None, NSS is initialized without a database.
        password_callback: Optional password callback function
        flags: Optional NSS initialization flags

    Example:
        >>> with NSSContext(db_name='sql:pki'):
        ...     cert = nss.find_cert_from_nickname('my_cert')
        ...     print(cert.subject)

        >>> with NSSContext():  # No database
        ...     data = b"hello world"
        ...     digest = nss.sha256_digest(data)
    """

    def xǁNSSContextǁ__init____mutmut_orig(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = password_callback
        self.flags = flags
        self._initialized = False

    def xǁNSSContextǁ__init____mutmut_1(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 1,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = password_callback
        self.flags = flags
        self._initialized = False

    def xǁNSSContextǁ__init____mutmut_2(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = None
        self.password_callback = password_callback
        self.flags = flags
        self._initialized = False

    def xǁNSSContextǁ__init____mutmut_3(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = None
        self.flags = flags
        self._initialized = False

    def xǁNSSContextǁ__init____mutmut_4(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = password_callback
        self.flags = None
        self._initialized = False

    def xǁNSSContextǁ__init____mutmut_5(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = password_callback
        self.flags = flags
        self._initialized = None

    def xǁNSSContextǁ__init____mutmut_6(
        self,
        db_name: Optional[str] = None,
        password_callback: Optional[Callable[..., Any]] = None,
        flags: int = 0,
    ):
        """Initialize NSS context manager."""
        self.db_name = db_name
        self.password_callback = password_callback
        self.flags = flags
        self._initialized = True

    xǁNSSContextǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNSSContextǁ__init____mutmut_1': xǁNSSContextǁ__init____mutmut_1,
        'xǁNSSContextǁ__init____mutmut_2': xǁNSSContextǁ__init____mutmut_2,
        'xǁNSSContextǁ__init____mutmut_3': xǁNSSContextǁ__init____mutmut_3,
        'xǁNSSContextǁ__init____mutmut_4': xǁNSSContextǁ__init____mutmut_4,
        'xǁNSSContextǁ__init____mutmut_5': xǁNSSContextǁ__init____mutmut_5,
        'xǁNSSContextǁ__init____mutmut_6': xǁNSSContextǁ__init____mutmut_6
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNSSContextǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNSSContextǁ__init____mutmut_mutants"), args, kwargs, self)
        return result

    __init__.__signature__ = _mutmut_signature(xǁNSSContextǁ__init____mutmut_orig)
    xǁNSSContextǁ__init____mutmut_orig.__name__ = 'xǁNSSContextǁ__init__'

    def xǁNSSContextǁ__enter____mutmut_orig(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_1(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(None)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_2(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(None)
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_3(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(None)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_4(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug(None)
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_5(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("XXInitializing NSS without databaseXX")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_6(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("initializing nss without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_7(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("INITIALIZING NSS WITHOUT DATABASE")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_8(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = None
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_9(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = False
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_10(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug(None)
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_11(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("XXNSS initialized successfullyXX")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_12(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("nss initialized successfully")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_13(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS INITIALIZED SUCCESSFULLY")
            return self

        except Exception as e:
            logger.error(f"Failed to initialize NSS: {e}")
            raise

    def xǁNSSContextǁ__enter____mutmut_14(self):
        """Initialize NSS on context entry."""
        try:
            import nss.nss as nss

            if self.password_callback:
                nss.set_password_callback(self.password_callback)

            if self.db_name:
                logger.debug(f"Initializing NSS with database: {self.db_name}")
                nss.nss_init(self.db_name)
            else:
                logger.debug("Initializing NSS without database")
                nss.nss_init_nodb()

            self._initialized = True
            logger.debug("NSS initialized successfully")
            return self

        except Exception as e:
            logger.error(None)
            raise

    xǁNSSContextǁ__enter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNSSContextǁ__enter____mutmut_1': xǁNSSContextǁ__enter____mutmut_1,
        'xǁNSSContextǁ__enter____mutmut_2': xǁNSSContextǁ__enter____mutmut_2,
        'xǁNSSContextǁ__enter____mutmut_3': xǁNSSContextǁ__enter____mutmut_3,
        'xǁNSSContextǁ__enter____mutmut_4': xǁNSSContextǁ__enter____mutmut_4,
        'xǁNSSContextǁ__enter____mutmut_5': xǁNSSContextǁ__enter____mutmut_5,
        'xǁNSSContextǁ__enter____mutmut_6': xǁNSSContextǁ__enter____mutmut_6,
        'xǁNSSContextǁ__enter____mutmut_7': xǁNSSContextǁ__enter____mutmut_7,
        'xǁNSSContextǁ__enter____mutmut_8': xǁNSSContextǁ__enter____mutmut_8,
        'xǁNSSContextǁ__enter____mutmut_9': xǁNSSContextǁ__enter____mutmut_9,
        'xǁNSSContextǁ__enter____mutmut_10': xǁNSSContextǁ__enter____mutmut_10,
        'xǁNSSContextǁ__enter____mutmut_11': xǁNSSContextǁ__enter____mutmut_11,
        'xǁNSSContextǁ__enter____mutmut_12': xǁNSSContextǁ__enter____mutmut_12,
        'xǁNSSContextǁ__enter____mutmut_13': xǁNSSContextǁ__enter____mutmut_13,
        'xǁNSSContextǁ__enter____mutmut_14': xǁNSSContextǁ__enter____mutmut_14
    }

    def __enter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNSSContextǁ__enter____mutmut_orig"), object.__getattribute__(self, "xǁNSSContextǁ__enter____mutmut_mutants"), args, kwargs, self)
        return result

    __enter__.__signature__ = _mutmut_signature(xǁNSSContextǁ__enter____mutmut_orig)
    xǁNSSContextǁ__enter____mutmut_orig.__name__ = 'xǁNSSContextǁ__enter__'

    def xǁNSSContextǁ__exit____mutmut_orig(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_1(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug(None)
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_2(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("XXShutting down NSSXX")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_3(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("shutting down nss")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_4(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("SHUTTING DOWN NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_5(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = None
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_6(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = True
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_7(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug(None)
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_8(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("XXNSS shutdown completeXX")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_9(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("nss shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_10(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS SHUTDOWN COMPLETE")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_11(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(None)
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return False

    def xǁNSSContextǁ__exit____mutmut_12(self, exc_type, exc_val, exc_tb):
        """Shutdown NSS on context exit."""
        if self._initialized:
            try:
                import nss.nss as nss

                logger.debug("Shutting down NSS")
                nss.nss_shutdown()
                self._initialized = False
                logger.debug("NSS shutdown complete")
            except Exception as e:
                logger.warning(f"Error during NSS shutdown: {e}")
                # Don't raise - we're already exiting

        # Return False to propagate any exception that occurred in the with block
        return True

    xǁNSSContextǁ__exit____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNSSContextǁ__exit____mutmut_1': xǁNSSContextǁ__exit____mutmut_1,
        'xǁNSSContextǁ__exit____mutmut_2': xǁNSSContextǁ__exit____mutmut_2,
        'xǁNSSContextǁ__exit____mutmut_3': xǁNSSContextǁ__exit____mutmut_3,
        'xǁNSSContextǁ__exit____mutmut_4': xǁNSSContextǁ__exit____mutmut_4,
        'xǁNSSContextǁ__exit____mutmut_5': xǁNSSContextǁ__exit____mutmut_5,
        'xǁNSSContextǁ__exit____mutmut_6': xǁNSSContextǁ__exit____mutmut_6,
        'xǁNSSContextǁ__exit____mutmut_7': xǁNSSContextǁ__exit____mutmut_7,
        'xǁNSSContextǁ__exit____mutmut_8': xǁNSSContextǁ__exit____mutmut_8,
        'xǁNSSContextǁ__exit____mutmut_9': xǁNSSContextǁ__exit____mutmut_9,
        'xǁNSSContextǁ__exit____mutmut_10': xǁNSSContextǁ__exit____mutmut_10,
        'xǁNSSContextǁ__exit____mutmut_11': xǁNSSContextǁ__exit____mutmut_11,
        'xǁNSSContextǁ__exit____mutmut_12': xǁNSSContextǁ__exit____mutmut_12
    }

    def __exit__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNSSContextǁ__exit____mutmut_orig"), object.__getattribute__(self, "xǁNSSContextǁ__exit____mutmut_mutants"), args, kwargs, self)
        return result

    __exit__.__signature__ = _mutmut_signature(xǁNSSContextǁ__exit____mutmut_orig)
    xǁNSSContextǁ__exit____mutmut_orig.__name__ = 'xǁNSSContextǁ__exit__'


@contextlib.contextmanager
def nss_context(
    db_name: Optional[str] = None,
    password_callback: Optional[Callable[..., Any]] = None,
    flags: int = 0,
) -> Generator[None, None, None]:
    """
    Functional context manager for NSS lifecycle.

    This is a functional alternative to the NSSContext class.

    Args:
        db_name: Path to NSS certificate database or None for no database
        password_callback: Optional password callback function
        flags: Optional NSS initialization flags

    Yields:
        None - context is active while NSS is initialized

    Example:
        >>> with nss_context('sql:pki'):
        ...     # NSS operations here
        ...     pass
    """
    context = NSSContext(db_name=db_name, password_callback=password_callback, flags=flags)
    with context:
        yield
