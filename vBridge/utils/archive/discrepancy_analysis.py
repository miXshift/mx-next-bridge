#!/usr/bin/env python3
"""
Analyze discrepancies between Excel and CSV outputs for Campaign Bridge
Removes rounding errors and identifies significant calculation differences
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook

def categorize_difference(excel_val, csv_val, tolerance=0.1):
    """Categorize the type of difference between Excel and CSV values"""
    abs_diff = abs(excel_val - csv_val)
    
    # Handle zero cases
    if csv_val == 0 and excel_val != 0:
        if abs(excel_val) < 1:
            return "Small value rounded to 0", abs_diff
        else:
            return "CSV shows 0, Excel non-zero", abs_diff
    
    # Check for simple rounding
    if abs_diff <= tolerance:
        return "Rounding difference", abs_diff
    
    # Check for percentage point differences
    if abs_diff > 1:
        return "Significant difference", abs_diff
    
    return "Moderate difference", abs_diff

def analyze_campaign_discrepancies():
    """Analyze discrepancies for 1000-CONQ-NONBRAND-ASIN-Skyflask campaign"""
    
    # Data from comparison
    comparison_data = {
        "Spend % Change": {"Excel": -19.06, "CSV": -19.1},
        "Spend Contribution": {"Excel": -12.59, "CSV": -10},
        "Total Ad Sales Contribution": {"Excel": -1.67, "CSV": -1},
        "ACoS Points Change": {"Excel": -3.88, "CSV": -3.9},
        "ACoS % Change": {"Excel": -16.65, "CSV": -16.6},
        "ACoS Contribution": {"Excel": -2.06, "CSV": 0},
        "ROAS % Change": {"Excel": 19.97, "CSV": 20.0},
        "ROAS Contribution": {"Excel": 0.005, "CSV": 0},
        "Conversion Rate Points Change": {"Excel": 2.07, "CSV": 2.1},
        "Conversion Rate % Change": {"Excel": 17.90, "CSV": 17.9},
        "Conversion Rate Contribution": {"Excel": 2.96, "CSV": 0},
        "Impressions % Change": {"Excel": 2.68, "CSV": 2.7},
        "Impressions Contribution": {"Excel": 0.57, "CSV": 0},
        "Clicks % Change": {"Excel": -19.42, "CSV": -19.4},
        "Clicks Contribution": {"Excel": -14.24, "CSV": -12},
        "CTR Points Change": {"Excel": -0.32, "CSV": -0.3},
        "CTR % Change": {"Excel": -21.52, "CSV": -21.5},
        "CTR Contribution": {"Excel": -0.04, "CSV": 0},
        "CPC Net Change": {"Excel": 0.004, "CSV": 0.0},
        "CPC % Change": {"Excel": 0.45, "CSV": 0.4},
        "CPC Contribution": {"Excel": 0.0002, "CSV": 0},
        "Same SKU Ad Sales % Change": {"Excel": 0.31, "CSV": 0.3},
        "Same SKU Ad Sales Contribution": {"Excel": 0.19, "CSV": 0},
        "Other SKU Sales Contribution": {"Excel": -19.04, "CSV": -12},
        "Same SKU Ad Orders Contribution": {"Excel": 1.22, "CSV": 1},
        "Other SKU Ad Orders Contribution": {"Excel": -31.28, "CSV": -26},
        "Total Ad Orders Contribution": {"Excel": -2.18, "CSV": -2}
    }
    
    print("DISCREPANCY ANALYSIS REPORT")
    print("=" * 80)
    print("Campaign: 1000-CONQ-NONBRAND-ASIN-Skyflask")
    print("=" * 80)
    
    # Categorize differences
    categories = {
        "Rounding difference": [],
        "Small value rounded to 0": [],
        "CSV shows 0, Excel non-zero": [],
        "Moderate difference": [],
        "Significant difference": []
    }
    
    for metric, values in comparison_data.items():
        excel_val = values["Excel"]
        csv_val = values["CSV"]
        category, diff = categorize_difference(excel_val, csv_val)
        
        categories[category].append({
            "metric": metric,
            "excel": excel_val,
            "csv": csv_val,
            "diff": diff
        })
    
    # Display results by category
    print("\n1. ROUNDING DIFFERENCES (≤ 0.1)")
    print("-" * 50)
    if categories["Rounding difference"]:
        for item in categories["Rounding difference"]:
            print(f"   {item['metric']:40} Excel={item['excel']:>8}, CSV={item['csv']:>8}")
    else:
        print("   None found")
    
    print("\n2. SMALL VALUES ROUNDED TO ZERO IN CSV")
    print("-" * 50)
    if categories["Small value rounded to 0"] or categories["CSV shows 0, Excel non-zero"]:
        for cat in ["Small value rounded to 0", "CSV shows 0, Excel non-zero"]:
            for item in categories[cat]:
                if "Contribution" in item['metric'] and item['csv'] == 0:
                    print(f"   {item['metric']:40} Excel={item['excel']:>8}, CSV={item['csv']:>8}")
    else:
        print("   None found")
    
    print("\n3. SIGNIFICANT CALCULATION DIFFERENCES (> 1.0)")
    print("-" * 50)
    if categories["Significant difference"]:
        for item in sorted(categories["Significant difference"], key=lambda x: x['diff'], reverse=True):
            print(f"   {item['metric']:40} Excel={item['excel']:>8}, CSV={item['csv']:>8}, Diff={item['diff']:>8.2f}")
    else:
        print("   None found")
    
    # Analyze contribution formula differences
    print("\n4. CONTRIBUTION CALCULATION ANALYSIS")
    print("-" * 50)
    print("   Formula: contribution = p1_mix * growth_rate * 10000")
    print("   where:")
    print("     p1_mix = campaign_jan_value / total_jan_value")
    print("     growth_rate = (campaign_feb_value / campaign_jan_value) - 1")
    print("\n   Possible causes of differences:")
    print("   a) Different handling of zero/null values in denominators")
    print("   b) Different total_january values between Excel and Python")
    print("   c) Intermediate calculation precision differences")
    print("   d) Different rounding strategies (Excel vs Python)")
    
    # Specific contribution issues
    print("\n5. SPECIFIC CONTRIBUTION DISCREPANCIES TO INVESTIGATE")
    print("-" * 50)
    major_contrib_diffs = [
        ("Spend Contribution", -12.59, -10, 2.59),
        ("Other SKU Sales Contribution", -19.04, -12, 7.04),
        ("Other SKU Ad Orders Contribution", -31.28, -26, 5.28),
        ("Clicks Contribution", -14.24, -12, 2.24)
    ]
    
    for metric, excel, csv, diff in major_contrib_diffs:
        print(f"   {metric:35} Excel={excel:>7}, CSV={csv:>7}, Diff={abs(diff):>5.2f}")
    
    print("\n   These require checking:")
    print("   - January total values used in p1_mix calculation")
    print("   - Whether totals include/exclude certain campaigns")
    print("   - Handling of special cases (nulls, zeros, etc.)")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_metrics = len(comparison_data)
    rounding_only = len(categories["Rounding difference"])
    zero_rounding = len(categories["Small value rounded to 0"]) + len(categories["CSV shows 0, Excel non-zero"])
    significant = len(categories["Significant difference"])
    
    print(f"Total metrics compared: {total_metrics}")
    print(f"Pure rounding differences: {rounding_only} ({rounding_only/total_metrics*100:.1f}%)")
    print(f"Small values rounded to 0: {zero_rounding} ({zero_rounding/total_metrics*100:.1f}%)")
    print(f"Significant differences: {significant} ({significant/total_metrics*100:.1f}%)")
    
    print("\nRECOMMENDED NEXT STEPS:")
    print("1. Verify total row calculations match between Excel and Python")
    print("2. Check contribution formula implementation against Excel formulas")
    print("3. Test edge cases: zero values, null handling, very small numbers")
    print("4. Compare intermediate calculation values (p1_mix, growth_rate)")

if __name__ == "__main__":
    analyze_campaign_discrepancies()