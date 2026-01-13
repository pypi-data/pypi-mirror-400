"""Thread safety tests for arlogi.

This module tests that the library is thread-safe and handles concurrent
access correctly, particularly around initialization and logger creation.
"""

import logging
import os
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from arlogi import (
    get_logger,
    get_json_logger,
    setup_logging,
)
from arlogi.factory import LoggerFactory


class TestConcurrentInitialization:
    """Test concurrent initialization of the logging system."""

    def test_concurrent_setup_does_not_duplicate_handlers(self):
        """Test that concurrent setup() calls don't duplicate handlers."""
        errors = []
        handler_counts = []

        def setup_thread(i):
            try:
                setup_logging(level=logging.INFO)
                root = logging.getLogger()
                handler_counts.append(len(root.handlers))
                time.sleep(0.001)  # Simulate work
            except Exception as e:
                errors.append((i, e))

        threads = []
        for i in range(50):
            t = threading.Thread(target=setup_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should not have any errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Should have reasonable number of handlers, not N*50
        root = logging.getLogger()
        # Filter out pytest handlers
        arlogi_handlers = [h for h in root.handlers
                          if not h.__class__.__name__.startswith('LogCapture')]
        assert len(arlogi_handlers) <= 2, f"Too many handlers: {len(arlogi_handlers)}"

    def test_concurrent_get_logger_initializes_once(self):
        """Test that concurrent get_logger() calls initialize successfully."""
        def get_logger_thread(i):
            logger = get_logger(f"test_{i}")
            logger.info(f"Message {i}")
            return logger

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(get_logger_thread, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()

        # Should have initialized
        assert LoggerFactory._initialized, "LoggerFactory should be initialized"

    def test_concurrent_get_global_logger(self):
        """Test that concurrent get_global_logger() calls are thread-safe."""
        loggers = []

        def get_global_thread(i):
            logger = LoggerFactory.get_global_logger()
            loggers.append(logger)
            logger.info(f"Message {i}")
            time.sleep(0.001)

        threads = []
        for i in range(50):
            t = threading.Thread(target=get_global_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All loggers should be the same instance
        assert all(logger is loggers[0] for logger in loggers), \
            "Not all loggers are the same instance"


class TestConcurrentLoggerCreation:
    """Test concurrent logger creation."""

    def test_concurrent_logger_creation_with_names(self):
        """Test creating many loggers concurrently with different names."""
        errors = []

        def create_logger(i):
            try:
                logger = get_logger(f"test_logger_{i}")
                logger.info(f"Message {i}")
                logger.debug(f"Debug message {i}")
                logger.warning(f"Warning {i}")
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(create_logger, i) for i in range(200)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_concurrent_json_logger_creation(self):
        """Test concurrent JSON logger creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            errors = []
            log_files = []

            def create_json_logger(i):
                try:
                    log_file = os.path.join(tmpdir, f"test_{i}.json")
                    logger = get_json_logger(f"json_{i}", log_file)
                    logger.info(f"Message {i}")
                    log_files.append(log_file)
                    time.sleep(0.001)
                except Exception as e:
                    errors.append((i, e))

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(create_json_logger, i) for i in range(50)]
                for future in as_completed(futures):
                    future.result()

            assert len(errors) == 0, f"Errors occurred: {errors}"

            # All log files should exist
            for log_file in log_files:
                assert os.path.exists(log_file), f"Log file not created: {log_file}"

    def test_concurrent_logger_with_levels(self):
        """Test concurrent logger creation with different levels."""
        errors = []
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        def create_logger_with_level(i):
            try:
                level = levels[i % len(levels)]
                logger = get_logger(f"level_test_{i}", level=level)
                logger.log(level, f"Message at level {level}")
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(create_logger_with_level, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestTraceRegistrationThreadSafety:
    """Test thread safety of TRACE level registration."""

    def test_concurrent_trace_registration(self):
        """Test that concurrent TRACE registration is safe."""
        errors = []

        def register_trace(i):
            try:
                from arlogi.levels import register_trace_level
                register_trace_level()
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(register_trace, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"

        # TRACE should be registered
        assert hasattr(logging, 'TRACE'), "TRACE level not registered"

    def test_trace_idempotency(self):
        """Test that multiple TRACE registrations are safe."""
        from arlogi.levels import register_trace_level

        errors = []
        for i in range(100):
            try:
                register_trace_level()
            except Exception as e:
                errors.append((i, e))

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert hasattr(logging, 'TRACE'), "TRACE level not registered"


class TestConcurrentLogging:
    """Test concurrent logging operations."""

    def test_concurrent_logging_to_same_logger(self):
        """Test concurrent logging to the same logger instance."""
        logger = get_logger("concurrent_test")
        message_count = [0]

        def log_messages(i):
            for j in range(10):
                logger.info(f"Message {i}-{j}")
                message_count[0] += 1
                time.sleep(0.0001)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(log_messages, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        # All messages should have been logged
        assert message_count[0] == 200, f"Expected 200 messages, got {message_count[0]}"

    def test_concurrent_logging_with_extra_fields(self):
        """Test concurrent logging with extra fields."""
        logger = get_logger("extra_test")
        errors = []

        def log_with_extra(i):
            try:
                logger.info(f"Message {i}", extra={"counter": i, "worker_id": threading.current_thread().name})
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(log_with_extra, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_concurrent_logging_at_different_levels(self):
        """Test concurrent logging at different levels."""
        logger = get_logger("level_test")
        errors = []

        def log_at_levels(i):
            try:
                logger.trace(f"Trace {i}")
                logger.debug(f"Debug {i}")
                logger.info(f"Info {i}")
                logger.warning(f"Warning {i}")
                logger.error(f"Error {i}")
                logger.critical(f"Critical {i}")
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(log_at_levels, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestConcurrentDirectoryCreation:
    """Test concurrent directory creation in JSON file handlers."""

    def test_concurrent_json_file_handler_same_directory(self):
        """Test concurrent JSON file handlers creating the same directory."""
        from arlogi.handlers import JSONFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            errors = []
            subdir = os.path.join(tmpdir, "nested", "dir")

            def create_handler(i):
                try:
                    log_file = os.path.join(subdir, f"test_{i}.json")
                    handler = JSONFileHandler(log_file)
                    handler.emit(
                        logging.LogRecord(
                            name="test",
                            level=logging.INFO,
                            pathname="test.py",
                            lineno=1,
                            msg=f"Message {i}",
                            args=(),
                            exc_info=None,
                        )
                    )
                    handler.close()
                    time.sleep(0.001)
                except Exception as e:
                    errors.append((i, e))

            # All threads try to create the same directory
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(create_handler, i) for i in range(50)]
                for future in as_completed(futures):
                    future.result()

            assert len(errors) == 0, f"Errors occurred: {errors}"

            # Directory should exist
            assert os.path.exists(subdir), "Directory not created"

            # All log files should exist
            for i in range(50):
                log_file = os.path.join(subdir, f"test_{i}.json")
                assert os.path.exists(log_file), f"Log file not created: {log_file}"


class TestStressTest:
    """Stress tests with high concurrency."""

    def test_high_concurrency_stress(self):
        """Stress test with high concurrency."""
        errors = []

        def stress_test(i):
            try:
                logger = get_logger(f"stress_{i % 50}")  # Reuse logger names
                for j in range(10):
                    logger.info(f"Stress message {i}-{j}")
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(stress_test, i) for i in range(500)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_rapid_initialization_and_logging(self):
        """Test rapid initialization and logging cycles."""
        errors = []

        def init_log_cycle(i):
            try:
                # Create logger, log, and let it go out of scope
                logger = get_logger(f"cycle_{i % 20}")
                logger.info(f"Cycle message {i}")
                time.sleep(0.0001)
            except Exception as e:
                errors.append((i, e))

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(init_log_cycle, i) for i in range(200)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors occurred: {errors}"
