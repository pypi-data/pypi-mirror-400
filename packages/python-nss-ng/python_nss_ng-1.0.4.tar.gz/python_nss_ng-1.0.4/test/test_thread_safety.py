# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

"""
Thread safety and concurrency tests.

This module tests concurrent operations to ensure thread safety
in multi-threaded environments.
"""

import sys
import os
import pytest
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


class TestBasicThreadSafety:
    """Basic thread safety tests."""

    def test_concurrent_imports(self):
        """Test that concurrent imports are safe."""
        sys.path.insert(0, 'src')

        errors = []

        def import_module():
            try:
                import deprecations
                import secure_logging
                import nss_context
            except Exception as e:
                errors.append(e)

        # Run multiple imports concurrently
        threads = []
        for _ in range(10):
            t = threading.Thread(target=import_module)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Import errors: {errors}"

    def test_thread_local_storage(self):
        """Test thread-local storage isolation."""
        thread_local = threading.local()
        results = {}

        def set_thread_value(thread_id):
            thread_local.value = thread_id
            time.sleep(0.01)  # Allow context switches
            results[thread_id] = thread_local.value

        threads = []
        for i in range(10):
            t = threading.Thread(target=set_thread_value, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Each thread should see its own value
        for thread_id, value in results.items():
            assert thread_id == value, "Thread-local storage leaked between threads"

    def test_concurrent_list_operations(self):
        """Test that concurrent list operations are handled."""
        shared_list = []
        lock = threading.Lock()

        def append_items(start, count):
            for i in range(start, start + count):
                with lock:
                    shared_list.append(i)

        threads = []
        for i in range(5):
            t = threading.Thread(target=append_items, args=(i * 100, 100))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have all items
        assert len(shared_list) == 500


class TestDeprecationThreadSafety:
    """Thread safety tests for deprecation handling."""

    def test_concurrent_deprecation_warnings(self):
        """Test concurrent deprecation warnings are safe."""
        sys.path.insert(0, 'src')

        try:
            from deprecations import warn_deprecated
        except ImportError:
            pytest.skip("deprecations module not available")

        errors = []

        def warn_in_thread():
            try:
                import warnings
                with warnings.catch_warnings(record=True):
                    warn_deprecated('test_symbol', 'Use new_symbol instead')
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(20):
            t = threading.Thread(target=warn_in_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors in concurrent warnings: {errors}"

    def test_concurrent_deprecation_checks(self):
        """Test concurrent deprecation status checks."""
        sys.path.insert(0, 'src')

        try:
            from deprecations import is_deprecated
        except ImportError:
            pytest.skip("deprecations module not available")

        results = []

        def check_deprecated():
            result = is_deprecated('PRNetAddr')
            results.append(result)

        threads = []
        for _ in range(50):
            t = threading.Thread(target=check_deprecated)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All threads should get the same answer
        assert all(r == results[0] for r in results), "Inconsistent deprecation status"


class TestSecureLoggingThreadSafety:
    """Thread safety tests for secure logging."""

    def test_concurrent_secure_logging(self):
        """Test concurrent secure logging operations."""
        sys.path.insert(0, 'src')

        try:
            from secure_logging import secure_log
            import logging
        except ImportError:
            pytest.skip("secure_logging module not available")

        errors = []
        logger = logging.getLogger('test')

        def log_message(message):
            try:
                secure_log(logger.info, message)
            except Exception as e:
                errors.append(e)

        threads = []
        messages = [f"Message {i}" for i in range(100)]

        for msg in messages:
            t = threading.Thread(target=log_message, args=(msg,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors in concurrent logging: {errors}"

    def test_concurrent_redaction(self):
        """Test concurrent message redaction."""
        sys.path.insert(0, 'src')

        try:
            from secure_logging import redact_message
        except ImportError:
            pytest.skip("secure_logging module not available")

        results = []

        def redact_in_thread(message):
            redacted = redact_message(message)
            results.append((message, redacted))

        test_messages = [
            "password=secret123",
            "key: abc123xyz",
            "Safe message",
            "token=Bearer xyz"
        ]

        threads = []
        for _ in range(10):
            for msg in test_messages:
                t = threading.Thread(target=redact_in_thread, args=(msg,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        # Check results are consistent for same input
        message_results = {}
        for original, redacted in results:
            if original not in message_results:
                message_results[original] = redacted
            else:
                assert message_results[original] == redacted, \
                    "Inconsistent redaction results for same message"


class TestNSSContextThreadSafety:
    """Thread safety tests for NSS context."""

    def test_concurrent_context_checks(self):
        """Test concurrent NSS context state checks."""
        sys.path.insert(0, 'src')

        try:
            from nss_context import NSSContext
        except ImportError:
            pytest.skip("nss_context module not available")

        errors = []

        def check_context():
            try:
                # Just checking that concurrent access to class doesn't crash
                assert NSSContext is not None
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(50):
            t = threading.Thread(target=check_context)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0


class TestConcurrentDataStructures:
    """Test concurrent access to shared data structures."""

    def test_concurrent_queue_operations(self):
        """Test thread-safe queue operations."""
        test_queue: queue.Queue[int] = queue.Queue()

        def producer(items):
            for item in items:
                test_queue.put(item)
                time.sleep(0.001)

        def consumer(results):
            while True:
                try:
                    item = test_queue.get(timeout=1)
                    results.append(item)
                    test_queue.task_done()
                except queue.Empty:
                    break

        results: list[int] = []

        # Start producers
        producer_threads = []
        for i in range(5):
            items = list(range(i * 20, (i + 1) * 20))
            t = threading.Thread(target=producer, args=(items,))
            producer_threads.append(t)
            t.start()

        # Start consumers
        consumer_threads = []
        for _ in range(3):
            t = threading.Thread(target=consumer, args=(results,))
            consumer_threads.append(t)
            t.start()

        # Wait for producers
        for t in producer_threads:
            t.join()

        # Wait for queue to empty
        test_queue.join()

        # Wait for consumers
        for t in consumer_threads:
            t.join()

        # Should have all items
        assert len(results) == 100
        assert sorted(results) == list(range(100))

    def test_concurrent_dict_operations(self):
        """Test concurrent dictionary operations with lock."""
        shared_dict = {}
        lock = threading.Lock()

        def update_dict(key, value):
            with lock:
                shared_dict[key] = value

        threads = []
        for i in range(100):
            t = threading.Thread(target=update_dict, args=(i, i * 2))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have all keys
        assert len(shared_dict) == 100
        for k, v in shared_dict.items():
            assert v == k * 2


class TestRaceConditions:
    """Tests for potential race conditions."""

    def test_check_then_act_race(self):
        """Test check-then-act pattern with proper locking."""
        counter = 0
        lock = threading.Lock()

        def increment_safely():
            nonlocal counter
            with lock:
                # Check-then-act is safe with lock
                if counter < 1000:
                    counter += 1

        threads = []
        for _ in range(10):
            for _ in range(100):
                t = threading.Thread(target=increment_safely)
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        # Should not exceed limit due to race
        assert counter <= 1000

    def test_double_checked_locking(self):
        """Test double-checked locking pattern."""
        instance = None
        lock = threading.Lock()
        create_count = 0

        def get_instance():
            nonlocal instance, create_count

            if instance is None:  # First check (no lock)
                with lock:
                    if instance is None:  # Second check (with lock)
                        instance = {"created": True}
                        create_count += 1

            return instance

        threads = []
        for _ in range(100):
            t = threading.Thread(target=get_instance)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should only create instance once
        assert create_count == 1
        assert instance is not None


class TestDeadlockPrevention:
    """Tests for deadlock scenarios."""

    def test_no_deadlock_with_ordered_locks(self):
        """Test that ordered lock acquisition prevents deadlocks."""
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        results = []

        def acquire_in_order():
            # Always acquire locks in same order
            with lock1:
                time.sleep(0.01)
                with lock2:
                    results.append(threading.current_thread().name)

        threads = []
        for i in range(10):
            t = threading.Thread(target=acquire_in_order, name=f"Thread-{i}")
            threads.append(t)
            t.start()

        # Should complete without deadlock
        for t in threads:
            t.join(timeout=5.0)
            assert not t.is_alive(), "Possible deadlock detected"

        assert len(results) == 10


class TestThreadPoolOperations:
    """Tests using thread pools."""

    def test_thread_pool_executor(self):
        """Test operations using ThreadPoolExecutor."""
        def process_item(item):
            time.sleep(0.01)
            return item * 2

        items = list(range(50))

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_item, item) for item in items]
            results = [future.result() for future in as_completed(futures)]

        # Should have all results
        assert len(results) == 50
        assert sorted(results) == [i * 2 for i in items]

    def test_thread_pool_exception_handling(self):
        """Test exception handling in thread pool."""
        def task_that_fails(should_fail):
            if should_fail:
                raise ValueError("Task failed")
            return "success"

        tasks = [True, False, True, False, False]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(task_that_fails, t) for t in tasks]

            results = []
            errors = []

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except ValueError as e:
                    errors.append(e)

        # Should have both successes and failures
        assert len(results) == 3
        assert len(errors) == 2


class TestAtomicOperations:
    """Tests for atomic operations."""

    def test_queue_is_atomic(self):
        """Test that queue operations are atomic."""
        test_queue: queue.Queue[int] = queue.Queue()

        def producer():
            for i in range(100):
                test_queue.put(i)

        def consumer():
            items = []
            for _ in range(100):
                try:
                    item = test_queue.get(timeout=2)
                    items.append(item)
                except queue.Empty:
                    break
            return items

        p_thread = threading.Thread(target=producer)
        c_thread = threading.Thread(target=consumer)

        p_thread.start()
        c_thread.start()

        p_thread.join()
        c_thread.join()

        # Queue should be empty
        assert test_queue.empty()


class TestMemoryVisibility:
    """Tests for memory visibility between threads."""

    def test_flag_visibility_with_lock(self):
        """Test that flag changes are visible across threads with locks."""
        flag = False
        lock = threading.Lock()
        results = []

        def setter():
            nonlocal flag
            time.sleep(0.1)
            with lock:
                flag = True

        def getter():
            for _ in range(100):
                with lock:
                    if flag:
                        results.append(True)
                        return
                time.sleep(0.01)
            results.append(False)

        t1 = threading.Thread(target=setter)
        t2 = threading.Thread(target=getter)

        t2.start()
        t1.start()

        t1.join()
        t2.join()

        # Getter should eventually see the flag
        assert True in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
