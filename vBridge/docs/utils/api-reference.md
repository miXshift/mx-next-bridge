# API Reference - Enhanced MixBridge Comparison System

## Core Classes

### EnhancedComparisonEngine

Main comparison engine for analyzing enhanced MixBridge outputs.

```python
class EnhancedComparisonEngine:
    def __init__(self, config: ComparisonConfig = None)
```

#### Methods

##### `load_excel_source() -> bool`
Loads Excel source of truth data.

**Returns**: `bool` - Success status
**Side Effects**: Populates `self.excel_df`

```python
engine = EnhancedComparisonEngine()
success = engine.load_excel_source()
```

##### `load_csv_output(csv_path: str) -> bool`
Loads enhanced CSV output data.

**Parameters**:
- `csv_path`: Path to CSV file

**Returns**: `bool` - Success status
**Side Effects**: Populates `self.csv_df`

```python
success = engine.load_csv_output('output/analyses/mixbridge_latest.csv')
```

##### `find_latest_csv() -> Optional[str]`
Finds the most recent CSV file in the configured directory.

**Returns**: `Optional[str]` - Path to latest CSV file or None if not found

```python
latest_csv = engine.find_latest_csv()
if latest_csv:
    engine.load_csv_output(latest_csv)
```

##### `compare_campaign_coverage() -> Dict[str, Any]`
Analyzes campaign coverage between Excel and CSV data.

**Returns**: Dictionary containing:
- `excel_campaigns`: Number of campaigns in Excel
- `csv_campaigns`: Number of campaigns in CSV
- `common_campaigns`: Number of shared campaigns
- `coverage_rate`: Percentage coverage
- `excel_only`: Count of Excel-only campaigns
- `csv_only`: Count of CSV-only campaigns
- `excel_only_list`: List of Excel-only campaign names (first 10)
- `csv_only_list`: List of CSV-only campaign names (first 10)

```python
coverage = engine.compare_campaign_coverage()
print(f"Coverage rate: {coverage['coverage_rate']:.1f}%")
```

##### `compare_total_metrics() -> Dict[str, Any]`
Compares total row metrics for accuracy assessment.

**Returns**: Dictionary containing:
- `metric_results`: List of individual metric comparisons
- `metrics_compared`: Number of metrics successfully compared
- `average_error`: Average relative error percentage
- `maximum_error`: Maximum relative error percentage
- `accuracy_score`: Overall accuracy score (100 - average_error)
- `overall_grade`: Grade (PERFECT/EXCELLENT/GOOD/FAIR/POOR)
- `grade_emoji`: Corresponding emoji indicator

```python
totals = engine.compare_total_metrics()
print(f"Overall grade: {totals['overall_grade']}")
print(f"Accuracy: {totals['accuracy_score']:.2f}%")
```

##### `compare_sample_campaigns(sample_size: int = 5) -> Dict[str, Any]`
Performs detailed verification on a sample of campaigns.

**Parameters**:
- `sample_size`: Number of campaigns to sample (default: 5)

**Returns**: Dictionary containing:
- `sample_size`: Actual number of campaigns sampled
- `campaign_results`: List of campaign comparison results

```python
samples = engine.compare_sample_campaigns(sample_size=10)
for result in samples['campaign_results']:
    print(f"Campaign: {result['campaign']}")
    for metric in result['metrics']:
        print(f"  {metric['metric']}: {metric['status']}")
```

##### `run_comprehensive_analysis(csv_path: Optional[str] = None) -> Dict[str, Any]`
Executes complete comparison analysis pipeline.

**Parameters**:
- `csv_path`: Optional path to specific CSV file (auto-detects if None)

**Returns**: Complete analysis results dictionary containing all comparison results

```python
results = engine.run_comprehensive_analysis()
# Results contain campaign_coverage, total_metrics, sample_campaigns
```

##### `save_results(results: Dict[str, Any])`
Saves comparison results to JSON file with timestamp.

**Parameters**:
- `results`: Results dictionary from comparison analysis

**Side Effects**: Creates JSON file in configured output directory

```python
engine.save_results(results)
# Creates: output/reports/comparison_results_YYYYMMDD_HHMMSS.json
```

##### `generate_summary_report(results: Dict[str, Any]) -> str`
Generates formatted text summary of comparison results.

**Parameters**:
- `results`: Results dictionary from comparison analysis

**Returns**: Formatted summary string

```python
summary = engine.generate_summary_report(results)
print(summary)
```

### ComparisonConfig

Configuration dataclass for comparison parameters.

```python
@dataclass
class ComparisonConfig:
    excel_path: str = 'data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx'
    csv_directory: str = 'output/analyses'
    output_directory: str = 'output/reports'
    tolerance: float = 0.01
    significant_digits: int = 4
    include_campaign_level: bool = True
    include_total_level: bool = True
    generate_html: bool = True
    generate_summary: bool = True
    save_detailed_results: bool = True
```

#### Parameters

- **excel_path**: Path to Excel source file
- **csv_directory**: Directory containing CSV outputs
- **output_directory**: Directory for saving results
- **tolerance**: Numeric comparison tolerance
- **significant_digits**: Precision for numeric comparisons
- **include_campaign_level**: Enable campaign-level analysis
- **include_total_level**: Enable total-level analysis
- **generate_html**: Enable HTML report generation
- **generate_summary**: Enable summary report generation
- **save_detailed_results**: Enable detailed results saving

## Standalone Functions

### compare_enhanced_outputs.py

#### `load_excel_source(excel_path: str) -> pd.DataFrame`
Loads Excel source with header detection.

**Parameters**:
- `excel_path`: Path to Excel file

**Returns**: `pd.DataFrame` - Loaded Excel data

```python
excel_df = load_excel_source('data/source.xlsx')
```

#### `load_csv_output(csv_path: str) -> pd.DataFrame`
Loads enhanced CSV output.

**Parameters**:
- `csv_path`: Path to CSV file

**Returns**: `pd.DataFrame` - Loaded CSV data

```python
csv_df = load_csv_output('output/analyses/latest.csv')
```

#### `find_latest_csv(csv_directory: str = 'output/analyses') -> str`
Finds most recent CSV file.

**Parameters**:
- `csv_directory`: Directory to search (default: 'output/analyses')

**Returns**: `str` - Path to latest CSV file

```python
latest = find_latest_csv()
```

#### `compare_campaign_coverage(excel_df: pd.DataFrame, csv_df: pd.DataFrame) -> dict`
Campaign coverage analysis function.

**Parameters**:
- `excel_df`: Excel DataFrame
- `csv_df`: CSV DataFrame

**Returns**: `dict` - Coverage analysis results

#### `compare_total_metrics(excel_df: pd.DataFrame, csv_df: pd.DataFrame) -> dict`
Total metrics comparison function.

**Parameters**:
- `excel_df`: Excel DataFrame
- `csv_df`: CSV DataFrame

**Returns**: `dict` - Total metrics analysis results

#### `compare_sample_campaigns(excel_df: pd.DataFrame, csv_df: pd.DataFrame, sample_size: int = 5) -> dict`
Sample campaign verification function.

**Parameters**:
- `excel_df`: Excel DataFrame
- `csv_df`: CSV DataFrame
- `sample_size`: Number of campaigns to sample

**Returns**: `dict` - Sample analysis results

#### `save_comparison_results(results: dict, output_dir: str = 'output/reports')`
Save comparison results to JSON.

**Parameters**:
- `results`: Results dictionary
- `output_dir`: Output directory

### generate_comparison_report.py

#### `load_comparison_results(results_file: str) -> Optional[Dict[str, Any]]`
Load comparison results from JSON file.

**Parameters**:
- `results_file`: Path to JSON results file

**Returns**: `Optional[Dict[str, Any]]` - Loaded results or None if failed

```python
results = load_comparison_results('output/reports/results.json')
```

#### `generate_markdown_report(results: Dict[str, Any]) -> str`
Generate comprehensive markdown report.

**Parameters**:
- `results`: Comparison results dictionary

**Returns**: `str` - Formatted markdown report

```python
markdown = generate_markdown_report(results)
with open('report.md', 'w') as f:
    f.write(markdown)
```

#### `generate_csv_summary(results: Dict[str, Any]) -> pd.DataFrame`
Generate CSV summary table.

**Parameters**:
- `results`: Comparison results dictionary

**Returns**: `pd.DataFrame` - Summary table

```python
summary_df = generate_csv_summary(results)
summary_df.to_csv('summary.csv', index=False)
```

#### `save_reports(results: Dict[str, Any], output_dir: str = '../output/reports') -> Tuple[str, str]`
Save both markdown and CSV reports.

**Parameters**:
- `results`: Comparison results dictionary
- `output_dir`: Output directory

**Returns**: `Tuple[str, str]` - Paths to markdown and CSV files

```python
md_path, csv_path = save_reports(results)
print(f"Reports saved: {md_path}, {csv_path}")
```

## Error Handling

### Common Exceptions

**FileNotFoundError**: Excel or CSV file not found
```python
try:
    engine.load_excel_source()
except FileNotFoundError:
    print("Excel file not found")
```

**ValueError**: Invalid data format or conversion errors
```python
try:
    results = engine.compare_total_metrics()
except ValueError as e:
    print(f"Data validation error: {e}")
```

**KeyError**: Missing expected columns
```python
try:
    coverage = engine.compare_campaign_coverage()
except KeyError as e:
    print(f"Missing column: {e}")
```

### Error Recovery Patterns

**Graceful Degradation**:
```python
results = engine.run_comprehensive_analysis()
if 'error' in results:
    print(f"Analysis failed: {results['error']}")
else:
    # Process successful results
    summary = engine.generate_summary_report(results)
```

**Validation Checks**:
```python
if engine.excel_df is None or engine.csv_df is None:
    print("Data not properly loaded")
    return
```

## Data Structures

### Results Dictionary Structure

```python
{
    "timestamp": "2025-07-18T16:18:48.544419",
    "excel_file": "data/source.xlsx",
    "csv_file": "output/analyses/mixbridge_latest.csv",
    "campaign_coverage": {
        "excel_campaigns": 56,
        "csv_campaigns": 157,
        "common_campaigns": 56,
        "coverage_rate": 35.67,
        "excel_only": 0,
        "csv_only": 101
    },
    "total_metrics": {
        "metric_results": [
            {
                "metric": "January Spend",
                "excel_value": 12345.67,
                "csv_value": 12345.67,
                "difference": 0.0,
                "relative_difference": 0.0,
                "grade": "PERFECT"
            }
        ],
        "overall_grade": "EXCELLENT",
        "accuracy_score": 99.98,
        "average_error": 0.02,
        "maximum_error": 0.05
    },
    "sample_campaigns": {
        "sample_size": 5,
        "campaign_results": [
            {
                "campaign": "Campaign A",
                "metrics": [
                    {
                        "metric": "January Spend",
                        "excel_value": 1000.0,
                        "csv_value": 1001.0,
                        "relative_difference": 0.1,
                        "status": "✅"
                    }
                ]
            }
        ]
    }
}
```

### Metric Result Structure

```python
{
    "metric": "January Spend",
    "excel_value": 12345.67,
    "csv_value": 12345.67,
    "difference": 0.0,
    "relative_difference": 0.0,
    "grade": "PERFECT",
    "grade_emoji": "🎯"
}
```

## Constants and Enums

### Grade Classifications

```python
GRADES = {
    "PERFECT": ("🎯", "< 0.01% error"),
    "EXCELLENT": ("✅", "< 0.1% error"),
    "GOOD": ("✅", "< 1.0% error"),
    "FAIR": ("⚠️", "< 5.0% error"),
    "POOR": ("❌", "≥ 5.0% error")
}
```

### Default Tolerance Values

```python
DEFAULT_TOLERANCE = 0.01  # 1 cent
PERCENTAGE_TOLERANCE = 1.0  # 1% for sample verification
PERFECT_THRESHOLD = 0.01  # 0.01% for perfect grade
EXCELLENT_THRESHOLD = 0.1  # 0.1% for excellent grade
```

### File Patterns

```python
CSV_PATTERN = "mixbridge_*.csv"
RESULTS_PATTERN = "comparison_results_*.json"
REPORT_PATTERN = "comparison_report_*.md"
SUMMARY_PATTERN = "comparison_summary_*.csv"
```