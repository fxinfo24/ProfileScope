"""
ProfileScope: Logging Utility
Provides centralized logging configuration
"""

import logging
from typing import Dict, Any
import os
import time
from functools import wraps


def setup_logger(name: str, config: Dict[str, Any] = None) -> logging.Logger:
    """
    Set up and configure a logger instance

    Args:
        name: Logger name
        config: Configuration options

    Returns:
        Configured logger instance
    """
    if config is None:
        config = {"level": "INFO", "file": "profilescope.log"}

    # Create logger
    logger = logging.getLogger(name)

    # Set level
    level_name = config.get("level", "INFO")
    level = getattr(logging, level_name)
    logger.setLevel(level)

    # Create handlers if logger has no handlers yet
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # File handler
        log_file = config.get("file")
        if log_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)

            # Add format to handlers
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            logger.addHandler(file_handler)

        logger.addHandler(console_handler)

    return logger


def log_http_request(logger):
    """
    Decorator for logging HTTP request information

    Args:
        logger: Logger instance to use for logging

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            start_time = time.time()
            result = func(request, *args, **kwargs)
            duration = time.time() - start_time

            logger.info(
                f"HTTP {request.method} {request.path} - "
                f"Status: {getattr(result, 'status_code', 'N/A')} - "
                f"Duration: {duration:.4f}s"
            )
            return result

        return wrapper

    return decorator
