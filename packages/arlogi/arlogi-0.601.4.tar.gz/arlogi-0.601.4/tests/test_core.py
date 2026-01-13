import logging

from arlogi import TRACE, LoggerProtocol, get_logger


def test_trace_level_registered():
    logger = get_logger("test_trace")
    assert hasattr(logger, "trace")
    assert logging.getLevelName(TRACE) == "TRACE"

def test_protocol_compliance():
    logger = get_logger("test_protocol")
    assert isinstance(logger, LoggerProtocol)

def test_test_mode_detection():
    from arlogi.factory import LoggerFactory
    assert LoggerFactory.is_test_mode() is True

def test_logging_calls(caplog):
    caplog.set_level(TRACE)
    logger = get_logger("test_calls")
    logger.trace("trace message")
    logger.debug("debug message")
    logger.info("info message")

    messages = [record.message for record in caplog.records]
    assert "trace message" in messages
    assert "debug message" in messages
    assert "info message" in messages
