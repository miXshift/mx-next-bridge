# MixBridge v2 Source Restructure

The `/src` directory has been restructured to improve organization and maintainability.

## New Structure

```
src/
├── __init__.py                    # Package initialization with backwards compatibility
├── core/                          # Core calculation engines
│   ├── __init__.py
│   ├── bridge_calculator.py       # Main bridge calculation logic
│   ├── enhanced_calculator.py     # Zero baseline handling (was enhanced_mixbridge_calculator.py)
│   ├── mixrate_calculator.py      # Rate metric calculations (was mixrate_bridge_calculator.py)
│   └── campaign_bridge.py         # Campaign-level bridge logic
├── data/                          # Data processing & validation
│   ├── __init__.py
│   ├── processor.py              # Data loading & transformation (was data_processor.py)
│   ├── validator.py              # Data validation (was mixbridge_validator.py)
│   └── utils.py                  # Calculation utilities (was calculation_utils.py)
├── output/                        # Output formatting & management
│   ├── __init__.py
│   ├── formatter.py              # Basic CSV formatting (was output_formatter.py)
│   ├── enhanced_formatter.py     # Advanced formatting (was enhanced_output_formatter.py)
│   └── manager.py                # File management (was improved_output_manager.py)
├── config/                        # Configuration & definitions
│   ├── __init__.py
│   ├── metrics.py                # Metric definitions (was metric_definitions.py)
│   ├── settings.py               # Configuration (was mixbridge_config.py)
│   └── constants.py              # Constants & thresholds
└── common/                        # Shared infrastructure
    ├── __init__.py
    ├── exceptions.py             # Custom exceptions
    └── logger.py                 # Logging utilities
```

## Updated Import Statements

### External Scripts/Tests (Updated)
```python
# OLD
from src.bridge_calculator import BridgeCalculator
from src.metric_definitions import MetricDefinitions
from src.mixbridge_validator import MixBridgeValidator
from src.exceptions import ValidationError
from src.mixrate_bridge_calculator import MixRateBridgeCalculator

# NEW
from src.core.bridge_calculator import BridgeCalculator
from src.config.metrics import MetricDefinitions
from src.data.validator import MixBridgeValidator
from src.common.exceptions import ValidationError
from src.core.mixrate_calculator import MixRateBridgeCalculator
```

### Package-Level Imports (Backwards Compatible)
```python
# These still work thanks to __init__.py re-exports
from src import BridgeCalculator, MetricDefinitions, MixBridgeValidator
```

## Benefits

1. **Logical Grouping**: Related functionality organized together
2. **Clear Boundaries**: Separation of concerns between modules
3. **Easier Navigation**: Developers can quickly find relevant code
4. **Better Testing**: Each module can be tested independently
5. **Reduced Coupling**: Clear interfaces between modules

## Migration Status

- ✅ **Phase 1**: Directory structure created
- ✅ **Phase 2**: Files moved with backwards compatibility
- ✅ **Phase 3**: External imports updated
- ⏳ **Phase 4**: Legacy cleanup (in progress)

## Legacy Files

The following files remain in the root `/src` directory for backwards compatibility:
- `bridge_calculator.py`
- `calculation_utils.py` 
- `campaign_bridge.py`
- `campaign_bridge_modular.py`
- `constants.py`
- `data_processor.py`
- `enhanced_mixbridge_calculator.py`
- `enhanced_output_formatter.py`
- `exceptions.py`
- `improved_output_manager.py`
- `logger.py`
- `metric_definitions.py`
- `mixbridge_config.py`
- `mixbridge_validator.py`
- `mixrate_bridge_calculator.py`
- `output_formatter.py`

**Note**: These will be removed in a future cleanup phase once full migration is confirmed.

## Files Updated

### Scripts
- `scripts/analysis/analyze_acos_issues.py`
- `scripts/analysis/analyze_roas_contributions.py`
- `scripts/verification/verify_all_contributions.py`
- `scripts/verification/verify_all_12_kpis.py`

### Tests
- `tests/test_mixbridge_validator.py`

## Validation

All imports have been tested and confirmed working:
- ✅ `src.config.constants` 
- ✅ `src.config.metrics`
- ✅ `src.common.logger`
- ✅ `src.core.bridge_calculator`
- ✅ Script imports functional

## Next Steps

1. Monitor usage for any remaining import issues
2. Plan removal of legacy files after full validation
3. Consider adding deprecation warnings to legacy files
4. Update documentation to reference new structure

## Implementation Date

Implemented: {{ current_date }}
Status: Active with backwards compatibility maintained