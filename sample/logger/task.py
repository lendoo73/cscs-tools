import logging
from log_config import access_logger_service, custom_logger_service

access_logger = access_logger_service.get_logger(__name__)
custom_logger = custom_logger_service.get_logger(__name__)

def my_task():
    access_logger.info("Subprocess started... using the same logfile as the main process")
    custom_logger.critical("Custom folder and format used for logging")
    my_second_task()

def my_second_task():
    custom_logger.setLevel(logging.DEBUG)
    custom_logger.debug("Debug logging dynamically set")
    custom_logger.setLevel(logging.INFO)
    custom_logger.critical("Only critical logs")
