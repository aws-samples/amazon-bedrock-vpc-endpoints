import logging
import os

def setup_logging(log_level=logging.INFO, log_format=None, log_file=None):
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s'

    # If no log_file is provided, create one based on the script's name
    if log_file is None:
        script_name = os.path.basename(__file__)
        log_file = script_name.replace('.py', '.log')

    # Clear previous logging handlers to avoid duplication
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up file handler to log only to the file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Get the root logger and add only the file handler
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
