# Data Requirements Verification for CPA and AOV KPIs

## Summary
Both CPA (Cost per Acquisition) and AOV (Average Order Value) KPIs have been successfully integrated into the vBridge system with proper data requirements verified.

## Data Field Requirements

### Required Fields for CPA and AOV
Both metrics depend on the following data fields:

1. **Spend** - Already established in system
   - Source field: `Cost` (renamed during processing)
   - Used for: CPA numerator

2. **Total Ad Sales** - Already established in system  
   - Source field: `Sales` (renamed during processing)
   - Used for: AOV numerator

3. **Total Ad Orders** - Already established in system ✅
   - Source field: `AttributedConversions14day` (renamed during processing)  
   - Used for: Both CPA and AOV denominators (mix determinant)

## KPI Definitions

### CPA (Cost per Acquisition)
```
Formula: Spend / Total Ad Orders
Bridge Type: MixRate Bridge (Standard)
Mix Determinant: Total Ad Orders
Contribution Unit: Currency (e.g., +/-$0.42)
```

### AOV (Average Order Value)  
```
Formula: Total Ad Sales / Total Ad Orders
Bridge Type: MixRate Bridge (Standard)
Mix Determinant: Total Ad Orders
Contribution Unit: Currency (e.g., +/-$0.42)
```

## Data Processing Pipeline

### Column Mapping (processor.py:297)
```python
column_mapping = {
    'Cost': 'Spend',
    'Sales': 'Total Ad Sales', 
    'AttributedConversions14day': 'Total Ad Orders'
}
```

### Data Validation
- `Total Ad Orders` is validated as an absolute metric in validator.py:710
- Field is consistently used across all calculation modules
- Well-established in test data and verification scripts

## System Integration Status ✅

- [x] Bridge mappings updated with CPA and AOV acronyms
- [x] Metric formulas defined in METRIC_FORMULAS
- [x] Bridge configurations set to MIXRATE_BRIDGE type  
- [x] Currency contribution units configured
- [x] Data field dependencies verified and available
- [x] Legacy metrics system removed and compatibility layer added

## Verification Results

1. **Data Availability**: All required fields (`Spend`, `Total Ad Sales`, `Total Ad Orders`) are established in the system
2. **Processing Pipeline**: Column mapping handles the conversion from raw data field names
3. **Calculation Engine**: Bridge calculator supports both metrics via MixRate Bridge methodology
4. **Output Format**: Both metrics will display contribution values in local currency format

The implementation is ready for testing and production use.