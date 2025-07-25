# MixBridge v2 Documentation

## Overview

MixBridge v2 calculates contribution metrics for advertising campaigns using three specialized bridge types for different metric categories.

## Quick Start

```python
from src.core.orchestrator import BridgeOrchestrator

# Initialize and calculate all metrics
orchestrator = BridgeOrchestrator(precision=12)
results = orchestrator.calculate_all_metrics(
    campaign_data=campaign_df,
    total_row=totals_df
)

# Apply to output DataFrame
output_df = orchestrator.apply_to_dataframe(
    output_df=output_df,
    total_row=totals_df
)
```

## Key Features

- **Three Bridge Types**: Mix Bridge, MixRate Bridge, MixRate Infinity
- **Configuration-Driven**: Easy KPI assignment via `bridge_mappings.py`
- **Unified Interface**: Single orchestrator for all calculations
- **Built-in Validation**: Mathematical consistency checks
- **Rich Metadata**: Complete audit trails
- **Zero Baseline Handling**: Delta assignment strategy

## Documentation

**[📚 Complete Index](INDEX.md)** - Full documentation guide

### Essential Guides
- **[Bridge Calculator Guide](refactor/bridge-calculator-refactor.md)** - Main system guide
- **[Examples](refactor/examples-refactor.md)** - Usage examples
- **[Bridge Types](refactor/bridge-types-guide.md)** - Three bridge types explained
- **[API Reference](refactor/api-reference-refactor.md)** - Complete API docs

### Support
- **[FAQ](faq.md)** - Common questions
- **[Troubleshooting](troubleshooting.md)** - Issue resolution

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```