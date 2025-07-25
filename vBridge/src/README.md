# Source Code Structure and Usage Guide

This guide provides an overview of the MixBridge v2 source code organization and how to work with the modular architecture.

## Directory Structure

```
src/
├── __init__.py                    # Package-level imports and convenience exports
├── core/                         # Calculation engines
│   ├── __init__.py
│   ├── bridge_calculator.py       # Main bridge calculation logic
│   ├── enhanced_calculator.py     # Zero baseline handling 
│   ├── mixrate_calculator.py      # Rate metric calculations
│   ├── campaign_bridge.py         # Campaign-level bridge logic
│   ├── campaign_bridge_modular.py # High-level API
│   ├── orchestrator.py           # NEW: Unified bridge orchestrator
│   └── bridges/                  # NEW: Bridge type implementations
│       ├── __init__.py
│       ├── base.py               # Abstract base calculator
│       ├── mix_bridge.py         # Traditional Mix Bridge
│       ├── mixrate_bridge.py     # Standard MixRate Bridge
│       └── mixrate_infinity.py   # MixRate with Infinity Error
├── data/                         # Data processing & validation
│   ├── __init__.py
│   ├── processor.py              # Data loading & transformation
│   ├── validator.py              # Data validation & consistency
│   └── utils.py                  # Calculation utilities
├── output/                       # Output formatting & management
│   ├── __init__.py
│   ├── formatter.py              # Basic CSV formatting
│   ├── enhanced_formatter.py     # Advanced formatting with metadata
│   └── manager.py                # File management & archiving
├── config/                       # Configuration & definitions
│   ├── __init__.py
│   ├── metrics.py                # Metric definitions & categorization
│   ├── settings.py               # Configuration management
│   ├── constants.py              # Constants & thresholds
│   └── bridge_mappings.py        # NEW: KPI to bridge type mappings
├── models/                       # NEW: Data models
│   ├── __init__.py
│   └── bridge_types.py           # Bridge type definitions and enums
├── common/                       # Shared infrastructure
│   ├── __init__.py
│   ├── exceptions.py             # Custom exceptions
│   └── logger.py                 # Logging utilities
├── examples/                     # NEW: Example scripts
│   ├── __init__.py
│   └── bridge_example.py         # Bridge calculator examples
└── tests/                        # NEW: Test suite
    ├── __init__.py
    └── test_bridge_refactor.py   # Comprehensive tests
```

## Quick Start

### New Refactored System (Recommended)

```python
# Use the unified orchestrator for all bridge calculations
from src.core.orchestrator import BridgeOrchestrator

# Initialize orchestrator
orchestrator = BridgeOrchestrator(precision=12)

# Calculate all metrics automatically
results = orchestrator.calculate_all_metrics(
    campaign_data=campaign_df,
    total_row=totals_df
)

# Or calculate a specific metric
roas_results = orchestrator.calculate_metric(
    campaign_data=campaign_df,
    total_row=totals_df,
    metric="ROAS"
)
```

### Legacy System (Still Available)

```python
# Traditional approach
from src.core.bridge_calculator import BridgeCalculator
from src.config.settings import MixBridgeConfig
from src.data.processor import OptimizedDataProcessor

# Configure and calculate
config = MixBridgeConfig(precision_decimals=4)
calculator = BridgeCalculator()
result = calculator.calculate_bridge(bridge_data, validate=True)
```

## Import Patterns

### Direct Module Imports (Recommended)
```python
# New system
from src.core.orchestrator import BridgeOrchestrator
from src.config.bridge_mappings import get_bridge_configuration
from src.models.bridge_types import BridgeType, ContributionUnit

# Legacy system
from src.core.bridge_calculator import BridgeCalculator
from src.config.metrics import MetricDefinitions
from src.data.processor import OptimizedDataProcessor
from src.data.validator import MixBridgeValidator
from src.output.enhanced_formatter import EnhancedOutputFormatter
```

### Package-Level Imports
```python
# Convenient imports from src/__init__.py
from src import (
    BridgeCalculator, MetricDefinitions, OptimizedDataProcessor,
    MixBridgeValidator, EnhancedOutputFormatter, get_logger,
    BridgeOrchestrator  # New unified orchestrator
)
```

### High-Level Campaign Bridge API
```python
from src.core.campaign_bridge_modular import CampaignBridge
from src.config.settings import MixBridgeConfig

# Simple usage
bridge = CampaignBridge('data.csv')
result = bridge.generate_bridge()
```

## Module Descriptions

### core/ - Calculation Engines
- **orchestrator.py**: NEW - Unified controller for all bridge calculations
- **bridge_calculator.py**: Legacy bridge calculation logic
- **enhanced_calculator.py**: Zero baseline handling strategies
- **mixrate_calculator.py**: Rate metric calculations (ACoS, ROAS, etc.)
- **campaign_bridge.py**: Campaign-level bridge analysis
- **bridges/**: NEW - Individual bridge type implementations

### data/ - Data Processing
- **processor.py**: Data loading, transformation, and preparation
- **validator.py**: Data validation and consistency checks
- **utils.py**: Calculation utilities and helper functions

### output/ - Output Management
- **formatter.py**: Basic CSV output formatting
- **enhanced_formatter.py**: Advanced formatting with metadata
- **manager.py**: File management, archiving, and organization

### config/ - Configuration
- **metrics.py**: Metric definitions and categorization
- **settings.py**: Configuration management
- **constants.py**: System constants and thresholds
- **bridge_mappings.py**: NEW - KPI to bridge type mappings

### models/ - Data Models
- **bridge_types.py**: NEW - Bridge type enums and configurations

### common/ - Shared Infrastructure
- **exceptions.py**: Custom exception classes
- **logger.py**: Logging configuration and utilities

## Key Features

### Bridge Calculator Refactor (v2.1)
The new system introduces three distinct bridge types:
1. **Mix Bridge**: Traditional calculation for absolute metrics
2. **MixRate Bridge**: Standard rate calculations  
3. **MixRate Infinity**: Special handling for infinity-prone metrics

See [Bridge Architecture Documentation](../docs/refactor/BRIDGE_ARCHITECTURE.md) for detailed architecture information.

### Configuration-Driven KPI Assignment
```python
# Metrics are now mapped to bridge types in config/bridge_mappings.py
from src.config.bridge_mappings import KPI_BRIDGE_MAPPINGS

# Example: ACoS uses MixRate Infinity bridge
KPI_BRIDGE_MAPPINGS["ACoS"] = BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_INFINITY,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    inverse_metric="ROAS",
    requires_percentage_conversion=True
)
```

## Testing

Run the comprehensive test suite:
```bash
# Test new bridge calculator system
python -m pytest src/tests/test_bridge_refactor.py -v

# Run all tests
python -m pytest tests/ -v
```

## Documentation

For more detailed information:
- **[Complete Documentation](../docs/INDEX.md)** - Full documentation index
- **[Bridge Calculator Refactor](../docs/refactor/bridge-calculator-refactor.md)** - New system guide
- **[API Reference](../docs/refactor/api-reference-refactor.md)** - Complete API documentation
- **[Migration Guide](../docs/refactor/migration-guide-refactor.md)** - Migrating from legacy system

## Development Guidelines

1. **Modular Design**: Keep functionality within appropriate modules
2. **Import Discipline**: Use explicit imports from specific modules
3. **Configuration**: Add new metrics via `config/bridge_mappings.py`
4. **Testing**: Add tests for new functionality
5. **Documentation**: Update module docstrings and documentation

## Version History

- **v2.1**: Bridge calculator refactor with three bridge types
- **v2.0**: Complete modular restructure
- **v1.x**: Legacy monolithic structure

---
*Last updated: July 2025*