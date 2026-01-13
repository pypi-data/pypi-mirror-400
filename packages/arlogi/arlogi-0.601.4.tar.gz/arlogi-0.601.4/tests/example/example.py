import os

import worker

from arlogi import LoggingConfig, LoggerFactory, get_json_logger, get_logger, get_syslog_logger


def main():
    # 1. Get log level from environment variable, default to INFO
    env_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Create LoggingConfig
    config = LoggingConfig(
        level=env_level,
        module_levels={
            "app.network": "TRACE",
            "app.database": "DEBUG",
        },
        show_time=False,    # Default is False for clean "start of line" look
        show_path=True,     # Show where the log came from
        json_file_name="logs/root_test.jsonl",
        json_file_only=False, # Default: keep console output too
    )

    # Apply configuration via factory
    LoggerFactory._apply_configuration(config)

    # 2. Get loggers
    logger = get_logger("app.main")
    net_logger = get_logger("app.network")
    db_logger = get_logger("app.database")

    print(f"--- Arlogi Example (LOG_LEVEL={env_level}) ---")

    # 3. Demonstrate standard and custom levels
    logger.critical(f"CRITICAL: Main application started with log level {env_level}")
    logger.trace("Main app TRACE example")
    logger.debug("Main app DEBUG example")
    logger.info("Main app INFO example")
    logger.info("Main app INFO example\nmultiline.", caller_depth=0)
    logger.warning("Main app WARNING example", caller_depth=0)
    logger.error("Main app ERROR example\n\n")

    # 4. Demonstrate module-specific levels
    # This will show if LOG_LEVEL=INFO because app.network is pinned to TRACE
    net_logger.critical("CRITICAL: Network application started with TRACE log level")
    net_logger.trace("Network application TRACE example")
    net_logger.debug("Network application DEBUG example")
    net_logger.info("Network application INFO example")
    net_logger.warning("Network application WARNING example")
    net_logger.error("Network application ERROR example\n\n")

    # This will show if LOG_LEVEL=INFO because app.database is pinned to DEBUG
    db_logger.critical("CRITICAL: Database application started with DEBUG log level")
    db_logger.trace("Database application TRACE example")
    db_logger.debug("Database application DEBUG example")
    db_logger.info("Database application INFO example")
    db_logger.warning("Database application WARNING example")
    db_logger.error("Database application ERROR example\n\n")

    # 5. Demonstrate dedicated loggers (bypass root handlers)
    print("\n--- Dedicated Loggers ---")

    # Logs only to JSON output (visible if running in a terminal or redirected)
    # Note: In a real app, you might redirect this to a file
    audit_logger = get_json_logger("audit", json_file_name="logs/dedicated_test.jsonl")
    audit_logger.info("User 'admin' logged in", extra={"ip": "192.168.1.1"})

    # Logs to syslog (might fail if no syslog server/socket is available, but has fallback)
    syslog_logger = get_syslog_logger("security")
    syslog_logger.warning("Unauthorized access attempt detected")

    # 6. Demonstrate Caller Attribution using caller_depth
    print("\n--- Caller Attribution ---")

    def worker_function():
        # caller_depth=0 shows this function name [worker_function]
        logger.info("Worker processing started", caller_depth=0)
        # caller_depth=1 shows where this was called from [main]
        logger.debug("Processing details", **{"caller_depth": 1})
        # caller_depth=1 shows caller of main [unknown or module level]
        logger.trace("Deep trace", caller_depth=1)

        # depth 1 in worker: [from __main__.main()]
        worker.do_work(depth=1)
        # depth 2 in worker: [from __main__.main()]
        worker.do_work(depth=2)

    worker_function()

    # 7. Demonstrate Cross-Module Caller Attribution
    print("\n--- Cross-Module Attribution ---")
    # worker.py uses a logger named "app.worker"
    # depth 0 in worker: [do_work()]
    worker.do_work(depth=0)
    # depth 1 in worker: [from __main__.main()]
    worker.do_work(depth=1)

    print("\n--- Done ---\n")

if __name__ == "__main__":
    main()
