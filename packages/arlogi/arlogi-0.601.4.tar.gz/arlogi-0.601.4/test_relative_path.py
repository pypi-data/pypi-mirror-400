#!/usr/bin/env python
"""Simple test to verify relative path functionality."""

from arlogi import setup_logging, get_logger

# Setup logging to show paths
setup_logging(
    level="INFO",
    show_time=False,
    show_level=True,
    show_path=True
)

# Get a logger
logger = get_logger("test")

# Log some messages
logger.info("This message should show with relative path")
logger.error("Error message with relative path")

# Test from a nested function
def nested_function():
    logger.info("Message from nested function")

nested_function()