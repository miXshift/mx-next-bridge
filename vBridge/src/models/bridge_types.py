"""
Bridge type definitions and enums for the MixBridge v2 system.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class BridgeType(Enum):
    """Enumeration of bridge calculation types."""
    MIX_BRIDGE = auto()           # Traditional Mix Bridge
    MIXRATE_BRIDGE = auto()       # Standard MixRate Bridge
    MIXRATE_INFINITY = auto()     # MixRate with Infinity Error handling


class ContributionUnit(Enum):
    """Units for displaying contribution values."""
    CURRENCY = "$"          # Local currency (e.g., +/-$0.42)
    BASIS_POINTS = "bps"    # Basis points (multiplied by 10000)
    PERCENTAGE = "%"        # Percentage points
    COUNT = "count"         # Raw count
    RATIO = "ratio"         # Dimensionless ratio


@dataclass
class BridgeConfiguration:
    """Configuration for a specific bridge calculation."""
    bridge_type: BridgeType
    mix_determinant: Optional[str] = None  # Column used to determine mix (e.g., "Spend", "Clicks")
    contribution_unit: ContributionUnit = ContributionUnit.CURRENCY
    inverse_metric: Optional[str] = None   # For infinity error handling (e.g., ROAS for ACoS)
    requires_percentage_conversion: bool = False  # If true, multiply by 10000 for basis points
    
    def __post_init__(self):
        """Validate configuration."""
        if self.bridge_type == BridgeType.MIXRATE_INFINITY and not self.inverse_metric:
            raise ValueError("MIXRATE_INFINITY requires an inverse_metric")
        if self.bridge_type in [BridgeType.MIXRATE_BRIDGE, BridgeType.MIXRATE_INFINITY] and not self.mix_determinant:
            raise ValueError("MixRate bridges require a mix_determinant")


@dataclass
class MetricFormula:
    """Defines how a metric is calculated."""
    numerator: str
    denominator: str
    is_percentage: bool = False
    multiplier: float = 1.0
    
    def calculate(self, num_value: float, denom_value: float) -> float:
        """Calculate the metric value."""
        if denom_value == 0:
            return 0.0
        value = (num_value / denom_value) * self.multiplier
        if self.is_percentage:
            value *= 100
        return value