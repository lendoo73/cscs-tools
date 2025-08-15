import os

from cscs_tools.logger.services.logger_service import LoggerService

# This code block creates a `/log` folder in the project root (if it doesn't exist)
# and automatically generates the corresponding log files (`access.log`, `error.log`).
error_logger_service = LoggerService(log_file="error.log")  # log files rotated in 30 days (as default)

access_logger_service = LoggerService(log_file="access.log", days=3) # logfiles rotated in 3 days


# This code block creates a `/log` folder at the path specified in `.env`
# Note: you must load the `.env` file before using these settings.
custom_logger_service = LoggerService(
    log_directory=os.getenv("LOG_DIRECTORY", ""),
    log_file=os.getenv("ACCESS_LOG_FILE", "access"),
    level=os.getenv("LEVEL", "INFO"),
    days=os.getenv("ROTATION", None),
    log_format=os.getenv("FORMAT", None)
)