import logging
from logging.handlers import RotatingFileHandler
import sys

# Define log formatting
LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create a logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)  # Set the lowest severity to capture

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# File Handler (rotating logs)
file_handler = RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
