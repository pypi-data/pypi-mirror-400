from arlogi import get_logger

logger = get_logger("app.worker")

def do_work(depth=0):
    logger.info(f"Worker doing work at depth {depth}", caller_depth=depth)
