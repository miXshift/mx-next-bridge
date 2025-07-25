"""
Configuration and constants for Mix Bridge analysis modules.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

# File paths
DEFAULT_EXCEL_PATH = "../data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx"
DEFAULT_OUTPUT_DIR = "../output"

# Sheet names
SHEET_NAMES = {
    "campaign": "Campaign Tab",
    "keyword": "Keyword Tab",
    "product": "Product Tab"
}

# Metric categories
ABSOLUTE_METRICS = [
    'Spend', 'Total Ad Sales', 'Impressions', 'Clicks',
    'Units Sold', 'Add to Carts', 'Purchases'
]

RATE_METRICS = [
    'ACoS', 'ROAS', 'CTR', 'Conversion Rate',
    'Add to Cart Rate', 'Purchase Rate', 'CPC'
]

PERCENTAGE_FORMAT_METRICS = ['ACoS', 'CTR', 'Conversion Rate', 'Add to Cart Rate', 'Purchase Rate']

# Mix Bridge specific constants
CONTRIBUTION_SCALE = 10000
DEFAULT_COMPARISON_TOLERANCE = 0.0001
ZERO_BASELINE_DUMMY_VALUE = 0.0000001

# Column mappings for Mix Bridge analysis
MIX_BRIDGE_COLUMNS = {
    "p1_mix": "P1 Mix",
    "mix_rate": "Mix Rate", 
    "contribution": "Contribution",
    "analytic_4": "Analytic Point 4",  # TBD
    "analytic_5": "Analytic Point 5"   # TBD
}

@dataclass
class ZeroBaselineConfig:
    """Configuration for zero baseline handling."""
    enabled: bool = True
    dummy_value: float = ZERO_BASELINE_DUMMY_VALUE
    strategy: str = "dummy_value"  # Options: "dummy_value", "skip", "zero"
    
@dataclass
class ComparisonConfig:
    """Configuration for data comparison operations."""
    tolerance: float = DEFAULT_COMPARISON_TOLERANCE
    output_format: str = "csv"  # Options: "csv", "json", "excel"
    include_metadata: bool = True
    
@dataclass
class CacheConfig:
    """Configuration for caching behavior."""
    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour
    max_size_mb: int = 100
    
class AnalysisConfig:
    """Main configuration class for Mix Bridge analysis."""
    
    def __init__(self):
        self.zero_baseline = ZeroBaselineConfig()
        self.comparison = ComparisonConfig()
        self.cache = CacheConfig()
        self.excel_path = DEFAULT_EXCEL_PATH
        self.output_dir = Path(DEFAULT_OUTPUT_DIR)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "zero_baseline": {
                "enabled": self.zero_baseline.enabled,
                "dummy_value": self.zero_baseline.dummy_value,
                "strategy": self.zero_baseline.strategy
            },
            "comparison": {
                "tolerance": self.comparison.tolerance,
                "output_format": self.comparison.output_format,
                "include_metadata": self.comparison.include_metadata
            },
            "cache": {
                "enabled": self.cache.enabled,
                "ttl_seconds": self.cache.ttl_seconds,
                "max_size_mb": self.cache.max_size_mb
            },
            "excel_path": str(self.excel_path),
            "output_dir": str(self.output_dir)
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AnalysisConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        if "zero_baseline" in config_dict:
            zb = config_dict["zero_baseline"]
            config.zero_baseline = ZeroBaselineConfig(
                enabled=zb.get("enabled", True),
                dummy_value=zb.get("dummy_value", ZERO_BASELINE_DUMMY_VALUE),
                strategy=zb.get("strategy", "dummy_value")
            )
            
        if "comparison" in config_dict:
            comp = config_dict["comparison"]
            config.comparison = ComparisonConfig(
                tolerance=comp.get("tolerance", DEFAULT_COMPARISON_TOLERANCE),
                output_format=comp.get("output_format", "csv"),
                include_metadata=comp.get("include_metadata", True)
            )
            
        if "cache" in config_dict:
            cache = config_dict["cache"]
            config.cache = CacheConfig(
                enabled=cache.get("enabled", True),
                ttl_seconds=cache.get("ttl_seconds", 3600),
                max_size_mb=cache.get("max_size_mb", 100)
            )
            
        config.excel_path = config_dict.get("excel_path", DEFAULT_EXCEL_PATH)
        config.output_dir = Path(config_dict.get("output_dir", DEFAULT_OUTPUT_DIR))
        
        return config

# Default configuration instance
default_config = AnalysisConfig()