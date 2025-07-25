#!/usr/bin/env python3
"""
Verify that the totals row contribution fix maintains mathematical consistency
"""

import pandas as pd

def verify_mathematical_consistency():
    """Verify that sum of campaign contributions equals total contribution"""
    
    print("MATHEMATICAL CONSISTENCY VERIFICATION")
    print("=" * 80)
    print("Mix Bridge Principle: Sum of campaign contributions = Total contribution")
    print("=" * 80)
    
    # Load CSV data
    csv_path = "../output/period_comparison.csv"
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
            except ValueError:
                continue  # Skip rows with parsing issues
    
    # Separate totals and campaigns
    totals_row = None
    campaign_rows = []
    
    for row in all_data:
        if 'Total' in row['Campaign Name']:
            totals_row = row
        else:
            campaign_rows.append(row)
    
    if not totals_row:
        print("ERROR: Could not find totals row")
        return
    
    # Check key metrics
    metrics_to_check = ['Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Clicks']
    
    print("VERIFICATION RESULTS:")
    print("-" * 60)
    print(f"{'Metric':<20} {'Total Contrib':<15} {'Sum Contrib':<15} {'Difference':<15} {'Status'}")
    print("-" * 60)
    
    all_passed = True
    
    for metric in metrics_to_check:
        contrib_col = f"{metric} Contribution"
        
        if contrib_col in totals_row:
            total_contrib = totals_row[contrib_col]
            
            # Sum campaign contributions
            campaign_contrib_sum = sum(row.get(contrib_col, 0) for row in campaign_rows)
            
            # Calculate difference
            diff = abs(total_contrib - campaign_contrib_sum)
            
            # Check if they match (within small tolerance for floating point)
            status = "✅ PASS" if diff < 0.01 else "❌ FAIL"
            if diff >= 0.01:
                all_passed = False
            
            print(f"{metric:<20} {total_contrib:<15.6f} {campaign_contrib_sum:<15.6f} {diff:<15.6f} {status}")
    
    print("-" * 60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Mathematical consistency maintained!")
        print("✅ Mix Bridge formula implemented correctly")
    else:
        print("❌ MATHEMATICAL INCONSISTENCY DETECTED")
        print("⚠️  Further investigation required")
    
    # Show the actual contribution values
    print(f"\nTOTALS ROW CONTRIBUTION VALUES (before fix was 0.0):")
    print("-" * 60)
    
    key_contribs = ['Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate', 'Clicks']
    for metric in key_contribs:
        contrib_col = f"{metric} Contribution"
        if contrib_col in totals_row:
            val = totals_row[contrib_col]
            print(f"{metric:<20}: {val:>12.6f}")

if __name__ == "__main__":
    verify_mathematical_consistency()