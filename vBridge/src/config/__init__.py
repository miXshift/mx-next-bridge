"""
Configuration Module

Contains configuration, metrics definitions, and constants:
- metrics: Metric definitions and categorization
- settings: Configuration management and settings
- constants: Constants, thresholds, and default values
"""

# Re-export main classes for easy access
try:
    from .metrics import MetricDefinitions
    from .settings import MixBridgeConfig
    from .constants import *
except ImportError:
    # Will be available after Phase 2
    pass

__all__ = [
    'MetricDefinitions',
    'MixBridgeConfig',
    'BASIS_POINTS_MULTIPLIER',
    'ZERO_TOLERANCE',
    'DEFAULT_ENCODING'
]