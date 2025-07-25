#!/usr/bin/env python3
"""
Investigate why absolute metrics still show discrepancies
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from campaign_bridge import CampaignBridge

def investigate_absolute_discrepancy():
    """Investigate the remaining discrepancy in absolute metrics"""
    
    print("ABSOLUTE METRICS DISCREPANCY INVESTIGATION")
    print("=" * 80)
    
    # Generate fresh data
    print("\nGenerating bridge data...")
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    bridge.load_data()
    bridge_df = bridge.calculate_bridge()
    csv_path = bridge.save_to_csv('output/period_comparison.csv')
    print(f"✓ Bridge data generated: {csv_path}")
    
    # Load CSV data
    csv_path = csv_path
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    # Parse headers
    top_headers = lines[0].strip().split(',')
    sub_headers = lines[1].strip().split(',')
    
    combined_headers = []
    for i, (top, sub) in enumerate(zip(top_headers, sub_headers)):
        if i == 0:
            combined_headers.append('Campaign Name')
        else:
            combined_headers.append(f"{top} {sub}")
    
    # Parse all data
    all_data = []
    for line in lines[2:]:
        if line.strip():
            row = line.strip().split(',')
            try:
                row_dict = {}
                for i, (header, val) in enumerate(zip(combined_headers, row)):
                    if i == 0:
                        row_dict[header] = val
                    else:
                        row_dict[header] = float(val) if val != '' else 0.0
                all_data.append(row_dict)
            except (ValueError, IndexError):
                continue  # Skip rows with parsing issues
    
    # Separate totals and campaigns
    totals_row = None
    campaign_rows = []
    
    for row in all_data:
        if 'Total' in row['Campaign Name']:
            totals_row = row
        else:
            campaign_rows.append(row)
    
    # Analyze Spend contribution in detail
    print("SPEND CONTRIBUTION DETAILED ANALYSIS:")
    print("-" * 60)
    
    total_spend_contrib = totals_row['Spend Contribution']
    campaign_spend_contribs = [row['Spend Contribution'] for row in campaign_rows]
    campaign_contrib_sum = sum(campaign_spend_contribs)
    
    print(f"Total Spend Contribution:     {total_spend_contrib:15.6f}")
    print(f"Sum of Campaign Contributions: {campaign_contrib_sum:15.6f}")
    print(f"Difference:                   {abs(total_spend_contrib - campaign_contrib_sum):15.6f}")
    
    # Check campaigns with zero January values
    print(f"\nCAMPAIGNS WITH ZERO JANUARY SPEND:")
    print("-" * 60)
    
    zero_jan_campaigns = []
    for row in campaign_rows:
        if row['Spend Jan 2025'] == 0:
            zero_jan_campaigns.append({
                'name': row['Campaign Name'],
                'jan': row['Spend Jan 2025'],
                'feb': row['Spend Feb 2025'],
                'contrib': row['Spend Contribution']
            })
    
    print(f"Found {len(zero_jan_campaigns)} campaigns with zero January spend:")
    for camp in zero_jan_campaigns[:5]:  # Show first 5
        print(f"  {camp['name'][:40]:<40} Jan: {camp['jan']:8.2f}, Feb: {camp['feb']:8.2f}, Contrib: {camp['contrib']:8.2f}")
    
    if len(zero_jan_campaigns) > 5:
        print(f"  ... and {len(zero_jan_campaigns) - 5} more")
    
    # Check the mathematical formula
    print(f"\nMIX BRIDGE FORMULA VERIFICATION:")
    print("-" * 60)
    
    total_jan = totals_row['Spend Jan 2025']
    total_feb = totals_row['Spend Feb 2025']
    
    if total_jan > 0:
        # Manual calculation
        manual_growth_rate = (total_feb / total_jan) - 1
        manual_contribution = 1.0 * manual_growth_rate * 10000
        
        print(f"Manual calculation:")
        print(f"  Total Jan Spend:    ${total_jan:,.2f}")
        print(f"  Total Feb Spend:    ${total_feb:,.2f}")
        print(f"  Growth Rate:        {manual_growth_rate:.10f}")
        print(f"  Manual Contribution: {manual_contribution:.6f}")
        print(f"  CSV Total Contrib:   {total_spend_contrib:.6f}")
        print(f"  Match:              {'✅ YES' if abs(manual_contribution - total_spend_contrib) < 0.001 else '❌ NO'}")
    
    # The discrepancy might be due to campaigns with zero January values
    # that still get non-zero contributions, which breaks the mathematical model
    print(f"\n🔍 ROOT CAUSE HYPOTHESIS:")
    print("-" * 60)
    print("Campaigns with zero January values can still have contributions")
    print("if they have February values, but this breaks the total calculation")
    print("because the total formula assumes all campaigns contribute to the total base.")
    print()
    print("This is a limitation of applying Mix Bridge to campaigns that")
    print("didn't exist in the baseline period (January).")

if __name__ == "__main__":
    investigate_absolute_discrepancy()