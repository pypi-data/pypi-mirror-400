import json
import logging

from arlogi import TRACE, get_json_logger, get_logger, setup_logging


def test_module_specific_levels():
    # Setup specific levels for submodules
    setup_logging(
        level=logging.INFO,
        module_levels={
            "app.db": logging.DEBUG,
            "app.net": TRACE
        }
    )

    db_logger = get_logger("app.db")
    net_logger = get_logger("app.net")
    root_logger = get_logger("app.other")

    # Directly verify levels
    assert db_logger.isEnabledFor(logging.DEBUG) is True
    assert net_logger.isEnabledFor(TRACE) is True
    assert root_logger.isEnabledFor(logging.DEBUG) is False
    assert root_logger.isEnabledFor(logging.INFO) is True

def test_json_logger(capsys):
    # Dedicated JSON logger should output to its own handler
    json_logger = get_json_logger("test_json")
    json_logger.info("json message", extra={"key": "value"})

    captured = capsys.readouterr()
    # Since get_json_logger creates a logger with JSONHandler directed to stdout by default (in our implementation it's a StreamHandler)
    # let's verify if we can catch the output.
    # Actually JSONHandler uses sys.stderr by default if stream is None, but let's check.
    # Our implementation: class JSONHandler(logging.StreamHandler): def __init__(self, stream: Any = None): super().__init__(stream)
    # StreamHandler defaults to sys.stderr.

    output = captured.err
    assert "json message" in output
    data = json.loads(output)
    assert data["message"] == "json message"
    assert data["level"] == "INFO"
    assert data["key"] == "value"

def test_trace_stacklevel(caplog):
    caplog.set_level(TRACE)
    logger = get_logger("test_stack")
    logger.trace("trace message")

    record = caplog.records[0]
    # Check if funcName is correct (it should be test_trace_stacklevel, not trace)
    assert record.funcName == "test_trace_stacklevel"

def test_caller_attribution(caplog):
    caplog.set_level(logging.DEBUG)
    logger = get_logger("test.attribution")

    def inner_func():
        logger.info("message", caller_depth=0)

    def outer_func():
        inner_func()
        logger.info("outer message", caller_depth=1)

    inner_func()
    assert "message" in caplog.text
    # The [ is escaped for Rich markup as \[
    assert r"\[inner_func()]" in caplog.text

    caplog.clear()
    outer_func()
    # From the inner_func call: [inner_func()]
    assert r"\[inner_func()]" in caplog.text
    # From the outer_func call (depth 1): [from .test_caller_attribution()]
    assert r"\[from .test_caller_attribution()]" in caplog.text
