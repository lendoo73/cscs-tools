# Logger  

## 🚀 Usage  

The `LoggerService` helps you easily set up **rotating log files** with configurable level, format, and retention days.  

### 1️⃣ Basic usage – project root `/log` folder  

```python
# log_config.py
from cscs_tools.logger.services.logger_service import LoggerService

# This will create a `/log` folder in the project root (if it doesn't exist)
# and automatically generate `access.log` and `error.log` files.
error_logger_service = LoggerService(log_file="error.log")  # Rotates every 30 days (default)
error_logger = error_logger_service.get_logger("error_logger")

access_logger_service = LoggerService(log_file="access.log", days=3)  # Rotates every 3 days
access_logger = access_logger_service.get_logger("access_logger")
```

---

### 2️⃣ Custom folder & settings from `.env`  

```python
# log_config.py
import os
from cscs_tools.logger.services.logger_service import LoggerService

# Make sure to load your .env file first
custom_logger_service = LoggerService(
    log_directory=os.getenv("LOG_DIRECTORY", ""),   # Path from .env
    log_file=os.getenv("ACCESS_LOG_FILE", "access"),  # File name from .env
    level=os.getenv("LEVEL", "INFO"),               # Logging level
    days=os.getenv("ROTATION", None),               # Rotation days
    log_format=os.getenv("FORMAT", None)            # Custom log format
)
custom_logger = custom_logger_service.get_logger("custom_logger")
```

---

## 📜 Example – Writing logs  

```python
from log_config import access_logger, error_logger, custom_logger

try:
    access_logger.info("Process started...")
    # Simulate process
    result = 1 / 0
except Exception as e:
    error_logger.error(f"Process error: {e}")

custom_logger.debug("Custom logger debug message")
custom_logger.critical("Custom logger critical message")
```

---

## ⚙️ Parameters  

| Parameter     | Type   | Default                              | Description |
|---------------|--------|--------------------------------------|-------------|
| `log_directory` | str  | `"log"`                              | Directory for log files (created if missing). |
| `log_file`    | str    | `"app.log"`                          | Log file name. |
| `level`       | str    | `"INFO"`                             | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `days`        | int    | `30`                                 | Number of days to keep rotated log files. |
| `log_format`  | str    | `"%(asctime)s - %(levelname)s - %(message)s"` | Log format string. |

---

## 🔄 Log Rotation  

- Rotation happens **daily**.
- Old logs are automatically deleted after the configured `days` retention period.
- Files are stored as `log_file.YYYY-MM-DD` in the specified directory.

---

## 🧱 Example `.env`  

```env
LOG_DIRECTORY=/var/log/myapp
ACCESS_LOG_FILE=access.log
LEVEL=DEBUG
ROTATION=7
FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```
