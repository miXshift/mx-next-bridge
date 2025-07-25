# MixBridge v2 User Guide

MixBridge v2 features a clean modular architecture for better development experience and maintainability.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Modular API](#modular-api)
3. [Basic Usage](#basic-usage)
4. [Output System](#output-system)
5. [Configuration](#configuration)
6. [Data Requirements](#data-requirements)
7. [Zero Baseline Handling](#zero-baseline-handling)
8. [Validation](#validation)
9. [Performance Optimization](#performance-optimization)
10. [Examples](#examples)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required packages: pandas, numpy
- CSV data file with campaign metrics

### Installation
```bash
# Navigate to the project directory
cd vBridge

# Ensure src directory is in your Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Modular API

### Recommended Approach (v2.0+)

The new modular structure provides better organization and clearer separation of concerns:

```python
# Import specific modules for your needs
from src.core.bridge_calculator import BridgeCalculator
from src.data.processor import OptimizedDataProcessor
from src.data.validator import MixBridgeValidator
from src.output.enhanced_formatter import EnhancedOutputFormatter
from src.config.settings import MixBridgeConfig

# Initialize components
config = MixBridgeConfig(precision_decimals=4)
processor = OptimizedDataProcessor()
calculator = BridgeCalculator()
validator = MixBridgeValidator()

# Load and process data
data = processor.load_campaign_data('data/campaign_data.csv')

# Calculate bridge metrics
results = calculator.calculate_bridge_metrics(data, config)

# Validate results
validation_results = validator.validate_output(results)

# Format output
formatter = EnhancedOutputFormatter(config)
formatted_output = formatter.format_enhanced_output(results)
```

### Module Specialization

Choose specific modules based on your needs:

```python
# For core calculations only
from src.core.bridge_calculator import BridgeCalculator

# For advanced zero baseline handling
from src.core.enhanced_calculator import EnhancedMixBridgeCalculator

# For rate metric calculations (ACoS, ROAS, etc.)
from src.core.mixrate_calculator import MixRateBridgeCalculator

# For data validation
from src.data.validator import MixBridgeValidator

# For custom metric definitions
from src.config.metrics import MetricDefinitions
```

## Basic Usage

### Simple Bridge Analysis

```python
# High-level API
from src.core.campaign_bridge_modular import CampaignBridge
# Or: from src import CampaignBridge

# Initialize with CSV file path
bridge = CampaignBridge('data/campaign_data.csv')

# Generate bridge analysis
result = bridge.generate_bridge()

# Access results
output_df = result['output_df']  # Campaign-level contributions
total_row = result['total_row']   # Period totals
summary = result['summary']       # Analysis summary
```

### Using Configuration

```python
from src.campaign_bridge_modular import CampaignBridge
from src.mixbridge_config import MixBridgeConfig

# Create custom configuration
config = MixBridgeConfig(
    precision_decimals=4,
    validation_tolerance=0.01,
    debug_mode=True
)

# Initialize with configuration (uses delta assignment strategy)
bridge = CampaignBridge('data/campaign_data.csv', config=config)
result = bridge.generate_bridge()
```

## Output System

MixBridge v2 features an enhanced output management system that makes it easy to find your latest analysis results and automatically manages file organization.

### Key Benefits

- **📄 Easy Access**: Latest analysis is always at `output/current/LATEST_mixbridge.csv`
- **📋 Backup**: Previous version automatically saved as `output/current/PREVIOUS_mixbridge.csv`
- **🗂️ Auto-Archive**: Old files automatically moved to `output/archive/` and compressed
- **📊 Metadata**: Rich information about each analysis in `output/current/LATEST_mixbridge_info.json`

### Quick Start

```python
from src.campaign_bridge_modular import CampaignBridge

# Run analysis - output is automatically managed
bridge = CampaignBridge('data/campaign_data.csv')
result = bridge.calculate_bridge()
latest_path, timestamped_path, previous_path = bridge.save_to_csv()

print(f"Latest analysis: {latest_path}")
# Output: Latest analysis: output/current/LATEST_mixbridge.csv
```

### Finding Your Files

**Latest Analysis** (always the same location):
```
output/current/LATEST_mixbridge.csv
```

**Previous Analysis** (backup):
```
output/current/PREVIOUS_mixbridge.csv
```

**Analysis Information**:
```
output/current/LATEST_mixbridge_info.json
```

### Command Line Tools

Check the status of your output files:
```bash
python3 output_manager_cli.py status
```

View latest file information:
```bash
python3 output_manager_cli.py latest
```

See recent analyses:
```bash
python3 output_manager_cli.py recent
```

Clean up old files:
```bash
python3 output_manager_cli.py cleanup --execute
```

For complete documentation, see:
- [Output System Documentation](output-system.md)
- [CLI Reference](cli-reference.md) 
- [Usage Examples](output-system-examples.md)

## Configuration

### Zero Baseline Strategy

MixBridge v2 uses **delta assignment** as the single strategy for handling zero baseline scenarios. This strategy:

- Calculates standard contributions for campaigns with baseline values
- Determines the "delta" (difference between total change and sum of standard contributions)  
- Proportionally assigns this delta to zero baseline campaigns based on their Period 2 mix
- Ensures mathematical consistency and accuracy

### Configuration Parameters

```python
config = MixBridgeConfig(
    precision_decimals=4,                       # Decimal precision
    validation_tolerance=0.01,                  # Validation tolerance (1%)
    debug_mode=False,                          # Enable debug logging
    enable_caching=True,                       # Cache intermediate results
    chunk_size=10000                          # Chunk size for large files
)
```

## Data Requirements

### Required Columns
Your CSV file must contain these columns:

- `DateKey`: Date in YYYYMMDD format
- `CampaignName`: Campaign identifier
- `Cost`: Advertising spend
- `Sales`: Total sales revenue
- `Impressions`: Ad impressions
- `Clicks`: Ad clicks
- `AttributedSalesSameSKU14day`: Same SKU sales
- `AttributedConversionsSameSKU14day`: Same SKU orders
- `AttributedConversions14day`: Total orders

### Data Format Example
```csv
DateKey,CampaignName,Cost,Sales,Impressions,Clicks,...
20250101,Campaign A,100.50,500.00,10000,50,...
20250102,Campaign A,120.75,600.25,12000,60,...
```

### Data Quality Requirements
- No missing values in required columns
- Numeric columns must contain valid numbers
- Dates must be in YYYYMMDD format
- Campaign names should be consistent

## Zero Baseline Handling

### Understanding Zero Baseline Scenarios

Zero baseline occurs when a campaign has no activity in Period 1 (January) but has activity in Period 2 (February). This creates mathematical challenges for percentage calculations.

### Delta Assignment Strategy

MixBridge v2 uses delta assignment to handle zero baseline scenarios mathematically consistently:

1. **Calculate Standard Contributions**: For campaigns with P1 > 0, calculate standard Mix Bridge contributions
2. **Determine Delta**: Calculate the difference between total change and sum of standard contributions  
3. **Proportional Assignment**: Distribute the delta to zero baseline campaigns based on their P2 mix

### Example: Delta Assignment Calculation

```python
# Campaign with zero baseline
# P1: Spend = $0, P2: Spend = $1000
# Total P1: $10000, Total P2: $12000

# Delta assignment calculation:
# Total delta = $12000 - $10000 = $2000
# Campaign proportion in P2 = $1000 / $12000 = 8.33%
# Campaign contribution = 8.33% × $2000 = $166.67
# Contribution in bps = ($166.67 / $10000) × 10000 = 167 bps
```

## Validation

### Automatic Validation

The system performs comprehensive validation checks:

```python
from src.mixbridge_validator import MixBridgeValidator

# Initialize validator
validator = MixBridgeValidator(config)

# Validate results
is_valid = validator.validate_contributions(output_df, total_row)

# Get detailed report
report = validator.get_validation_report()
print(f"Success rate: {report['summary']['success_rate']}%")
```

### Validation Checks

1. **Mathematical Consistency**: Ensures contributions sum correctly
2. **Data Integrity**: Checks for NaN, infinite, or unrealistic values
3. **Business Logic**: Validates business rule compliance
4. **Precision**: Monitors calculation precision
5. **Zero Baseline Handling**: Validates zero baseline scenarios

### Custom Validation

```python
# Add custom validation
validator.validate_required_columns(df, ['CampaignName', 'Cost'])
validator.validate_non_negative_values(df, ['Cost', 'Sales'])
validator.validate_percentage_bounds(df, ['CTR', 'CVR'])
```

## Performance Optimization

### Large File Handling

```python
from src.data_processor import OptimizedDataProcessor

# Initialize with chunking for large files
processor = OptimizedDataProcessor('large_file.csv', chunk_size=50000)

# Load with automatic chunking detection
jan_data, feb_data = processor.load_data(use_chunking=None)
```

### Memory Optimization

```python
# Enable all optimizations
config = MixBridgeConfig(
    enable_caching=True,
    optimize_dtypes=True,
    chunk_size=25000
)

bridge = CampaignBridge('data.csv', config=config)
```

### Performance Tips

1. **Use appropriate chunk sizes** for your system memory
2. **Enable dtype optimization** for large datasets
3. **Use delta_assignment strategy** for best performance
4. **Cache intermediate results** for repeated analysis
5. **Monitor memory usage** with `get_processing_stats()`

## Examples

### Example 1: Basic Analysis

```python
from src.campaign_bridge_modular import CampaignBridge

# Simple bridge analysis
bridge = CampaignBridge('campaign_data.csv')
result = bridge.generate_bridge()

# Display summary
print("Bridge Analysis Summary:")
print(f"Total campaigns: {len(result['output_df'])}")
print(f"Validation passed: {result['validation_passed']}")

# Export results
result['output_df'].to_csv('bridge_results.csv', index=False)
```

### Example 2: Custom Configuration

```python
from src.campaign_bridge_modular import CampaignBridge
from src.mixbridge_config import MixBridgeConfig

# Custom configuration for high-precision analysis
config = MixBridgeConfig(
    precision_decimals=6,
    validation_tolerance=0.001,  # 0.1% tolerance
    debug_mode=True
)

bridge = CampaignBridge('data.csv', config=config)
result = bridge.generate_bridge()

# Detailed validation report
if result['validator']:
    result['validator'].print_validation_report()
```

### Example 3: Batch Processing

```python
import glob
from src.campaign_bridge_modular import CampaignBridge

# Process multiple files
csv_files = glob.glob('data/*.csv')
results = {}

for file_path in csv_files:
    print(f"Processing {file_path}...")
    bridge = CampaignBridge(file_path)
    results[file_path] = bridge.generate_bridge()
    
    # Save individual results
    output_file = file_path.replace('.csv', '_bridge.csv')
    results[file_path]['output_df'].to_csv(output_file, index=False)

print(f"Processed {len(results)} files successfully")
```

### Example 4: Advanced Validation

```python
from src.mixbridge_validator import MixBridgeValidator
from src.campaign_bridge_modular import CampaignBridge

# Generate bridge with detailed validation
bridge = CampaignBridge('data.csv')
result = bridge.generate_bridge()

# Additional validation checks
validator = result['validator']

# Check for outliers in contributions
for metric in ['Spend', 'Total Ad Sales']:
    outliers = validator.detect_outliers(
        result['output_df'], 
        f'{metric} - Contribution',
        threshold=2.5
    )
    if len(outliers) > 0:
        print(f"Found {len(outliers)} outliers in {metric}")

# Generate comprehensive report
report = validator.get_validation_report()
print(f"Validation Summary:")
print(f"- Total checks: {report['summary']['total_checks']}")
print(f"- Success rate: {report['summary']['success_rate']}%")
print(f"- Warnings: {len(report['by_severity']['warning'])}")
print(f"- Errors: {len(report['by_severity']['error'])}")
```

## Next Steps

- Review [API Reference](api-reference.md) for detailed function documentation
- Check [Troubleshooting](troubleshooting.md) for common issues  
- See [Performance](performance.md) for optimization guidelines
- Explore [Scripts vs Utils Guide](scripts-vs-utils-guide.md) for development workflows