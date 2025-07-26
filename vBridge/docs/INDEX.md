# MixBridge v2 Documentation

## Quick Start

1. [README](README.md) - System overview
2. [Bridge Calculator Guide](refactor/bridge-calculator-refactor.md) - Main system guide
3. [Examples](refactor/examples-refactor.md) - Usage examples

## Core System

### Bridge Calculator
- **[Complete Guide](refactor/bridge-calculator-refactor.md)** - System overview and usage
- **[API Reference](refactor/api-reference-refactor.md)** - API documentation
- **[Bridge Types](refactor/bridge-types-guide.md)** - Three bridge types explained
- **[Migration Guide](refactor/migration-guide-refactor.md)** - Migrate from legacy system
- **[Examples](refactor/examples-refactor.md)** - Usage examples
- **[Architecture](refactor/BRIDGE_ARCHITECTURE.md)** - Technical architecture

### System Features
- **[Output System](system/output-system.md)** - File management
- **[Unique Filename System](unique-filename-system.md)** - Unique file naming and organization
- **[CLI Tools](system/cli-reference.md)** - Command-line tools
- **[Configuration](system/configuration.md)** - Configuration options
- **[Performance](system/performance.md)** - Optimization guidelines

### Utilities
- **[Utils Overview](utils/README.md)** - Utility tools overview
- **[Comparison System](utils/comparison-system.md)** - Validation tools
- **[Utils API](utils/api-reference.md)** - API documentation

## Reference
- **[FAQ](faq.md)** - Frequently asked questions
- **[Troubleshooting](troubleshooting.md)** - Common issues
- **[Methodology](mixrate-bridge-methodology.md)** - Mathematical methodology & percent change aggregation

## Quick Reference

### Bridge Types
- **Mix Bridge**: Absolute metrics (Spend, Sales, Units)
- **MixRate Bridge**: Rate calculations (ROAS, CTR, CPC)
- **MixRate Infinity**: Infinity-prone metrics (ACoS)

### Key APIs
```python
# Main system
from src.core.orchestrator import BridgeOrchestrator
orchestrator = BridgeOrchestrator()
results = orchestrator.calculate_all_metrics(campaign_data, total_row)
```

### Common Tasks
- **Add metric**: Update `src/config/bridge_mappings.py`
- **Run calculations**: `BridgeOrchestrator.calculate_all_metrics()`
- **Validate results**: `BridgeOrchestrator.validate_all_contributions()`