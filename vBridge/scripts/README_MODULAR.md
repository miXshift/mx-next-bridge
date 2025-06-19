# vBridge Modular Structure

The vBridge KPI Analysis system has been refactored from a single large file (985 lines) into a modular structure for better maintainability, readability, and extensibility.

## 📁 File Structure

```
scripts/
├── __init__.py                 # Package initialization
├── config_manager.py          # Configuration and formatting management
├── data_processor.py          # Data loading and preprocessing
├── analysis_steps.py          # All analysis step implementations
├── vbridge_main.py            # Main orchestrator class
├── vBridge.py                 # Compatibility layer (imports from modules)
├── test_vbridge.py            # Unit tests
├── test_complete_analysis.py  # Integration tests
└── README_MODULAR.md          # This file
```

## 🔧 Module Breakdown

### 1. `config_manager.py` (118 lines)
**Purpose**: Manages configuration and formatting for KPI analysis

**Key Components**:
- `ConfigManager` class
- KPI format loading from `kpi_format.py`
- Column name mappings
- Value formatting methods
- Bridge type configuration

**Main Methods**:
- `format_value()` - Format values according to specifications
- `format_change_value()` - Format change values with proper units
- `format_contribution_value()` - Format contribution values
- `get_bridge_type()` - Get bridge type for KPIs

### 2. `data_processor.py` (105 lines)
**Purpose**: Handles data loading, preprocessing, and aggregation

**Key Components**:
- `DataProcessor` class
- CSV loading and validation
- Date conversion and column selection
- Data aggregation by campaign and period

**Main Methods**:
- `load_and_preprocess_data()` - Load and clean CSV data
- `aggregate_data_for_period()` - Aggregate metrics by campaign for date ranges
- `_select_attribution_columns()` - Dynamically select 14-day vs 7-day attribution

### 3. `analysis_steps.py` (550 lines)
**Purpose**: Contains all analysis step implementations

**Key Components**:
- `AnalysisStep` (abstract base class)
- `Step1KPICalculation` - Calculate all KPIs for both periods
- `Step2AbsoluteContributions` - Calculate absolute metric contributions
- `Step3MixRateContributions` - Calculate mix/rate contributions
- `Step4AcosRoasInfinityHandling` - Handle ACoS/ROAS infinity cases
- `SummaryReportGenerator` - Generate formatted reports

**Each Step Includes**:
- Organized output directories
- Error handling and validation
- Progress reporting
- Formatted CSV outputs

### 4. `vbridge_main.py` (130 lines)
**Purpose**: Main orchestrator that coordinates all analysis steps

**Key Components**:
- `VBridge` class (main entry point)
- Complete 4-step analysis workflow
- Results aggregation and reporting

**Main Method**:
- `run_complete_analysis()` - Execute the full analysis pipeline

### 5. `vBridge.py` (35 lines)
**Purpose**: Backward compatibility layer

**Key Components**:
- Imports all classes from modular structure
- Maintains existing API
- Preserves main execution block

## 🚀 Usage

### Setup (First Time)

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Option 1: Use the main orchestrator (recommended)
```python
from vbridge_main import VBridge

# Initialize and run analysis
vbridge = VBridge(output_dir='output')
results = vbridge.run_complete_analysis(
    csv_file_path='data.csv',
    p1_start_date='2025-01-01',
    p1_end_date='2025-01-31', 
    p2_start_date='2025-02-01',
    p2_end_date='2025-02-28'
)
```

### Option 2: Use individual modules
```python
from config_manager import ConfigManager
from data_processor import DataProcessor
from analysis_steps import Step1KPICalculation

# Use individual components
config = ConfigManager()
processor = DataProcessor(config)
step1 = Step1KPICalculation(config, 'output')
```

### Option 3: Backward compatibility
```python
# This still works exactly as before
from vBridge import VBridge

vbridge = VBridge()
results = vbridge.run_complete_analysis(...)
```

## 📊 Output Structure

The modular system maintains the same organized output structure:

```
output/
├── step1_kpi_calculation/      # (No direct files - calculations in memory)
├── step2_absolute_contributions/
│   ├── spend_absolute_contribution.csv
│   ├── total_ad_sales_absolute_contribution.csv
│   ├── ... (9 total files)
│   └── all_absolute_metric_contributions.csv
├── step3_mix_rate_contributions/
│   ├── clickthrough_rate_mix_rate_contributions.csv
│   ├── conversion_rate_mix_rate_contributions.csv
│   ├── ... (5 total files)
├── step4_acos_roas_final/
│   └── acos_roas_final_contributions.csv
└── summary_reports/
    ├── campaign_kpis_mom_change.csv
    ├── p1_campaign_kpis.csv
    ├── p2_campaign_kpis.csv
    ├── p1_totals_kpis.csv
    └── p2_totals_kpis.csv
```

## ✅ Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Readability**: Smaller files are easier to understand and navigate
3. **Testability**: Individual modules can be tested in isolation
4. **Extensibility**: New analysis steps can be added easily
5. **Reusability**: Components can be used independently
6. **Debugging**: Issues can be isolated to specific modules
7. **Collaboration**: Multiple developers can work on different modules

## 🔄 Migration Guide

### For Existing Code
- **No changes required** - the original `vBridge.py` import still works
- All existing scripts and tests continue to function

### For New Development
- Import from specific modules for better performance
- Use `vbridge_main.VBridge` as the main entry point
- Extend `AnalysisStep` to create new analysis steps

## 🧪 Testing

The existing test files continue to work:
- `test_vbridge.py` - Unit tests for individual components
- `test_complete_analysis.py` - Integration tests for full workflow

## 📈 Performance

- **Faster imports**: Only load needed modules
- **Memory efficiency**: Modules loaded on demand
- **Better error isolation**: Issues contained to specific modules

## 🔮 Future Enhancements

The modular structure enables:
- Plugin architecture for custom analysis steps
- Configuration-driven analysis workflows
- Parallel processing of independent steps
- API endpoints for individual modules
- Docker containerization of specific components 