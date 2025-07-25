# Configuration Guide

## Overview

MixBridge v2 uses a flexible configuration system that allows you to customize calculation strategies, precision settings, validation parameters, and performance options. Configuration can be set globally or per-instance.

## Configuration Object

### MixBridgeConfig

```python
# New modular structure (recommended)
from src.config.settings import MixBridgeConfig

config = MixBridgeConfig(
    precision_decimals=4,
    validation_tolerance=0.01,
    debug_mode=False,
    enable_caching=True,
    chunk_size=10000
)

# Legacy import (still supported)
from src.mixbridge_config import MixBridgeConfig
```

## Configuration Parameters

### Core Calculation Settings

#### Zero Baseline Handling

MixBridge v2 uses **delta assignment** as the single strategy for handling campaigns with zero baseline values. This strategy:

- Calculates standard contributions for campaigns with baseline values
- Determines the "delta" (difference between total change and sum of standard contributions)
- Proportionally assigns this delta to zero baseline campaigns based on their Period 2 mix
- Ensures mathematical consistency and accuracy

No configuration is required - delta assignment is used automatically.

#### `precision_decimals`
- **Type**: `int`
- **Default**: `4`
- **Range**: `1-12`
- **Description**: Number of decimal places for calculations

```python
# High precision for detailed analysis
config = MixBridgeConfig(precision_decimals=6)

# Lower precision for performance
config = MixBridgeConfig(precision_decimals=2)
```

### Validation Settings

#### `validation_tolerance`
- **Type**: `float`
- **Default**: `0.01` (1%)
- **Description**: Tolerance for validation checks as percentage

```python
# Strict validation (0.1% tolerance)
config = MixBridgeConfig(validation_tolerance=0.001)

# Relaxed validation (5% tolerance)
config = MixBridgeConfig(validation_tolerance=0.05)
```

#### `enable_validation`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Enable comprehensive validation checks

### Performance Settings

#### `enable_caching`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Cache intermediate results for better performance

#### `chunk_size`
- **Type**: `int`
- **Default**: `10000`
- **Description**: Number of rows to process in each chunk for large files

```python
# Large chunks for high-memory systems
config = MixBridgeConfig(chunk_size=50000)

# Small chunks for memory-constrained systems
config = MixBridgeConfig(chunk_size=5000)
```

#### `optimize_dtypes`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Optimize data types for memory efficiency

### Debug and Logging

#### `debug_mode`
- **Type**: `bool`
- **Default**: `False`
- **Description**: Enable debug logging and detailed output

```python
# Enable debug mode for troubleshooting
config = MixBridgeConfig(debug_mode=True)
```

#### `log_level`
- **Type**: `str`
- **Default**: `'INFO'`
- **Options**: `'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'`, `'CRITICAL'`

## Predefined Profiles

### Performance Profile
```python
config = MixBridgeConfig.get_profile('performance')
# Equivalent to:
config = MixBridgeConfig(
    zero_baseline_strategy='dummy_value',
    precision_decimals=2,
    validation_tolerance=0.05,
    enable_caching=True,
    chunk_size=50000,
    optimize_dtypes=True
)
```

### Accuracy Profile
```python
config = MixBridgeConfig.get_profile('accuracy')
# Equivalent to:
config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=6,
    validation_tolerance=0.001,
    enable_caching=True,
    chunk_size=25000,
    debug_mode=False
)
```

### Debug Profile
```python
config = MixBridgeConfig.get_profile('debug')
# Equivalent to:
config = MixBridgeConfig(
    zero_baseline_strategy='hybrid',
    precision_decimals=4,
    validation_tolerance=0.01,
    debug_mode=True,
    enable_caching=False,
    chunk_size=5000
)
```

## Global Configuration

### Setting Global Configuration

```python
from src.mixbridge_config import set_config, MixBridgeConfig

# Set global configuration
global_config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=4
)
set_config(global_config)

# All instances will use this configuration by default
bridge = CampaignBridge('data.csv')  # Uses global config
```

### Getting Global Configuration

```python
from src.mixbridge_config import get_config

current_config = get_config()
print(current_config.to_dict())
```

### Resetting Configuration

```python
from src.mixbridge_config import reset_config

reset_config()  # Resets to default values
```

## Configuration Examples

### Small Dataset Configuration

```python
# Optimized for small datasets (< 100MB)
config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=4,
    validation_tolerance=0.01,
    chunk_size=25000,
    enable_caching=True,
    optimize_dtypes=False  # Less benefit for small data
)
```

### Large Dataset Configuration

```python
# Optimized for large datasets (> 1GB)
config = MixBridgeConfig(
    zero_baseline_strategy='dummy_value',  # Faster calculation
    precision_decimals=3,  # Reduce precision for speed
    validation_tolerance=0.02,  # Relaxed validation
    chunk_size=100000,  # Large chunks
    enable_caching=True,
    optimize_dtypes=True  # Important for memory
)
```

### High-Precision Analysis

```python
# For critical financial analysis
config = MixBridgeConfig(
    zero_baseline_strategy='hybrid',
    precision_decimals=8,
    validation_tolerance=0.0001,  # 0.01% tolerance
    enable_caching=True,
    debug_mode=True  # Detailed logging
)
```

### Development Configuration

```python
# For development and testing
config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=4,
    validation_tolerance=0.1,  # Relaxed for testing
    debug_mode=True,
    enable_caching=False,  # Disable caching for testing
    chunk_size=1000  # Small chunks for testing
)
```

## Dynamic Configuration

### Runtime Configuration Changes

```python
from src.campaign_bridge_modular import CampaignBridge

# Start with default configuration
bridge = CampaignBridge('data.csv')

# Change configuration before processing
bridge.config.zero_baseline_strategy = 'hybrid'
bridge.config.precision_decimals = 6

result = bridge.generate_bridge()
```

### Conditional Configuration

```python
import os
from src.mixbridge_config import MixBridgeConfig

# Environment-based configuration
if os.getenv('ENVIRONMENT') == 'production':
    config = MixBridgeConfig.get_profile('accuracy')
elif os.getenv('ENVIRONMENT') == 'development':
    config = MixBridgeConfig.get_profile('debug')
else:
    config = MixBridgeConfig.get_profile('performance')

bridge = CampaignBridge('data.csv', config=config)
```

### File Size-Based Configuration

```python
import os
from pathlib import Path
from src.mixbridge_config import MixBridgeConfig

def get_config_for_file(file_path):
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    
    if file_size_mb < 50:
        # Small file configuration
        return MixBridgeConfig(
            chunk_size=10000,
            optimize_dtypes=False
        )
    elif file_size_mb < 500:
        # Medium file configuration
        return MixBridgeConfig(
            chunk_size=25000,
            optimize_dtypes=True
        )
    else:
        # Large file configuration
        return MixBridgeConfig(
            chunk_size=100000,
            optimize_dtypes=True,
            precision_decimals=3
        )

config = get_config_for_file('data.csv')
bridge = CampaignBridge('data.csv', config=config)
```

## Configuration Validation

### Automatic Validation

```python
# Configuration is automatically validated
try:
    config = MixBridgeConfig(
        zero_baseline_strategy='invalid_strategy',  # Will raise error
        precision_decimals=15  # Will raise error (max 12)
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Manual Validation

```python
config = MixBridgeConfig()

# Check if configuration is valid
if hasattr(config, 'validate'):
    is_valid = config.validate()
    if not is_valid:
        print("Configuration validation failed")
```

## Configuration Serialization

### Save Configuration

```python
import json
from src.mixbridge_config import MixBridgeConfig

config = MixBridgeConfig(
    zero_baseline_strategy='delta_assignment',
    precision_decimals=4
)

# Save to JSON file
config_dict = config.to_dict()
with open('config.json', 'w') as f:
    json.dump(config_dict, f, indent=2)
```

### Load Configuration

```python
import json
from src.mixbridge_config import MixBridgeConfig

# Load from JSON file
with open('config.json', 'r') as f:
    config_dict = json.load(f)

config = MixBridgeConfig.from_dict(config_dict)
```

## Best Practices

### Performance Optimization

1. **Use appropriate chunk sizes** based on available memory
2. **Enable dtype optimization** for large datasets
3. **Use dummy_value strategy** for initial analysis, delta_assignment for final results
4. **Reduce precision** for large-scale processing
5. **Enable caching** for repeated analysis

### Accuracy Optimization

1. **Use delta_assignment or hybrid strategy** for zero baselines
2. **Increase precision** for financial calculations
3. **Tighten validation tolerance** for critical analysis
4. **Enable debug mode** for detailed validation reports

### Development Best Practices

1. **Use configuration profiles** for different environments
2. **Validate configuration** before processing
3. **Document configuration choices** in your code
4. **Test with different configurations** to understand trade-offs

### Configuration Management

```python
# Good: Centralized configuration
class ProjectConfig:
    @staticmethod
    def get_production_config():
        return MixBridgeConfig.get_profile('accuracy')
    
    @staticmethod
    def get_development_config():
        return MixBridgeConfig.get_profile('debug')
    
    @staticmethod
    def get_test_config():
        return MixBridgeConfig(
            validation_tolerance=0.1,
            debug_mode=True,
            enable_caching=False
        )

# Usage
config = ProjectConfig.get_production_config()
bridge = CampaignBridge('data.csv', config=config)
```

## Configuration Reference

### Complete Parameter List

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `zero_baseline_strategy` | str | 'delta_assignment' | Zero baseline handling strategy |
| `precision_decimals` | int | 4 | Decimal precision for calculations |
| `validation_tolerance` | float | 0.01 | Validation tolerance (as percentage) |
| `debug_mode` | bool | False | Enable debug logging |
| `enable_validation` | bool | True | Enable validation checks |
| `enable_caching` | bool | True | Cache intermediate results |
| `chunk_size` | int | 10000 | Chunk size for large file processing |
| `optimize_dtypes` | bool | True | Optimize data types for memory |
| `log_level` | str | 'INFO' | Logging level |

### Strategy Options

| Strategy | Performance | Accuracy | Memory Usage | Best For |
|----------|-------------|----------|--------------|----------|
| `dummy_value` | High | Medium | Low | Initial analysis, large datasets |
| `delta_assignment` | Medium | High | Medium | Final analysis, accurate results |
| `hybrid` | Medium | High | Medium | Complex scenarios, mixed requirements |