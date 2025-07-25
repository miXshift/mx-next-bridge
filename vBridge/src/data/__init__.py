"""
Data Processing Module

Handles data loading, transformation, validation, and utilities:
- processor: Data loading and transformation operations
- validator: Data validation and consistency checking
- utils: Calculation utilities and helper functions
"""

# Re-export main classes for easy access
try:
    from .processor import OptimizedDataProcessor
    from .validator import MixBridgeValidator
    from .utils import safe_divide, calculate_rate_metric
except ImportError:
    # Will be available after Phase 2
    pass

__all__ = [
    'OptimizedDataProcessor',
    'MixBridgeValidator',
    'safe_divide',
    'calculate_rate_metric'
]