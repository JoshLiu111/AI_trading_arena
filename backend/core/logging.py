# backend/core/logging.py

"""
Centralized logging configuration for the backend
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance (convenience function)
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return setup_logger(name)
