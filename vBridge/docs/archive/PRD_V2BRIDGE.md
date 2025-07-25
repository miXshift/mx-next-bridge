# Product Requirements Document: vBridge
## Mix Bridge Analysis Tool

### Document Information
- **Version**: 1.0
- **Date**: January 2025
- **Status**: Production
- **Author**: MixShift Analytics Team

---

## 1. Executive Summary

vBridge is a Python-based analytical tool that implements the Mix Bridge methodology for marketing campaign performance analysis. It calculates contribution metrics to explain period-over-period changes in marketing KPIs by decomposing variance into mix and rate components. The tool processes campaign data from CSV files and generates detailed contribution analyses with timestamped outputs.

## 2. Product Overview

### 2.1 Purpose
The Mix Bridge methodology helps marketers understand what drives changes in their metrics between time periods. By separating the impact of campaign mix changes from performance rate changes, it provides actionable insights into campaign portfolio optimization.

### 2.2 Key Value Propositions
- **Variance Decomposition**: Breaks down metric changes into explainable components
- **Mathematical Rigor**: Uses proven statistical methods for contribution analysis
- **Scalability**: Handles large campaign datasets efficiently
- **Accuracy**: Maintains 12-decimal precision for financial calculations
- **Auditability**: Generates timestamped outputs for tracking analysis history

## 3. Technical Architecture

### 3.1 Core Components

```
vBridge/
├── src/
│   └── campaign_bridge.py      # Core Mix Bridge implementation
├── utils/                      # Analysis and verification utilities
├── data/                       # Input data files
├── output/                     # Timestamped output files
└── docs/                       # Documentation
```

### 3.2 Key Classes
- **CampaignBridge**: Main class implementing Mix Bridge calculations
  - `load_data()`: Loads and validates campaign data
  - `calculate_bridge()`: Performs contribution calculations
  - `save_to_csv()`: Exports results with timestamps

### 3.3 Dependencies
- pandas >= 1.3.0
- numpy >= 1.21.0
- Python >= 3.8

## 4. Functional Requirements

### 4.1 Data Input
- **Format**: CSV files with campaign performance data
- **Required Columns**: Campaign name, metric values for two periods
- **Supported Metrics**: 
  - Absolute metrics: Spend, Sales, Clicks, Orders, Units
  - Rate metrics: ACoS, ROAS, CTR, Conversion Rate, CPC

### 4.2 Core Calculations

#### 4.2.1 Contribution Formula
For each campaign and metric:
```
contribution = p1_mix × growth_rate × 10000
```
Where:
- `p1_mix = campaign_value_p1 / total_value_p1`
- `growth_rate = (value_p2 / value_p1) - 1`
- Result is in basis points

#### 4.2.2 Special Handling

**Rate Metrics**:
- Non-additive metrics (ACoS, ROAS, CTR, etc.)
- Total row contributions set to 0 (mathematically correct)

**Zero Baseline Edge Cases**:
- When P1 = 0 and P2 ≠ 0 for absolute metrics
- Uses dummy value (0.0000001) to enable calculation
- Maintains mathematical consistency

### 4.3 Output Requirements

#### 4.3.1 File Format
- CSV with two-tier headers matching Excel structure
- Columns: Campaign, [Metric - Period1], [Metric - Period2], [Metric - Net Change], [Metric - % Change], [Metric - Contribution]
- Total row aggregating all campaigns

#### 4.3.2 File Naming
- Base name + military time timestamp (HHMM)
- Example: `period_comparison_1430.csv`

#### 4.3.3 Precision
- All calculations use 12 decimal places
- Percentage values in decimal format (0.17 not 17%)

## 5. Non-Functional Requirements

### 5.1 Performance
- Process 1000+ campaigns in < 5 seconds
- Memory efficient for large datasets

### 5.2 Accuracy
- Mathematical precision to 12 decimal places
- Validation against Excel reference implementations
- Consistent rounding behavior

### 5.3 Usability
- Clear error messages for data issues
- Progress indicators for long operations
- Intuitive command-line interface

### 5.4 Maintainability
- Modular code structure
- Comprehensive documentation
- Utility scripts for testing and validation

## 6. Mathematical Framework

### 6.1 Mix Bridge Methodology
The Mix Bridge decomposes period-over-period variance into:
1. **Mix Effect**: Impact of shifting budget between campaigns
2. **Rate Effect**: Impact of performance changes within campaigns

### 6.2 Mathematical Properties
- Contributions sum to total variance (except for rate metrics)
- Sign conventions: positive = favorable, negative = unfavorable
- Basis point representation for interpretability

### 6.3 Edge Case Handling
- Zero denominators: Skip calculation, set contribution to 0
- New campaigns (P1=0): Use dummy value for absolute metrics
- Discontinued campaigns: Normal calculation applies

## 7. User Interface

### 7.1 Command Line Usage
```bash
# Basic usage
python src/campaign_bridge.py

# Run specific utility
python utils/detailed_campaign_comparison.py
```

### 7.2 Configuration
- Input/output paths configurable
- Metric lists customizable
- Precision settings adjustable

## 8. Testing & Validation

### 8.1 Test Utilities
- `verify_totals_fix.py`: Validates total calculations
- `analyze_zero_baseline_issue.py`: Tests edge cases
- `detailed_campaign_comparison.py`: Compares with Excel

### 8.2 Validation Criteria
- Individual contributions sum to total (within tolerance)
- Consistent with Excel reference implementation
- Handles all edge cases gracefully

## 9. Known Limitations

### 9.1 Current Constraints
- Two-period comparison only (no multi-period)
- CSV input format required
- Rate metrics require special interpretation

### 9.2 Future Enhancements
- Multi-period bridge analysis
- API interface for integration
- Interactive visualization
- Automated anomaly detection

## 10. Success Metrics

### 10.1 Accuracy
- 100% calculation accuracy vs Excel reference
- < 0.1 basis point tolerance on aggregations

### 10.2 Adoption
- Used for monthly campaign analysis
- Integrated into reporting workflows
- Positive user feedback on insights

### 10.3 Performance
- Sub-second response for typical datasets
- Handles enterprise-scale campaign counts

## 11. Appendix

### 11.1 Glossary
- **Mix Bridge**: Variance decomposition methodology
- **Contribution**: Basis point impact on total change
- **P1/P2**: Period 1 and Period 2 in comparison
- **Basis Point**: 1/100th of a percentage point

### 11.2 References
- Mathematical Decomposition Patterns (see docs/)
- Mix Bridge Technical Scoping Document
- Excel reference implementation

### 11.3 Version History
- v1.0: Initial production release with core Mix Bridge functionality
- Includes timestamping, precision improvements, zero baseline handling