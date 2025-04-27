import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Ensure the logs folder exists
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Configure logging
log_file = os.path.join(log_folder, "application.log")
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Rotate the log file if it already exists
if os.path.exists(log_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rotated_log_file = os.path.join(log_folder, f"application_{timestamp}.log")
    os.rename(log_file, rotated_log_file)

# Set up a rotating file handler with UTF-8 encoding
file_handler = RotatingFileHandler(
    log_file, maxBytes=1 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 1MB per file, keep 5 backups
)
file_handler.setFormatter(log_formatter)

# Read console logging configuration from the .env file
console_logging = os.getenv("CONSOLE_LOGGING").lower() == "on"

# Function to configure the logger
def configure_logger():
    """
    Configures the root logger to log to a file and optionally to the console.
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Add the file handler
    root_logger.addHandler(file_handler)

    # Add a console handler if console_logging is enabled
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

# Function to configure a logger for Uvicorn
def configure_uvicorn_logger():
    """
    Configures a logger for Uvicorn to integrate its logs into the application's logging system.
    """
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.INFO)

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.setLevel(logging.INFO)

    # Add the file handler to both loggers
    uvicorn_access_logger.addHandler(file_handler)
    uvicorn_error_logger.addHandler(file_handler)

    # Add a console handler if console_logging is enabled
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        uvicorn_access_logger.addHandler(console_handler)
        uvicorn_error_logger.addHandler(console_handler)

    # Prepend "API Log -" to all Uvicorn logs
    class APILogFilter(logging.Filter):
        def filter(self, record):
            record.msg = f"API Log - {record.msg}"
            return True

    uvicorn_access_logger.addFilter(APILogFilter())
    uvicorn_error_logger.addFilter(APILogFilter())

# Function to get a logger
def get_logger(name):
    """
    Returns a logger for the given name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger.
    """
    return logging.getLogger(name)

# Configure the logger based on the .env setting
configure_logger()
configure_uvicorn_logger()