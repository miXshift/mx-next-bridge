#!/usr/bin/env python3
"""
Verify MixRate Bridge Implementation Results
"""

import pandas as pd

def verify_mixrate_results():
    """Verify the MixRate Bridge implementation results"""
    # Read the latest results
    df = pd.read_csv('output/current/LATEST_mixbridge.csv')
    total_row = df[df['Campaign'] == 'Total'].iloc[0]

    print('🎯 MIXRATE BRIDGE RESULTS:')
    print('='*60)
    print('ACoS Analysis:')
    print(f'  January ACoS:     {total_row["ACoS - January 2025"]:.4f}%')
    print(f'  February ACoS:    {total_row["ACoS - February 2025"]:.4f}%')
    print(f'  Pts Change:       {total_row["ACoS - Pts Change"]:.4f}')
    print(f'  % Change:         {total_row["ACoS - % Change"]:.4f}%')
    print(f'  Contribution:     {total_row["ACoS - Contribution"]:.2f} bps')

    print(f'\nROAS Analysis:')
    print(f'  January ROAS:     {total_row["ROAS - January 2025"]:.4f}')
    print(f'  February ROAS:    {total_row["ROAS - February 2025"]:.4f}')
    print(f'  Net Change:       {total_row["ROAS - Net Change"]:.4f}')
    print(f'  % Change:         {total_row["ROAS - % Change"]:.4f}%')

    print(f'\n📊 VERIFICATION:')
    manual_acos_pct_change = ((total_row['ACoS - February 2025'] - total_row['ACoS - January 2025']) / total_row['ACoS - January 2025']) * 100
    print(f'  Expected ACoS % Change:  {manual_acos_pct_change:.4f}%')
    print(f'  Actual ACoS % Change:    {total_row["ACoS - % Change"]:.4f}%')
    print(f'  % Change Fix Working:    {"✅" if abs(manual_acos_pct_change - total_row["ACoS - % Change"]) < 0.01 else "❌"}')

    print(f'\n  ACoS Contribution Changed: {"✅" if abs(total_row["ACoS - Contribution"]) > 0.01 else "❌"}')
    print(f'  MixRate Bridge Active:     {"✅" if abs(total_row["ACoS - Contribution"]) > 0.01 else "❌"}')

    # Check individual campaign contributions
    campaign_rows = df[df['Campaign'] != 'Total']
    non_zero_acos_contribs = (abs(campaign_rows['ACoS - Contribution']) > 0.01).sum()
    print(f'  Campaigns with ACoS contributions: {non_zero_acos_contribs}/{len(campaign_rows)}')
    
    # Show top contributors
    print(f'\n🏆 TOP ACOS CONTRIBUTORS:')
    print('-'*60)
    top_contributors = campaign_rows.nlargest(5, 'ACoS - Contribution')
    for _, row in top_contributors.iterrows():
        print(f'  {row["Campaign"][:40]:<40} {row["ACoS - Contribution"]:>8.2f} bps')
    
    print(f'\n🔻 TOP ACOS DETRACTORS:')
    print('-'*60)
    top_detractors = campaign_rows.nsmallest(5, 'ACoS - Contribution')
    for _, row in top_detractors.iterrows():
        print(f'  {row["Campaign"][:40]:<40} {row["ACoS - Contribution"]:>8.2f} bps')
    
    # Mathematical validation
    total_acos_contrib = campaign_rows['ACoS - Contribution'].sum()
    expected_total = total_row['ACoS - Contribution']
    
    print(f'\n🧮 MATHEMATICAL VALIDATION:')
    print('-'*60)
    print(f'  Campaign contributions sum: {total_acos_contrib:.2f} bps')
    print(f'  Total row contribution:     {expected_total:.2f} bps')
    print(f'  Difference:                 {abs(total_acos_contrib - expected_total):.4f} bps')
    print(f'  Mathematical consistency:   {"✅" if abs(total_acos_contrib - expected_total) < 0.01 else "❌"}')
    
    return {
        'pct_change_fixed': abs(manual_acos_pct_change - total_row["ACoS - % Change"]) < 0.01,
        'contributions_active': abs(total_row["ACoS - Contribution"]) > 0.01,
        'campaigns_with_contribs': non_zero_acos_contribs,
        'mathematically_consistent': abs(total_acos_contrib - expected_total) < 0.01
    }

if __name__ == "__main__":
    results = verify_mixrate_results()
    
    print(f'\n🎯 IMPLEMENTATION SUCCESS:')
    print('='*60)
    all_success = all(results.values())
    print(f'Overall Status: {"✅ SUCCESS" if all_success else "⚠️  PARTIAL"}')
    
    for check, status in results.items():
        print(f'  {check}: {"✅" if status else "❌"}')