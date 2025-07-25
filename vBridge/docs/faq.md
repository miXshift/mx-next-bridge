# Frequently Asked Questions (FAQ)

## General Questions

### What is MixBridge v2?

MixBridge v2 is a campaign bridge analysis system that calculates contribution metrics across advertising campaigns. It's designed to handle zero baseline scenarios, provide performance optimization, and ensure robust validation of calculations.

### What's new in v2 compared to the original version?

- **Enhanced Performance**: 40-70% faster processing with vectorized operations
- **Robust Error Handling**: Comprehensive exception handling and validation
- **Type Safety**: Full type hints for better IDE support
- **Memory Optimization**: 30-50% reduction in memory usage
- **Modular Architecture**: Clean separation of concerns and extensible design
- **Zero Baseline Strategies**: Multiple approaches for handling zero baseline scenarios

### What are the system requirements?

- Python 3.8 or higher
- pandas >= 1.3.0
- numpy >= 1.20.0
- Memory: 2GB minimum, 8GB recommended for large datasets
- Storage: Temporary space for chunked processing

## Data and Input Questions

### What data format does MixBridge v2 accept?

MixBridge v2 accepts CSV files with the following required columns:
- `DateKey`: Date in YYYYMMDD format (e.g., 20250101)
- `CampaignName`: Campaign identifier
- `Cost`: Advertising spend
- `Sales`: Total sales revenue
- `Impressions`: Ad impressions
- `Clicks`: Ad clicks
- `AttributedSalesSameSKU14day`: Same SKU sales
- `AttributedConversionsSameSKU14day`: Same SKU orders
- `AttributedConversions14day`: Total orders

### Can I use data from different date ranges?

Currently, MixBridge v2 is designed for January 2025 vs February 2025 comparisons. To use different date ranges, you would need to:
1. Update the date filtering logic in the data processor
2. Modify the column naming convention
3. Adjust the validation rules

### How do I handle missing data?

```python
import pandas as pd
import numpy as np

# Load and clean data
df = pd.read_csv('data.csv')

# Fill missing numeric values with zeros
numeric_cols = ['Cost', 'Sales', 'Impressions', 'Clicks']
df[numeric_cols] = df[numeric_cols].fillna(0)

# For categorical data, fill with 'Unknown'
df['CampaignName'] = df['CampaignName'].fillna('Unknown')

# Save cleaned data
df.to_csv('data_cleaned.csv', index=False)
```

### What file sizes can MixBridge v2 handle?

- **Small files** (< 100MB): Process normally without chunking
- **Medium files** (100MB - 1GB): Automatic chunking detection
- **Large files** (> 1GB): Manual chunking recommended

```python
# For large files, use explicit chunking
from src.data_processor import OptimizedDataProcessor
processor = OptimizedDataProcessor('large_file.csv', chunk_size=50000)
```

## Configuration Questions

### Which zero baseline strategy should I use?

**For most cases**: Use `'delta_assignment'` (default)
- Most accurate for mathematical consistency
- Handles zero baselines proportionally
- Recommended for financial analysis

**For performance**: Use `'dummy_value'`
- Fastest processing
- Good for initial analysis
- May slightly distort percentages

**For complex scenarios**: Use `'hybrid'`
- Combines both approaches
- Good for mixed data scenarios

```python
# Recommended configuration
config = MixBridgeConfig(zero_baseline_strategy='delta_assignment')
```

### How do I optimize performance for large datasets?

```python
# Performance-optimized configuration
config = MixBridgeConfig(
    zero_baseline_strategy='dummy_value',  # Faster
    precision_decimals=3,  # Reduce precision
    validation_tolerance=0.02,  # Relaxed validation
    chunk_size=100000,  # Large chunks
    enable_caching=True,
    optimize_dtypes=True
)
```

### What precision should I use for financial data?

For financial calculations, use higher precision:

```python
# High precision for financial analysis
config = MixBridgeConfig(
    precision_decimals=6,  # Or higher
    validation_tolerance=0.001,  # 0.1% tolerance
    zero_baseline_strategy='delta_assignment'
)
```

## Zero Baseline Questions

### What is a zero baseline scenario?

A zero baseline occurs when a campaign has no activity in Period 1 (January) but has activity in Period 2 (February). This creates mathematical challenges because:
- Percentage change calculation requires division by zero
- Traditional contribution calculations fail
- Results can be mathematically inconsistent

### How does delta assignment work?

Delta assignment proportionally assigns the total period change based on each campaign's contribution in Period 2:

1. Calculate total delta: `Total P2 - Total P1`
2. Calculate campaign's P2 proportion: `Campaign P2 / Total P2`
3. Assign contribution: `Proportion × Total Delta`
4. Convert to basis points: `(Contribution / Total P1) × 10000`

### When should I be concerned about zero baselines?

Monitor zero baselines when:
- You have many new campaigns launched in Period 2
- You're analyzing seasonal campaigns
- There are significant campaign structure changes
- You need mathematically consistent results

## Validation Questions

### What does validation check?

MixBridge v2 performs comprehensive validation:
1. **Data Integrity**: Checks for NaN, infinite, or invalid values
2. **Mathematical Consistency**: Verifies calculations sum correctly
3. **Business Logic**: Validates business rule compliance
4. **Precision**: Monitors calculation accuracy
5. **Zero Baseline Handling**: Validates zero baseline scenarios

### Why am I getting validation warnings?

Common validation warnings:
- **Mathematical inconsistencies**: Check data quality and calculation parameters
- **Outliers detected**: Review campaigns with extreme values
- **Precision issues**: Adjust `precision_decimals` setting
- **Zero baseline handling**: Review `zero_baseline_strategy` choice

### How do I customize validation rules?

```python
from src.mixbridge_validator import MixBridgeValidator

# Create validator with custom tolerance
validator = MixBridgeValidator()

# Add custom validation checks
validator.validate_percentage_bounds(df, ['CTR', 'CVR'])
validator.validate_non_negative_values(df, ['Cost', 'Sales'])

# Detect outliers with custom threshold
outliers = validator.detect_outliers(df, 'Cost', threshold=2.5)
```

### Why don't individual campaign percent changes sum to the total percent change?

This is a fundamental mathematical principle: **percent changes cannot be directly summed when they have different denominators (base values)**. 

For example:
- Campaign A: $100 → $110 = 10% increase
- Campaign B: $10 → $15 = 50% increase
- Total: $110 → $125 = 13.64% increase (NOT 60%!)

Each campaign's percent change is based on its own January value, so they cannot be meaningfully added together. The total percent change is correctly calculated from the aggregated total values. 

For more details, see the [Understanding Percent Change Aggregation](mixrate-bridge-methodology.md#understanding-percent-change-aggregation) section in the methodology document.

## Performance Questions

### Why is processing slow?

Common performance issues:
1. **Large file size**: Use chunked processing
2. **Inefficient configuration**: Use performance profile
3. **Memory constraints**: Reduce chunk size and enable dtype optimization
4. **Debug mode enabled**: Disable for production processing

### How can I monitor memory usage?

```python
from src.data_processor import OptimizedDataProcessor
import psutil
import os

# Monitor system memory
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f} MB")

# Get processing statistics
processor = OptimizedDataProcessor('data.csv')
stats = processor.get_processing_stats()
print(f"DataFrame memory: {stats['memory_usage_mb']:.1f} MB")
```

### What's the difference between chunked and direct loading?

**Direct Loading**:
- Loads entire file into memory at once
- Faster for small to medium files
- May cause memory errors for large files

**Chunked Loading**:
- Processes file in smaller pieces
- Uses more CPU but less memory
- Required for very large files
- Automatically detected based on file size

## Error Questions

### What should I do if I get a `MemoryError`?

```python
# Reduce memory usage
config = MixBridgeConfig(
    chunk_size=10000,  # Smaller chunks
    optimize_dtypes=True,  # Enable optimization
    enable_caching=False  # Disable caching temporarily
)

# Use chunked processing
from src.data_processor import OptimizedDataProcessor
processor = OptimizedDataProcessor('data.csv', chunk_size=10000)
jan_data, feb_data = processor.load_data(use_chunking=True)
```

### How do I handle `ValidationError`s?

```python
from src.exceptions import ValidationError

try:
    result = bridge.generate_bridge()
except ValidationError as e:
    print(f"Validation failed: {e}")
    
    # Get detailed validation report
    if hasattr(bridge, 'validator'):
        bridge.validator.print_validation_report()
    
    # Try with relaxed validation
    config = MixBridgeConfig(validation_tolerance=0.05)
    bridge = CampaignBridge('data.csv', config=config)
    result = bridge.generate_bridge()
```

### What does `CalculationError` mean?

`CalculationError` indicates mathematical computation problems:
- Division by zero in calculations
- Infinite or NaN values produced
- Mathematical inconsistencies

Solutions:
1. Use appropriate zero baseline strategy
2. Clean input data
3. Adjust calculation parameters

## Integration Questions

### How do I integrate MixBridge v2 into my workflow?

```python
# Automated workflow example
import pandas as pd
from src.campaign_bridge_modular import CampaignBridge
from src.mixbridge_config import MixBridgeConfig

def process_bridge_analysis(input_file, output_file, config_profile='accuracy'):
    """Automated bridge analysis workflow"""
    
    # Get configuration
    config = MixBridgeConfig.get_profile(config_profile)
    
    # Process bridge analysis
    bridge = CampaignBridge(input_file, config=config)
    result = bridge.generate_bridge()
    
    # Save results
    result['output_df'].to_csv(output_file, index=False)
    
    # Return summary
    return {
        'campaigns_processed': len(result['output_df']),
        'validation_passed': result['validation_passed'],
        'processing_time': result.get('processing_time', 'Unknown')
    }

# Usage
summary = process_bridge_analysis('data.csv', 'results.csv')
print(f"Processed {summary['campaigns_processed']} campaigns")
```

### Can I process multiple files in batch?

```python
import glob
from pathlib import Path

def batch_process_files(input_pattern, output_dir):
    """Process multiple CSV files in batch"""
    
    files = glob.glob(input_pattern)
    results = {}
    
    for file_path in files:
        print(f"Processing {file_path}...")
        
        # Generate output filename
        input_name = Path(file_path).stem
        output_path = Path(output_dir) / f"{input_name}_bridge.csv"
        
        # Process file
        try:
            bridge = CampaignBridge(file_path)
            result = bridge.generate_bridge()
            
            # Save results
            result['output_df'].to_csv(output_path, index=False)
            results[file_path] = 'Success'
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            results[file_path] = f'Error: {e}'
    
    return results

# Usage
results = batch_process_files('data/*.csv', 'results/')
```

### How do I export results to different formats?

```python
# Export to multiple formats
result = bridge.generate_bridge()
output_df = result['output_df']

# CSV (default)
output_df.to_csv('results.csv', index=False)

# Excel with multiple sheets
with pd.ExcelWriter('results.xlsx') as writer:
    output_df.to_excel(writer, sheet_name='Campaign_Analysis', index=False)
    result['total_row'].to_excel(writer, sheet_name='Totals', index=False)

# JSON for API integration
output_df.to_json('results.json', orient='records', indent=2)

# Parquet for data science workflows
output_df.to_parquet('results.parquet', index=False)
```

## Best Practices Questions

### What are the recommended workflow steps?

1. **Data Preparation**:
   - Validate CSV format and required columns
   - Clean missing or invalid data
   - Check date formats

2. **Configuration**:
   - Choose appropriate strategy for your use case
   - Set precision based on requirements
   - Configure performance settings

3. **Processing**:
   - Run bridge analysis
   - Review validation results
   - Handle any errors or warnings

4. **Results Review**:
   - Examine contribution calculations
   - Validate business logic
   - Export results in required format

### How should I handle production deployments?

```python
# Production configuration
production_config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=6,
    validation_tolerance=0.001,
    debug_mode=False,  # Disable debug in production
    enable_caching=True,
    chunk_size=50000
)

# Error handling for production
def production_bridge_analysis(file_path):
    try:
        bridge = CampaignBridge(file_path, config=production_config)
        result = bridge.generate_bridge()
        
        if not result['validation_passed']:
            # Log validation issues but continue
            logger.warning("Validation warnings detected")
            
        return result
        
    except Exception as e:
        # Log error and handle gracefully
        logger.error(f"Bridge analysis failed: {e}")
        raise
```

### How do I ensure data quality?

```python
from src.mixbridge_validator import MixBridgeValidator

def validate_input_data(df):
    """Comprehensive input data validation"""
    
    validator = MixBridgeValidator()
    
    # Required columns check
    required_cols = ['DateKey', 'CampaignName', 'Cost', 'Sales']
    validator.validate_required_columns(df, required_cols)
    
    # Data quality checks
    numeric_cols = ['Cost', 'Sales', 'Impressions', 'Clicks']
    validator.validate_numeric_columns(df, numeric_cols)
    validator.validate_non_negative_values(df, numeric_cols)
    
    # Date validation
    validator.validate_date_column(df, 'DateKey')
    
    # Check for outliers
    for col in numeric_cols:
        outliers = validator.detect_outliers(df, col)
        if len(outliers) > 0:
            print(f"Warning: {len(outliers)} outliers detected in {col}")
    
    return True

# Usage
df = pd.read_csv('data.csv')
validate_input_data(df)
```