# Bridge Calculator Refactor API Reference

## Core Classes

### BridgeOrchestrator

The main entry point for all bridge calculations.

```python
class BridgeOrchestrator:
    def __init__(self, precision: int = 12)
```

#### Methods

##### `calculate_metric()`
Calculate contributions for a single metric.

```python
def calculate_metric(self,
                   campaign_data: pd.DataFrame,
                   total_row: pd.DataFrame,
                   metric: str,
                   p1_suffix: str = "January 2025",
                   p2_suffix: str = "February 2025") -> Dict[str, Any]
```

**Parameters**:
- `campaign_data`: Campaign-level data DataFrame
- `total_row`: Total row with aggregate values
- `metric`: Metric name (must be in `KPI_BRIDGE_MAPPINGS`)
- `p1_suffix`: Period 1 column suffix
- `p2_suffix`: Period 2 column suffix

**Returns**:
```python
{
    "contributions": np.ndarray,           # Raw contribution values
    "formatted_contributions": List[str],  # Formatted for display
    "metadata": Dict[str, Any]            # Calculation metadata
}
```

##### `calculate_all_metrics()`
Calculate contributions for multiple metrics in batch.

```python
def calculate_all_metrics(self,
                        campaign_data: pd.DataFrame,
                        total_row: pd.DataFrame,
                        metrics: Optional[List[str]] = None,
                        p1_suffix: str = "January 2025",
                        p2_suffix: str = "February 2025") -> Dict[str, Any]
```

**Parameters**:
- `metrics`: List of metrics to calculate (None for all configured metrics)

**Returns**:
```python
{
    "contributions": Dict[str, np.ndarray],  # Contributions by metric
    "metadata": Dict[str, Dict],             # Metadata by metric
    "summary": Dict[str, Any]                # Processing summary
}
```

##### `apply_to_dataframe()`
Apply calculations directly to an output DataFrame.

```python
def apply_to_dataframe(self,
                     output_df: pd.DataFrame,
                     total_row: pd.DataFrame,
                     metrics: Optional[List[str]] = None,
                     p1_suffix: str = "January 2025",
                     p2_suffix: str = "February 2025") -> pd.DataFrame
```

**Parameters**:
- `output_df`: DataFrame to update with contributions

**Returns**: Updated DataFrame with contribution columns populated

##### `validate_all_contributions()`
Validate mathematical consistency of contributions.

```python
def validate_all_contributions(self,
                             output_df: pd.DataFrame,
                             total_row: pd.DataFrame,
                             tolerance: float = 0.01) -> Dict[str, bool]
```

**Returns**: Dictionary mapping metrics to validation results

## Bridge Calculator Classes

### BaseBridgeCalculator

Abstract base class for all bridge calculators.

```python
class BaseBridgeCalculator(ABC):
    def __init__(self, configuration: BridgeConfiguration, precision: int = 12)
```

#### Abstract Methods

##### `calculate_contributions()`
```python
@abstractmethod
def calculate_contributions(self,
                          campaign_data: pd.DataFrame,
                          total_row: pd.DataFrame,
                          metric: str,
                          p1_suffix: str = "January 2025",
                          p2_suffix: str = "February 2025") -> np.ndarray
```

#### Concrete Methods

##### `validate_inputs()`
Validate input data before calculation.

##### `format_contributions()`
Format contribution values according to contribution unit.

##### `calculate_and_validate()`
Calculate contributions with full validation pipeline.

### MixBridgeCalculator

Traditional Mix Bridge implementation for absolute metrics.

```python
class MixBridgeCalculator(BaseBridgeCalculator):
    # Inherits all methods from BaseBridgeCalculator
```

**Formula**: `Contribution = P1 Mix × Growth Rate × Total P1 Value`

**Special Handling**: Zero baseline campaigns use delta assignment

### MixRateBridgeCalculator

Standard MixRate Bridge for rate metrics.

```python
class MixRateBridgeCalculator(BaseBridgeCalculator):
    # Inherits all methods from BaseBridgeCalculator
```

**Formula**:
- `Mix Impact = (P2 Mix - P1 Mix) × (P2 Rate - P2 Total Rate)`
- `Rate Impact = (P2 Rate - P1 Rate) × P1 Mix`

**Requirements**: Must specify `mix_determinant` in configuration

### MixRateInfinityCalculator

MixRate Bridge with infinity error handling.

```python
class MixRateInfinityCalculator(BaseBridgeCalculator):
    # Inherits all methods from BaseBridgeCalculator
```

**Process**:
1. Calculate inverse metric (e.g., ROAS for ACoS)
2. Apply MixRate Bridge to inverse metric
3. Transform contributions back using relative impact methodology

**Requirements**: Must specify `inverse_metric` in configuration

## Configuration Classes

### BridgeConfiguration

Configuration for a specific bridge calculation.

```python
@dataclass
class BridgeConfiguration:
    bridge_type: BridgeType
    mix_determinant: Optional[str] = None
    contribution_unit: ContributionUnit = ContributionUnit.CURRENCY
    inverse_metric: Optional[str] = None
    requires_percentage_conversion: bool = False
```

**Fields**:
- `bridge_type`: Type of bridge calculation to use
- `mix_determinant`: Column used to determine campaign mix (required for rate metrics)
- `contribution_unit`: Unit for displaying contributions
- `inverse_metric`: Inverse metric for infinity error handling
- `requires_percentage_conversion`: Convert to basis points (×10000)

### MetricFormula

Defines calculation formula for derived metrics.

```python
@dataclass
class MetricFormula:
    numerator: str
    denominator: str
    is_percentage: bool = False
    multiplier: float = 1.0
    
    def calculate(self, num_value: float, denom_value: float) -> float
```

## Enums

### BridgeType

```python
class BridgeType(Enum):
    MIX_BRIDGE = auto()           # Traditional Mix Bridge
    MIXRATE_BRIDGE = auto()       # Standard MixRate Bridge
    MIXRATE_INFINITY = auto()     # MixRate with Infinity Error
```

### ContributionUnit

```python
class ContributionUnit(Enum):
    CURRENCY = "$"          # Local currency (e.g., +$0.42)
    BASIS_POINTS = "bps"    # Basis points (×10000)
    PERCENTAGE = "%"        # Percentage points
    COUNT = "count"         # Raw count
    RATIO = "ratio"         # Dimensionless ratio
```

## Configuration Functions

### `get_bridge_configuration()`

```python
def get_bridge_configuration(metric: str) -> BridgeConfiguration
```

Get bridge configuration for a specific metric.

**Raises**: `KeyError` if metric not found

### `get_metrics_by_bridge_type()`

```python
def get_metrics_by_bridge_type(bridge_type: BridgeType) -> List[str]
```

Get all metrics using a specific bridge type.

### `get_metric_formula()`

```python
def get_metric_formula(metric: str) -> Optional[MetricFormula]
```

Get calculation formula for a metric (returns None for base metrics).

### `is_calculated_metric()`

```python
def is_calculated_metric(metric: str) -> bool
```

Check if metric is calculated from other metrics.

## Metadata Structure

### Calculation Metadata

```python
{
    "metric": str,                          # Metric name
    "bridge_type": str,                     # Bridge type used
    "contribution_unit": str,               # Display unit
    "period_1": str,                        # P1 period name
    "period_2": str,                        # P2 period name
    "total_p1_value": float,               # Total P1 value
    "total_p2_value": float,               # Total P2 value
    "total_change": float,                  # Total change
    "total_contributions": float,           # Sum of contributions
    "contribution_count": int,              # Number of campaigns
    "mathematical_consistency": bool,       # Validation result
    "mix_determinant": Optional[str],       # Mix determinant (rate metrics)
    "inverse_metric": Optional[str]         # Inverse metric (infinity handling)
}
```

### Summary Metadata

```python
{
    "total_metrics": int,                   # Total metrics processed
    "successful_calculations": int,         # Successful calculations
    "failed_calculations": int,             # Failed calculations
    "success_rate": float,                  # Success percentage
    "metrics_by_type": Dict[str, List[str]], # Metrics grouped by bridge type
    "consistency_check": Dict[str, str]     # Validation results by metric
}
```

## Error Handling

### Exception Types

- `ValidationError`: Input validation failures
- `CalculationError`: Calculation failures
- `KeyError`: Missing metric configurations

### Error Response Format

```python
{
    "contributions": np.ndarray,        # Zero array
    "formatted_contributions": List[str], # Zero strings
    "metadata": {
        "error": str,                   # Error message
        "metric": str,                  # Metric name
        "bridge_type": str              # Bridge type attempted
    }
}
```

## Usage Examples

### Basic Single Metric

```python
from src.core.orchestrator import BridgeOrchestrator

orchestrator = BridgeOrchestrator()
results = orchestrator.calculate_metric(
    campaign_data=campaigns_df,
    total_row=totals_df,
    metric="ROAS"
)

contributions = results["contributions"]
metadata = results["metadata"]
```

### Batch Processing

```python
metrics = ["Spend", "ROAS", "ACoS", "CTR"]
all_results = orchestrator.calculate_all_metrics(
    campaign_data=campaigns_df,
    total_row=totals_df,
    metrics=metrics
)

summary = all_results["summary"]
success_rate = summary["success_rate"]
```

### DataFrame Integration

```python
# Apply to existing output DataFrame
output_df = orchestrator.apply_to_dataframe(
    output_df=results_df,
    total_row=totals_df,
    metrics=["Spend", "ROAS", "ACoS"]
)

# Validate results
validation = orchestrator.validate_all_contributions(
    output_df=output_df,
    total_row=totals_df,
    tolerance=0.01
)
```

### Custom Configuration

```python
from src.config.bridge_mappings import KPI_BRIDGE_MAPPINGS
from src.models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit

# Add new metric
KPI_BRIDGE_MAPPINGS["Custom Metric"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Custom Base",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)

# Use immediately
results = orchestrator.calculate_metric(
    campaign_data=data,
    total_row=totals,
    metric="Custom Metric"
)
```

## Performance Considerations

### Calculator Caching
- Calculator instances are cached and reused
- Cache key includes bridge type and configuration
- Reduces object creation overhead

### Batch Optimization
- Metrics grouped by bridge type for efficient processing
- Shared validation reduces redundant checks
- Memory-efficient data handling

### Validation Performance
- Optional validation with configurable tolerance
- Early exit on critical errors
- Detailed logging for performance monitoring