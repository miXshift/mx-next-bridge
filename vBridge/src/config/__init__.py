"""
Configuration Module

Contains configuration, bridge mappings, and constants:
- bridge_mappings: KPI to bridge type mappings and metric formulas
- settings: Configuration management and settings
- constants: Constants, thresholds, and default values
"""

# Re-export main classes for easy access
try:
    from .bridge_mappings import KPI_BRIDGE_MAPPINGS, get_bridge_configuration, get_metrics_by_bridge_type
    from .settings import MixBridgeConfig
    from .constants import *
except ImportError:
    # Will be available after Phase 2
    pass

__all__ = [
    'KPI_BRIDGE_MAPPINGS',
    'get_bridge_configuration',
    'get_metrics_by_bridge_type',
    'MixBridgeConfig',
    'BASIS_POINTS_MULTIPLIER',
    'ZERO_TOLERANCE',
    'DEFAULT_ENCODING'
]