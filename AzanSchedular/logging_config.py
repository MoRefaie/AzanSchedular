import json
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


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


# --- Read CONSOLE_LOGGING directly from system.json ---
def get_console_logging_setting():
    # Try to find system.json in MEIPASS or local config
    if hasattr(__builtins__, '_MEIPASS'):
        config_path = os.path.join(__builtins__._MEIPASS, 'config', 'system.json')
    else:
        config_path = os.path.join(os.getcwd(), 'config', 'system.json')
    try:
        with open(config_path, "r") as f:
            sys_config = json.load(f)
        return str(sys_config.get("CONSOLE_LOGGING", "Off")).lower() == "on"
    except Exception:
        return False


console_logging = get_console_logging_setting()


# Function to configure the logger
def configure_logger():
    """
    Configures the root logger to log to a file and optionally to the console.
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Custom formatter that prepends 'API - ' to Uvicorn logs
    class UvicornFilter(logging.Filter):
        def filter(self, record):
            if record.name.startswith("uvicorn"):
                record.msg = f"API Log - {record.msg}"
            return True

    # Add the custom filter to the file handler
    file_handler.addFilter(UvicornFilter())

    # Add the file handler
    root_logger.addHandler(file_handler)

    # Add a console handler if console_logging is enabled
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)


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
