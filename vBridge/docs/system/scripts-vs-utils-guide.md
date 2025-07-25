# Scripts vs Utils: Decision Guide

This guide explains when to use the `/scripts` directory versus the `/utils` directory in the MixBridge v2 project.

## Quick Decision Matrix

| Need | Use | Example |
|------|-----|---------|
| Debug calculation issue | `/scripts/debugging/` | `debug_acos_issue.py` |
| Verify implementation | `/scripts/verification/` | `verify_mixrate_bridge.py` |
| Analyze specific metric | `/scripts/analysis/` | `analyze_acos_issues.py` |
| Compare CSV to Excel | `/utils/` | `compare_enhanced_outputs.py` |
| Production validation | `/utils/` | Enhanced Comparison System |
| One-off investigation | `/scripts/` | Quick debugging script |

## Directory Overview

### `/scripts` - Ad-Hoc Debugging & Analysis Tools

**Purpose**: Quick debugging, verification, and analysis tools for immediate issues

**When to use:**
- ✅ Debugging specific calculation problems
- ✅ Verifying implementation results
- ✅ Analyzing individual metrics or issues
- ✅ One-off investigations
- ✅ Quick validation of fixes
- ✅ Troubleshooting runtime issues

**Characteristics:**
- Simple standalone scripts
- Direct CSV reading from `output/current/`
- Focused on specific issues
- Minimal dependencies
- Quick to write and execute

### `/utils` - Production Validation System

**Purpose**: Comprehensive Excel-to-CSV comparison and systematic validation

**When to use:**
- ✅ Comparing output to Excel documents (per CLAUDE.md)
- ✅ Production-grade validation workflow
- ✅ Quality assurance and grading
- ✅ Systematic comparison analysis
- ✅ Generating stakeholder reports
- ✅ Campaign coverage analysis

**Characteristics:**
- Modular architecture with reusable components
- Complex Excel processing capabilities
- Comprehensive documentation
- Quality grading system
- Multiple output formats (JSON, Markdown, CSV)

## Usage Scenarios

### Scenario 1: "ACoS contributions are showing as zero"

**Use `/scripts/debugging/`**

```bash
# Quick debugging
python scripts/debugging/debug_acos_issue.py

# Detailed analysis
python scripts/analysis/analyze_acos_issues.py
```

**Why scripts?** This is a specific calculation issue requiring immediate debugging.

### Scenario 2: "Validate our output matches the Excel source"

**Use `/utils/`**

```bash
# Excel comparison (as required by CLAUDE.md)
python utils/compare_enhanced_outputs.py

# Generate comprehensive report
python utils/generate_comparison_report.py output/reports/comparison_results_*.json
```

**Why utils?** This requires systematic Excel comparison with quality grading.

### Scenario 3: "Check if all 12 KPIs are calculating correctly"

**Use `/scripts/verification/`**

```bash
python scripts/verification/verify_all_12_kpis.py
```

**Why scripts?** This is verification of internal calculations, not Excel comparison.

### Scenario 4: "Find a specific campaign in the data"

**Use `/scripts/debugging/`**

```bash
python scripts/debugging/find_campaign.py "Campaign Name"
```

**Why scripts?** This is a simple debugging utility for immediate needs.

### Scenario 5: "Generate quality report for stakeholders"

**Use `/utils/`**

```bash
# Run comprehensive analysis with grading
python utils/compare_enhanced_outputs.py
python utils/generate_comparison_report.py output/reports/comparison_results_*.json
```

**Why utils?** This requires production-grade reporting with quality metrics.

## Directory Structure Reference

### `/scripts` Structure
```
scripts/
├── analysis/          # Analyze specific issues or metrics
├── debugging/         # Debug calculation problems  
├── verification/      # Verify implementation results
├── demo_*.py         # Demonstration scripts
└── *_cli.py          # Command-line utilities
```

### `/utils` Structure  
```
utils/
├── compare_*.py              # Excel comparison tools
├── enhanced_comparison_*.py  # Main comparison engine
├── generate_*.py            # Report generators
├── modules/                 # Reusable components
├── docs/                    # Comprehensive documentation
└── archive/                 # Legacy analysis tools
```

## Decision Flowchart

```
Issue or Task
    ↓
Need to compare with Excel?
    ↓ YES → Use /utils (per CLAUDE.md)
    ↓ NO
    ↓
Is it a calculation issue?
    ↓ YES → Use /scripts/debugging/
    ↓ NO  
    ↓
Need to verify implementation?
    ↓ YES → Use /scripts/verification/
    ↓ NO
    ↓
Want to analyze specific metrics?
    ↓ YES → Use /scripts/analysis/
    ↓ NO
    ↓
One-off investigation?
    ↓ YES → Create in appropriate /scripts/ subdirectory
```

## Key Guidelines

### From CLAUDE.md
- **"when comparing output to excel documents, always use the /utils directory"**
- **"when creating ad hoc scripts for testing, analysis, debugging, or verification store the new file in relevant scripts folder"**

### Best Practices

1. **Excel Comparisons**: Always use `/utils` - it's designed for this purpose
2. **Quick Debugging**: Use `/scripts/debugging/` for immediate issues  
3. **Implementation Verification**: Use `/scripts/verification/` for internal validation
4. **Metric Analysis**: Use `/scripts/analysis/` for deep-dives into specific metrics
5. **Production Reports**: Use `/utils` for stakeholder-ready quality reports

### When Creating New Files

**Create in `/scripts/` when:**
- Debugging specific calculation issues
- Quick one-off analysis needs
- Verifying internal implementation  
- Simple standalone utilities

**Create in `/utils/` when:**
- Enhancing Excel comparison capabilities
- Adding new validation dimensions
- Improving quality grading system
- Building reusable analysis components

## Examples by Use Case

### Daily Development Workflow

```bash
# 1. Run MixBridge calculations
python src/enhanced_mixbridge_calculator.py

# 2. Quick verification of results
python scripts/verification/verify_all_contributions.py

# 3. Compare against Excel source (required)
python utils/compare_enhanced_outputs.py
```

### Debugging Workflow

```bash
# 1. Identify issue
python scripts/debugging/check_current_totals.py

# 2. Debug specific metric
python scripts/analysis/analyze_acos_issues.py

# 3. Verify fix
python scripts/verification/verify_mixrate_bridge.py

# 4. Final validation against Excel
python utils/compare_enhanced_outputs.py
```

### Quality Assurance Workflow

```bash
# 1. Comprehensive Excel comparison
python utils/compare_enhanced_outputs.py

# 2. Generate stakeholder reports
python utils/generate_comparison_report.py output/reports/comparison_results_*.json

# 3. Review quality grades and coverage analysis
```

## Summary

- **`/scripts`** = Quick debugging, verification, and analysis tools
- **`/utils`** = Production validation system with Excel comparison
- **Excel comparisons** = Always use `/utils` (per CLAUDE.md)
- **Ad-hoc debugging** = Always use appropriate `/scripts` subdirectory
- **Quality reports** = Use `/utils` for comprehensive stakeholder reporting

The separation maintains clear boundaries between immediate debugging needs and systematic production validation.