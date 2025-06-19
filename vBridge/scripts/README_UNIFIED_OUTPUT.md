# VBridge Unified Output Feature

## Overview

The VBridge analysis system now supports **unified output mode**, which consolidates all analysis results into a single, well-organized CSV file instead of creating multiple individual files across different directories.

## Usage

### Unified Output Mode (Single File)

```python
from vbridge_main import VBridge

# Initialize with unified output enabled
vbridge = VBridge(output_dir='output', unified_output=True)

# Run analysis - creates single unified file
results = vbridge.run_complete_analysis(
    csv_file_path='your_data.csv',
    p1_start_date='2025-01-01',
    p1_end_date='2025-01-31',
    p2_start_date='2025-02-01',
    p2_end_date='2025-02-28'
)
```

**Output:** Single file `output/vbridge_unified_analysis.csv`

### Individual Files Mode (Original)

```python
from vbridge_main import VBridge

# Initialize with individual files (default)
vbridge = VBridge(output_dir='output', unified_output=False)

# Run analysis - creates multiple files in subdirectories
results = vbridge.run_complete_analysis(
    csv_file_path='your_data.csv',
    p1_start_date='2025-01-01',
    p1_end_date='2025-01-31',
    p2_start_date='2025-02-01',
    p2_end_date='2025-02-28'
)
```

**Output:** Multiple files organized in step-specific subdirectories

## Unified File Structure

The unified output file contains clearly separated sections:

```
================================================================================
SECTION: STEP2_ABSOLUTE_CONTRIBUTIONS_SPEND_ABSOLUTE_CONTRIBUTION
DESCRIPTION: Absolute contribution analysis for Spend - shows how each campaign contributed to the total change in Spend between periods
================================================================================

[Campaign data with contribution analysis]

================================================================================
SECTION: STEP2_ABSOLUTE_CONTRIBUTIONS_TOTAL_AD_SALES_ABSOLUTE_CONTRIBUTION
DESCRIPTION: Absolute contribution analysis for Total Ad Sales - shows how each campaign contributed to the total change in Total Ad Sales between periods
================================================================================

[Campaign data with contribution analysis]

... [Additional sections for all metrics and steps]
```

## Section Types

The unified file includes the following section types:

### Step 2: Absolute Contributions
- Individual metric contributions (9 metrics)
- Combined absolute metric contributions

### Step 3: Mix/Rate Contributions  
- Individual KPI mix/rate contributions (5 KPIs)
- Mix Impact, Rate Impact, and Total Contribution analysis

### Step 4: ACoS/ROAS Final
- Final ACoS/ROAS contributions with infinity handling

### Summary Reports
- Period 1 (P1) campaign KPIs
- Period 2 (P2) campaign KPIs  
- P1 and P2 totals/aggregates
- Month-over-Month (MoM) changes

## Benefits

### Unified Output Mode
✅ **Single file convenience** - Everything in one place  
✅ **Easy sharing** - Send one file instead of multiple  
✅ **Reduced clutter** - No subdirectory management  
✅ **Clear organization** - Sections with descriptions  

### Individual Files Mode
✅ **Step-by-step analysis** - Focus on specific steps  
✅ **Granular access** - Open only needed files  
✅ **Familiar structure** - Original workflow preserved  
✅ **Tool compatibility** - Works with existing scripts  

## Testing

Use the test script to compare both modes:

```bash
python test_unified_output.py
```

This will:
1. Run analysis in unified mode → `output_unified/vbridge_unified_analysis.csv`
2. Run analysis in individual mode → `output_individual/[multiple files]`
3. Compare file sizes and structure
4. Show recommendations

## Migration

### From Individual Files to Unified
Simply change the initialization:

```python
# Old way
vbridge = VBridge(output_dir='output')

# New way  
vbridge = VBridge(output_dir='output', unified_output=True)
```

### Backward Compatibility
The original individual files mode remains the default and unchanged. Existing code will continue to work without modifications.

## File Format Details

- **Format:** CSV with section headers
- **Encoding:** UTF-8
- **Separators:** Section headers use `=` characters (80 wide)
- **Descriptions:** Each section includes a description of its contents
- **Data:** Standard CSV format for each data section

## Performance

- **Memory:** Unified mode uses slightly more memory (collects all data before writing)
- **Speed:** Similar performance to individual files mode
- **File Size:** Unified file is typically smaller than sum of individual files (less overhead)

## Recommendations

- **Use unified output** for final reports, sharing, and archival
- **Use individual files** for development, debugging, and step-specific analysis
- **Both modes** produce identical analytical results 