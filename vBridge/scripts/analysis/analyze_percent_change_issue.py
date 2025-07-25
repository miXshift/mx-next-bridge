#!/usr/bin/env python3
"""
Analyze why percent change values for individual campaigns don't sum to total percent change
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_percent_change_issue():
    """Analyze the mathematical relationship between campaign and total percent changes"""
    
    # Load the output data
    csv_path = Path("/home/kyle/workspace/ms/mx-next-bridge/vBridge/output/current/LATEST_mixbridge.csv")
    df = pd.read_csv(csv_path)
    
    # Separate total row from campaign rows
    total_row = df[df['Campaign'] == 'Total'].iloc[0]
    campaign_rows = df[df['Campaign'] != 'Total']
    
    print("=" * 80)
    print("PERCENT CHANGE ANALYSIS")
    print("=" * 80)
    
    # Analyze a specific metric: Spend
    metric = "Spend"
    
    print(f"\nAnalyzing metric: {metric}")
    print("-" * 40)
    
    # Extract values
    total_jan = total_row[f'{metric} - January 2025']
    total_feb = total_row[f'{metric} - February 2025']
    total_pct_change = total_row[f'{metric} - % Change']
    
    print(f"Total January: ${total_jan:,.2f}")
    print(f"Total February: ${total_feb:,.2f}")
    print(f"Total % Change: {total_pct_change:.4f}%")
    
    # Calculate what the total % change should be
    calculated_total_pct = ((total_feb - total_jan) / total_jan) * 100
    print(f"Calculated Total % Change: {calculated_total_pct:.4f}%")
    print(f"Match: {np.isclose(total_pct_change, calculated_total_pct)}")
    
    # Sum individual campaign percent changes
    campaign_pct_sum = campaign_rows[f'{metric} - % Change'].sum()
    print(f"\nSum of Campaign % Changes: {campaign_pct_sum:.4f}%")
    print(f"Difference from Total: {campaign_pct_sum - total_pct_change:.4f}%")
    
    # The issue: percent changes don't sum because they have different bases
    print("\n" + "=" * 80)
    print("WHY PERCENT CHANGES DON'T SUM:")
    print("=" * 80)
    
    print("\nPercent change is calculated as: ((New - Old) / Old) * 100")
    print("Each campaign has its own 'Old' value as the denominator")
    print("You cannot sum percentages with different denominators!\n")
    
    # Demonstrate with top 5 campaigns
    print("Top 5 Campaigns by January Spend:")
    print("-" * 60)
    
    top_campaigns = campaign_rows.nlargest(5, f'{metric} - January 2025')
    
    for _, row in top_campaigns.iterrows():
        campaign = row['Campaign']
        jan_val = row[f'{metric} - January 2025']
        feb_val = row[f'{metric} - February 2025']
        pct_change = row[f'{metric} - % Change']
        
        # Calculate the absolute change
        abs_change = feb_val - jan_val
        
        print(f"\n{campaign[:50]}...")
        print(f"  Jan: ${jan_val:,.2f}, Feb: ${feb_val:,.2f}")
        print(f"  Absolute Change: ${abs_change:,.2f}")
        print(f"  % Change: {pct_change:.2f}% (base: ${jan_val:,.2f})")
    
    # Show the correct way to aggregate percent changes
    print("\n" + "=" * 80)
    print("CORRECT WAY TO AGGREGATE PERCENT CHANGES:")
    print("=" * 80)
    
    # Method 1: Weight by January values
    print("\nMethod 1: Weighted Average by January Values")
    print("-" * 40)
    
    # Calculate weights based on January values
    campaign_jan_values = campaign_rows[f'{metric} - January 2025']
    campaign_pct_changes = campaign_rows[f'{metric} - % Change']
    
    # Remove any NaN or infinite values
    valid_mask = np.isfinite(campaign_jan_values) & np.isfinite(campaign_pct_changes) & (campaign_jan_values != 0)
    
    weights = campaign_jan_values[valid_mask] / campaign_jan_values[valid_mask].sum()
    weighted_avg_pct = (campaign_pct_changes[valid_mask] * weights).sum()
    
    print(f"Weighted Average % Change: {weighted_avg_pct:.4f}%")
    print(f"Total % Change: {total_pct_change:.4f}%")
    print(f"Difference: {weighted_avg_pct - total_pct_change:.4f}%")
    
    # Method 2: Calculate from absolute changes
    print("\nMethod 2: Calculate from Sum of Absolute Changes")
    print("-" * 40)
    
    total_abs_change = campaign_rows[f'{metric} - Net Change'].sum()
    total_jan_sum = campaign_rows[f'{metric} - January 2025'].sum()
    
    recalc_pct_change = (total_abs_change / total_jan_sum) * 100
    
    print(f"Sum of Absolute Changes: ${total_abs_change:,.2f}")
    print(f"Sum of January Values: ${total_jan_sum:,.2f}")
    print(f"Recalculated % Change: {recalc_pct_change:.4f}%")
    print(f"Total % Change: {total_pct_change:.4f}%")
    print(f"Match: {np.isclose(recalc_pct_change, total_pct_change)}")
    
    # Analyze all metrics
    print("\n" + "=" * 80)
    print("ANALYSIS FOR ALL METRICS:")
    print("=" * 80)
    
    metrics = ['Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
               'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
               'Other SKU Ad Orders', 'Total Ad Orders']
    
    print(f"\n{'Metric':<25} {'Total %':<12} {'Sum of %':<12} {'Difference':<12} {'Weighted %':<12}")
    print("-" * 75)
    
    for metric in metrics:
        if f'{metric} - % Change' in total_row.index:
            total_pct = total_row[f'{metric} - % Change']
            sum_pct = campaign_rows[f'{metric} - % Change'].sum()
            
            # Calculate weighted average
            jan_values = campaign_rows[f'{metric} - January 2025']
            pct_values = campaign_rows[f'{metric} - % Change']
            
            valid_mask = np.isfinite(jan_values) & np.isfinite(pct_values) & (jan_values != 0)
            if valid_mask.any():
                weights = jan_values[valid_mask] / jan_values[valid_mask].sum()
                weighted_pct = (pct_values[valid_mask] * weights).sum()
            else:
                weighted_pct = 0
            
            print(f"{metric:<25} {total_pct:>11.2f}% {sum_pct:>11.2f}% {sum_pct-total_pct:>11.2f}% {weighted_pct:>11.2f}%")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT:")
    print("=" * 80)
    print("\nPercent changes CANNOT be directly summed because they have different denominators.")
    print("The total percent change is calculated from the total values, not from individual percents.")
    print("\nTo properly aggregate percent changes, you must either:")
    print("1. Use a weighted average (weighted by the base values)")
    print("2. Sum the absolute changes and divide by the sum of base values")
    print("3. Calculate the total percent change directly from total values")

if __name__ == "__main__":
    analyze_percent_change_issue()