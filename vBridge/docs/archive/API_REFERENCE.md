# Enhanced MixBridge API Reference

## Table of Contents
1. [Module Overview](#module-overview)
2. [EnhancedMixBridgeCalculator](#enhancedmixbridgecalculator)
3. [MixBridgeConfig](#mixbridgeconfig)
4. [ContributionValidator](#contributionvalidator)
5. [BridgeCalculator (Enhanced)](#bridgecalculator-enhanced)
6. [Usage Examples](#usage-examples)
7. [Type Definitions](#type-definitions)
8. [Error Handling](#error-handling)

---

## Module Overview

### Import Structure
```python
# Core enhanced calculator
from enhanced_mixbridge_calculator import EnhancedMixBridgeCalculator

# Configuration management
from mixbridge_config import MixBridgeConfig, ConfigManager, get_config

# Validation framework
from mixbridge_validator import ContributionValidator, ValidationResult

# Enhanced bridge calculator (backward compatible)
from bridge_calculator import BridgeCalculator
```

### Module Dependencies
```python
# Required dependencies
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import json
import warnings
from dataclasses import dataclass, asdict
```

---

## EnhancedMixBridgeCalculator

### Class Definition
```python
class EnhancedMixBridgeCalculator:
    """
    Advanced Mix Bridge calculator with multiple zero baseline handling strategies
    """
```

### Constructor
```python
def __init__(self, strategy: str = 'hybrid', precision: int = 12)
```

**Parameters:**
- `strategy` (str): Calculation strategy ('dummy_value', 'delta_assignment', 'hybrid')
- `precision` (int): Decimal precision for calculations (0-15)

**Raises:**
- `ValueError`: If strategy is not valid or precision is out of range

**Example:**
```python
calculator = EnhancedMixBridgeCalculator(
    strategy='hybrid',
    precision=12
)
```

### Methods

#### `get_absolute_metrics()`
```python
def get_absolute_metrics(self) -> List[str]
```

**Returns:**
- `List[str]`: List of absolute (summable) metrics

**Example:**
```python
metrics = calculator.get_absolute_metrics()
# Returns: ['Spend', 'Total Ad Sales', 'Impressions', 'Clicks', ...]
```

#### `calculate_contributions_enhanced()`
```python
def calculate_contributions_enhanced(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame, 
    strategy: Optional[str] = None
) -> pd.DataFrame
```

**Parameters:**
- `output_df` (pd.DataFrame): Campaign data dataframe with period columns
- `total_row` (pd.DataFrame): Totals row dataframe  
- `strategy` (Optional[str]): Override default strategy

**Returns:**
- `pd.DataFrame`: DataFrame with calculated contributions

**Raises:**
- `ValueError`: If strategy is unknown

**Example:**
```python
result_df = calculator.calculate_contributions_enhanced(
    output_df=campaign_data,
    total_row=totals_data,
    strategy='hybrid'
)
```

#### `get_calculation_summary()`
```python
def get_calculation_summary(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame
) -> Dict[str, Any]
```

**Parameters:**
- `output_df` (pd.DataFrame): Campaign data with contributions
- `total_row` (pd.DataFrame): Totals row

**Returns:**
- `Dict[str, Any]`: Dictionary with calculation summary statistics

**Example:**
```python
summary = calculator.get_calculation_summary(result_df, total_row)
print(f"Strategy: {summary['strategy_used']}")
print(f"Zero baseline campaigns: {summary['zero_baseline_campaigns']}")
```

### Private Methods

#### `_calculate_dummy_value_method()`
```python
def _calculate_dummy_value_method(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame
) -> pd.DataFrame
```

Internal method implementing dummy value strategy.

#### `_calculate_delta_assignment_method()`
```python
def _calculate_delta_assignment_method(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame
) -> pd.DataFrame
```

Internal method implementing delta assignment strategy.

#### `_calculate_hybrid_method()`
```python
def _calculate_hybrid_method(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame
) -> pd.DataFrame
```

Internal method implementing hybrid strategy.

---

## MixBridgeConfig

### Class Definition
```python
@dataclass
class MixBridgeConfig:
    """Configuration dataclass for MixBridge calculations"""
```

### Configuration Fields
```python
# Zero baseline handling
zero_baseline_strategy: str = 'hybrid'
dummy_value: float = 1e-7

# Calculation precision  
precision_decimals: int = 12
validation_tolerance: float = 1e-6

# Auditing and logging
enable_audit_trail: bool = True
mathematical_validation: bool = True
debug_mode: bool = False

# Output formatting
output_precision: int = 2
percentage_as_decimal: bool = True

# Performance settings
enable_parallel_processing: bool = False
chunk_size: int = 1000
```

### Class Methods

#### `create_config()`
```python
@classmethod
def create_config(cls, **overrides) -> 'MixBridgeConfig'
```

**Parameters:**
- `**overrides`: Configuration parameters to override

**Returns:**
- `MixBridgeConfig`: Configuration instance

**Example:**
```python
config = MixBridgeConfig.create_config(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=15,
    debug_mode=True
)
```

#### `from_file()`
```python
@classmethod
def from_file(cls, config_path: str) -> 'MixBridgeConfig'
```

**Parameters:**
- `config_path` (str): Path to JSON configuration file

**Returns:**
- `MixBridgeConfig`: Configuration loaded from file

**Raises:**
- `ValueError`: If JSON is invalid

**Example:**
```python
config = MixBridgeConfig.from_file('config/production.json')
```

### Instance Methods

#### `to_file()`
```python
def to_file(self, config_path: str) -> None
```

**Parameters:**
- `config_path` (str): Path to save configuration file

**Example:**
```python
config.to_file('config/my_config.json')
```

#### `update()`
```python
def update(self, **kwargs) -> None
```

**Parameters:**
- `**kwargs`: Parameters to update

**Raises:**
- `ValueError`: If parameter is unknown or invalid

**Example:**
```python
config.update(
    precision_decimals=10,
    debug_mode=True
)
```

#### `get_strategy_info()`
```python
def get_strategy_info(self) -> Dict[str, str]
```

**Returns:**
- `Dict[str, str]`: Strategy name and description

**Example:**
```python
info = config.get_strategy_info()
print(f"Strategy: {info['strategy']}")
print(f"Description: {info['description']}")
```

### ConfigManager Class

#### Constructor
```python
def __init__(self, config_path: Optional[str] = None)
```

#### Methods

##### `apply_profile()`
```python
def apply_profile(self, profile_name: str) -> None
```

**Parameters:**
- `profile_name` (str): Profile name ('production', 'development', 'performance', 'accuracy')

**Raises:**
- `ValueError`: If profile name is unknown

**Example:**
```python
manager = ConfigManager()
manager.apply_profile('production')
```

##### `get_profile_configs()`
```python
def get_profile_configs(self) -> Dict[str, MixBridgeConfig]
```

**Returns:**
- `Dict[str, MixBridgeConfig]`: Available configuration profiles

### Global Functions

#### `get_config()`
```python
def get_config() -> MixBridgeConfig
```

**Returns:**
- `MixBridgeConfig`: Global configuration instance

#### `set_config_path()`
```python
def set_config_path(path: str) -> None
```

**Parameters:**
- `path` (str): Path to configuration file

#### `apply_config_profile()`
```python
def apply_config_profile(profile_name: str) -> None
```

**Parameters:**
- `profile_name` (str): Profile to apply globally

---

## ContributionValidator

### Class Definition
```python
class ContributionValidator:
    """Validation framework for contribution calculations"""
```

### Constructor
```python
def __init__(self, config: Optional[MixBridgeConfig] = None)
```

**Parameters:**
- `config` (Optional[MixBridgeConfig]): Configuration object, uses global if None

### Methods

#### `validate_contributions()`
```python
def validate_contributions(
    self, 
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame
) -> bool
```

**Parameters:**
- `output_df` (pd.DataFrame): Campaign data with contributions
- `total_row` (pd.DataFrame): Totals row dataframe

**Returns:**
- `bool`: True if all validations pass, False otherwise

**Example:**
```python
validator = ContributionValidator()
is_valid = validator.validate_contributions(output_df, total_row)

if not is_valid:
    print("Validation failed!")
    validator.print_validation_report()
```

#### `get_validation_report()`
```python
def get_validation_report(self) -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Comprehensive validation report

**Example:**
```python
report = validator.get_validation_report()
print(f"Success rate: {report['summary']['success_rate']}%")
print(f"Failed checks: {report['summary']['failed']}")
```

#### `print_validation_report()`
```python
def print_validation_report(self) -> None
```

Prints formatted validation report to console.

### ValidationResult Class

```python
@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = 'info'  # 'info', 'warning', 'error'
```

---

## BridgeCalculator (Enhanced)

### Enhanced Methods

#### `calculate_contributions()` (Enhanced)
```python
@staticmethod
def calculate_contributions(
    output_df: pd.DataFrame, 
    total_row: pd.DataFrame, 
    strategy: str = 'hybrid'
) -> pd.DataFrame
```

**Parameters:**
- `output_df` (pd.DataFrame): Campaign data dataframe
- `total_row` (pd.DataFrame): Totals row dataframe  
- `strategy` (str): Zero baseline handling strategy

**Returns:**
- `pd.DataFrame`: DataFrame with calculated contributions

**Example:**
```python
result = BridgeCalculator.calculate_contributions(
    output_df=campaign_data,
    total_row=totals_data,
    strategy='hybrid'
)
```

#### `calculate_bridge()` (Enhanced)
```python
@staticmethod
def calculate_bridge(
    bridge_data: pd.DataFrame, 
    strategy: str = 'hybrid', 
    validate: bool = True
) -> pd.DataFrame
```

**Parameters:**
- `bridge_data` (pd.DataFrame): Campaign data for analysis
- `strategy` (str): Zero baseline handling strategy
- `validate` (bool): Enable validation checks

**Returns:**
- `pd.DataFrame`: DataFrame with calculated contributions

**Example:**
```python
result = BridgeCalculator.calculate_bridge(
    bridge_data=merged_data,
    strategy='delta_assignment',
    validate=True
)
```

---

## Usage Examples

### Basic Usage
```python
from enhanced_mixbridge_calculator import EnhancedMixBridgeCalculator
from mixbridge_config import MixBridgeConfig

# Create configuration
config = MixBridgeConfig(
    zero_baseline_strategy='hybrid',
    precision_decimals=12,
    mathematical_validation=True
)

# Initialize calculator
calculator = EnhancedMixBridgeCalculator(
    strategy=config.zero_baseline_strategy,
    precision=config.precision_decimals
)

# Calculate contributions
result_df = calculator.calculate_contributions_enhanced(
    output_df, total_row
)

# Get summary
summary = calculator.get_calculation_summary(result_df, total_row)
print(f"Zero baseline campaigns: {summary['zero_baseline_campaigns']}")
```

### Strategy Comparison
```python
strategies = ['dummy_value', 'delta_assignment', 'hybrid']
results = {}

for strategy in strategies:
    calculator = EnhancedMixBridgeCalculator(strategy=strategy)
    results[strategy] = calculator.calculate_contributions_enhanced(
        output_df.copy(), total_row, strategy
    )

# Compare results
for metric in ['Spend', 'Total Ad Sales']:
    print(f"\n{metric} Total Contributions:")
    for strategy in strategies:
        total = results[strategy][f'{metric} - Contribution'].sum()
        print(f"  {strategy}: {total:.2f} bps")
```

### Configuration Profiles
```python
from mixbridge_config import apply_config_profile, get_config

# Apply production profile
apply_config_profile('production')
config = get_config()

# Use configuration
calculator = EnhancedMixBridgeCalculator(
    strategy=config.zero_baseline_strategy,
    precision=config.precision_decimals
)
```

### Validation Workflow
```python
from mixbridge_validator import ContributionValidator

# Calculate with validation
result_df = BridgeCalculator.calculate_bridge(
    bridge_data, 
    strategy='hybrid',
    validate=True
)

# Custom validation
validator = ContributionValidator()
is_valid = validator.validate_contributions(result_df[1:], result_df[0:1])

if not is_valid:
    report = validator.get_validation_report()
    
    # Check specific validation types
    warnings = report['by_severity']['warning']
    errors = report['by_severity']['error']
    
    if errors:
        print("Critical validation errors detected:")
        for error in errors:
            print(f"  - {error['message']}")
    
    if warnings:
        print("Validation warnings:")
        for warning in warnings:
            print(f"  - {warning['message']}")
```

### Error Handling
```python
try:
    # Calculate with error handling
    result = calculator.calculate_contributions_enhanced(
        output_df, total_row, strategy='invalid_strategy'
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
    
    # Fallback to basic calculation
    result = BridgeCalculator._calculate_contributions_original(
        output_df, total_row
    )
```

---

## Type Definitions

### DataFrames

#### Campaign Data DataFrame
```python
# Required columns for campaign data
campaign_columns = [
    'CampaignName',                    # str
    'Spend - January 2025',           # float
    'Spend - February 2025',          # float
    'Total Ad Sales - January 2025',  # float
    'Total Ad Sales - February 2025', # float
    # ... additional metric columns
]
```

#### Output DataFrame
```python
# Output columns after contribution calculation
output_columns = [
    'Campaign',                       # str
    'Spend - January 2025',          # float
    'Spend - February 2025',         # float
    'Spend - Net Change',            # float
    'Spend - % Change',              # float
    'Spend - Contribution',          # float
    # ... repeated for each metric
]
```

### Configuration Types
```python
# Strategy options
StrategyType = Literal['dummy_value', 'delta_assignment', 'hybrid']

# Profile options  
ProfileType = Literal['production', 'development', 'performance', 'accuracy']

# Severity levels
SeverityType = Literal['info', 'warning', 'error']
```

### Return Types
```python
# Calculation summary return type
CalculationSummary = TypedDict('CalculationSummary', {
    'strategy_used': str,
    'total_campaigns': int,
    'metrics_processed': int,
    'zero_baseline_campaigns': Dict[str, int],
    'contribution_totals': Dict[str, float]
})

# Validation report return type
ValidationReport = TypedDict('ValidationReport', {
    'summary': Dict[str, Union[int, float]],
    'by_severity': Dict[str, List[Dict[str, Any]]],
    'config_used': Dict[str, Union[str, float, int]]
})
```

---

## Error Handling

### Exception Types

#### Configuration Errors
```python
# Invalid strategy
try:
    calculator = EnhancedMixBridgeCalculator(strategy='invalid')
except ValueError as e:
    print(f"Invalid strategy: {e}")

# Invalid precision
try:
    calculator = EnhancedMixBridgeCalculator(precision=20)
except ValueError as e:
    print(f"Invalid precision: {e}")
```

#### Calculation Errors
```python
# Missing required columns
try:
    result = calculator.calculate_contributions_enhanced(
        incomplete_df, total_row
    )
except KeyError as e:
    print(f"Missing required column: {e}")

# Invalid data types
try:
    result = calculator.calculate_contributions_enhanced(
        string_data_df, total_row
    )
except TypeError as e:
    print(f"Invalid data type: {e}")
```

#### Validation Errors
```python
# Validation tolerance exceeded
validator = ContributionValidator()
is_valid = validator.validate_contributions(output_df, total_row)

if not is_valid:
    # Check for mathematical inconsistencies
    report = validator.get_validation_report()
    
    for result in validator.validation_results:
        if result.severity == 'error':
            print(f"Validation error: {result.message}")
            if result.details:
                print(f"Details: {result.details}")
```

### Best Practices for Error Handling

#### Graceful Degradation
```python
def calculate_with_fallback(bridge_data, preferred_strategy='hybrid'):
    """Calculate with fallback to simpler strategies on error"""
    strategies = [preferred_strategy, 'dummy_value', 'original']
    
    for strategy in strategies:
        try:
            if strategy == 'original':
                return BridgeCalculator._calculate_contributions_original(
                    output_df, total_row
                )
            else:
                return BridgeCalculator.calculate_bridge(
                    bridge_data, strategy=strategy, validate=False
                )
        except Exception as e:
            print(f"Strategy {strategy} failed: {e}")
            continue
    
    raise RuntimeError("All calculation strategies failed")
```

#### Validation with Recovery
```python
def validated_calculation(bridge_data, strategy='hybrid'):
    """Perform calculation with validation and recovery"""
    result = BridgeCalculator.calculate_bridge(
        bridge_data, strategy=strategy, validate=True
    )
    
    # Check if validation passed
    validator = ContributionValidator()
    campaign_data = result.iloc[1:]  # Exclude total row
    total_row = result.iloc[0:1]
    
    is_valid = validator.validate_contributions(campaign_data, total_row)
    
    if not is_valid:
        # Try with more conservative strategy
        print("Validation failed, trying conservative approach...")
        result = BridgeCalculator.calculate_bridge(
            bridge_data, strategy='dummy_value', validate=False
        )
    
    return result
```

---

This API reference provides comprehensive documentation for all public interfaces in the Enhanced MixBridge system. For implementation examples and usage patterns, refer to the User Guide and Strategy Guide documentation.