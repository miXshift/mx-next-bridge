# MixBridge v2 Source Restructure Guide

## Quick Reference

### New Import Structure

| **Module Type** | **New Location** | **Legacy Location** |
|-----------------|-------------------|---------------------|
| **Core Calculators** | `src.core.*` | `src.*` |
| **Data Processing** | `src.data.*` | `src.*` |
| **Output Management** | `src.output.*` | `src.*` |
| **Configuration** | `src.config.*` | `src.*` |
| **Common Utils** | `src.common.*` | `src.*` |

### Quick Migration Examples

```python
# OLD → NEW
from src.bridge_calculator import BridgeCalculator
from src.core.bridge_calculator import BridgeCalculator

from src.metric_definitions import MetricDefinitions  
from src.config.metrics import MetricDefinitions

from src.mixbridge_validator import MixBridgeValidator
from src.data.validator import MixBridgeValidator

from src.exceptions import ValidationError
from src.common.exceptions import ValidationError
```

## Documentation Updates Applied

### ✅ Main Documentation Files
- **`docs/README.md`**: Added modular structure overview and updated examples
- **`docs/api-reference.md`**: Complete restructure with new module organization
- **`docs/user-guide.md`**: Added new modular API section and migration guide

### ✅ Configuration & Usage
- **`docs/configuration.md`**: Updated import statements for new structure
- **Project `README.md`**: Added v2.0 restructure notice and updated project structure

### ✅ New Documentation Added
- **`src/RESTRUCTURE.md`**: Detailed technical documentation of the restructure
- **`docs/scripts-vs-utils-guide.md`**: Guide for when to use utils vs scripts
- **`docs/v2-restructure-guide.md`**: This quick reference guide

## Backwards Compatibility

✅ **All legacy imports still work** - no breaking changes  
✅ **Legacy API methods remain functional**  
✅ **Existing workflows continue to work without modification**

## Benefits

1. **Logical Organization**: Related functionality grouped together
2. **Easier Navigation**: Developers can quickly find relevant code  
3. **Better Testing**: Each module can be tested independently
4. **Clearer Boundaries**: Separation of concerns between modules
5. **Improved Maintainability**: Centralized configuration and utilities

## Migration Timeline

- **Phase 1** ✅: Create modular structure 
- **Phase 2** ✅: Move files with backwards compatibility
- **Phase 3** ✅: Update external scripts and tests
- **Phase 4** ✅: Update documentation
- **Future**: Remove legacy files after full adoption

## Key Files Updated

### Python Files (5)
- `scripts/analysis/analyze_acos_issues.py`
- `scripts/analysis/analyze_roas_contributions.py` 
- `scripts/verification/verify_all_contributions.py`
- `scripts/verification/verify_all_12_kpis.py`
- `tests/test_mixbridge_validator.py`

### Documentation Files (5)
- `docs/README.md` - Added modular structure section
- `docs/api-reference.md` - Complete restructure
- `docs/user-guide.md` - Added new API and migration guide
- `docs/configuration.md` - Updated imports
- `README.md` - Added v2.0 notice

### New Files Created (3)
- `src/RESTRUCTURE.md` - Technical documentation
- `docs/scripts-vs-utils-guide.md` - Development workflow guide
- `docs/v2-restructure-guide.md` - This quick reference

## Status

🎯 **Complete**: All documentation reflects the new modular structure while maintaining full backwards compatibility. Developers can use either the new recommended imports or legacy imports during transition.