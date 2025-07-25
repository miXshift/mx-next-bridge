# Bridge Calculator Guide

## Overview

The bridge calculator uses three specialized bridge types for different metric categories, with configuration-driven KPI assignments.

## Bridge Types

### 1. Mix Bridge
**For**: Absolute/summable metrics (Spend, Sales, Units, Impressions, Clicks)  
**Formula**: `Contribution = P1 Mix × Growth Rate × Total P1 Value`

```python
"Spend": BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,
    contribution_unit=ContributionUnit.CURRENCY
)
```

### 2. MixRate Bridge  
**For**: Rate metrics (ROAS, CTR, CPC, Conversion Rate)  
**Formula**: Mix Impact + Rate Impact calculation

```python
"ROAS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.CURRENCY
)
```

### 3. MixRate Infinity
**For**: Metrics prone to infinity errors (ACoS)  
**Method**: Calculate via inverse metric, transform back

```python
"ACoS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_INFINITY,
    mix_determinant="Spend",
    inverse_metric="ROAS",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)
```

## Usage

### Basic Usage
```python
from src.core.orchestrator import BridgeOrchestrator

# Initialize and calculate
orchestrator = BridgeOrchestrator(precision=12)
results = orchestrator.calculate_all_metrics(
    campaign_data=df,
    total_row=totals
)

# Apply to output DataFrame
output_df = orchestrator.apply_to_dataframe(
    output_df=output_df,
    total_row=totals
)
```

### Single Metric
```python
# Calculate specific metric
result = orchestrator.calculate_metric(
    campaign_data=df,
    total_row=totals,
    metric="ROAS"
)

contributions = result["contributions"]
metadata = result["metadata"]
```

### Validation
```python
# Validate all contributions
validation = orchestrator.validate_all_contributions(
    output_df=df,
    total_row=totals,
    tolerance=0.01
)
```

## Configuration

### KPI Mappings
All metrics are configured in `src/config/bridge_mappings.py`:

```python
KPI_BRIDGE_MAPPINGS = {
    "Spend": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "ACoS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_INFINITY,
        mix_determinant="Spend",
        inverse_metric="ROAS",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    )
}
```

### Adding New Metrics

1. **Add configuration** to `bridge_mappings.py`:
```python
KPI_BRIDGE_MAPPINGS["New Metric"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.BASIS_POINTS
)
```

2. **Add formula** (if calculated metric):
```python
METRIC_FORMULAS["New Metric"] = MetricFormula(
    numerator="Value1",
    denominator="Value2",
    is_percentage=True
)
```

3. **Ensure data columns exist**:
- `"New Metric - January 2025"`
- `"New Metric - February 2025"`

## Architecture

```
src/
├── models/bridge_types.py          # Core data structures
├── config/bridge_mappings.py       # KPI configurations  
├── core/
│   ├── orchestrator.py            # Central controller
│   └── bridges/
│       ├── base.py                # Abstract base
│       ├── mix_bridge.py          # Traditional bridge
│       ├── mixrate_bridge.py      # Standard rate bridge
│       └── mixrate_infinity.py    # Infinity error bridge
└── tests/test_bridge_refactor.py   # Test suite
```

## Key Features

- **Configuration-Driven**: Easy metric assignment without code changes
- **Type Safety**: Strong typing with dataclasses and enums
- **Validation**: Built-in mathematical consistency checks
- **Metadata**: Complete audit trails for debugging
- **Zero Baseline Handling**: Delta assignment for zero baseline scenarios

## Testing

```bash
# Run bridge calculator tests
python -m pytest src/tests/test_bridge_refactor.py -v
```

## Common Issues

**Contributions don't sum to total**: Check metric configuration and data column names  
**Infinity errors**: Use MIXRATE_INFINITY bridge type  
**Zero baseline issues**: System handles automatically with delta assignment  
**Missing columns**: Ensure P1/P2 columns exist for all configured metrics