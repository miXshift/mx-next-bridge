#!/usr/bin/env python3
"""
Analyze the zero baseline issue and propose a solution
"""

import sys
import os
import pandas as pd

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from campaign_bridge import CampaignBridge

def analyze_zero_baseline_issue():
    """Analyze why zero baseline causes contribution mismatch"""
    
    print("ZERO BASELINE CONTRIBUTION ANALYSIS")
    print("=" * 80)
    
    # Generate fresh data
    print("\nGenerating bridge data...")
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    bridge.load_data()
    bridge_df = bridge.calculate_bridge()
    
    # Analyze campaigns
    total_row = bridge_df.iloc[0]
    campaign_rows = bridge_df.iloc[1:]
    
    # Categorize campaigns
    zero_baseline_campaigns = []
    normal_campaigns = []
    
    for _, row in campaign_rows.iterrows():
        if row['Spend - January 2025'] == 0:
            zero_baseline_campaigns.append(row)
        else:
            normal_campaigns.append(row)
    
    print(f"\nCAMPAIGN BREAKDOWN:")
    print(f"Total campaigns: {len(campaign_rows)}")
    print(f"Normal campaigns (Jan > 0): {len(normal_campaigns)}")
    print(f"Zero baseline campaigns (Jan = 0): {len(zero_baseline_campaigns)}")
    
    # Calculate contributions
    normal_contrib_sum = sum(c['Spend - Contribution'] for c in normal_campaigns)
    zero_contrib_sum = sum(c['Spend - Contribution'] for c in zero_baseline_campaigns)
    total_contrib = total_row['Spend - Contribution']
    
    print(f"\nCONTRIBUTION ANALYSIS:")
    print(f"Normal campaigns contribution sum: {normal_contrib_sum:.6f}")
    print(f"Zero baseline contribution sum:    {zero_contrib_sum:.6f}")
    print(f"All campaigns contribution sum:    {normal_contrib_sum + zero_contrib_sum:.6f}")
    print(f"Total row contribution:            {total_contrib:.6f}")
    print(f"Discrepancy:                       {abs(total_contrib - (normal_contrib_sum + zero_contrib_sum)):.6f}")
    
    # Check if any zero baseline campaigns have February spend
    zero_with_feb_spend = [c for c in zero_baseline_campaigns if c['Spend - February 2025'] > 0]
    
    print(f"\nZERO BASELINE CAMPAIGNS WITH FEBRUARY SPEND: {len(zero_with_feb_spend)}")
    for camp in zero_with_feb_spend[:5]:
        print(f"  {camp['Campaign'][:50]:<50} Feb: ${camp['Spend - February 2025']:8.2f}")
    
    # Analyze the mathematical issue
    print(f"\n🔍 MATHEMATICAL ANALYSIS:")
    print("-" * 60)
    
    # Total calculation
    total_jan = total_row['Spend - January 2025']
    total_feb = total_row['Spend - February 2025']
    total_growth = (total_feb / total_jan) - 1
    expected_total_contrib = 1.0 * total_growth * 10000
    
    print(f"Total calculation:")
    print(f"  Jan: ${total_jan:,.2f}, Feb: ${total_feb:,.2f}")
    print(f"  Growth rate: {total_growth:.10f}")
    print(f"  Expected contribution: {expected_total_contrib:.6f}")
    
    # The issue: zero baseline campaigns contribute to Feb total but not Jan total
    zero_feb_total = sum(c['Spend - February 2025'] for c in zero_baseline_campaigns)
    adjusted_feb_total = total_feb - zero_feb_total
    adjusted_growth = (adjusted_feb_total / total_jan) - 1
    adjusted_total_contrib = 1.0 * adjusted_growth * 10000
    
    print(f"\nAdjusted calculation (excluding zero baseline campaigns):")
    print(f"  Zero baseline Feb total: ${zero_feb_total:,.2f}")
    print(f"  Adjusted Feb total: ${adjusted_feb_total:,.2f}")
    print(f"  Adjusted growth rate: {adjusted_growth:.10f}")
    print(f"  Adjusted contribution: {adjusted_total_contrib:.6f}")
    print(f"  Matches normal campaign sum? {abs(adjusted_total_contrib - normal_contrib_sum) < 0.1}")
    
    print(f"\n📌 ROOT CAUSE:")
    print("-" * 60)
    print("The total row includes February spend from zero-baseline campaigns")
    print("in its growth calculation, but these campaigns can't contribute")
    print("to the Mix Bridge because they have no baseline to calculate p1_mix.")
    print()
    print("Excel likely handles this by either:")
    print("1. Excluding zero-baseline campaigns from totals")
    print("2. Using a different formula for these campaigns")
    print("3. Setting their contribution to 0")
    
    print(f"\n✅ SOLUTION OPTIONS:")
    print("-" * 60)
    print("1. EXCLUDE APPROACH: Don't include zero-baseline campaigns in totals")
    print("2. ZERO CONTRIBUTION: Set contribution to 0 for zero-baseline campaigns")
    print("3. SEPARATE HANDLING: Use a different calculation method for new campaigns")

if __name__ == "__main__":
    analyze_zero_baseline_issue()