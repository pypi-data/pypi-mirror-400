# Create a thread pool executor for application
import logging
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger("appLogger")

executor = ThreadPoolExecutor(max_workers=50)
log.info(f"Thread pool executor created with max workers: {50}")


def get_executor():
    return executor
