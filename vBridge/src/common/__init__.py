"""
Common Infrastructure Module

Shared utilities and infrastructure:
- exceptions: Custom exception classes
- logger: Logging configuration and utilities
"""

# Re-export main classes for easy access
try:
    from .exceptions import *
    from .logger import get_logger
except ImportError:
    # Will be available after Phase 2
    pass

__all__ = [
    'CalculationError',
    'ValidationError',
    'ConfigurationError',
    'DataProcessingError',
    'FileOperationError',
    'get_logger'
]