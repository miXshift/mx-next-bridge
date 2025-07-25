# Troubleshooting Guide

## Table of Contents

1. [Common Issues](#common-issues)
2. [Data Loading Problems](#data-loading-problems)
3. [Calculation Errors](#calculation-errors)
4. [Validation Failures](#validation-failures)
5. [Performance Issues](#performance-issues)
6. [Configuration Problems](#configuration-problems)
7. [Debug Techniques](#debug-techniques)
8. [Error Reference](#error-reference)

## Common Issues

### Import Errors

**Problem**: `ImportError: attempted relative import with no known parent package`

**Solution**:
```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run from project root
cd /path/to/vBridge
python -c "from src.campaign_bridge_modular import CampaignBridge"
```

**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
# Install required dependencies
pip install pandas numpy

# Or install from requirements file
pip install -r requirements.txt
```

### File Path Issues

**Problem**: `FileNotFoundError: CSV file not found`

**Solution**:
```python
import os
from pathlib import Path

# Use absolute paths
csv_path = Path("/full/path/to/data.csv").resolve()
bridge = CampaignBridge(str(csv_path))

# Or verify file exists
if not os.path.exists(csv_path):
    print(f"File not found: {csv_path}")
```

## Data Loading Problems

### Large File Handling

**Problem**: `MemoryError` when loading large CSV files

**Solution**:
```python
from src.data_processor import OptimizedDataProcessor

# Use chunked processing
processor = OptimizedDataProcessor('large_file.csv', chunk_size=25000)
jan_data, feb_data = processor.load_data(use_chunking=True)

# Monitor memory usage
stats = processor.get_processing_stats()
print(f"Memory usage: {stats['memory_usage_mb']:.1f} MB")
```

### Date Format Issues

**Problem**: `ValueError: time data does not match format '%Y%m%d'`

**Solutions**:
```python
# Check date format in your CSV
import pandas as pd
df = pd.read_csv('data.csv')
print(df['DateKey'].head())  # Should be like 20250101

# If dates are in different format, convert first
df['DateKey'] = pd.to_datetime(df['Date']).dt.strftime('%Y%m%d')
```

### Missing Columns

**Problem**: `ValidationError: Missing required columns`

**Solution**:
```python
# Check available columns
df = pd.read_csv('data.csv')
print("Available columns:", df.columns.tolist())

# Required columns for MixBridge
required = [
    'DateKey', 'CampaignName', 'Cost', 'Sales', 
    'Impressions', 'Clicks', 'AttributedSalesSameSKU14day',
    'AttributedConversionsSameSKU14day', 'AttributedConversions14day'
]

missing = set(required) - set(df.columns)
if missing:
    print(f"Missing columns: {missing}")
```

### Encoding Issues

**Problem**: `UnicodeDecodeError` when reading CSV

**Solution**:
```python
# Try different encodings
import pandas as pd

encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
for encoding in encodings:
    try:
        df = pd.read_csv('data.csv', encoding=encoding)
        print(f"Successfully read with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue
```

## Calculation Errors

### Zero Division Errors

**Problem**: `CalculationError: Division by zero in calculations`

**Solution**:
```python
# Use safe calculation utilities
from src.calculation_utils import safe_divide

# Instead of direct division
result = safe_divide(numerator, denominator, fill_value=0.0)

# Enable zero baseline handling
from src.mixbridge_config import MixBridgeConfig
config = MixBridgeConfig(zero_baseline_strategy='delta_assignment')
```

### Infinite Values

**Problem**: `ValidationError: Contains infinite values`

**Solution**:
```python
# Check for infinite values
import numpy as np
import pandas as pd

df = pd.read_csv('data.csv')
for col in df.select_dtypes(include=[np.number]).columns:
    inf_count = np.isinf(df[col]).sum()
    if inf_count > 0:
        print(f"Column {col} has {inf_count} infinite values")
        
# Clean infinite values
df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
```

### Precision Issues

**Problem**: Calculations producing unexpected decimal places

**Solution**:
```python
# Adjust precision in configuration
config = MixBridgeConfig(
    precision_decimals=4,  # Set desired precision
    validation_tolerance=0.001  # Tighter tolerance
)

# Or use calculation utilities
from src.calculation_utils import calculate_rate_metric
ctr = calculate_rate_metric(clicks, impressions, precision=2)
```

## Validation Failures

### Mathematical Inconsistencies

**Problem**: `ValidationResult: Mathematical inconsistencies detected`

**Diagnosis**:
```python
# Get detailed validation report
bridge = CampaignBridge('data.csv')
result = bridge.generate_bridge()

if result['validator']:
    report = result['validator'].get_validation_report()
    
    # Check inconsistencies
    for severity in ['error', 'warning']:
        for item in report['by_severity'][severity]:
            print(f"{severity.upper()}: {item['message']}")
            if item['details']:
                print(f"Details: {item['details']}")
```

**Solutions**:
```python
# Increase validation tolerance
config = MixBridgeConfig(validation_tolerance=0.05)  # 5% tolerance

# Use different calculation strategy
config = MixBridgeConfig(zero_baseline_strategy='hybrid')

# Enable debug mode for detailed logging
config = MixBridgeConfig(debug_mode=True)
```

### Data Quality Issues

**Problem**: `ValidationError: Non-numeric data in columns`

**Solution**:
```python
# Clean data before processing
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

# Convert to numeric, coerce errors to NaN
numeric_cols = ['Cost', 'Sales', 'Impressions', 'Clicks']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill NaN values appropriately
df[numeric_cols] = df[numeric_cols].fillna(0)

# Save cleaned data
df.to_csv('data_cleaned.csv', index=False)
```

### Outlier Detection

**Problem**: Validation warnings about outliers

**Analysis**:
```python
from src.mixbridge_validator import MixBridgeValidator

validator = MixBridgeValidator()

# Detect outliers in spend data
outliers = validator.detect_outliers(df, 'Cost', threshold=3.0)
print(f"Found {len(outliers)} outliers in Cost:")
print(outliers.head())

# Check outlier campaigns
outlier_campaigns = df[df['Cost'].isin(outliers)]['CampaignName'].unique()
print(f"Campaigns with outliers: {outlier_campaigns}")
```

## Performance Issues

### Slow Processing

**Problem**: Bridge generation taking too long

**Optimization**:
```python
# Use optimized configuration
config = MixBridgeConfig(
    enable_caching=True,
    chunk_size=50000  # Larger chunks for better performance
)

# Monitor processing time
import time
start_time = time.time()
result = bridge.generate_bridge()
print(f"Processing time: {time.time() - start_time:.2f} seconds")

# Check processing stats
if hasattr(bridge, 'processor'):
    stats = bridge.processor.get_processing_stats()
    print(f"Memory usage: {stats['memory_usage_mb']:.1f} MB")
```

### Memory Usage

**Problem**: High memory consumption

**Solutions**:
```python
# Use chunked processing
from src.data_processor import OptimizedDataProcessor
processor = OptimizedDataProcessor('data.csv', chunk_size=25000)

# Enable data type optimization
processor.load_data(use_chunking=True)

# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Current memory usage: {memory_mb:.1f} MB")
```

## Configuration Problems

### Invalid Strategy

**Problem**: `ConfigurationError: Strategy must be one of...`

**Solution**:
```python
# Check valid strategies
valid_strategies = ['dummy_value', 'delta_assignment', 'hybrid']
print(f"Valid strategies: {valid_strategies}")

# Use correct strategy name
config = MixBridgeConfig(zero_baseline_strategy='delta_assignment')
```

### Configuration Conflicts

**Problem**: Configuration parameters conflicting

**Diagnosis**:
```python
# Validate configuration
config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=4,
    validation_tolerance=0.01
)

# Check if configuration is valid
if hasattr(config, 'validate'):
    is_valid = config.validate()
    print(f"Configuration valid: {is_valid}")
```

## Debug Techniques

### Enable Debug Logging

```python
from src.mixbridge_config import MixBridgeConfig
from src.logger import setup_logger
import logging

# Enable debug logging
config = MixBridgeConfig(debug_mode=True)
logger = setup_logger(level=logging.DEBUG)

# Process with detailed logging
bridge = CampaignBridge('data.csv', config=config)
result = bridge.generate_bridge()
```

### Step-by-Step Debugging

```python
# Debug data loading
from src.data_processor import OptimizedDataProcessor

processor = OptimizedDataProcessor('data.csv')
print("Loading data...")
jan_data, feb_data = processor.load_data()
print(f"January records: {len(jan_data)}")
print(f"February records: {len(feb_data)}")

# Debug aggregation
print("Aggregating January data...")
jan_agg = processor.aggregate_period_data(jan_data)
print(f"January campaigns: {len(jan_agg)}")
print(jan_agg.head())
```

### Validation Debugging

```python
from src.mixbridge_validator import MixBridgeValidator

# Create validator with debug config
config = MixBridgeConfig(debug_mode=True, validation_tolerance=0.1)
validator = MixBridgeValidator(config)

# Run individual validation checks
validator.validate_required_columns(df, ['CampaignName', 'Cost'])
validator.validate_numeric_columns(df, ['Cost', 'Sales'])
validator.validate_non_negative_values(df, ['Cost', 'Sales'])

# Get detailed report
validator.print_validation_report()
```

## Error Reference

### ValidationError Types

| Error | Cause | Solution |
|-------|-------|----------|
| Missing required columns | CSV lacks expected columns | Add missing columns or check column names |
| Non-numeric data | Text in numeric columns | Clean data, convert to numeric |
| Negative values | Negative costs/sales | Validate business logic, clean data |
| Invalid dates | Wrong date format | Convert dates to YYYYMMDD format |
| Percentage out of bounds | CTR/CVR > 100% | Check calculation logic |

### CalculationError Types

| Error | Cause | Solution |
|-------|-------|----------|
| Division by zero | Zero baseline values | Use zero baseline strategy |
| Mathematical inconsistency | Calculation errors | Check input data quality |
| Infinite values | Division overflow | Use safe_divide utility |
| Precision loss | Excessive decimal places | Adjust precision_decimals |

### ConfigurationError Types

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid strategy | Wrong strategy name | Use valid strategy names |
| Parameter conflicts | Incompatible settings | Review configuration |
| Missing configuration | Required config missing | Provide complete config |

### FileOperationError Types

| Error | Cause | Solution |
|-------|-------|----------|
| File not found | Wrong file path | Check file path and existence |
| Permission denied | Insufficient permissions | Check file permissions |
| Encoding error | Wrong file encoding | Try different encodings |
| Corrupted file | Damaged CSV file | Validate and repair file |

## Getting Help

### Information to Provide

When reporting issues, include:

1. **System Information**:
   ```python
   import sys
   import pandas as pd
   import numpy as np
   
   print(f"Python version: {sys.version}")
   print(f"Pandas version: {pd.__version__}")
   print(f"NumPy version: {np.__version__}")
   ```

2. **Error Details**:
   - Full error message and stack trace
   - Configuration used
   - Data sample (anonymized)
   - Expected vs actual behavior

3. **Environment**:
   - Operating system
   - Memory available
   - File size being processed

### Debug Information Generation

```python
# Generate debug report
def generate_debug_report(csv_path, config=None):
    import sys
    import os
    from src.mixbridge_config import MixBridgeConfig
    
    print("=== MixBridge Debug Report ===")
    print(f"Python version: {sys.version}")
    print(f"File path: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if os.path.exists(csv_path):
        print(f"File size: {os.path.getsize(csv_path)} bytes")
    
    if config:
        print(f"Configuration: {config.to_dict()}")
    
    # Try basic operations
    try:
        from src.data_processor import OptimizedDataProcessor
        processor = OptimizedDataProcessor(csv_path)
        stats = processor.get_processing_stats()
        print(f"Processing stats: {stats}")
    except Exception as e:
        print(f"Error during processing: {e}")

# Usage
generate_debug_report('data.csv', config)
```