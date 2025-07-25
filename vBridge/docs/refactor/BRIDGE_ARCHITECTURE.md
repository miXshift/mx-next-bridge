# Bridge Calculator Architecture

## Overview

The bridge calculator implements three specialized calculation types with configuration-driven metric assignments.

## Core Components

### 1. Bridge Types (`models/bridge_types.py`)
- **BridgeType Enum**: MIX_BRIDGE, MIXRATE_BRIDGE, MIXRATE_INFINITY
- **ContributionUnit Enum**: CURRENCY, BASIS_POINTS, PERCENTAGE, COUNT, RATIO
- **BridgeConfiguration**: Metric configuration dataclass
- **MetricFormula**: Calculation formula definitions

### 2. Bridge Mappings (`config/bridge_mappings.py`)
Central registry mapping KPIs to configurations:

```python
"Spend": BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,
    contribution_unit=ContributionUnit.CURRENCY
)

"ACoS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_INFINITY,
    mix_determinant="Spend",
    inverse_metric="ROAS",
    contribution_unit=ContributionUnit.BASIS_POINTS
)
```

### 3. Bridge Calculators (`core/bridges/`)

#### Base Calculator (`base.py`)
Abstract base class with validation, formatting, and metadata generation.

#### Mix Bridge (`mix_bridge.py`)
Traditional bridge for absolute metrics.  
**Formula**: `Contribution = P1 Mix × Growth Rate × Total P1 Value`

#### MixRate Bridge (`mixrate_bridge.py`)
Standard rate calculations with Mix Impact + Rate Impact.

#### MixRate Infinity (`mixrate_infinity.py`)
Handles infinity-prone metrics via inverse methodology.

### 4. Orchestrator (`core/orchestrator.py`)
Central controller that automatically selects calculators and manages workflow.

## Usage

```python
from src.core.orchestrator import BridgeOrchestrator

orchestrator = BridgeOrchestrator(precision=12)
results = orchestrator.calculate_all_metrics(
    campaign_data=df,
    total_row=totals
)
```

## Bridge Type Selection

- **Mix Bridge**: Absolute metrics (Spend, Sales, Impressions, Clicks)
- **MixRate Bridge**: Rate metrics (ROAS, CTR, CPC, Conversion Rate)  
- **MixRate Infinity**: Infinity-prone metrics (ACoS via ROAS inverse)

## Key Features

- **Configuration-Driven**: Easy metric assignment via `bridge_mappings.py`
- **Type Safety**: Strong typing with dataclasses and enums
- **Validation**: Built-in mathematical consistency checks
- **Extensibility**: Easy to add new bridge types or metrics
- **Mathematical Consistency**: Contribution validation and precision control