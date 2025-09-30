import logging, os, sys
from logging.handlers import TimedRotatingFileHandler


class LoggerService:
    """
    A service for managing configurable rotating log files.

    This class provides an easy way to create named loggers with
    daily rotation and automatic cleanup of old log files. It
    supports custom log directories, filenames, log levels, and formats.

    Attributes
    ----------
    log_directory : str
        Absolute path to the directory where log files are stored.
    log_file : str
        Name of the log file.
    days : int
        Number of days to keep old log files.
    logger : logging.Logger
        The base logger instance configured for this service.

    Parameters
    ----------
    log_directory : str, optional
        Directory path where log files are stored (default is "log").
    log_file : str, optional
        Name of the log file (default is "app.log").
    level : str, optional
        Logging level as a string (default is "INFO").
        Supported values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
    days : int, optional
        Number of days to keep old log files (default is 30).
    log_format : str, optional
        Format string for log messages
        (default is "%(asctime)s - %(levelname)s - %(message)s").

    Methods
    -------
    get_logger(name: str) -> logging.Logger
        Return a named logger instance for the specified component or module.

    Examples
    --------
    >>> # Create a logger service with default settings
    >>> logger_service = LoggerService()
    >>> logger = logger_service.get_logger('my_module')
    >>> logger.info('Logging initialized for my_module.')

    >>> # Create a logger service with custom settings
    >>> logger_service = LoggerService(
    ...     log_directory='logs',
    ...     log_file='access.log',
    ...     level='DEBUG',
    ...     days=7,
    ...     log_format='%(levelname)s | %(name)s | %(message)s'
    ... )
    >>> logger = logger_service.get_logger('api')
    >>> logger.debug('Debug log for API.')
    """

    def __init__(
            self,
            log_directory="log",
            log_file="app.log",
            level="INFO",
            days=30,
            log_format="%(asctime)s - %(levelname)s - %(message)s",
            to_stdout=False
    ):
        """
        Initialize the LoggerService with configurable logging parameters.

        This sets up a logging directory and prepares a timed rotating file handler
        with the specified logging level and format.

        Parameters
        ----------
        log_directory : str, optional
            Directory path where log files are stored (default is 'log').
            The directory will be created if it does not exist.
        log_file : str, optional
            Name of the log file (default is 'app.log').
        level : str, optional
            Logging level for the logger (default is 'INFO').
            Common values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
        days : int, optional
            Number of days to keep old log files before rotating out (default is 30).
        log_format : str, optional
            Format string for log messages (default is '%(asctime)s - %(levelname)s - %(message)s').
        to_stdout : bool, optional
            If True, logs are written to stdout instead of a file (default is False).
        """
        self.log_directory = os.path.abspath(log_directory)
        self.log_file = log_file
        self.days = days
        self.to_stdout = to_stdout
        self.logger = self._configure_logging(level, log_format)

    def _configure_logging(self, level, log_format):
        """
        Configure and return a logger instance with a TimedRotatingFileHandler.

        This method creates the log directory if it does not exist, sets up
        a file handler that rotates logs daily, and retains logs for the
        specified number of days. The logger is configured with the provided
        logging level and message format.

        Parameters
        ----------
        level : str
            Logging level for the logger. Common values: 'DEBUG', 'INFO',
            'WARNING', 'ERROR', 'CRITICAL'.
        log_format : str
            Format string for log messages.

        Returns
        -------
        logging.Logger
            Configured logger instance that writes to the specified log file
            and rotates logs daily.
        """
        logger = logging.getLogger(self.log_file)

        log_formatter = logging.Formatter(log_format)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

        if self.to_stdout:
            handler = logging.StreamHandler(sys.stdout)
        else:
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)


            handler = TimedRotatingFileHandler(
                filename=os.path.join(self.log_directory, self.log_file),
                when="D",
                interval=1,
                backupCount=self.days,
                encoding="utf-8",
                delay=False
            )

        handler.setFormatter(log_formatter)

        logger.addHandler(handler)
        logger.propagate = False  # Prevent log messages from being propagated to the root logger

        return logger

    def get_logger(self, name: str):
        """
            Return a named logger instance for the specified component or module.

            Parameters
            ----------
            name : str
                Name of the component or module.

            Returns
            -------
            logging.Logger
                Logger instance configured for the specified name.
        """
        return logging.getLogger(f"{self.log_file}.{name}")
