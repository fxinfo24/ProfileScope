"""
ProfileScope: Logging Utility Module
Provides standardized logging for the application
"""

import logging
import os
from typing import Dict, Any
import time
from functools import wraps


def setup_logger(name: str, config: Dict[str, Any] = None) -> logging.Logger:
    """
    Set up and configure a logger

    Args:
        name: Logger name
        config: Dictionary with logging configuration

    Returns:
        Configured logger instance
    """
    if config is None:
        config = {"level": "INFO", "file": None}

    # Create logger
    logger = logging.getLogger(name)

    # Set level based on config
    level_name = config.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Always add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if configured
    log_file = config.get("file")
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

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
