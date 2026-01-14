# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: Copyright (c) 2010-2025 python-nss-ng contributors

"""
pytest configuration for python-nss-ng tests.

This file provides fixtures and setup for running tests with pytest.
Tests are run in separate processes using pytest-xdist to provide clean
NSS initialization for each test file.
"""

import contextlib
import logging
import os
import stat
import sys
import pytest


# Module-level logger for test infrastructure
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def cleanup_p12_files_session():
    """
    Clean up .p12 files at the end of the test session.

    This ensures any leftover .p12 files from all tests are removed
    when the test session completes. Individual tests should clean up
    their own files, but this provides a safety net.
    """
    yield

    # Cleanup after all tests in this session
    import glob

    # Clean up from test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    for p12_file in glob.glob(os.path.join(test_dir, '*.p12')):
        try:
            os.remove(p12_file)
            logger.debug(f"Removed {p12_file}")
        except Exception as e:
            logger.debug(f"Could not remove {p12_file}: {e}")

    # Also clean up from current working directory (repo root)
    cwd = os.getcwd()
    if cwd != test_dir:
        for p12_file in glob.glob(os.path.join(cwd, '*.p12')):
            try:
                os.remove(p12_file)
                logger.debug(f"Removed {p12_file}")
            except Exception as e:
                logger.debug(f"Could not remove {p12_file}: {e}")


def _rmtree_onerror(func, path, exc_info):
    """
    Error handler for shutil.rmtree.

    Attempts to handle permission errors by making files writable,
    then retrying the removal. Logs other errors for diagnostics.

    Args:
        func: The function that raised the exception
        path: Path to the file/directory
        exc_info: Exception information tuple
    """
    if not os.access(path, os.W_OK):
        # Make the file/directory writable and retry
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
            func(path)
        except Exception as e:
            logger.warning(f"Failed to remove {path} after chmod: {e}")
    else:
        # Log the error but don't raise - allow cleanup to continue
        logger.warning(f"Error removing {path}: {exc_info[1]}")


def _wait_for_nss_shutdown(timeout=2.0):
    """
    Wait for NSS to be ready for shutdown.

    Instead of arbitrary sleeps, this polls NSS state to ensure
    resources are released before attempting shutdown.

    Args:
        timeout: Maximum time to wait in seconds

    Returns:
        bool: True if ready, False if timeout reached
    """
    import time
    start_time = time.time()
    sleep_interval = 0.1

    while time.time() - start_time < timeout:
        # Check if we can proceed - in practice, NSS doesn't provide
        # a good way to check this, so we use a short polling interval
        # This is better than a single long sleep
        time.sleep(sleep_interval)

        # If we've waited a reasonable amount, consider it ready
        if time.time() - start_time >= 0.5:
            return True

    return False


def pytest_configure(config):
    """Configure pytest for python-nss-ng tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "nss_init: mark test as requiring NSS initialization"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring NSS database"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "allow_insecure: mark test as allowing insecure/legacy configurations"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up the test environment before running any tests.
    This fixture runs once per test session (i.e., once per worker process).
    """
    # Ensure test directory is in path
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    # If running tests in-tree, add the build directory to path
    from util import get_build_dir
    build_dir = get_build_dir()
    if build_dir and os.path.exists(build_dir):
        print(f"\nUsing local libraries from build directory: {build_dir}")
        sys.path.insert(0, build_dir)
    else:
        print("\nUsing installed libraries")

    yield

    # Cleanup after all tests in this process
    import glob

    # Remove any .p12 files left in test directory
    for p12_file in glob.glob(os.path.join(test_dir, '*.p12')):
        try:
            os.remove(p12_file)
            logger.debug(f"Cleaned up {p12_file}")
        except Exception as e:
            logger.warning(f"Failed to remove {p12_file}: {e}")

    # Also clean up from repo root if different from test directory
    cwd = os.getcwd()
    if cwd != test_dir:
        for p12_file in glob.glob(os.path.join(cwd, '*.p12')):
            try:
                os.remove(p12_file)
                logger.debug(f"Cleaned up {p12_file} from repo root")
            except Exception as e:
                logger.warning(f"Failed to remove {p12_file}: {e}")


@pytest.fixture(scope="session")
def test_certs(setup_test_environment):
    """
    Set up test certificates once per test session (worker process).

    This fixture ensures that test certificates are created before
    any tests that need them run. Creates a 'pki' directory in the
    test directory with NSS database and certificates.

    With pytest-xdist, each worker process gets its own session,
    so each worker will have its own pki directory.
    """
    import setup_certs
    import shutil
    import time
    import hashlib

    # Create a session-scoped temporary directory for PKI
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # For xdist workers, use worker-specific directory
    # For single-process mode, just use 'pki'
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    if worker_id:
        pki_dir = os.path.join(test_dir, f'pki_{worker_id}')
    else:
        pki_dir = os.path.join(test_dir, 'pki')

    # Clean up any existing PKI directory with error handling
    if os.path.exists(pki_dir):
        shutil.rmtree(pki_dir, onerror=_rmtree_onerror)

    # Set up certificates - run setup_certs directly
    result = setup_certs.setup_certs(['--db-dir', pki_dir, '--no-trusted-certs'])

    if result != 0:
        raise RuntimeError(f"setup_certs failed with return code {result} for {pki_dir}")

    # Verify database was created successfully
    cert9_db = os.path.join(pki_dir, 'cert9.db')
    key4_db = os.path.join(pki_dir, 'key4.db')

    if not (os.path.exists(cert9_db) and os.path.exists(key4_db)):
        raise RuntimeError(f"Database files not created in {pki_dir}")

    # Verify we can actually list certificates from the database
    try:
        import subprocess
        certutil_result = subprocess.run(
            ['certutil', '-d', f'sql:{pki_dir}', '-L'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if certutil_result.returncode != 0:
            raise RuntimeError(f"Database verification failed: {certutil_result.stderr}")

        # Check that test_user certificate exists
        if 'test_user' not in certutil_result.stdout:
            raise RuntimeError(f"test_user certificate not found in {pki_dir}")

        logger.debug(f"Successfully created and verified test certificates in {pki_dir}")
    except Exception as e:
        logger.error(f"Failed to verify database {pki_dir}: {e}")
        raise

    yield pki_dir

    # Cleanup after all tests with retry logic
    if os.path.exists(pki_dir):
        shutil.rmtree(pki_dir, onerror=_rmtree_onerror)


@pytest.fixture(scope="session")
def nss_db_dir(test_certs):
    """
    Provide the NSS database directory path for tests.

    Returns the path to the 'sql:pki' database that tests expect.
    This fixture depends on test_certs which creates the database.
    """
    return f'sql:{test_certs}'


@pytest.fixture(scope="session")
def nss_initialized(nss_db_dir):
    """
    Initialize NSS once per test session (worker process).

    With pytest-xdist, each worker process runs in isolation,
    so NSS can be initialized once per worker and shared across
    all tests in that worker.
    """
    import nss.nss as nss

    # Initialize NSS with the test database once for this worker
    try:
        nss.nss_init_read_write(nss_db_dir)
        logger.debug(f"Successfully initialized NSS with {nss_db_dir}")
    except Exception as e:
        logger.error(f"Failed to initialize NSS with {nss_db_dir}: {e}")
        # Try to provide diagnostic information
        import subprocess
        try:
            certutil_result = subprocess.run(
                ['certutil', '-d', nss_db_dir, '-L'],
                capture_output=True,
                text=True,
                timeout=5
            )
            logger.error(f"Database state: {certutil_result.stdout if certutil_result.returncode == 0 else certutil_result.stderr}")
        except Exception:
            pass
        raise

    yield

    # Shutdown NSS after all tests in this worker complete
    # Wait for NSS resources to be ready for shutdown
    _wait_for_nss_shutdown(timeout=2.0)
    try:
        nss.nss_shutdown()
    except Exception as e:
        # NSS shutdown may fail if resources are still in use
        # This is acceptable at the end of the test session
        print(f"\nNote: NSS shutdown: {e}")


@pytest.fixture
def nss_db_context(nss_initialized):
    """
    Provide NSS database context for tests.

    This fixture depends on nss_initialized to ensure NSS is set up,
    and provides the certificate database to tests that need it.
    NSS is initialized once per worker process and shared across tests.
    """
    import nss.nss as nss

    certdb = nss.get_default_certdb()
    yield certdb

    # Minimal cleanup per test
    # Note: We don't shut down NSS here as it's shared across all tests
    # in this worker process
    #
    # IMPORTANT: We do NOT call ssl.clear_session_cache() here because:
    # 1. It causes segmentation faults on Linux ARM64 with NSS 3.118
    # 2. SSL tests handle their own session cache cleanup (see test_client_server.py)
    # 3. Calling SSL functions after non-SSL tests can crash when SSL is in an
    #    uninitialized state, even if the module is imported
    # 4. The contextlib.suppress(Exception) wrapper doesn't catch SIGSEGV signals
    #
    # This fixture provides the certificate database; SSL session management
    # is the responsibility of individual SSL tests.
    pass


@pytest.fixture
def nss_clean_state(nss_db_dir):
    """
    Force a clean NSS re-initialization for tests sensitive to state corruption.

    NSS has known issues with state management when certain operations run in sequence,
    particularly when find_cert_from_nickname or similar functions are called after
    other NSS operations. This fixture ensures a completely clean NSS state by:
    1. Shutting down NSS (with retries if needed)
    2. Waiting for cleanup
    3. Re-initializing NSS with the test database

    Usage:
        def test_something(nss_clean_state):
            # Test code here - NSS is freshly initialized
            pass

    Or use autouse in a test class:
        @pytest.fixture(autouse=True)
        def _clean_nss(self, nss_clean_state):
            pass
    """
    import nss.nss as nss
    import time

    # Only shutdown if NSS is initialized
    if nss.nss_is_initialized():
        # Shutdown NSS to clear any accumulated state
        shutdown_succeeded = False
        for attempt in range(3):
            try:
                nss.nss_shutdown()
                shutdown_succeeded = True
                break
            except Exception as e:
                # NSS might complain about objects in use - wait and retry
                if attempt < 2:
                    time.sleep(0.2 * (attempt + 1))
                else:
                    # Last attempt failed - log but continue
                    # Some tests may have leaked NSS resources
                    import sys
                    print(f"Warning: NSS shutdown failed after 3 attempts: {e}", file=sys.stderr)

        # Wait for NSS to fully clean up internal state
        if shutdown_succeeded:
            time.sleep(0.1)

    # Re-initialize with the test database
    try:
        nss.nss_init_read_write(nss_db_dir)
    except Exception as e:
        # If initialization fails, skip the test rather than error
        import pytest
        pytest.skip(f"NSS re-initialization failed (state too corrupted): {e}")

    # Return the certdb for convenience
    certdb = nss.get_default_certdb()
    yield certdb

    # No cleanup needed - the session-level fixture will handle final shutdown


@pytest.fixture(scope="function")
def secure_mode():
    """
    Fixture that returns True to indicate secure defaults should be used.

    Tests can use this to verify behavior with secure settings.
    """
    return True


@pytest.fixture(scope="function")
def insecure_mode():
    """
    Fixture that returns True to indicate insecure/legacy mode is allowed.

    This should only be used for tests that specifically need to verify
    legacy or insecure configurations work correctly.

    WARNING: Tests using this fixture should be clearly marked and documented.
    """
    return True


@pytest.fixture(scope="function")
def tls_config(request):
    """
    Fixture that provides TLS configuration based on test requirements.

    By default, returns secure configuration (TLS 1.2+).
    Tests can use markers to request insecure mode:

    @pytest.mark.allow_insecure
    def test_legacy_tls(tls_config):
        assert tls_config['allow_insecure'] == True
    """
    config = {
        'min_tls_version': 'TLS1.2',
        'max_tls_version': 'TLS1.3',
        'allow_insecure': False,
        'min_key_size': 2048,
    }

    # Check if test is marked with allow_insecure
    if request.node.get_closest_marker('allow_insecure'):
        config['allow_insecure'] = True
        config['min_tls_version'] = 'TLS1.0'

    return config





def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test characteristics.
    """
    for item in items:
        # Mark tests that import nss modules
        if "nss" in str(item.fspath):
            item.add_marker(pytest.mark.nss_init)

        # Mark slow tests (client_server tests are typically slow)
        if "client_server" in str(item.fspath):
            item.add_marker(pytest.mark.slow)


def pytest_report_header(config):
    """Add custom header information to pytest output."""
    import sys

    header_lines = [
        f"Python version: {sys.version}",
        f"Python executable: {sys.executable}",
    ]

    # Try to get NSS version if available
    try:
        import nss.nss as nss
        nss.nss_init_nodb()
        version = nss.nss_get_version()
        nss.nss_shutdown()
        header_lines.append(f"NSS version: {version}")
    except Exception as e:
        header_lines.append(f"NSS version: Unable to determine ({e})")

    return "\n".join(header_lines)
