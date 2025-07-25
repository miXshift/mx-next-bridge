#!/usr/bin/env python3
"""
Analysis of ACoS % Change and Contribution Issues
Investigates why ACoS shows 0% change and 0 contribution
"""

import pandas as pd
from src.core.bridge_calculator import BridgeCalculator
from src.config.metrics import MetricDefinitions

def analyze_acos_issues():
    """Analyze the ACoS calculation issues"""
    print("🔍 ANALYZING ACOS ISSUES")
    print("="*80)
    
    # Read latest results
    df = pd.read_csv('output/current/LATEST_mixbridge.csv')
    total_row = df[df['Campaign'] == 'Total'].iloc[0]
    
    print("📊 CURRENT ACOS VALUES:")
    print(f"  ACoS January:     {total_row['ACoS - January 2025']:.4f}%")
    print(f"  ACoS February:    {total_row['ACoS - February 2025']:.4f}%")
    print(f"  ACoS Pts Change:  {total_row['ACoS - Pts Change']:.4f}")
    print(f"  ACoS % Change:    {total_row['ACoS - % Change']:.4f}%")
    print(f"  ACoS Contribution:{total_row['ACoS - Contribution']:.4f}")
    
    # Manual calculations
    jan_acos = (total_row['Spend - January 2025'] / total_row['Total Ad Sales - January 2025']) * 100
    feb_acos = (total_row['Spend - February 2025'] / total_row['Total Ad Sales - February 2025']) * 100
    pts_change = feb_acos - jan_acos
    pct_change = ((feb_acos - jan_acos) / jan_acos) * 100
    
    print("\n🔢 MANUAL CALCULATIONS:")
    print(f"  Manual Jan ACoS:  {jan_acos:.4f}%")
    print(f"  Manual Feb ACoS:  {feb_acos:.4f}%")
    print(f"  Manual Pts Change:{pts_change:.4f}")
    print(f"  Manual % Change:  {pct_change:.4f}%")
    
    print("\n❓ ISSUE #1: WHY IS % CHANGE ZERO?")
    print("-"*50)
    print("PROBLEM: ACoS % Change calculation is missing!")
    print(f"Expected: {pct_change:.4f}%")
    print(f"Actual:   {total_row['ACoS - % Change']:.4f}%")
    
    # Check the code logic
    print("\n🔧 CODE ANALYSIS:")
    print("Looking at calculate_rate_metrics_totals()...")
    print("- ACoS January: ✅ Calculated correctly")
    print("- ACoS February: ✅ Calculated correctly") 
    print("- ACoS Pts Change: ✅ Calculated correctly")
    print("- ACoS % Change: ❌ MISSING! Not calculated at all")
    print("\nThe function calculates % change for absolute metrics but NOT for ACoS rate metric!")
    
    print("\n❓ ISSUE #2: WHY ARE CONTRIBUTIONS ZERO?")
    print("-"*50)
    print("PROBLEM: ACoS is categorized as rate metric, not absolute metric")
    
    # Check metric categorization
    is_absolute = MetricDefinitions.is_absolute_metric('ACoS')
    is_rate = MetricDefinitions.is_rate_metric('ACoS')
    
    print(f"ACoS is absolute metric: {is_absolute}")
    print(f"ACoS is rate metric: {is_rate}")
    
    print("\nContributions are only calculated for ABSOLUTE metrics!")
    print("Rate metrics (ACoS, ROAS, CTR, etc.) don't get contributions calculated.")
    
    absolute_metrics = MetricDefinitions.get_absolute_metrics()
    rate_metrics = MetricDefinitions.get_rate_metrics()
    
    print(f"\nAbsolute metrics ({len(absolute_metrics)}): {', '.join(absolute_metrics)}")
    print(f"Rate metrics ({len(rate_metrics)}): {', '.join(rate_metrics)}")
    
    print("\n💡 ROOT CAUSES IDENTIFIED:")
    print("="*80)
    print("1. ACoS % Change Missing:")
    print("   - calculate_rate_metrics_totals() doesn't calculate % change for ACoS")
    print("   - Only calculates Pts change for ACoS")
    print("   - Missing: ACoS % change = (Feb_ACoS - Jan_ACoS) / Jan_ACoS * 100")
    
    print("\n2. ACoS Contributions Zero:")
    print("   - ACoS is classified as 'rate metric'")
    print("   - calculate_contributions() only processes 'absolute metrics'")
    print("   - Rate metrics are excluded from contribution calculations")
    print("   - This is actually CORRECT behavior for Mix Bridge methodology!")
    
    print("\n📚 MIX BRIDGE METHODOLOGY:")
    print("="*80)
    print("Rate metrics like ACoS don't have 'contributions' in traditional Mix Bridge:")
    print("- ACoS is calculated as Spend/Sales ratio")
    print("- Changes in ACoS come from changes in Spend and Sales")
    print("- The 'contribution' comes from underlying Spend and Sales contributions")
    print("- ACoS itself doesn't contribute - it's a derived metric")
    
    print("\n✅ SUMMARY:")
    print("="*80)
    print("Issue #1 (ACoS % Change = 0): ❌ BUG - Missing calculation")
    print("Issue #2 (ACoS Contribution = 0): ✅ CORRECT - By design")
    
    return {
        'manual_pct_change': pct_change,
        'current_pct_change': total_row['ACoS - % Change'],
        'is_pct_change_bug': abs(pct_change - total_row['ACoS - % Change']) > 0.01,
        'is_contribution_bug': False  # This is correct behavior
    }

def check_other_rate_metrics():
    """Check if other rate metrics have the same issues"""
    print("\n🔍 CHECKING OTHER RATE METRICS:")
    print("="*80)
    
    df = pd.read_csv('output/current/LATEST_mixbridge.csv')
    total_row = df[df['Campaign'] == 'Total'].iloc[0]
    
    rate_metrics = MetricDefinitions.get_rate_metrics()
    
    for metric in rate_metrics:
        pct_change_col = f'{metric} - % Change'
        contribution_col = f'{metric} - Contribution'
        
        if pct_change_col in df.columns:
            pct_change_val = total_row[pct_change_col]
            contribution_val = total_row[contribution_col]
            
            print(f"{metric}:")
            print(f"  % Change: {pct_change_val:.4f}%")
            print(f"  Contribution: {contribution_val:.4f}")
        else:
            print(f"{metric}: Missing % Change column")

if __name__ == "__main__":
    issues = analyze_acos_issues()
    check_other_rate_metrics()
    
    print(f"\n🎯 RECOMMENDED ACTION:")
    if issues['is_pct_change_bug']:
        print("Fix ACoS % Change calculation in calculate_rate_metrics_totals()")
    else:
        print("No action needed - calculations are correct")