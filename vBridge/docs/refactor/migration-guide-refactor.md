# Migration Guide: Bridge Calculator Refactor

## Overview

This guide helps you migrate from the legacy bridge calculation system to the new modular architecture with three distinct bridge types and configuration-driven KPI assignments.

## What Changed

### Before (Legacy System)
- Mixed calculation logic in single files
- Implicit bridge type detection
- Manual metric categorization  
- Scattered configuration across multiple files
- Limited error handling and validation

### After (Refactored System)
- **Three explicit bridge types** with clear separation
- **Configuration-driven approach** for easy metric management
- **Centralized orchestrator** for unified interface
- **Comprehensive validation** and error handling
- **Rich metadata** and audit trails

## Migration Checklist

### ✅ Step 1: Update Imports

**Old Imports:**
```python
from src.core.bridge_calculator import BridgeCalculator
from src.core.mixrate_calculator import MixRateBridgeCalculator
from src.config.metrics import MetricDefinitions
```

**New Imports:**
```python
from src.core.orchestrator import BridgeOrchestrator
from src.config.bridge_mappings import get_bridge_configuration
from src.models.bridge_types import BridgeType, ContributionUnit
```

### ✅ Step 2: Replace Calculator Usage

**Old Pattern:**
```python
# Manual calculator selection and management
calculator = BridgeCalculator()
result_df = calculator.calculate_bridge(bridge_data)

# Separate rate metric handling
mixrate_calc = MixRateBridgeCalculator()
output_df, total_row = mixrate_calc.calculate_rate_metric_contributions(
    output_df, total_row
)

# Manual contribution summing
total_row = calculator.sum_contributions_to_total(output_df, total_row)
```

**New Pattern:**
```python
# Unified orchestrator handles everything
orchestrator = BridgeOrchestrator()

# Single method for all calculations
result_df = orchestrator.apply_to_dataframe(
    output_df=output_df,
    total_row=total_row
    # Automatically processes all configured metrics
)
```

### ✅ Step 3: Update Metric Definitions

**Old System:**
```python
# Scattered across multiple files
def get_absolute_metrics():
    return ['Spend', 'Total Ad Sales', 'Impressions', ...]

def get_rate_metrics():
    return ['ACoS', 'ROAS', 'CTR', ...]

def get_mixrate_infinity_metrics():
    return ['ACoS']

# Manual logic to determine calculation method
if metric in get_absolute_metrics():
    # Traditional mix bridge
elif metric in get_mixrate_infinity_metrics():
    # Special infinity handling
else:
    # Standard mixrate
```

**New System:**
```python
# Centralized configuration in bridge_mappings.py
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
    "ACoS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_INFINITY,
        mix_determinant="Spend",
        inverse_metric="ROAS",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    )
}

# Automatic bridge type selection
config = get_bridge_configuration("ACoS")
# config.bridge_type = BridgeType.MIXRATE_INFINITY
```

### ✅ Step 4: Update Method Calls

**Old Methods:**
```python
# Multiple separate method calls
output_df, columns = BridgeCalculator.create_output_dataframe(bridge_data)
output_df = BridgeCalculator.calculate_period_values(output_df, bridge_data)
total_row = BridgeCalculator.create_total_row(output_df, columns)
total_row = BridgeCalculator.calculate_rate_metrics_totals(total_row)
output_df = BridgeCalculator.calculate_contributions(output_df, total_row)
output_df, total_row = BridgeCalculator.calculate_rate_metric_contributions(output_df, total_row)
total_row = BridgeCalculator.sum_contributions_to_total(output_df, total_row)
```

**New Methods:**
```python
# Single orchestrator call handles entire pipeline
orchestrator = BridgeOrchestrator()

# Option 1: Apply to existing DataFrame
updated_df = orchestrator.apply_to_dataframe(output_df, total_row)

# Option 2: Calculate specific metrics
results = orchestrator.calculate_all_metrics(campaign_data, total_row)

# Option 3: Single metric calculation
metric_result = orchestrator.calculate_metric(campaign_data, total_row, "ROAS")
```

## Feature Comparison

| Feature | Legacy System | Refactored System |
|---------|---------------|-------------------|
| **Bridge Types** | Implicit detection | 3 explicit types |
| **Configuration** | Scattered across files | Centralized mapping |
| **Error Handling** | Basic | Comprehensive with recovery |
| **Validation** | Manual checks | Built-in consistency validation |
| **Metadata** | Limited | Rich calculation details |
| **Testing** | Partial coverage | 15 comprehensive test cases |
| **Extensibility** | Requires code changes | Configuration-driven |

## Code Migration Examples

### Example 1: Basic Bridge Calculation

**Before:**
```python
from src.core.bridge_calculator import BridgeCalculator

# Legacy approach
calculator = BridgeCalculator()
result_df = calculator.calculate_bridge(bridge_data, validate=True)

# Save results
latest_path, timestamped_path, previous_path = calculator.save_bridge_analysis(
    result_df, 
    periods={'p1': 'jan2025', 'p2': 'feb2025'}
)
```

**After:**
```python
from src.core.orchestrator import BridgeOrchestrator

# New approach
orchestrator = BridgeOrchestrator()

# Apply calculations to existing output structure
result_df = orchestrator.apply_to_dataframe(
    output_df=existing_output_df,
    total_row=total_row
)

# Built-in validation
validation_results = orchestrator.validate_all_contributions(
    result_df, total_row, tolerance=0.01
)

# Use existing save mechanism
latest_path, timestamped_path, previous_path = BridgeCalculator.save_bridge_analysis(
    result_df, 
    periods={'p1': 'jan2025', 'p2': 'feb2025'}
)
```

### Example 2: Rate Metric Handling

**Before:**
```python
from src.core.mixrate_calculator import MixRateBridgeCalculator

# Separate rate metric processing
mixrate_calc = MixRateBridgeCalculator()
output_df = mixrate_calc.calculate_all_rate_metric_contributions(output_df, total_row)

# Manual ACoS handling
if 'ACoS - January 2025' in output_df.columns:
    output_df = mixrate_calc._calculate_acos_via_roas_inverse(output_df, total_row)
```

**After:**
```python
from src.core.orchestrator import BridgeOrchestrator

# Unified processing - handles all rate metrics automatically
orchestrator = BridgeOrchestrator()
output_df = orchestrator.apply_to_dataframe(output_df, total_row)

# Automatic ACoS handling via configuration
# No special code needed - handled by MixRateInfinityCalculator
```

### Example 3: Adding New Metrics

**Before:**
```python
# Required changes to multiple files
# 1. Update metric_definitions.py
def get_all_metrics():
    return [..., 'New Metric']

# 2. Update bridge_calculator.py  
def calculate_period_values(self, output_df, bridge_data):
    # Add special handling for new metric
    if metric == 'New Metric':
        # Custom calculation logic
        
# 3. Update validation logic
# 4. Update formatting logic
# 5. Update saving logic
```

**After:**
```python
# Single configuration addition
from src.config.bridge_mappings import KPI_BRIDGE_MAPPINGS
from src.models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit

# Add new metric configuration
KPI_BRIDGE_MAPPINGS["New Metric"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Base Column",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)

# Use immediately - no other changes needed
orchestrator = BridgeOrchestrator()
results = orchestrator.calculate_metric(data, totals, "New Metric")
```

## Validation Migration

### Old Validation Approach
```python
# Manual validation checks
try:
    from mixbridge_validator import ContributionValidator
    validator = ContributionValidator()
    is_valid = validator.validate_contributions(output_df, total_row)
    if not is_valid:
        print("⚠️  Warning: Validation failed")
except ImportError:
    print("ℹ️  Validation module not available")
```

### New Validation Approach
```python
# Built-in validation with detailed results
orchestrator = BridgeOrchestrator()

# Comprehensive validation
validation_results = orchestrator.validate_all_contributions(
    output_df, total_row, tolerance=0.01
)

# Check specific metrics
failed_metrics = [metric for metric, valid in validation_results.items() if not valid]
if failed_metrics:
    print(f"⚠️  Validation failed for: {', '.join(failed_metrics)}")

# Get detailed metadata for debugging
results = orchestrator.calculate_all_metrics(campaign_data, total_row)
summary = results['summary']
print(f"Success rate: {summary['success_rate']:.1f}%")
```

## Testing Migration

### Legacy Testing
```python
# Manual testing
def test_bridge_calculation():
    calculator = BridgeCalculator()
    result = calculator.calculate_bridge(test_data)
    
    # Basic assertions
    assert len(result) > 0
    assert 'Spend - Contribution' in result.columns
```

### New Testing
```python
# Comprehensive test suite available
# Run: python src/tests/test_bridge_refactor.py

# Custom testing
def test_new_bridge_system():
    orchestrator = BridgeOrchestrator()
    
    # Test single metric
    results = orchestrator.calculate_metric(test_data, totals, "ROAS")
    assert "contributions" in results
    assert "metadata" in results
    assert results["metadata"]["mathematical_consistency"]
    
    # Test batch processing
    all_results = orchestrator.calculate_all_metrics(test_data, totals)
    assert all_results["summary"]["success_rate"] == 100.0
    
    # Test validation
    validation = orchestrator.validate_all_contributions(output_df, totals)
    assert all(validation.values())
```

## Common Migration Issues

### Issue 1: Missing Configuration
**Problem**: `KeyError: No bridge configuration found for metric: CustomMetric`

**Solution**: Add metric to bridge mappings
```python
KPI_BRIDGE_MAPPINGS["CustomMetric"] = BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,  # Choose appropriate type
    contribution_unit=ContributionUnit.CURRENCY
)
```

### Issue 2: Different Contribution Values
**Problem**: Contributions differ from legacy system

**Solution**: Verify configuration matches legacy logic
```python
# Check bridge type assignment
config = get_bridge_configuration("YourMetric")
print(f"Bridge type: {config.bridge_type}")
print(f"Mix determinant: {config.mix_determinant}")

# For rate metrics, ensure correct mix determinant
# ROAS should use "Spend", CTR should use "Impressions", etc.
```

### Issue 3: Validation Failures
**Problem**: Mathematical consistency checks fail

**Solution**: Check tolerance and data quality
```python
# Increase tolerance if needed
validation = orchestrator.validate_all_contributions(
    output_df, total_row, tolerance=0.1  # Increased from 0.01
)

# Debug with metadata
results = orchestrator.calculate_metric(data, totals, "ProblematicMetric")
metadata = results['metadata']
print(f"Total change: {metadata['total_change']}")
print(f"Total contributions: {metadata['total_contributions']}")
print(f"Difference: {abs(metadata['total_change'] - metadata['total_contributions'])}")
```

## Performance Considerations

### Legacy Performance
- Multiple separate calculations
- Repeated validation checks
- No calculator reuse
- Manual error handling

### New Performance
- **Calculator Caching**: Reuse calculator instances
- **Batch Processing**: Group similar metrics
- **Early Validation**: Catch issues before calculation
- **Parallel-Ready**: Architecture supports future parallelization

### Migration Performance Tips
```python
# Reuse orchestrator instance
orchestrator = BridgeOrchestrator()

# Process metrics in batches
all_results = orchestrator.calculate_all_metrics(data, totals)

# Rather than individual calls
# for metric in metrics:
#     orchestrator.calculate_metric(data, totals, metric)  # Slower
```

## Rollback Strategy

If you need to rollback to the legacy system:

1. **Keep Legacy Code**: Don't delete legacy files until migration is complete
2. **Gradual Migration**: Migrate metric by metric rather than all at once
3. **Validation Comparison**: Run both systems in parallel during transition
4. **Feature Flags**: Use configuration to switch between systems

```python
# Transition approach
USE_LEGACY_BRIDGE = False  # Feature flag

if USE_LEGACY_BRIDGE:
    # Legacy calculation
    calculator = BridgeCalculator()
    result = calculator.calculate_bridge(data)
else:
    # New calculation
    orchestrator = BridgeOrchestrator()
    result = orchestrator.apply_to_dataframe(output_df, total_row)
```

## Support and Troubleshooting

### Getting Help
1. **Run Tests**: `python src/tests/test_bridge_refactor.py`
2. **Check Examples**: `python src/examples/bridge_example.py`
3. **Enable Debug Logging**: Set log level to DEBUG
4. **Review Metadata**: Use calculation metadata for troubleshooting

### Debug Checklist
- [ ] All required columns present in data
- [ ] Metric configured in `bridge_mappings.py`
- [ ] Correct bridge type assigned
- [ ] Mix determinant specified for rate metrics
- [ ] Inverse metric defined for infinity-prone metrics
- [ ] Contribution units appropriate for metric type
- [ ] Data quality issues resolved

## Next Steps

After migration:

1. **Remove Legacy Code**: Clean up unused legacy bridge calculation code
2. **Update Documentation**: Update any documentation referencing old system
3. **Add New Metrics**: Take advantage of easy metric addition
4. **Enhance Validation**: Implement additional validation rules as needed
5. **Monitor Performance**: Track calculation performance and optimize as needed

The new system provides a solid foundation for future enhancements while maintaining backward compatibility and improving maintainability.