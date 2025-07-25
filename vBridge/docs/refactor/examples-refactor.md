# Bridge Calculator Refactor Examples

## Quick Start Examples

### Basic Usage

```python
from src.core.orchestrator import BridgeOrchestrator
import pandas as pd

# Initialize orchestrator
orchestrator = BridgeOrchestrator(precision=12)

# Your campaign data
campaign_data = pd.DataFrame({
    'Campaign': ['Campaign A', 'Campaign B', 'Campaign C'],
    'Spend - January 2025': [1000, 2000, 1500],
    'Spend - February 2025': [1200, 1800, 2000],
    'Total Ad Sales - January 2025': [5000, 8000, 4500],
    'Total Ad Sales - February 2025': [6000, 7500, 6000],
    # ... other metrics
})

# Total row
total_row = pd.DataFrame([{
    'Campaign': 'Total',
    'Spend - January 2025': 4500,
    'Spend - February 2025': 5000,
    'Total Ad Sales - January 2025': 17500,
    'Total Ad Sales - February 2025': 19500,
    # ... other metrics
}])

# Calculate single metric
results = orchestrator.calculate_metric(
    campaign_data=campaign_data,
    total_row=total_row,  
    metric="Spend"
)

print("Contributions:", results["contributions"])
print("Formatted:", results["formatted_contributions"])
print("Metadata:", results["metadata"])
```

### Batch Processing All Metrics

```python
# Calculate all configured metrics at once
all_results = orchestrator.calculate_all_metrics(
    campaign_data=campaign_data,
    total_row=total_row
)

# Access results
contributions_by_metric = all_results["contributions"]
metadata_by_metric = all_results["metadata"]
summary = all_results["summary"]

print(f"Success rate: {summary['success_rate']:.1f}%")
print(f"Processed {summary['total_metrics']} metrics")

# Check individual metrics
spend_contributions = contributions_by_metric["Spend"]
roas_metadata = metadata_by_metric["ROAS"]
```

### DataFrame Integration

```python
# Create output DataFrame structure
output_df = campaign_data.copy()

# Add contribution columns
for metric in ["Spend", "ROAS", "ACoS", "CTR"]:
    output_df[f"{metric} - Contribution"] = 0.0

# Apply all calculations
output_df = orchestrator.apply_to_dataframe(
    output_df=output_df,
    total_row=total_row,
    metrics=["Spend", "ROAS", "ACoS", "CTR"]  # Optional: specify metrics
)

# Contributions are now populated
print(output_df[["Campaign", "Spend - Contribution", "ROAS - Contribution"]])
```

## Bridge Type Examples

### Type 1: Mix Bridge (Traditional)

```python
from src.config.bridge_mappings import get_bridge_configuration

# Example: Spend metric (absolute/summable)
config = get_bridge_configuration("Spend")
print(f"Bridge type: {config.bridge_type}")  # BridgeType.MIX_BRIDGE
print(f"Unit: {config.contribution_unit}")   # ContributionUnit.CURRENCY

# Calculate
results = orchestrator.calculate_metric(campaign_data, total_row, "Spend")

# Results show dollar contributions
# Campaign A: +$200.00
# Campaign B: -$200.00  
# Campaign C: +$500.00
```

### Type 2: MixRate Bridge (Standard)

```python
# Example: ROAS metric (rate without infinity risk)
config = get_bridge_configuration("ROAS")
print(f"Bridge type: {config.bridge_type}")      # BridgeType.MIXRATE_BRIDGE
print(f"Mix determinant: {config.mix_determinant}")  # "Spend"
print(f"Unit: {config.contribution_unit}")       # ContributionUnit.CURRENCY

# Calculate
results = orchestrator.calculate_metric(campaign_data, total_row, "ROAS")

# Results show currency contributions to ROAS change
# Campaign A: +$0.02
# Campaign B: +$0.05
# Campaign C: -$0.06
```

### Type 3: MixRate Bridge with Infinity Error Handling

```python
# Example: ACoS metric (prone to infinity errors)
config = get_bridge_configuration("ACoS")
print(f"Bridge type: {config.bridge_type}")      # BridgeType.MIXRATE_INFINITY  
print(f"Mix determinant: {config.mix_determinant}")  # "Spend"
print(f"Inverse metric: {config.inverse_metric}")    # "ROAS"
print(f"Unit: {config.contribution_unit}")       # ContributionUnit.BASIS_POINTS

# Calculate
results = orchestrator.calculate_metric(campaign_data, total_row, "ACoS")

# Results show basis point contributions to ACoS change
# Campaign A: -13 bps
# Campaign B: -34 bps  
# Campaign C: +40 bps
```

## Advanced Examples

### Custom Metric Configuration

```python
from src.config.bridge_mappings import KPI_BRIDGE_MAPPINGS, METRIC_FORMULAS
from src.models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit, MetricFormula

# Add custom calculated metric
METRIC_FORMULAS["CPA"] = MetricFormula(
    numerator="Spend",
    denominator="Total Ad Orders",
    is_percentage=False
)

# Configure bridge calculation
KPI_BRIDGE_MAPPINGS["CPA"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Total Ad Orders",
    contribution_unit=ContributionUnit.CURRENCY
)

# Use immediately
results = orchestrator.calculate_metric(campaign_data, total_row, "CPA")
```

### Error Handling

```python
# Handle missing metrics gracefully
try:
    results = orchestrator.calculate_metric(
        campaign_data, total_row, "NonexistentMetric"
    )
except KeyError as e:
    print(f"Metric not configured: {e}")

# Check for calculation errors
results = orchestrator.calculate_all_metrics(campaign_data, total_row)
failed_metrics = []

for metric, metadata in results["metadata"].items():
    if "error" in metadata:
        failed_metrics.append(metric)
        print(f"Error in {metric}: {metadata['error']}")

print(f"Failed metrics: {failed_metrics}")
```

### Validation and Quality Checks

```python
# Comprehensive validation
validation_results = orchestrator.validate_all_contributions(
    output_df=output_df,
    total_row=total_row,
    tolerance=0.01
)

# Check results
passed = [k for k, v in validation_results.items() if v]
failed = [k for k, v in validation_results.items() if not v]

print(f"✅ Passed: {len(passed)} metrics")
print(f"❌ Failed: {len(failed)} metrics")

if failed:
    print(f"Failed metrics: {', '.join(failed)}")

# Detailed metadata for debugging
for metric in failed:
    results = orchestrator.calculate_metric(campaign_data, total_row, metric)
    metadata = results["metadata"]
    print(f"\n{metric} Debug Info:")
    print(f"  Total change: {metadata['total_change']:.4f}")
    print(f"  Total contributions: {metadata['total_contributions']:.4f}")
    print(f"  Mathematical consistency: {metadata['mathematical_consistency']}")
```

### Performance Monitoring

```python
import time

# Time batch processing
start_time = time.time()
all_results = orchestrator.calculate_all_metrics(campaign_data, total_row)
elapsed = time.time() - start_time

summary = all_results["summary"]
print(f"Processed {summary['total_metrics']} metrics in {elapsed:.3f}s")
print(f"Average: {elapsed/summary['total_metrics']*1000:.1f}ms per metric")

# Monitor calculation success
print(f"Success rate: {summary['success_rate']:.1f}%")
print(f"Consistent results: {len([m for m, s in summary['consistency_check'].items() if s == 'PASS'])}")
```

## Integration Examples

### With Existing Bridge Calculator

```python
# Hybrid approach during migration
from src.core.bridge_calculator import BridgeCalculator

# Use legacy for data preparation
legacy_calculator = BridgeCalculator()
output_df, columns = legacy_calculator.create_output_dataframe(bridge_data)
output_df = legacy_calculator.calculate_period_values(output_df, bridge_data)
total_row = legacy_calculator.create_total_row(output_df, columns)

# Use new system for contribution calculations
orchestrator = BridgeOrchestrator()
output_df = orchestrator.apply_to_dataframe(output_df, total_row)

# Use legacy for saving
legacy_calculator.save_bridge_analysis(
    pd.concat([total_row, output_df], ignore_index=True),
    periods={'p1': 'jan2025', 'p2': 'feb2025'}
)
```

### With Campaign Bridge

```python
from src.core.campaign_bridge import main as campaign_bridge_main

# Replace the contribution calculation part
def enhanced_campaign_bridge():
    # ... existing campaign bridge setup ...
    
    # Replace legacy bridge calculation
    # OLD: result_df = calculator.calculate_bridge(bridge_data)
    
    # NEW: Use orchestrator
    orchestrator = BridgeOrchestrator()
    result_df = orchestrator.apply_to_dataframe(output_df, total_row)
    
    # ... rest of campaign bridge logic ...
    
    return result_df

# Run enhanced campaign bridge
result = enhanced_campaign_bridge()
```

### Custom Validation Rules

```python
class CustomBridgeOrchestrator(BridgeOrchestrator):
    """Extended orchestrator with custom validation."""
    
    def validate_business_rules(self, output_df, total_row):
        """Custom business rule validation."""
        validation_results = {}
        
        # Rule 1: ROAS contributions should be reasonable
        if "ROAS - Contribution" in output_df.columns:
            roas_contribs = output_df["ROAS - Contribution"].abs()
            max_reasonable = 1.0  # $1.00 max contribution
            validation_results["ROAS_reasonable"] = roas_contribs.max() <= max_reasonable
        
        # Rule 2: Spend contributions should sum to total spend change
        if "Spend - Contribution" in output_df.columns:
            campaign_sum = output_df["Spend - Contribution"].sum()
            total_change = (
                total_row["Spend - February 2025"].iloc[0] - 
                total_row["Spend - January 2025"].iloc[0]
            )
            validation_results["Spend_consistency"] = abs(campaign_sum - total_change) < 0.01
        
        return validation_results

# Use custom orchestrator
custom_orchestrator = CustomBridgeOrchestrator()
output_df = custom_orchestrator.apply_to_dataframe(output_df, total_row)

# Run custom validation
business_validation = custom_orchestrator.validate_business_rules(output_df, total_row)
print("Business rule validation:", business_validation)
```

## Testing Examples

### Unit Testing Your Integration

```python
import unittest
import numpy as np

class TestBridgeIntegration(unittest.TestCase):
    
    def setUp(self):
        self.orchestrator = BridgeOrchestrator()
        self.sample_data = self.create_sample_data()
        self.total_row = self.create_total_row()
    
    def create_sample_data(self):
        return pd.DataFrame({
            'Campaign': ['A', 'B'],
            'Spend - January 2025': [1000, 2000],
            'Spend - February 2025': [1200, 1800],
            'Total Ad Sales - January 2025': [5000, 8000],
            'Total Ad Sales - February 2025': [6000, 7200],
        })
    
    def create_total_row(self):
        return pd.DataFrame([{
            'Campaign': 'Total',
            'Spend - January 2025': 3000,
            'Spend - February 2025': 3000,
            'Total Ad Sales - January 2025': 13000,
            'Total Ad Sales - February 2025': 13200,
        }])
    
    def test_spend_calculation(self):
        """Test Mix Bridge calculation for Spend."""
        results = self.orchestrator.calculate_metric(
            self.sample_data, self.total_row, "Spend"
        )
        
        contributions = results["contributions"]
        metadata = results["metadata"]
        
        # Mathematical consistency
        self.assertTrue(metadata["mathematical_consistency"])
        
        # Sum equals total change
        expected_change = 3000 - 3000  # 0
        self.assertAlmostEqual(contributions.sum(), expected_change, places=2)
    
    def test_roas_calculation(self):
        """Test MixRate Bridge calculation for ROAS."""
        # Add ROAS columns
        self.sample_data['ROAS - January 2025'] = (
            self.sample_data['Total Ad Sales - January 2025'] / 
            self.sample_data['Spend - January 2025']
        )
        self.sample_data['ROAS - February 2025'] = (
            self.sample_data['Total Ad Sales - February 2025'] / 
            self.sample_data['Spend - February 2025']
        )
        
        self.total_row['ROAS - January 2025'] = 13000 / 3000
        self.total_row['ROAS - February 2025'] = 13200 / 3000
        
        results = self.orchestrator.calculate_metric(
            self.sample_data, self.total_row, "ROAS"
        )
        
        # Should not have NaN or infinite values
        contributions = results["contributions"]
        self.assertFalse(np.any(np.isnan(contributions)))
        self.assertFalse(np.any(np.isinf(contributions)))
    
    def test_batch_processing(self):
        """Test batch processing multiple metrics."""
        # Add required columns for rate metrics
        self.add_rate_metric_columns()
        
        results = self.orchestrator.calculate_all_metrics(
            self.sample_data, self.total_row,
            metrics=["Spend", "ROAS"]
        )
        
        # Check structure
        self.assertIn("contributions", results)
        self.assertIn("metadata", results)
        self.assertIn("summary", results)
        
        # Check success
        summary = results["summary"]
        self.assertEqual(summary["successful_calculations"], 2)
        self.assertEqual(summary["failed_calculations"], 0)
    
    def add_rate_metric_columns(self):
        """Helper to add rate metric columns."""
        for period in ['January 2025', 'February 2025']:
            self.sample_data[f'ROAS - {period}'] = (
                self.sample_data[f'Total Ad Sales - {period}'] / 
                self.sample_data[f'Spend - {period}']
            )
            
            self.total_row[f'ROAS - {period}'] = (
                self.total_row[f'Total Ad Sales - {period}'] / 
                self.total_row[f'Spend - {period}']
            )

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
def test_full_integration():
    """Test complete integration with realistic data."""
    
    # Load real data (replace with your data loading)
    campaign_data = load_campaign_data()  # Your data loading function
    total_row = calculate_totals(campaign_data)  # Your totals calculation
    
    # Initialize orchestrator
    orchestrator = BridgeOrchestrator()
    
    # Process all metrics
    results = orchestrator.calculate_all_metrics(campaign_data, total_row)
    
    # Comprehensive validation
    assert results["summary"]["success_rate"] == 100.0, "Some calculations failed"
    
    # Apply to DataFrame
    output_df = create_output_structure(campaign_data)  # Your DataFrame creation
    output_df = orchestrator.apply_to_dataframe(output_df, total_row)
    
    # Validate results
    validation = orchestrator.validate_all_contributions(output_df, total_row)
    failed_validations = [k for k, v in validation.items() if not v]
    
    if failed_validations:
        print(f"⚠️  Validation failures: {failed_validations}")
    else:
        print("✅ All validations passed")
    
    # Save results
    save_path = save_results(output_df)  # Your save function
    print(f"📄 Results saved to: {save_path}")
    
    return output_df

# Run integration test
result_df = test_full_integration()
```

These examples demonstrate the key patterns for using the refactored bridge calculator system. The new architecture provides much more flexibility and reliability while maintaining the same mathematical accuracy as the legacy system.