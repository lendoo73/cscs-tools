import time
from log_config import access_logger, error_logger
from sample.logger.subrocess import subprocess


try:
    access_logger.info("Process started...")
    subprocess()
    x = 1 / 0
except Exception as e:
    error_logger.info(f"Process error: {e}")
