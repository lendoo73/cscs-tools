from log_config import access_logger_service, error_logger_service
from sample.logger.task import my_task


access_logger = access_logger_service.get_logger(__name__)
error_logger = error_logger_service.get_logger(__name__)

try:
    access_logger.info("Process started...")
    my_task()
    x = 1 / 0
except Exception as e:
    error_logger.info(f"Process error: {e}")
