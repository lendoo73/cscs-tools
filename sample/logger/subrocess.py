import logging
from log_config import access_logger, custom_logger

def subprocess():
    access_logger.info("Subprocess started... using the same logfile as the main process")
    # access_logger.setLevel(logging.DEBUG)  # Uncomment to enable debug logging
    access_logger.debug("Debug logging executed")
    custom_logger.debug("Debug logging executed")
    custom_logger.critical("Custom folder and format used for logging")
