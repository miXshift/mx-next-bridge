# vBridge - Modular KPI Analysis Architecture

This document outlines the modular Python implementation for the vBridge2 KPI analysis system. For general usage and overview, see the [📖 Main README](README.md).

## 🏗️ Modular Architecture Overview

The vBridge module implements a clean, modular architecture for the 4-step KPI analysis process with the following benefits:

- **🔧 Maintainable**: Each component has a single responsibility
- **🧪 Testable**: Individual modules can be tested in isolation  
- **🔄 Reusable**: Components can be used independently
- **📈 Extensible**: Easy to add new analysis steps or modify existing ones
- **🐛 Debuggable**: Issues can be isolated to specific modules

## 📁 Core Components

### `ConfigManager`
**Purpose**: Configuration and formatting management

**Key Features**:
- Loads KPI format configuration from `kpi_format.py`
- Manages column mappings and KPI name translations
- Provides semantic formatting functions (currency, percentage, BPS, etc.)
- Handles bridge type configuration (M, MR, MR+I)

### `DataProcessor`
**Purpose**: Data loading, preprocessing, and aggregation

**Key Features**:
- CSV loading with robust error handling
- Dynamic attribution column selection (14-day vs 7-day)
- Date conversion and data cleaning
- Campaign-based aggregation for analysis periods

### Analysis Steps (All inherit from `AnalysisStep`)

#### `Step1KPICalculation`
- Calculates all 14 KPIs for both periods
- Generates totals for validation
- Passes results to subsequent steps

#### `Step2AbsoluteContributions`
- Processes all 9 absolute metrics (bridge_type = "M")
- Applies Rate Change formula
- Generates individual and combined contribution files

#### `Step3MixRateContributions`
- Processes all 5 calculated KPIs (bridge_type = "MR")
- Applies Mixed Rate Change formula
- Handles proper mix drivers and BPS scaling

#### `Step4AcosRoasInfinityHandling`
- Special handling for ACoS/ROAS (bridge_type = "MR+I")
- Uses ROAS transformation for infinity cases
- Generates final corrected contributions

#### `SummaryReportGenerator`
- Creates formatted summary reports
- Generates MoM change analysis
- Saves period KPIs with proper formatting

### `VBridge` (Main Orchestrator)
**Purpose**: Coordinates all analysis steps

**Key Features**:
- Initializes all components
- Manages execution flow
- Provides simple interface for complete analysis
- Returns structured results

## 🚀 Usage Examples

### Setup (First Time)

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage (Recommended)

```python
from scripts.vBridge import VBridge

# Initialize and run complete analysis
vbridge = VBridge(output_dir='output')
results = vbridge.run_complete_analysis(
    csv_file_path='your_data.csv',
    p1_start_date='2025-01-01',
    p1_end_date='2025-01-31',
    p2_start_date='2025-02-01',
    p2_end_date='2025-02-28'
)

# Access results
print(f"Analysis completed with {len(results['p1_kpis'])} campaigns")
```

### Advanced Usage - Individual Components

```python
from scripts.config_manager import ConfigManager
from scripts.data_processor import DataProcessor
from scripts.analysis_steps import Step1KPICalculation

# Initialize components
config = ConfigManager()
processor = DataProcessor(config)
step1 = Step1KPICalculation(config, 'output')

# Load and process data
df = processor.load_and_preprocess_data('your_data.csv')

# Run individual steps
p1_kpis, p2_kpis, p1_totals, p2_totals = step1.execute(
    df, p1_start, p1_end, p2_start, p2_end
)
```

### Custom Configuration

```python
from scripts.config_manager import ConfigManager

# Customize configuration
config = ConfigManager()
config.CAMPAIGN_NAME_COL = 'YourCampaignColumn'
config.DATE_COL = 'YourDateColumn'

# Use with other components
from scripts.vbridge_main import VBridge
vbridge = VBridge(config=config, output_dir='custom_output')
```

## 📊 Output Structure

The modular system maintains organized outputs:

```
output/
├── step1_kpi_calculation/      # (Calculations in memory)
├── step2_absolute_contributions/
│   ├── spend_absolute_contribution.csv
│   ├── total_ad_sales_absolute_contribution.csv
│   ├── ... (7 more files)
│   └── all_absolute_metric_contributions.csv
├── step3_mix_rate_contributions/
│   ├── clickthrough_rate_mix_rate_contributions.csv
│   ├── conversion_rate_mix_rate_contributions.csv
│   ├── cost_per_click_mix_rate_contributions.csv
│   ├── acos_mix_rate_contributions.csv
│   └── roas_mix_rate_contributions.csv
├── step4_acos_roas_final/
│   └── acos_roas_final_contributions.csv
└── summary_reports/
    ├── campaign_kpis_mom_change.csv
    ├── p1_campaign_kpis.csv
    ├── p2_campaign_kpis.csv
    ├── p1_totals_kpis.csv
    └── p2_totals_kpis.csv
```

See [📖 Output Documentation](output/README.md) for detailed file descriptions.

## 🔧 Configuration

### KPI Format Configuration

The system uses `kpi_format.py` with semantic formatting types:

```python
"Spend": {
    "bridge_type": "M",
    "calc_from": "Cost",
    "formats": {
        "period_values": {"type": "currency"},
        "net_change": {"type": "currency"},
        "percent_change": {"type": "percentage"},
        "contribution": {"type": "bps"}
    }
}
```

**Available Format Types**:
- `currency`: $1,234.56
- `percentage`: 13.1%
- `percentage_precise`: 12.45%
- `integer`: 1,234
- `decimal`: 3.45
- `bps`: +150 BPS

### Bridge Types

- **`M`**: Mix analysis for absolute metrics
- **`MR`**: Mix Rate analysis for calculated metrics
- **`MR+I`**: Mix Rate with infinity handling for ACoS/ROAS

## 🧪 Testing

### Run Modular Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# Test individual components
python scripts/test_vbridge.py

# Test complete integration
python scripts/test_complete_analysis.py
```

### Test Coverage

The test suite verifies:
- ✅ Configuration management
- ✅ Data processing functionality
- ✅ Component initialization
- ✅ Step class instantiation
- ✅ Integration between components
- ✅ End-to-end workflow

## 🔄 Migration from Previous Versions

### From Earlier Implementations

```python
# Current modular approach
from scripts.vBridge import VBridge
vbridge = VBridge()
results = vbridge.run_complete_analysis(csv_path, p1_start, p1_end, p2_start, p2_end)
```

### Benefits of the Modular System

1. **Better Performance**: Only load needed modules
2. **Easier Testing**: Test individual components
3. **Cleaner Code**: Separation of concerns
4. **Extensibility**: Add new steps easily
5. **Maintainability**: Smaller, focused files

## 🔮 Extending the System

### Adding New Analysis Steps

```python
from scripts.analysis_steps import AnalysisStep

class CustomAnalysisStep(AnalysisStep):
    def execute(self, *args, **kwargs):
        # Your custom analysis logic
        results = self.perform_analysis()
        
        # Save results using inherited methods
        self.save_results(results, 'custom_output.csv')
        
        return results
```

### Custom Formatters

```python
from scripts.config_manager import ConfigManager

class CustomConfigManager(ConfigManager):
    def format_custom_value(self, value):
        # Your custom formatting logic
        return f"Custom: {value}"
```

### New Data Sources

```python
from scripts.data_processor import DataProcessor

class DatabaseProcessor(DataProcessor):
    def load_and_preprocess_data(self, connection_string):
        # Load from database instead of CSV
        return processed_dataframe
```

## 📚 Related Documentation

- [📖 Main README](README.md) - Overview and quick start
- [📖 Modular Structure](scripts/README_MODULAR.md) - Detailed file breakdown
- [📖 Output Structure](output/README.md) - Generated files documentation
- [📖 Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Development history

## 🎯 Key Advantages

1. **🔧 Modular Design**: Each component has a single responsibility
2. **🧪 Comprehensive Testing**: Individual and integration tests
3. **📈 Performance**: Load only what you need
4. **🔄 Reusability**: Use components independently
5. **🐛 Debugging**: Isolate issues to specific modules
6. **📚 Documentation**: Clear separation of concerns
7. **🔮 Future-Proof**: Easy to extend and modify

The modular architecture provides a solid foundation for complex KPI analysis while maintaining simplicity for basic use cases. 