#!/usr/bin/env python3
"""
Analyze why ROAS contributions are showing zero
"""

import pandas as pd
from src.config.metrics import MetricDefinitions

def analyze_roas_contributions():
    """Analyze ROAS contribution issues"""
    print('🔍 ROAS CONTRIBUTION ANALYSIS:')
    print('='*60)
    
    # Read the latest results
    df = pd.read_csv('output/current/LATEST_mixbridge.csv')
    total_row = df[df['Campaign'] == 'Total'].iloc[0]
    
    print('ROAS Totals Row:')
    print(f'  January ROAS:     {total_row["ROAS - January 2025"]:.4f}')
    print(f'  February ROAS:    {total_row["ROAS - February 2025"]:.4f}')
    print(f'  Net Change:       {total_row["ROAS - Net Change"]:.4f}')
    print(f'  % Change:         {total_row["ROAS - % Change"]:.4f}%')
    print(f'  Contribution:     {total_row["ROAS - Contribution"]:.4f}')

    # Check individual campaigns
    campaign_rows = df[df['Campaign'] != 'Total']
    roas_contribs = campaign_rows['ROAS - Contribution']
    non_zero_roas = (abs(roas_contribs) > 0.01).sum()

    print(f'\nROAS Campaign Contributions:')
    print(f'  Non-zero contributions: {non_zero_roas}/{len(campaign_rows)}')
    print(f'  Sum of campaign contribs: {roas_contribs.sum():.4f}')
    print(f'  Min contribution: {roas_contribs.min():.4f}')
    print(f'  Max contribution: {roas_contribs.max():.4f}')

    print(f'\n📊 COMPARISON WITH ACOS:')
    print(f'  ACoS Contribution (Total): {total_row["ACoS - Contribution"]:.2f} bps')
    print(f'  ROAS Contribution (Total): {total_row["ROAS - Contribution"]:.4f}')

    # Check metric categorization
    print(f'\n🔧 METRIC CATEGORIZATION:')
    absolute_metrics = MetricDefinitions.get_absolute_metrics()
    rate_metrics = MetricDefinitions.get_rate_metrics()

    print(f'  ROAS in absolute metrics: {"ROAS" in absolute_metrics}')
    print(f'  ROAS in rate metrics: {"ROAS" in rate_metrics}')
    print(f'  ACoS in absolute metrics: {"ACoS" in absolute_metrics}')  
    print(f'  ACoS in rate metrics: {"ACoS" in rate_metrics}')
    
    print(f'\n📋 ALL ABSOLUTE METRICS:')
    for i, metric in enumerate(absolute_metrics, 1):
        print(f'  {i:2d}. {metric}')
        
    print(f'\n📋 ALL RATE METRICS:')
    for i, metric in enumerate(rate_metrics, 1):
        print(f'  {i:2d}. {metric}')

    # Check which metrics get contributions
    print(f'\n🔍 CONTRIBUTION ANALYSIS:')
    contribution_cols = [col for col in df.columns if 'Contribution' in col]
    for col in contribution_cols:
        metric_name = col.replace(' - Contribution', '')
        total_contrib = total_row[col]
        campaign_contrib_sum = campaign_rows[col].sum()
        non_zero_campaigns = (abs(campaign_rows[col]) > 0.01).sum()
        
        print(f'  {metric_name:20} | Total: {total_contrib:>8.2f} | Campaigns: {non_zero_campaigns:>3d} | Sum: {campaign_contrib_sum:>8.2f}')

    print(f'\n💡 ROOT CAUSE ANALYSIS:')
    print('='*60)
    
    # Check if ROAS gets processed by MixRate Bridge
    if "ROAS" in rate_metrics and total_row["ROAS - Contribution"] == 0:
        print("❌ ISSUE: ROAS is a rate metric but has zero contribution")
        print("   EXPECTED: ROAS should get contributions via MixRate Bridge")
        print("   ACTUAL: Only ACoS is being processed by MixRate Bridge")
        print("   CAUSE: MixRate Bridge calculator only implements ACoS, not ROAS")
    
    if "ROAS" in absolute_metrics:
        print("❌ ISSUE: ROAS incorrectly categorized as absolute metric")
        print("   EXPECTED: ROAS should be in rate metrics (it's a ratio)")
        print("   ACTUAL: ROAS getting processed by traditional Mix Bridge")
    
    # Check traditional vs MixRate processing
    print(f'\n🧩 PROCESSING LOGIC:')
    print(f'  Traditional Mix Bridge processes: {len(absolute_metrics)} absolute metrics')
    print(f'  MixRate Bridge processes: Only ACoS (hardcoded)')
    print(f'  Other rate metrics: {[m for m in rate_metrics if m != "ACoS"]} get zero contributions')
    
    print(f'\n🎯 SOLUTION:')
    print('  Option 1: Extend MixRate Bridge to handle ROAS directly')
    print('  Option 2: ROAS gets contributions from underlying Spend/Sales contributions')
    print('  Option 3: Design decision - rate metrics inherently have zero contributions')

if __name__ == "__main__":
    analyze_roas_contributions()