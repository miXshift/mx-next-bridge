# API Reference

MixBridge v2 features a clean modular architecture with organized modules for better maintainability and development experience.

## Table of Contents

1. [Core Calculation Engines](#core-calculation-engines)
2. [Data Processing & Validation](#data-processing--validation)
3. [Output Management](#output-management)
4. [Configuration & Settings](#configuration--settings)
5. [Common Infrastructure](#common-infrastructure)
6. [Package-Level Imports](#package-level-imports)

## Core Calculation Engines

### `src.core.bridge_calculator`

Main bridge calculation logic.

#### `BridgeCalculator`

```python
from src.core.bridge_calculator import BridgeCalculator

class BridgeCalculator:
    """Handles bridge calculations and metric computations"""
```

**Key Methods:**
- `get_metric_list() -> List[str]`: Get list of all metrics
- `create_output_dataframe()`: Create structured output dataframe
- `calculate_contributions()`: Calculate campaign contributions

### `src.core.enhanced_calculator`

Zero baseline handling with delta assignment strategy.

#### `EnhancedMixBridgeCalculator`

```python
from src.core.enhanced_calculator import EnhancedMixBridgeCalculator

class EnhancedMixBridgeCalculator:
    """Advanced calculator using delta assignment for zero baseline handling"""
```

### `src.core.mixrate_calculator`

Rate metric calculations with infinity error handling.

#### `MixRateBridgeCalculator`

```python
from src.core.mixrate_calculator import MixRateBridgeCalculator

class MixRateBridgeCalculator:
    """MixRate Bridge calculator for rate metrics using inverse methodology"""
```

## Data Processing & Validation

### `src.data.processor`

Optimized data loading and transformation.

#### `OptimizedDataProcessor`

```python
from src.data.processor import OptimizedDataProcessor

class OptimizedDataProcessor:
    """Optimized data loading and processing operations"""
```

### `src.data.validator`

Data validation and consistency checking.

#### `MixBridgeValidator`

```python
from src.data.validator import MixBridgeValidator

class MixBridgeValidator:
    """Comprehensive validation framework for bridge analysis"""
```

### `src.data.utils`

Calculation utilities and helper functions.

```python
from src.data.utils import safe_divide, calculate_rate_metric
```

## Output Management

### `src.output.formatter`

Basic CSV formatting and structure.

#### `OutputFormatter`

```python
from src.output.formatter import OutputFormatter

class OutputFormatter:
    """Handles output formatting and CSV generation"""
```

### `src.output.enhanced_formatter`

Advanced formatting with metadata and archiving.

#### `EnhancedOutputFormatter`

```python
from src.output.enhanced_formatter import EnhancedOutputFormatter

class EnhancedOutputFormatter:
    """Enhanced output formatter with semantic naming and file management"""
```

### `src.output.manager`

File management and archiving operations.

#### `ImprovedOutputManager`

```python
from src.output.manager import ImprovedOutputManager

class ImprovedOutputManager:
    """Advanced file management with automatic archiving"""
```

## Configuration & Settings

### `src.config.metrics`

Metric definitions and categorization.

#### `MetricDefinitions`

```python
from src.config.metrics import MetricDefinitions

class MetricDefinitions:
    """Centralized metric definitions and categorization"""
```

**Key Methods:**
- `get_all_metrics() -> List[str]`: Get all defined metrics
- `get_absolute_metrics() -> List[str]`: Get summable metrics
- `get_rate_metrics() -> List[str]`: Get rate/percentage metrics
- `is_absolute_metric(metric: str) -> bool`: Check if metric is absolute

### `src.config.settings`

Configuration management and settings.

#### `MixBridgeConfig`

```python
from src.config.settings import MixBridgeConfig

class MixBridgeConfig:
    """Configuration management for MixBridge operations"""
```

### `src.config.constants`

Constants, thresholds, and default values.

```python
from src.config.constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
```

## Common Infrastructure

### `src.common.exceptions`

Custom exception classes.

```python
from src.common.exceptions import (
    CalculationError,
    ValidationError, 
    ConfigurationError,
    DataProcessingError,
    FileOperationError
)
```

### `src.common.logger`

Logging configuration and utilities.

```python
from src.common.logger import get_logger

logger = get_logger(__name__)
```

## Package-Level Imports

For convenience, key classes are available at the package level:

### High-Level API

#### `CampaignBridge`

```python
class CampaignBridge:
    def __init__(self, csv_path: str, config: Optional[MixBridgeConfig] = None)
```

**Parameters:**
- `csv_path` (str): Path to the source CSV file
- `config` (MixBridgeConfig, optional): Configuration object

**Methods:**

##### `generate_bridge() -> Dict[str, Any]`

Generates complete bridge analysis.

**Returns:**
- Dictionary with keys:
  - `output_df`: Campaign-level contribution analysis
  - `total_row`: Period totals and summary metrics
  - `summary`: Analysis summary statistics
  - `validation_passed`: Boolean validation result
  - `validator`: Validator instance with detailed results

**Example:**
```python
bridge = CampaignBridge('data.csv')
result = bridge.generate_bridge()
campaigns_df = result['output_df']
```

##### `get_bridge_summary() -> Dict[str, Any]`

Returns summary statistics for the bridge analysis.

**Returns:**
- Dictionary with analysis metadata and statistics

## Data Processing

### data_processor

Optimized data loading and processing operations.

#### `OptimizedDataProcessor`

```python
class OptimizedDataProcessor:
    def __init__(self, csv_path: Union[str, Path], chunk_size: int = 10000)
```

**Methods:**

##### `load_data(use_chunking: bool = None) -> Tuple[pd.DataFrame, pd.DataFrame]`

Load and filter CSV data with performance optimizations.

**Parameters:**
- `use_chunking` (bool, optional): Force chunked reading. Auto-detects if None.

**Returns:**
- Tuple of (january_data, february_data)

##### `aggregate_period_data(period_df: pd.DataFrame) -> pd.DataFrame`

Aggregate campaign data for a period with vectorized operations.

**Parameters:**
- `period_df`: Period-filtered DataFrame

**Returns:**
- Aggregated DataFrame with calculated metrics

##### `get_processing_stats() -> Dict`

Get processing statistics and metadata.

**Returns:**
- Dictionary with file statistics and memory usage

#### `DataProcessor` (Legacy)

Backward-compatible alias for `OptimizedDataProcessor`.

## Validation

### mixbridge_validator

Comprehensive validation framework for bridge calculations.

#### `MixBridgeValidator`

```python
class MixBridgeValidator:
    def __init__(self, config: Optional[MixBridgeConfig] = None)
```

**Methods:**

##### `validate_contributions(output_df: pd.DataFrame, total_row: pd.DataFrame) -> bool`

Comprehensive validation of contribution calculations.

**Parameters:**
- `output_df`: Campaign data with contributions
- `total_row`: Totals row dataframe

**Returns:**
- True if all validations pass, False otherwise

##### `validate_required_columns(df: pd.DataFrame, required_columns: List[str], dataset_name: str = "dataset") -> None`

Validate that required columns exist in DataFrame.

**Raises:**
- `ValidationError`: If required columns are missing

##### `validate_numeric_columns(df: pd.DataFrame, numeric_columns: List[str], dataset_name: str = "dataset") -> None`

Validate that specified columns contain numeric data.

##### `validate_date_column(df: pd.DataFrame, date_column: str, dataset_name: str = "dataset") -> None`

Validate date column format and values.

##### `validate_metric_calculations(df: pd.DataFrame, tolerance: float = 0.0001) -> None`

Validate calculated metrics match expected values.

##### `validate_non_negative_values(df: pd.DataFrame, columns: List[str], dataset_name: str = "dataset") -> None`

Validate that specified columns contain non-negative values.

##### `validate_percentage_bounds(df: pd.DataFrame, percentage_columns: List[str], dataset_name: str = "dataset") -> None`

Validate that percentage columns are within 0-100 bounds.

##### `detect_outliers(df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.Series`

Detect outliers using z-score method.

**Parameters:**
- `df`: DataFrame containing the data
- `column`: Column to check for outliers
- `threshold`: Z-score threshold for outlier detection

**Returns:**
- Series of outlier values

##### `get_validation_report() -> Dict[str, Any]`

Generate comprehensive validation report.

**Returns:**
- Dictionary with validation results and summary

##### `print_validation_report() -> None`

Print formatted validation report to console.

#### `ValidationResult`

```python
@dataclass
class ValidationResult:
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = 'info'  # 'info', 'warning', 'error'
```

## Configuration

### mixbridge_config

Configuration management for bridge calculations.

#### `MixBridgeConfig`

```python
class MixBridgeConfig:
    def __init__(
        self,
        zero_baseline_strategy: str = 'delta_assignment',
        precision_decimals: int = 4,
        validation_tolerance: float = 0.01,
        debug_mode: bool = False,
        enable_caching: bool = True,
        chunk_size: int = 10000
    )
```

**Parameters:**
- `zero_baseline_strategy`: Strategy for zero baseline handling ('dummy_value', 'delta_assignment', 'hybrid')
- `precision_decimals`: Number of decimal places for calculations
- `validation_tolerance`: Tolerance for validation checks (as percentage)
- `debug_mode`: Enable debug logging and detailed output
- `enable_caching`: Enable caching of intermediate results
- `chunk_size`: Chunk size for large file processing

**Methods:**

##### `get_profile(profile_name: str) -> 'MixBridgeConfig'`

Get predefined configuration profile.

**Parameters:**
- `profile_name`: Profile name ('fast', 'accurate', 'debug')

**Returns:**
- Configuration instance with profile settings

##### `validate() -> bool`

Validate configuration parameters.

##### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

##### `from_dict(data: Dict[str, Any]) -> 'MixBridgeConfig'`

Create configuration from dictionary.

#### Configuration Functions

##### `get_config() -> MixBridgeConfig`

Get the global configuration instance.

##### `set_config(config: MixBridgeConfig) -> None`

Set the global configuration instance.

##### `reset_config() -> None`

Reset configuration to defaults.

## Utilities

### metric_definitions

Centralized metric definitions and category management.

#### `MetricDefinitions`

```python
class MetricDefinitions:
```

**Static Methods:**

##### `get_absolute_metrics() -> List[str]`

Get list of absolute (summable) metrics.

##### `get_rate_metrics() -> List[str]`

Get list of rate/ratio metrics.

##### `get_all_metrics() -> List[str]`

Get complete list of all metrics.

##### `get_percentage_metrics() -> List[str]`

Get list of metrics expressed as percentages.

##### `is_absolute_metric(metric: str) -> bool`

Check if a metric is an absolute (summable) metric.

##### `is_rate_metric(metric: str) -> bool`

Check if a metric is a rate/ratio metric.

##### `get_metric_category(metric: str) -> str`

Get the category of a metric ('absolute', 'rate', 'unknown').

##### `validate_metric(metric: str) -> bool`

Validate that a metric is recognized.

##### `get_metric_display_unit(metric: str) -> str`

Get the display unit for a metric.

### calculation_utils

Shared calculation utilities for mathematical operations.

#### Functions

##### `safe_divide(numerator, denominator, fill_value: float = 0.0, handle_inf: bool = True)`

Perform safe division with zero and infinity handling.

**Parameters:**
- `numerator`: Numerator values
- `denominator`: Denominator values  
- `fill_value`: Value to use when denominator is zero
- `handle_inf`: Whether to replace infinite values with fill_value

**Returns:**
- Division result with safe handling of edge cases

##### `calculate_percentage_change(baseline, actual, handle_zero_baseline: str = 'zero')`

Calculate percentage change with zero baseline handling.

**Parameters:**
- `baseline`: Baseline values
- `actual`: Actual values
- `handle_zero_baseline`: How to handle zero baseline ('zero', 'skip', 'error')

**Returns:**
- Percentage change values

##### `calculate_contribution_bps(campaign_baseline, campaign_actual, total_baseline, strategy: str = 'standard')`

Calculate contribution in basis points.

**Parameters:**
- `campaign_baseline`: Campaign baseline values
- `campaign_actual`: Campaign actual values
- `total_baseline`: Total baseline value
- `strategy`: Calculation strategy ('standard', 'zero_safe')

**Returns:**
- Contribution values in basis points

##### `calculate_rate_metric(numerator, denominator, as_percentage: bool = True, precision: int = 4)`

Calculate rate metrics (CTR, CVR, etc.) with proper formatting.

##### `validate_calculation_inputs(baseline, actual, allow_negative: bool = True, check_consistency: bool = True) -> Tuple[bool, str]`

Validate inputs for calculations.

**Returns:**
- Tuple of (is_valid, error_message)

##### `format_metric_value(value, metric_name: str, precision: int = 2) -> str`

Format metric value for display based on metric type.

##### `detect_calculation_anomalies(values: pd.Series, metric_name: str, threshold_multiplier: float = 3.0) -> pd.Series`

Detect anomalous values in calculations.

### logger

Centralized logging configuration.

#### Functions

##### `setup_logger(name: str = "mixbridge", level: int = logging.INFO, log_file: Optional[Path] = None, console_output: bool = True) -> logging.Logger`

Set up a logger with consistent formatting.

##### `get_logger(name: str) -> logging.Logger`

Get a child logger with the given name.

## Exceptions

### exceptions

Custom exception hierarchy for the MixBridge system.

#### Exception Classes

##### `MixBridgeError(Exception)`

Base exception for all MixBridge errors.

##### `ValidationError(MixBridgeError)`

Raised when data validation fails.

##### `ConfigurationError(MixBridgeError)`

Raised when configuration is invalid or missing.

##### `CalculationError(MixBridgeError)`

Raised when calculations fail or produce invalid results.

##### `DataProcessingError(MixBridgeError)`

Raised when data processing operations fail.

##### `FileOperationError(MixBridgeError)`

Raised when file read/write operations fail.

##### `InvalidMetricError(MixBridgeError)`

Raised when an invalid metric is requested.

##### `InsufficientDataError(MixBridgeError)`

Raised when there's not enough data to perform calculations.

## Constants

### constants

System-wide constants and configuration values.

#### Key Constants

- `BASIS_POINTS_MULTIPLIER = 10000`: Multiplier for basis point calculations
- `DEFAULT_DECIMAL_PLACES = 4`: Default decimal precision
- `ZERO_TOLERANCE = 1e-10`: Tolerance for zero comparisons
- `PERCENTAGE_TOLERANCE = 0.0001`: Tolerance for percentage comparisons
- `CHUNK_SIZE = 10000`: Default chunk size for large file processing
- `VOLUME_METRICS`: List of volume-based metrics
- `RATE_METRICS`: List of rate-based metrics
- `COST_METRICS`: List of cost-based metrics
- `ALL_METRICS`: Combined list of all metrics

## Usage Examples

### Basic Usage

```python
# Package-level imports for convenience
from src import CampaignBridge, MixBridgeConfig

# Or direct module import
from src.core.campaign_bridge_modular import CampaignBridge
from src.config.settings import MixBridgeConfig

# Create configuration
config = MixBridgeConfig(precision_decimals=4)

# Generate bridge
bridge = CampaignBridge('data.csv', config=config)
result = bridge.generate_bridge()

# Access results
campaigns = result['output_df']
totals = result['total_row']
```

### Advanced Validation

```python
from src import MixBridgeValidator
# Or: from src.data.validator import MixBridgeValidator

# Create validator
validator = MixBridgeValidator(config)

# Validate data
validator.validate_required_columns(df, ['CampaignName', 'Cost'])
validator.validate_numeric_columns(df, ['Cost', 'Sales'])

# Check contributions
is_valid = validator.validate_contributions(output_df, total_row)
report = validator.get_validation_report()
```

### Custom Processing

```python
from src import OptimizedDataProcessor, safe_divide, calculate_rate_metric
# Or: from src.data.processor import OptimizedDataProcessor
# Or: from src.data.utils import safe_divide, calculate_rate_metric

# Load and process data
processor = OptimizedDataProcessor()
data = processor.load_campaign_data('large_file.csv')

# Custom calculations
safe_ratio = safe_divide(numerator, denominator, fill_value=0.0)
rate_value = calculate_rate_metric(numerator, denominator, rate_type='percentage')
```