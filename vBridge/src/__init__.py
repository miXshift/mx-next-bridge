"""
MixBridge v2 Source Package

Modular MixBridge calculation engine with organized modules:

- core: Bridge calculation engines and algorithms
- data: Data processing, validation, and utilities  
- output: Output formatting and file management
- config: Configuration, metrics definitions, and constants
- common: Shared infrastructure (logging, exceptions)

Example Usage:
    from src.core.bridge_calculator import BridgeCalculator
    from src.config.metrics import MetricDefinitions
    from src.data.processor import OptimizedDataProcessor
"""

# Package-level exports for convenience
from .core.bridge_calculator import BridgeCalculator
from .core.enhanced_calculator import EnhancedMixBridgeCalculator
from .core.mixrate_calculator import MixRateBridgeCalculator
from .core.campaign_bridge_modular import CampaignBridge
from .data.validator import MixBridgeValidator
from .data.processor import OptimizedDataProcessor
from .data.utils import safe_divide, calculate_rate_metric
from .config.metrics import MetricDefinitions
from .config.settings import MixBridgeConfig
from .config.constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
from .output.formatter import OutputFormatter
from .output.enhanced_formatter import EnhancedOutputFormatter
from .output.manager import ImprovedOutputManager
from .common.exceptions import (
    CalculationError, ValidationError, ConfigurationError, 
    DataProcessingError, FileOperationError
)
from .common.logger import get_logger

__version__ = "2.0.0"
__author__ = "MixBridge Team"

# Convenience collections
__all__ = [
    # Core calculators
    'BridgeCalculator', 'EnhancedMixBridgeCalculator', 'MixRateBridgeCalculator', 'CampaignBridge',
    # Data processing
    'MixBridgeValidator', 'OptimizedDataProcessor', 'safe_divide', 'calculate_rate_metric',
    # Configuration
    'MetricDefinitions', 'MixBridgeConfig', 'BASIS_POINTS_MULTIPLIER', 'ZERO_TOLERANCE',
    # Output management
    'OutputFormatter', 'EnhancedOutputFormatter', 'ImprovedOutputManager',
    # Common utilities
    'CalculationError', 'ValidationError', 'ConfigurationError', 'DataProcessingError', 
    'FileOperationError', 'get_logger'
]