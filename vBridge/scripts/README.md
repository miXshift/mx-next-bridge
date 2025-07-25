# Scripts Directory

This directory contains utility and maintenance scripts for the MixBridge v2 project.

## Directory Structure

### `analysis/`
Scripts for analyzing calculation results and identifying issues:
- `analyze_acos_issues.py` - Investigates ACoS calculation issues
- `analyze_headers.py` - Examines data header structures  
- `analyze_roas_contributions.py` - Analyzes ROAS contribution calculations
- `advanced_filtering_analysis.py` - Advanced filtering logic analysis

### `debugging/`
Scripts for debugging and investigating specific issues:
- `debug_acos_issue.py` - Debugs ACoS calculation problems
- `compare_campaign_lists.py` - Compares campaign data between sources
- `check_current_totals.py` - Validates total calculations
- `find_campaign.py` - Locates specific campaigns in data
- `find_filtering_rule.py` - Identifies filtering rule applications
- `get_all_kpis.py` - Retrieves all KPI definitions
- `investigate_differences.py` - Investigates data discrepancies

### `verification/`
Scripts for verifying calculation results and mathematical consistency:
- `verify_all_12_kpis.py` - Verifies all 12 KPI calculations
- `verify_all_contributions.py` - Validates contribution calculations
- `verify_mixrate_bridge.py` - Verifies MixRate Bridge implementation
- `totals_comparison.py` - Compares total row calculations
- `test_cpa_aov_integration.py` - Tests CPA and AOV KPI integration
- `test_cpa_aov_calculation.py` - Tests CPA and AOV calculation accuracy

### Root Scripts
- `demo_improved_output.py` - Demonstrates improved output formatting
- `output_manager_cli.py` - Command-line interface for output management

## Usage

All scripts can be run from the project root directory:

```bash
# Run analysis scripts
python scripts/analysis/analyze_acos_issues.py

# Run debugging scripts  
python scripts/debugging/debug_acos_issue.py

# Run verification scripts
python scripts/verification/verify_mixrate_bridge.py

# Run CLI tools
python scripts/output_manager_cli.py
```

## Purpose

These scripts were moved from the root directory to improve project organization and make it easier to find specific debugging and analysis tools.