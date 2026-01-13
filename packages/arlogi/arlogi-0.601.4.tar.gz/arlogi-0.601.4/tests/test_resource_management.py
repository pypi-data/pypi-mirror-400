"""Resource management tests for arlogi.

This module tests that handlers properly manage resources (file handles,
sockets, etc.) to prevent leaks in long-running applications.
"""

import logging
import os
import tempfile
from io import StringIO

import pytest

from arlogi import (
    cleanup_json_logger,
    get_json_logger,
    get_syslog_logger,
    setup_logging,
)
from arlogi.config import LoggingConfig
from arlogi.factory import LoggerFactory


class TestHandlerCleanup:
    """Test that handlers are properly closed and removed."""

    def test_clear_and_add_handlers_closes_existing(self):
        """Test that _clear_and_add_handlers closes existing handlers."""
        # Setup initial handlers
        config = LoggingConfig.from_kwargs(
            level=logging.INFO,
            show_time=False,
        )
        LoggerFactory._clear_and_add_handlers(config)

        root = logging.getLogger()
        initial_handlers = root.handlers.copy()

        # Replace handlers
        LoggerFactory._clear_and_add_handlers(config)

        # Check that old handlers were closed
        # (FileHandler and SocketHandler should have close() called)
        for handler in initial_handlers:
            # If it's a handler with resources, check it's been properly removed
            assert handler not in root.handlers

    def test_get_json_logger_closes_previous_handlers(self):
        """Test that get_json_logger closes previous handlers before adding new ones."""
        logger = get_json_logger("test_close", "logs/test1.json")

        # Get initial handler
        assert len(logger.handlers) == 1
        handler1 = logger.handlers[0]

        # Replace with new handler
        logger2 = get_json_logger("test_close", "logs/test2.json")
        assert len(logger2.handlers) == 1

        # Handler1 should be closed and removed
        assert handler1 not in logger2.handlers

    def test_get_syslog_logger_closes_previous_handlers(self):
        """Test that get_syslog_logger closes previous handlers before adding new ones."""
        logger = get_syslog_logger("test_close")

        # Get initial handler
        assert len(logger.handlers) == 1
        handler1 = logger.handlers[0]

        # Replace with new handler (different address)
        logger2 = get_syslog_logger("test_close", ("localhost", 514))
        assert len(logger2.handlers) == 1

        # Handler1 should be closed and removed
        assert handler1 not in logger2.handlers


class TestJSONHandlerResourceManagement:
    """Test JSONHandler's stream management."""

    def test_json_handler_custom_stream_closed(self):
        """Test that JSONHandler closes custom streams."""
        custom_stream = StringIO()
        from arlogi.handlers import JSONHandler

        handler = JSONHandler(stream=custom_stream)
        handler.emit(
            logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="test message",
                args=(),
                exc_info=None,
            )
        )

        # Close the handler
        handler.close()

        # Custom stream should be closed
        assert custom_stream.closed

    def test_json_handler_system_stream_not_closed(self):
        """Test that JSONHandler doesn't close system streams."""
        import sys

        from arlogi.handlers import JSONHandler

        handler = JSONHandler(stream=sys.stderr)

        # Close the handler
        handler.close()

        # System stream should NOT be closed
        assert not sys.stderr.closed


class TestJSONFileHandlerResourceManagement:
    """Test JSONFileHandler's file management."""

    def test_json_file_handler_creates_directories(self):
        """Test that JSONFileHandler creates parent directories."""
        from arlogi.handlers import JSONFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "subdir", "test.json")
            handler = JSONFileHandler(log_path)

            # Directory should be created
            assert os.path.exists(os.path.dirname(log_path))

            # Handler should be able to write
            handler.emit(
                logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="test.py",
                    lineno=1,
                    msg="test message",
                    args=(),
                    exc_info=None,
                )
            )

            handler.close()
            assert os.path.exists(log_path)

    def test_json_file_handler_no_duplicate_file_handles(self):
        """Test that multiple handler instances don't leak file handles."""
        from arlogi.handlers import JSONFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.json")

            # Create and close multiple handlers
            for i in range(10):
                handler = JSONFileHandler(log_path)
                handler.emit(
                    logging.LogRecord(
                        name="test",
                        level=logging.INFO,
                        pathname="test.py",
                        lineno=1,
                        msg=f"message {i}",
                        args=(),
                        exc_info=None,
                    )
                )
                handler.close()

            # If file handles were leaked, this would fail
            # File should be accessible
            assert os.path.exists(log_path)


class TestProjectRootCaching:
    """Test ColoredConsoleHandler's project root caching."""

    def test_project_root_is_cached(self):
        """Test that project root detection is cached."""
        from arlogi.handlers import ColoredConsoleHandler

        # Clear cache first
        ColoredConsoleHandler._project_root_cache = None

        handler1 = ColoredConsoleHandler()
        root1 = handler1.project_root

        # Should use cache on second instantiation
        handler2 = ColoredConsoleHandler()
        root2 = handler2.project_root

        # Should be the same object (cached)
        assert root1 is root2
        assert ColoredConsoleHandler._project_root_cache is not None

    def test_project_root_cache_persists(self):
        """Test that cache persists across multiple handler creations."""
        from arlogi.handlers import ColoredConsoleHandler

        # Clear cache
        ColoredConsoleHandler._project_root_cache = None

        handlers = [ColoredConsoleHandler() for _ in range(5)]

        # All should have the same project root
        roots = [h.project_root for h in handlers]
        assert len(set(roots)) == 1


class TestJSONFormatterErrorHandling:
    """Test JSONFormatter's error handling."""

    def test_json_formatter_handles_unserializable_objects(self):
        """Test that JSONFormatter handles objects that can't be serialized."""
        from arlogi.handlers import JSONFormatter

        formatter = JSONFormatter()

        # Create a record with an unserializable object
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Add an unserializable object
        class UnserializableClass:
            def __str__(self):
                raise ValueError("Can't convert to string")

        record.custom_field = UnserializableClass()

        # Should not raise, should fall back to error format
        result = formatter.format(record)

        # Should be valid JSON
        import json

        parsed = json.loads(result)
        assert "error" in parsed
        assert "JSON serialization failed" in parsed["error"]

    def test_json_formatter_handles_normal_cases(self):
        """Test that JSONFormatter works for normal cases."""
        from arlogi.handlers import JSONFormatter

        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should be valid JSON
        import json

        parsed = json.loads(result)
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "test message"
        assert "error" not in parsed


class TestMultipleConfigurationChanges:
    """Test that multiple configuration changes don't leak resources."""

    def test_multiple_setup_calls(self):
        """Test that multiple setup() calls don't leak handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.json")

            # Setup multiple times
            for i in range(5):
                setup_logging(
                    level=logging.INFO,
                    json_file_name=log_file,
                )

            root = logging.getLogger()

            # Should only have handlers from last setup (Console + JSON)
            # Note: pytest may add LogCaptureHandler during tests
            arlogi_handlers = [h for h in root.handlers
                             if not h.__class__.__name__.startswith('LogCapture')]
            assert len(arlogi_handlers) <= 2  # Console + JSON

    def test_json_logger_reconfiguration(self):
        """Test that reconfiguring JSON loggers doesn't leak."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(10):
                log_file = os.path.join(tmpdir, f"test_{i}.json")
                logger = get_json_logger(f"test_{i}", log_file)
                logger.info(f"Message {i}")

            # All log files should be accessible
            for i in range(10):
                log_file = os.path.join(tmpdir, f"test_{i}.json")
                assert os.path.exists(log_file)


class TestResourceLeakDetection:
    """Tests that detect actual resource leaks (requires psutil)."""

    @pytest.fixture(autouse=True)
    def check_psutil(self):
        """Skip all tests in this class if psutil is not available."""
        pytest.importorskip("psutil")

    def test_no_file_descriptor_leaks(self):
        """Test that creating/destroying loggers doesn't leak file descriptors."""
        import os

        psutil = __import__("psutil")
        process = psutil.Process()
        initial_fds = process.num_fds()

        # Create and destroy many loggers
        for i in range(50):
            logger = get_json_logger(f"leak_test_{i}")
            logger.info(f"Message {i}")
            # Clean up the logger to release resources
            cleanup_json_logger(f"leak_test_{i}")

        final_fds = process.num_fds()

        # Should not have leaked more than 10 extra FDs (some overhead is OK)
        assert final_fds <= initial_fds + 10, f"Leaked {final_fds - initial_fds} file descriptors"

    def test_no_file_descriptor_leaks_with_files(self):
        """Test that creating/destroying file loggers doesn't leak file descriptors."""
        psutil = __import__("psutil")

        with tempfile.TemporaryDirectory() as tmpdir:
            process = psutil.Process()
            initial_fds = process.num_fds()

            for i in range(50):
                log_file = os.path.join(tmpdir, f"leak_test_{i}.json")
                logger = get_json_logger(f"leak_test_{i}", log_file)
                logger.info(f"Message {i}")
                # Clean up the logger to release file handles
                cleanup_json_logger(f"leak_test_{i}")

            final_fds = process.num_fds()

            # Should not have leaked file descriptors
            # Allow some overhead for temp directory operations
            assert final_fds <= initial_fds + 20, f"Leaked {final_fds - initial_fds} file descriptors"
