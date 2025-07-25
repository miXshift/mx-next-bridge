"""Centralized logging configuration for the MixBridge calculator system."""

import logging
import sys
from pathlib import Path
from typing import Optional
try:
    from ..config.constants import LOG_FORMAT, LOG_DATE_FORMAT
except ImportError:
    # Backwards compatibility during migration
    try:
        from .constants import LOG_FORMAT, LOG_DATE_FORMAT
    except ImportError:
        from constants import LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(
    name: str = "mixbridge",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional file path for logging
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
default_logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """Get a child logger with the given name."""
    return default_logger.getChild(name)