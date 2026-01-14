"""
OpenJobs Logger - Configurable logging for the scraper
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = 'openjobs', log_dir: str = 'logs', level: int = logging.INFO):
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Name of the logger
        log_dir: Directory to store log files
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    log = logging.getLogger(name)
    log.setLevel(level)

    # Remove existing handlers if any
    if log.handlers:
        log.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create file handler (if log_dir is set)
    if log_dir:
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'openjobs_{today}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        log.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)

    return log


def get_logger(name: str = 'openjobs'):
    """
    Get or create a logger with the given name.

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Create default logger instance
# Don't create log files by default - set OPENJOBS_LOG_DIR env var to enable
log_dir = os.getenv('OPENJOBS_LOG_DIR', '')
logger = setup_logger(log_dir=log_dir if log_dir else None)
