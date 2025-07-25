# Migration Guide: Bridge Calculator Refactor

This guide helps transition from the old bridge calculation system to the new modular architecture.

## Key Changes

### 1. Centralized Configuration
- **Old**: Metric definitions scattered across multiple files
- **New**: All metric-to-bridge mappings in `config/bridge_mappings.py`

### 2. Explicit Bridge Types
- **Old**: Implicit logic determining calculation method
- **New**: Three explicit bridge types with clear separation

### 3. Unified Interface
- **Old**: Different methods for different metric types
- **New**: Single orchestrator handles all calculations

## Migration Steps

### Step 1: Update Imports

**Old:**
```python
from src.core.bridge_calculator import BridgeCalculator
from src.core.mixrate_calculator import MixRateBridgeCalculator
```

**New:**
```python
from src.core.orchestrator import BridgeOrchestrator
from src.config.bridge_mappings import get_bridge_configuration
```

### Step 2: Replace Calculator Usage

**Old:**
```python
# Manual calculator selection
calculator = BridgeCalculator()
result = calculator.calculate_bridge(bridge_data)

# Separate rate metric handling
mixrate_calc = MixRateBridgeCalculator()
output_df, total_row = mixrate_calc.calculate_rate_metric_contributions(
    output_df, total_row
)
```

**New:**
```python
# Automatic calculator selection
orchestrator = BridgeOrchestrator()

# Single method for all metrics
output_df = orchestrator.apply_to_dataframe(
    output_df=output_df,
    total_row=total_row,
    metrics=None  # Process all configured metrics
)
```

### Step 3: Update Metric Definitions

**Old:**
```python
# In metric_definitions.py
def get_absolute_metrics():
    return ['Spend', 'Total Ad Sales', ...]

def get_rate_metrics():
    return ['ACoS', 'ROAS', ...]
```

**New:**
```python
# In config/bridge_mappings.py
KPI_BRIDGE_MAPPINGS = {
    "Spend": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "ROAS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Spend",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    # ... more mappings
}
```

### Step 4: Handle Contribution Units

**Old:**
```python
# Manual formatting
if metric in ['ACoS', 'CTR']:
    contribution *= 10000  # Convert to basis points
```

**New:**
```python
# Automatic formatting based on configuration
config = get_bridge_configuration("ACoS")
# config.contribution_unit = ContributionUnit.BASIS_POINTS
# config.requires_percentage_conversion = True
# Formatting handled automatically
```

## New Features

### 1. Metadata Generation
```python
results = orchestrator.calculate_metric(
    campaign_data, total_row, "ROAS"
)
metadata = results['metadata']
# Access calculation details, validation status, etc.
```

### 2. Batch Processing
```python
# Process multiple metrics efficiently
results = orchestrator.calculate_all_metrics(
    campaign_data, total_row,
    metrics=["Spend", "ROAS", "ACoS", "CTR"]
)
```

### 3. Built-in Validation
```python
# Validate all contributions
validation = orchestrator.validate_all_contributions(
    output_df, total_row, tolerance=0.01
)
```

## Adding New Metrics

### Old Process:
1. Update multiple files (metric_definitions.py, calculators, etc.)
2. Add conditional logic for calculation method
3. Handle edge cases manually

### New Process:
1. Add formula (if calculated metric):
```python
METRIC_FORMULAS["New Rate"] = MetricFormula(
    numerator="Value1",
    denominator="Value2",
    is_percentage=True
)
```

2. Add configuration:
```python
KPI_BRIDGE_MAPPINGS["New Rate"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Value2",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)
```

That's it! The orchestrator handles everything else.

## Backward Compatibility

The new system maintains backward compatibility through:
1. Same column naming conventions
2. Same mathematical calculations
3. Compatible output format

To ensure smooth migration:
- Test with sample data first
- Compare outputs with old system
- Use validation features to verify correctness

## Common Issues and Solutions

### Issue: Missing columns in data
**Solution**: Ensure all required columns exist:
- `{Metric} - January 2025`
- `{Metric} - February 2025`
- Mix determinant columns for rate metrics

### Issue: Different contribution values
**Solution**: Check:
- Correct bridge type assigned
- Mix determinant matches old logic
- Contribution unit and conversion settings

### Issue: Validation failures
**Solution**: 
- Increase tolerance if needed
- Check for data quality issues
- Verify total row calculations

## Testing Migration

```python
# Simple test to verify migration
def test_migration():
    # Create test data
    campaign_data, total_row = create_test_data()
    
    # Old method
    old_calculator = BridgeCalculator()
    old_result = old_calculator.calculate_bridge(campaign_data)
    
    # New method
    orchestrator = BridgeOrchestrator()
    new_result = orchestrator.apply_to_dataframe(
        campaign_data.copy(), total_row
    )
    
    # Compare results
    for metric in ["Spend", "ROAS", "ACoS"]:
        old_col = f"{metric} - Contribution"
        assert np.allclose(
            old_result[old_col], 
            new_result[old_col],
            rtol=1e-5
        )
```

## Benefits After Migration

1. **Clearer Code**: Each bridge type in its own module
2. **Easier Maintenance**: Configuration-driven approach
3. **Better Testing**: Isolated components
4. **Enhanced Features**: Metadata, validation, batch processing
5. **Extensibility**: Easy to add new metrics or bridge types