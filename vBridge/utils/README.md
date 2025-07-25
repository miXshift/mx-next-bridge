# Utils Directory

This directory contains comparison utilities and analysis tools for validating MixBridge calculations against external sources (primarily Excel files).

## Overview

The utils directory provides tools for:
- **Comparison Analysis**: Compare MixBridge outputs with Excel reference files
- **Validation**: Verify calculation accuracy and mathematical consistency  
- **Analysis**: Deep-dive analysis of specific calculation methodologies
- **Reporting**: Generate comparison reports and discrepancy analysis

## Key Tools

### Main Comparison Tools
- `compare_outputs.py` - Basic output comparison functionality
- `compare_enhanced_outputs.py` - Advanced comparison with detailed analysis
- `enhanced_comparison_system.py` - Comprehensive comparison framework
- `generate_comparison_report.py` - Generate detailed comparison reports

### Excel Analysis
- `read_excel.py` - Excel file reading and parsing utilities
- `manual_comparison.py` - Manual comparison workflows

### Specialized Analysis  
- `compare_zero_baseline_handling.py` - Zero baseline scenario validation
- `test_zero_baseline_handling.py` - Zero baseline testing utilities
- `analyze_contribution.py` - Contribution analysis tools

### Modules
The `modules/` subdirectory contains reusable components:
- `bridge_calculations.py` - Bridge calculation utilities
- `data_comparison.py` - Data comparison functions
- `excel_operations.py` - Excel file operations
- `reporting.py` - Report generation utilities
- `validation.py` - Validation and verification functions

## Usage

### Basic Comparison
```bash
# Compare MixBridge output with Excel reference
python utils/compare_outputs.py
```

### Enhanced Analysis
```bash
# Run comprehensive comparison analysis
python utils/enhanced_comparison_system.py

# Generate detailed comparison report
python utils/generate_comparison_report.py
```

### Excel Analysis
```bash
# Read and analyze Excel file structure
python utils/read_excel.py path/to/excel/file.xlsx
```

## Documentation

For detailed documentation on the utils system, see:
- **[Utils Documentation](docs/utils/)** - Complete utils documentation
- **[Comparison System Guide](docs/utils/comparison-system.md)** - Comparison system overview
- **[Utils API Reference](docs/utils/api-reference.md)** - API documentation
- **[Quick Start Guide](docs/utils/quick-start.md)** - Getting started with utils

## Purpose

These utilities are essential for:
1. **Quality Assurance**: Ensuring MixBridge calculations match expected results
2. **Validation**: Verifying mathematical consistency and accuracy
3. **Development**: Supporting development and debugging workflows
4. **Analysis**: Understanding calculation differences and improvements

## Archive

The `archive/` subdirectory contains historical analysis scripts and investigation tools that were used during development but are kept for reference.