#!/usr/bin/env python3
"""
Test script to verify that contribution totals are now calculated correctly
"""

import pandas as pd
import sys
sys.path.append('src')

from campaign_bridge import CampaignBridge

def test_contribution_totals():
    print("🔍 TESTING CONTRIBUTION TOTAL FIX")
    print("=" * 80)
    
    # Initialize the bridge calculator
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    
    # Load and process data
    bridge.load_data()
    
    # Calculate bridge
    print("\n📊 Calculating bridge metrics...")
    bridge_df = bridge.calculate_bridge()
    
    # Get total row and campaign data
    total_row = bridge_df[bridge_df['Campaign'] == 'Total']
    campaign_rows = bridge_df[bridge_df['Campaign'] != 'Total']
    
    print("\n📈 Contribution Analysis:")
    print("-" * 80)
    
    # Check each absolute metric
    absolute_metrics = [
        'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
        'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
        'Other SKU Ad Orders', 'Total Ad Orders'
    ]
    
    all_correct = True
    
    for metric in absolute_metrics:
        # Sum individual campaign contributions
        campaign_sum = campaign_rows[f'{metric} - Contribution'].sum()
        
        # Get total row contribution
        total_value = total_row[f'{metric} - Contribution'].iloc[0]
        
        # Check if they match
        difference = abs(campaign_sum - total_value)
        is_correct = difference < 0.01  # Allow for small rounding differences
        
        status = "✅" if is_correct else "❌"
        
        print(f"\n{metric}:")
        print(f"  Campaign contributions sum: {campaign_sum:.6f}")
        print(f"  Total row contribution:     {total_value:.6f}")
        print(f"  Difference:                 {difference:.6f} {status}")
        
        if not is_correct:
            all_correct = False
    
    # Check rate metrics (should be 0)
    print("\n\n📊 Rate Metrics (should be 0):")
    print("-" * 80)
    
    rate_metrics = ['ACoS', 'ROAS', 'Conversion Rate', 'CTR', 'CPC']
    
    for metric in rate_metrics:
        total_value = total_row[f'{metric} - Contribution'].iloc[0]
        is_zero = abs(total_value) < 0.0001
        status = "✅" if is_zero else "❌"
        
        print(f"{metric}: {total_value} {status}")
        
        if not is_zero:
            all_correct = False
    
    print("\n" + "=" * 80)
    
    if all_correct:
        print("✅ SUCCESS: All contribution totals are now calculated correctly!")
        print("   - Absolute metrics: Sum of individual contributions")
        print("   - Rate metrics: Correctly set to 0")
    else:
        print("❌ FAILED: Some contribution totals are still incorrect")
    
    # Save the corrected output
    print("\n💾 Saving corrected output...")
    output_path = bridge.save_to_csv('output/analyses/mixbridge_jan2025-feb2025_corrected.csv')
    print(f"✅ Saved to: {output_path}")
    
    return all_correct

if __name__ == "__main__":
    success = test_contribution_totals()
    sys.exit(0 if success else 1)