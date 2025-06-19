# vBridge2 - KPI Analysis and Mix/Rate Bridge Calculator

A comprehensive Python system for calculating Key Performance Indicators (KPIs) from advertising campaign data and performing advanced mix/rate bridge analysis.

> 📚 **New to this project?** See the [📖 Project Overview](PROJECT_OVERVIEW.md) for a complete documentation guide and navigation help.

## 🚀 Quick Start

```bash
# Activate virtual environment (recommended)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Run complete analysis using the modular system
python scripts/vBridge.py

# Validate implementation
python scripts/test_complete_analysis.py
```

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Output Structure](#output-structure)
- [Configuration](#configuration)
- [Testing](#testing)

## Overview

vBridge2 implements a systematic 4-step process for advertising KPI analysis:

1. **KPI Calculation**: Calculates 14 direct and derived advertising KPIs
2. **Mix Contribution**: Analyzes contribution of campaigns to absolute metric changes
3. **Mix Rate Contribution**: Decomposes calculated KPI changes into mix and rate effects
4. **ACoS/ROAS Infinity Handling**: Special handling for ACoS/ROAS bridge calculations

### Key Features

- ✅ **Complete Coverage**: All 14 KPIs processed systematically
- ✅ **Modular Architecture**: Clean, maintainable, and extensible code structure
- ✅ **Robust Error Handling**: Graceful handling of edge cases and missing data
- ✅ **Comprehensive Testing**: Full test suite with validation
- ✅ **Flexible Configuration**: Easy customization of column mappings and formatting
- ✅ **Rich Output**: 21+ output files with proper formatting

## Architecture

The system uses a **modular architecture** with clean separation of concerns:

### Core Components (`scripts/` modules)
- **`vBridge.py`**: Main entry point and compatibility layer
- **`vbridge_main.py`**: Main orchestrator class
- **`config_manager.py`**: Configuration and formatting management
- **`data_processor.py`**: Data loading and preprocessing
- **`analysis_steps.py`**: All analysis step implementations
- **Test suites**: Comprehensive testing framework

### Benefits
- ✅ **Testable**: Individual modules can be tested in isolation
- ✅ **Maintainable**: Clean separation of concerns
- ✅ **Extensible**: Easy to add new analysis steps
- ✅ **Reusable**: Components can be used independently

See [📖 Modular Documentation](scripts/README_MODULAR.md) for detailed architecture information.

## Installation

### Prerequisites

**Option 1: Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Option 2: Global Installation**

```bash
pip install pandas numpy openpyxl python-dateutil matplotlib
```

### Setup

1. Clone or download the project
2. **Set up virtual environment** (see Prerequisites above)
3. Place your CSV data file in the project root
4. Configure analysis parameters (see [Configuration](#configuration))

## Usage

### Basic Usage

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
```

### Command Line Usage

```bash
# Activate virtual environment first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Run complete analysis with default settings
python scripts/vBridge.py
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

## Documentation

| Document | Purpose |
|----------|---------|
| [📖 Main README](README.md) | This overview and quick start guide |
| [📖 vBridge Modular](README_vBridge.md) | Detailed modular architecture documentation |
| [📖 Modular Structure](scripts/README_MODULAR.md) | File structure and module breakdown |
| [📖 Output Structure](output/README.md) | Generated files and directory organization |
| [📖 Implementation Summary](IMPLEMENTATION_SUMMARY.md) | Development history and improvements |

### Detailed Function Documentation

For comprehensive function documentation, formulas, and implementation details, see the sections below:

<details>
<summary><strong>Step 1: KPI Calculation</strong></summary>

Calculates all 14 KPIs from raw campaign data:

**Absolute Metrics (9):**
- Spend, Total Ad Sales, Impressions, Clicks, Total Ad Orders
- Same SKU Ad Sales, Other SKU Sales, Same SKU Ad Orders, Other SKU Ad Orders

**Calculated Metrics (5):**
- ACoS, ROAS, Conversion Rate, CTR, CPC

**Key Functions:**
- `load_and_preprocess_data()` - Data loading and cleaning
- `aggregate_data_for_period()` - Period-based aggregation
- `calculate_kpis()` - KPI computation with zero-division handling

</details>

<details>
<summary><strong>Step 2: Mix Contribution (Absolute Metrics)</strong></summary>

Calculates contribution of each campaign to total change in absolute metrics using the Rate Change formula.

**Formula:**
```
Contribution (BPS) = (P2_Value - P1_Value) / P1_Total * 10000
```

**Function:**
- `calculate_absolute_metric_contribution()` - Rate contribution in basis points

</details>

<details>
<summary><strong>Step 3: Mix Rate Contribution (Calculated KPIs)</strong></summary>

Decomposes calculated KPI changes into mix effects and rate effects using the Mixed Rate Change formula.

**Formulas:**
```
Mix Impact = (P2_Mix - P1_Mix) × (P2_KPI - P2_Total_KPI)
Rate Impact = (P2_KPI - P1_KPI) × P1_Mix
Total Contribution = Mix Impact + Rate Impact
```

**Function:**
- `calculate_mix_rate_contribution()` - Mix and rate decomposition

</details>

<details>
<summary><strong>Step 4: ACoS/ROAS Infinity Handling</strong></summary>

Special handling for ACoS and ROAS calculations when sales approach zero, using ROAS transformation method.

**Function:**
- `calculate_acos_roas_bridge_contribution()` - Infinity-safe ACoS/ROAS analysis

</details>

## Output Structure

The system generates organized outputs in the `output/` directory:

```
output/
├── step2_absolute_contributions/     # 9 absolute metric files + combined
├── step3_mix_rate_contributions/     # 5 calculated KPI files  
├── step4_acos_roas_final/           # Final ACoS/ROAS contributions
└── summary_reports/                 # Formatted KPIs and MoM changes
```

See [📖 Output Documentation](output/README.md) for complete file descriptions.

## Configuration

### Column Mappings

```python
# Default column configuration
CAMPAIGN_ID_COL = 'CampaignID'
CAMPAIGN_NAME_COL = 'CampaignName'
DATE_COL = 'DateKey'
COST_COL = 'Cost'
CLICKS_COL = 'Clicks'
IMPRESSIONS_COL = 'Impressions'

# Attribution columns (7-day default)
SALES_COL_ATTR = 'AttributedSales7day'
ORDERS_COL_ATTR = 'AttributedConversions7day'
```

### KPI Formatting

The system uses semantic formatting types defined in `kpi_format.py`:

- **`currency`**: $1,234.56 (2 decimals)
- **`percentage`**: 13.1% (1 decimal)
- **`percentage_precise`**: 12.45% (2 decimals)
- **`integer`**: 1,234 (whole numbers)
- **`decimal`**: 3.45 (2 decimals)
- **`bps`**: +150 BPS (basis points)

### Analysis Periods

Configure your analysis periods in the main script:

```python
# Example: January vs February 2025
p1_start_date = pd.to_datetime('2025-01-01')
p1_end_date = pd.to_datetime('2025-01-31')
p2_start_date = pd.to_datetime('2025-02-01')
p2_end_date = pd.to_datetime('2025-02-28')
```

## Testing

### Run Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Comprehensive integration tests
python scripts/test_complete_analysis.py

# Modular component tests
python scripts/test_vbridge.py
```

### Expected Test Output

```
============================================================
TEST SUMMARY
============================================================
✓ Step 1: KPI Calculation: PASSED
✓ Step 2: Absolute Contributions: PASSED
✓ Step 3: Mix Rate Contributions: PASSED
✓ Step 4: ACoS/ROAS Handling: PASSED
✓ Complete Integration: PASSED

🎉 ALL TESTS PASSED!
```

## Migration Guide

### From Previous Versions

If upgrading from earlier implementations:

1. **Use only** the modular `vBridge.py` system
2. **Update automation** to call `python scripts/vBridge.py`
3. **Review outputs** - now generates 21+ files with comprehensive coverage
4. **Test thoroughly** - run the test suite to validate

### Backward Compatibility

The system maintains backward compatibility:
- Existing import statements continue to work
- Same output formats and file structures
- All previous functionality preserved

## Support and Development

### Key Improvements Made

1. ✅ **Unified Sequential Process**: All 4 steps in proper sequence
2. ✅ **Complete Coverage**: All 14 KPIs processed systematically  
3. ✅ **Modular Architecture**: Clean, maintainable code structure
4. ✅ **Comprehensive Testing**: Full validation suite
5. ✅ **Rich Documentation**: Multiple documentation levels
6. ✅ **Robust Error Handling**: Graceful edge case management

### Future Enhancements

- Database integration (MongoDB support)
- Web interface for interactive analysis
- API endpoints for programmatic access
- Advanced attribution window handling
- Custom mix driver logic

---

**For detailed implementation information, see [📖 Implementation Summary](IMPLEMENTATION_SUMMARY.md)**