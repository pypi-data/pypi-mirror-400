import os
import logging

def get_logger(logfile, name='mylogger', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s'):
    # Ensure the directory for the logfile exists
    log_dir = os.path.dirname(logfile)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File Handler: prints to logfile
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logging.Formatter(format))
    logger.addHandler(fileHandler)

    # Console Handler: prints to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(format))
    logger.addHandler(consoleHandler)
    logger.propagate = False
    return logger


def close(logger):
    logger.handlers = []