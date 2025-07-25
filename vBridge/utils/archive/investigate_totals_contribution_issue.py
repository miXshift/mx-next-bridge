#!/usr/bin/env python3
"""
Investigate why individual campaign contributions don't sum to total contributions
"""

import pandas as pd
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from campaign_bridge import CampaignBridge

def analyze_contribution_logic():
    """Analyze the contribution calculation logic and totals issue"""
    
    print("CONTRIBUTION SUMMATION INVESTIGATION")
    print("=" * 80)
    print("Checking if individual campaign contributions sum to total row contributions")
    
    # First, run the campaign bridge to generate the data
    print("\nGenerating campaign bridge data...")
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    bridge.load_data()
    bridge_df = bridge.calculate_bridge()
    saved_path = bridge.save_to_csv('output/period_comparison.csv')
    print(f"✓ Campaign bridge data generated: {saved_path}")
    
    # Load the CSV data from the timestamped file using pandas
    csv_path = saved_path
    
    # Read the CSV with proper handling
    import csv
    totals_data = None
    campaign_data = []
    
    with open(csv_path, 'r') as f:
        # Skip the two header rows
        lines = f.readlines()
        top_headers = lines[0].strip().split(',')
        sub_headers = lines[1].strip().split(',')
        
        # Combine headers
        combined_headers = []
        for i, (top, sub) in enumerate(zip(top_headers, sub_headers)):
            if i == 0:
                combined_headers.append('Campaign Name')
            else:
                combined_headers.append(f"{top} {sub}")
        
        # Parse data rows using csv reader for proper comma handling
        csv_reader = csv.reader(lines[2:])
        for row in csv_reader:
            if row and row[0]:  # Skip empty rows
                row_dict = {}
                for i, (header, val) in enumerate(zip(combined_headers, row)):
                    if i == 0:  # Campaign name
                        row_dict[header] = val
                    else:  # Numeric values
                        try:
                            row_dict[header] = float(val) if val != '' else 0.0
                        except ValueError:
                            row_dict[header] = 0.0
                
                if 'Total' in row[0]:
                    totals_data = row_dict
                else:
                    campaign_data.append(row_dict)
    
    print("CONTRIBUTION CALCULATION ANALYSIS:")
    print("=" * 60)
    print("Mix Bridge Formula: contribution = p1_mix * growth_rate * 10000")
    print("Where:")
    print("  p1_mix = campaign_jan_value / total_jan_value")
    print("  growth_rate = (campaign_feb_value / campaign_jan_value) - 1")
    print()
    
    # Check Spend contribution
    print("SPEND CONTRIBUTION ANALYSIS:")
    print("-" * 40)
    
    total_spend_jan = totals_data['Spend Jan 2025']
    total_spend_feb = totals_data['Spend Feb 2025']
    total_spend_contrib = totals_data['Spend Contribution']
    
    print(f"Total Spend January:     ${total_spend_jan:,.2f}")
    print(f"Total Spend February:    ${total_spend_feb:,.2f}")
    print(f"Total Spend Contribution: {total_spend_contrib}")
    
    # For totals row, the calculation would be:
    # p1_mix = total_jan / total_jan = 1.0
    # growth_rate = (total_feb / total_jan) - 1
    # contribution = 1.0 * growth_rate * 10000
    
    if total_spend_jan > 0:
        totals_p1_mix = total_spend_jan / total_spend_jan  # = 1.0
        totals_growth_rate = (total_spend_feb / total_spend_jan) - 1
        expected_totals_contrib = totals_p1_mix * totals_growth_rate * 10000
        
        print(f"\nExpected Totals Row Calculation:")
        print(f"  P1 Mix (total/total):     {totals_p1_mix}")
        print(f"  Growth Rate:              {totals_growth_rate:.10f}")
        print(f"  Expected Contribution:    {expected_totals_contrib:.6f}")
        print(f"  Actual CSV Contribution:  {total_spend_contrib}")
        
        if abs(expected_totals_contrib) > 0.001:
            print(f"  ❌ ISSUE: Totals row should show {expected_totals_contrib:.2f}, not 0")
        else:
            print(f"  ✅ OK: Contribution correctly shows 0")
    
    # Sum up all campaign contributions to see what totals should be
    print(f"\nCAMPAIGN CONTRIBUTIONS SUM:")
    print("-" * 40)
    
    campaign_contrib_sum = sum(camp['Spend Contribution'] for camp in campaign_data)
    print(f"Sum of all campaign Spend contributions: {campaign_contrib_sum:.6f}")
    print(f"Totals row Spend contribution:           {total_spend_contrib}")
    
    # Check for mismatch
    mismatch = abs(campaign_contrib_sum - total_spend_contrib)
    print(f"\nMISMATCH ANALYSIS:")
    print(f"Difference: {mismatch:.6f}")
    if mismatch > 0.001:
        print(f"❌ MISMATCH DETECTED: Individual contributions don't sum to total!")
        
        # Show some individual campaign details
        print(f"\nDETAILED CAMPAIGN ANALYSIS (top 5 contributions):")
        sorted_campaigns = sorted(campaign_data, key=lambda x: abs(x['Spend Contribution']), reverse=True)
        for i, camp in enumerate(sorted_campaigns[:5]):
            print(f"\n{i+1}. {camp['Campaign Name']}")
            print(f"   January: ${camp['Spend Jan 2025']:,.2f}")
            print(f"   February: ${camp['Spend Feb 2025']:,.2f}")
            print(f"   Contribution: {camp['Spend Contribution']:.6f}")
            
            # Recalculate expected contribution
            if total_spend_jan > 0 and camp['Spend Jan 2025'] > 0:
                p1_mix = camp['Spend Jan 2025'] / total_spend_jan
                growth_rate = (camp['Spend Feb 2025'] / camp['Spend Jan 2025']) - 1
                expected_contrib = p1_mix * growth_rate * 10000
                print(f"   Expected: {expected_contrib:.6f}")
                if abs(expected_contrib - camp['Spend Contribution']) > 0.001:
                    print(f"   ⚠️  Individual calculation mismatch!")
    
    # The mathematical property of Mix Bridge contributions:
    # Sum of all campaign contributions should equal the total contribution
    print(f"\n📊 MATHEMATICAL CONSISTENCY CHECK:")
    print(f"Theory: Sum of campaign contributions = Total portfolio contribution")
    print(f"Expected total (from calculation): {expected_totals_contrib:.6f}")
    print(f"Actual total (from CSV):          {total_spend_contrib:.6f}")
    print(f"Sum of individuals:               {campaign_contrib_sum:.6f}")
    
    # Check both relationships
    print(f"\nRELATIONSHIP CHECKS:")
    
    # Check 1: Does CSV total match expected calculation?
    if abs(expected_totals_contrib - total_spend_contrib) < 0.001:
        print(f"✅ Total row calculation is correct")
    else:
        print(f"❌ Total row calculation error: {abs(expected_totals_contrib - total_spend_contrib):.6f}")
    
    # Check 2: Do individuals sum to total?
    if abs(campaign_contrib_sum - total_spend_contrib) < 0.001:
        print(f"✅ Individual contributions sum to total")
    else:
        print(f"❌ Individual contributions DON'T sum to total!")
        print(f"   Difference: {abs(campaign_contrib_sum - total_spend_contrib):.6f}")
        
        # Investigate why
        print(f"\n   POSSIBLE CAUSES:")
        print(f"   1. Dummy value (0.0000001) handling differences")
        print(f"   2. Campaigns with zero baseline values")
        print(f"   3. Rounding precision issues")
        print(f"   4. Different calculation methods for totals vs individuals")
    
    # Check if totals row is being calculated correctly
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    print("-" * 40)
    
    if total_spend_contrib == 0 and abs(expected_totals_contrib) > 0.001:
        print("❌ ISSUE: Totals row contribution calculation is not implemented")
        print("   The code calculates contributions for campaigns but not for totals row")
        print("   This breaks the mathematical consistency of Mix Bridge methodology")
    elif total_spend_contrib == 0 and abs(expected_totals_contrib) < 0.001:
        print("✅ OK: Totals row correctly shows 0 (no overall portfolio growth)")
    
    # Return detailed results
    return {
        'expected_total': expected_totals_contrib,
        'actual_total': total_spend_contrib,
        'campaign_sum': campaign_contrib_sum,
        'mismatch': abs(campaign_contrib_sum - total_spend_contrib),
        'saved_path': saved_path
    }

def check_other_metrics(saved_path):
    """Check if the issue exists for other metrics too"""
    
    print(f"\n\nOTHER METRICS CHECK:")
    print("=" * 60)
    
    # Load CSV data from the timestamped file
    csv_path = saved_path
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    # Get totals row using csv reader
    import csv
    csv_reader = csv.reader([lines[2]])
    totals_line = next(csv_reader)
    
    # Check contribution columns (every 5th column starting from index 5)
    metrics = ['Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate', 
               'Impressions', 'Clicks', 'CTR', 'CPC', 'Same SKU Ad Sales',
               'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders']
    
    print("Totals Row Contribution Values:")
    print("-" * 40)
    
    for i, metric in enumerate(metrics):
        contrib_index = 5 + (i * 5)  # Contribution is every 5th column
        if contrib_index < len(totals_line):
            contrib_val = float(totals_line[contrib_index])
            print(f"{metric:<25}: {contrib_val}")
    
    print(f"\n🔍 OBSERVATION:")
    print("If ALL totals row contributions are 0, this confirms the issue is systemic")

if __name__ == "__main__":
    results = analyze_contribution_logic()
    check_other_metrics(results['saved_path'])
    
    print(f"\n\n🎯 SUMMARY:")
    print("=" * 60)
    if results['mismatch'] > 0.001:
        print(f"❌ CRITICAL ISSUE: Individual contributions don't sum to total")
        print(f"   Mismatch amount: {results['mismatch']:.6f}")
        print(f"   This violates the mathematical consistency of Mix Bridge methodology")
    else:
        print(f"✅ All contributions are mathematically consistent")