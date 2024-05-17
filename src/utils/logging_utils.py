import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging():
    log_folder = 'C:\\T3100\\Projects\\Parkinglot_usage_analyse\\logs'
    log_file = os.path.join(log_folder, "main.log")  # Path to the error log file
    
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)  # Set the root logger's level to ERROR or higher

    # Create a rotating file handler with log rotation (max 1 MB, keep 3 backup files)
    file_handler = RotatingFileHandler(log_file, maxBytes=1e6, backupCount=3)
    file_handler.setLevel(logging.ERROR)  # Set the log level to ERROR or higher
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger