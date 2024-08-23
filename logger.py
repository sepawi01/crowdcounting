import logging
import logging.config
import os

# Directory where logs will be stored
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

def setup_logger():
    # Create a logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the logging level for the root logger

    # Formatter for the logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler for writing logs to a file
    file_handler = logging.FileHandler(os.path.join(log_directory, "app.log"))
    file_handler.setLevel(logging.INFO)  # Set file logging level to INFO
    file_handler.setFormatter(formatter)

    # Console handler for outputting logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Set console logging level to DEBUG
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger