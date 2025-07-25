# MixBridge v2 - Campaign Bridge Analysis Tool

A Python application that replicates Excel-based marketing campaign bridge reporting, converting daily campaign data into automated month-over-month performance analysis with **EXCELLENT accuracy** and 10-decimal precision, featuring resolved contribution calculations and decimal percentage format.

> **v2.0 Update**: The source code has been restructured into a modular architecture for better organization and maintainability. See [documentation](docs/) for migration guidance.

## Overview

This tool processes daily campaign performance data and generates bridge reports that analyze variance between time periods using Mix Bridge methodology. It replicates the functionality of complex Excel reports while enabling automated processing of large datasets.

## Project Structure

```
vBridge/
├── README.md                 # This file
├── src/                      # Modular source code (v2.0)
│   ├── core/                 # Calculation engines
│   ├── data/                 # Data processing & validation  
│   ├── output/               # Output formatting & management
│   ├── config/               # Configuration & definitions
│   ├── common/               # Shared infrastructure
│   └── [legacy files]        # Legacy compatibility files
├── scripts/                  # Analysis, debugging & verification tools
│   ├── analysis/
│   ├── debugging/
│   └── verification/
├── utils/                    # Excel comparison & validation system
│   ├── enhanced_comparison_system.py
│   ├── modules/              # Reusable comparison components
│   └── archive/              # Legacy analysis tools  
├── docs/                     # Comprehensive documentation
│   ├── README.md             # Documentation overview
│   ├── user-guide.md         # Step-by-step usage guide
│   ├── api-reference.md      # Complete API documentation
│   ├── scripts-vs-utils-guide.md  # Development workflows
│   └── archive/              # Historical documentation
├── data/                     # Source data files
│   ├── Hydrapak YTD - campaign.csv
│   ├── HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx
│   ├── Vertical Bridge Technical Scoping Document - 3.11.2025.docx.txt
│   ├── kpi_formula_analysis.json
│   └── kpi_formula_analysis_detailed.json
├── output/                   # Generated reports
│   └── period_comparison.csv # Main output with two-tier headers
└── venv/                     # Python virtual environment
```

## Key Features

- **Automated Bridge Analysis**: Converts daily campaign data into month-over-month variance analysis
- **Enhanced Zero Baseline Handling**: Three sophisticated strategies for P1=0 scenarios (dummy_value, delta_assignment, hybrid)
- **High-Precision Calculations**: 10-decimal precision eliminates rounding errors
- **Comprehensive Validation**: 6-check validation framework with detailed reporting
- **Flexible Configuration**: Profile-based configuration management (production, development, performance, accuracy)
- **Decimal Percentage Format**: Consistent 0.17 format instead of 17% for precise comparisons
- **Complete Contribution Calculations**: Includes all metrics including zero baseline campaigns
- **Two-Tier Headers**: Clean output format with KPI groupings and dimensional analysis
- **Mix Bridge Methodology**: Implements proper variance decomposition formulas with division-by-zero protection
- **14 Metric Groups**: Processes spend, sales, ROAS, ACoS, CTR, conversions, and more
- **Scalable Processing**: Handles 9,000+ daily records efficiently
- **Modular Architecture**: Clean separation of concerns for maintainability
- **Backward Compatibility**: 100% compatible with existing implementations
- **Production Ready**: Comprehensive validation and resolved calculation issues

## Quick Start

### Installation

1. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install pandas openpyxl xlrd numpy
   ```

### Usage

1. **Basic Usage (Enhanced - Recommended)**:
   ```bash
   # Run with hybrid strategy (default, handles zero baseline scenarios)
   python src/campaign_bridge_modular.py
   
   # Run with specific zero baseline handling strategy
   python src/campaign_bridge_modular.py delta_assignment  # Most accurate
   python src/campaign_bridge_modular.py dummy_value       # Fastest
   python src/campaign_bridge_modular.py hybrid           # Balanced (default)
   
   # Disable validation for performance
   python src/campaign_bridge_modular.py hybrid --no-validate
   ```

2. **Legacy Usage**:
   ```bash
   # Original monolithic version (still supported)
   python src/campaign_bridge.py
   ```

3. **View Results**:
   - Output saved to `output/period_comparison.csv`
   - Two-tier header format for easy analysis
   - 156 campaigns analyzed with 14 metric groups
   - 10-decimal precision with decimal percentage format (0.17 vs 17%)
   - Zero baseline campaigns properly handled with contribution attribution

## Output Format

The generated CSV features a **two-tier header structure**:

```
Row 1: Campaign Name | Spend | Spend | Spend | Spend | Spend | Total Ad Sales | ...
Row 2:             | Jan 2025 | Feb 2025 | Net Change | % Change | Contribution | Jan 2025 | ...
```

### 14 Metric Groups Analyzed:
1. **Spend** - Advertising investment
2. **Total Ad Sales** - Revenue generated  
3. **ACoS** - Advertising Cost of Sales
4. **ROAS** - Return on Ad Spend
5. **Conversion Rate** - Orders/Clicks efficiency
6. **Impressions** - Ad visibility
7. **Clicks** - Ad engagement
8. **CTR** - Click-through rate
9. **CPC** - Cost per click
10. **Same SKU Ad Sales** - Direct product sales
11. **Other SKU Sales** - Cross-sell revenue
12. **Same SKU Ad Orders** - Direct conversions
13. **Other SKU Ad Orders** - Cross-sell conversions
14. **Total Ad Orders** - All conversions

## Validation & Accuracy

### Comprehensive Testing ✅
- **EXCELLENT accuracy** with resolved calculation issues
- **All contribution calculations** now working correctly for all metric types
- **10-decimal precision** eliminates rounding errors
- **Decimal percentage format** ensures consistent comparisons
- **Rate metrics** (ACoS, ROAS, CTR, Conversion Rate) now properly calculated
- **Data scope differences** identified and explained (Excel: 55 campaigns vs CSV: 156)

### Validation Tools
```bash
# Compare outputs with Excel (updated for decimal format)
python utils/detailed_campaign_comparison.py

# Investigate contribution calculations
python utils/investigate_contribution_zeros.py

# Analyze data source differences
python utils/investigate_data_source_differences.py

# Create discrepancy analysis reports
python utils/discrepancy_analysis.py
```

## Data Processing Details

### Input Data
- **Source**: `data/Hydrapak YTD - campaign.csv`
- **Records**: 9,478 daily campaign performance records
- **Time Period**: January 2025 vs February 2025
- **Campaigns**: 156 unique campaigns processed

### Processing Logic
1. **Date Aggregation**: Groups daily data by campaign and period
2. **Rate Calculations**: Computes ACoS, ROAS, CTR, conversion rates as decimals (not percentages)
3. **Mix Bridge Analysis**: Applies variance decomposition methodology with formula: `p1_mix * growth_rate * 10000`
4. **Contribution Calculations**: Includes ALL metrics (absolute and rate) in contribution analysis
5. **High Precision Output**: 10-decimal places for exact calculations

## Customization

### Change Time Periods
Edit date filters in `src/data_processor.py`:
```python
# Update date ranges in DataProcessor.load_data()
self.jan_data = self.df[
    (self.df['Date'] >= '2025-01-01') & 
    (self.df['Date'] <= '2025-01-31')
].copy()
```

### Add New Metrics
1. Update aggregation dictionary in `DataProcessor.aggregate_period_data()`
2. Add calculation logic in `BridgeCalculator` class
3. Include in output formatting in `OutputFormatter` class

## Documentation

### Enhanced MixBridge Documentation (v2.0)
- **[Enhanced MixBridge User Guide](docs/ENHANCED_MIXBRIDGE_USER_GUIDE.md)** - Comprehensive guide to zero baseline handling and new features
- **[Zero Baseline Strategies Guide](docs/ZERO_BASELINE_STRATEGIES_GUIDE.md)** - Technical deep-dive into the three calculation strategies
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation for enhanced modules
- **[PRD vBridge](docs/PRD_V2BRIDGE.md)** - Product requirements and technical architecture

### Legacy Documentation
- **[Development Summary](docs/DEVELOPMENT_SUMMARY.md)** - Complete development process and technical decisions
- **[Skyflask Comparison](docs/SKYFLASK_COMPARISON_REPORT.md)** - Detailed KPI validation for sample campaign
- **[Contribution Analysis](docs/CONTRIBUTION_ANALYSIS_REPORT.md)** - Investigation of formula discrepancies and solutions

### Recent Improvements (Latest)
- ✅ **Fixed rate metrics contributions**: ACoS, ROAS, CTR, Conversion Rate now properly calculated
- ✅ **Implemented decimal percentage format**: 0.17 instead of 17% for consistency
- ✅ **Added 10-decimal precision**: Eliminates all rounding errors
- ✅ **Resolved data scope differences**: Explained Excel vs CSV total variations

### Utility Scripts
```bash
# Excel structure analysis
python utils/analyze_campaign_tab.py

# KPI formula examination  
python utils/analyze_kpi_formulas.py

# Output validation
python utils/compare_outputs.py
```

## Technical Architecture

### Modular Design
- **`data_processor.py`**: Data loading, filtering, and aggregation logic
- **`bridge_calculator.py`**: Bridge calculations and metric computations
- **`output_formatter.py`**: CSV formatting with two-tier headers
- **`campaign_bridge_modular.py`**: Main orchestrator using modular components

### Core Technologies
- **Framework**: Pure Python with pandas for data processing
- **Performance**: Vectorized operations for efficient large dataset handling
- **Accuracy**: Exact Excel formula replication with proper error handling
- **Output**: CSV format maintains data integrity and summable structure
- **Dependencies**: pandas, openpyxl, xlrd, numpy

## Troubleshooting

### Common Issues
1. **File not found**: Ensure data files are in `data/` directory
2. **Missing dependencies**: Run `pip install pandas openpyxl xlrd numpy`
3. **Virtual environment**: Always activate venv before running
4. **Date format**: Ensure DateKey column is YYYYMMDD format

### Getting Help
- Check `docs/` directory for detailed documentation
- Run validation scripts to verify setup
- Review error messages for specific guidance

## Production Status

✅ **Production Ready - ENHANCED WITH ZERO BASELINE HANDLING**
- **EXCELLENT calculation accuracy** with all issues resolved
- **Complete contribution calculations** for all 14 metric types including zero baseline scenarios
- **Zero baseline handling** with three sophisticated strategies (dummy_value, delta_assignment, hybrid)
- **10-decimal precision** eliminates rounding discrepancies
- **Decimal percentage format** ensures consistent data analysis
- **Comprehensive validation framework** with detailed reporting
- **Flexible configuration management** with profiles and persistence
- **Clean, analyzable output format** with proper two-tier headers

### Recent Enhancements (v2.0)
- 🆕 **Added**: Enhanced zero baseline handling with three calculation strategies
- 🆕 **Added**: Comprehensive validation framework with 6 validation checks
- 🆕 **Added**: Configuration management system with profiles
- 🆕 **Added**: Command-line strategy selection and validation control
- 🔧 **Enhanced**: Bridge calculator with strategy parameter and validation
- 🔧 **Enhanced**: Main script with strategy summary and error handling
- ✅ **Result**: Complete solution for P1=0 division by zero scenarios

## License

This project is for internal use and analysis purposes.