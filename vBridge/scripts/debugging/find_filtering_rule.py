#!/usr/bin/env python3
"""
Find what campaign name filtering rule would make totals match Excel exactly
"""

import pandas as pd
import openpyxl

def main():
    print('🔍 FINDING CAMPAIGN NAME FILTERING RULE TO MATCH EXCEL TOTALS')
    print('=' * 70)

    # Load Excel totals (we know these from previous analysis)
    excel_jan_total = 43959.94
    excel_feb_total = 49667.68
    
    print(f'🎯 TARGET TOTALS (from Excel):')
    print(f'  January 2025: ${excel_jan_total:,.2f}')
    print(f'  February 2025: ${excel_feb_total:,.2f}')

    # Load CSV campaign data
    csv_df = pd.read_csv('output/analyses/mixbridge_jan2025-feb2025_delta_20250721_190317.csv')
    csv_campaigns = csv_df[~csv_df['Campaign'].astype(str).str.contains('Total', case=False, na=False)]
    
    print(f'\n📊 STARTING WITH {len(csv_campaigns)} CSV CAMPAIGNS')
    
    # Test different filtering rules
    print(f'\n🧪 TESTING FILTERING RULES:')
    
    # Rule 1: Exclude campaigns starting with specific prefixes
    prefixes_to_exclude = ['GO:', 'Amplio-', '1000-']
    
    for prefix in prefixes_to_exclude:
        filtered = csv_campaigns[~csv_campaigns['Campaign'].str.startswith(prefix)]
        jan_total = filtered['Spend - January 2025'].sum()
        feb_total = filtered['Spend - February 2025'].sum()
        excluded_count = len(csv_campaigns) - len(filtered)
        
        jan_diff = abs(excel_jan_total - jan_total)
        feb_diff = abs(excel_feb_total - feb_total)
        
        print(f'  Exclude "{prefix}*": {excluded_count} campaigns removed')
        print(f'    Jan: ${jan_total:,.2f} (diff: ${jan_diff:,.2f})')
        print(f'    Feb: ${feb_total:,.2f} (diff: ${feb_diff:,.2f})')
    
    # Rule 2: Exclude all campaigns with these prefixes combined
    combined_filter = csv_campaigns[
        ~csv_campaigns['Campaign'].str.startswith('GO:') &
        ~csv_campaigns['Campaign'].str.startswith('Amplio-') &
        ~csv_campaigns['Campaign'].str.startswith('1000-')
    ]
    
    jan_total = combined_filter['Spend - January 2025'].sum()
    feb_total = combined_filter['Spend - February 2025'].sum()
    excluded_count = len(csv_campaigns) - len(combined_filter)
    
    jan_diff = abs(excel_jan_total - jan_total)
    feb_diff = abs(excel_feb_total - feb_total)
    jan_rel_diff = (jan_diff / excel_jan_total * 100) if excel_jan_total != 0 else 0
    feb_rel_diff = (feb_diff / excel_feb_total * 100) if excel_feb_total != 0 else 0
    
    print(f'\n📋 COMBINED RULE: Exclude "GO:*", "Amplio-*", "1000-*"')
    print(f'  Campaigns excluded: {excluded_count}')
    print(f'  Campaigns remaining: {len(combined_filter)}')
    print(f'  January total: ${jan_total:,.2f} (diff: ${jan_diff:,.2f}, {jan_rel_diff:.3f}%)')
    print(f'  February total: ${feb_total:,.2f} (diff: ${feb_diff:,.2f}, {feb_rel_diff:.3f}%)')
    
    # Rule 3: Only include campaigns starting with "10000-"
    only_10000 = csv_campaigns[csv_campaigns['Campaign'].str.startswith('10000-')]
    
    jan_total = only_10000['Spend - January 2025'].sum()
    feb_total = only_10000['Spend - February 2025'].sum()
    
    jan_diff = abs(excel_jan_total - jan_total)
    feb_diff = abs(excel_feb_total - feb_total)
    jan_rel_diff = (jan_diff / excel_jan_total * 100) if excel_jan_total != 0 else 0
    feb_rel_diff = (feb_diff / excel_feb_total * 100) if excel_feb_total != 0 else 0
    
    print(f'\n📋 RULE: Include ONLY "10000-*" campaigns')
    print(f'  Campaigns included: {len(only_10000)}')
    print(f'  January total: ${jan_total:,.2f} (diff: ${jan_diff:,.2f}, {jan_rel_diff:.3f}%)')
    print(f'  February total: ${feb_total:,.2f} (diff: ${feb_diff:,.2f}, {feb_rel_diff:.3f}%)')
    
    # Rule 4: Exclude zero-spend campaigns
    non_zero_campaigns = csv_campaigns[
        (csv_campaigns['Spend - January 2025'] > 0) | 
        (csv_campaigns['Spend - February 2025'] > 0)
    ]
    
    jan_total = non_zero_campaigns['Spend - January 2025'].sum()
    feb_total = non_zero_campaigns['Spend - February 2025'].sum()
    excluded_count = len(csv_campaigns) - len(non_zero_campaigns)
    
    jan_diff = abs(excel_jan_total - jan_total)
    feb_diff = abs(excel_feb_total - feb_total)
    jan_rel_diff = (jan_diff / excel_jan_total * 100) if excel_jan_total != 0 else 0
    feb_rel_diff = (feb_diff / excel_feb_total * 100) if excel_feb_total != 0 else 0
    
    print(f'\n📋 RULE: Exclude zero-spend campaigns')
    print(f'  Campaigns excluded: {excluded_count}')
    print(f'  Campaigns remaining: {len(non_zero_campaigns)}')
    print(f'  January total: ${jan_total:,.2f} (diff: ${jan_diff:,.2f}, {jan_rel_diff:.3f}%)')
    print(f'  February total: ${feb_total:,.2f} (diff: ${feb_diff:,.2f}, {feb_rel_diff:.3f}%)')
    
    # Rule 5: Combination - exclude specific prefixes AND zero-spend
    optimal_filter = csv_campaigns[
        ~csv_campaigns['Campaign'].str.startswith('GO:') &
        ~csv_campaigns['Campaign'].str.startswith('Amplio-') &
        ~csv_campaigns['Campaign'].str.startswith('1000-') &
        ((csv_campaigns['Spend - January 2025'] > 0) | 
         (csv_campaigns['Spend - February 2025'] > 0))
    ]
    
    jan_total = optimal_filter['Spend - January 2025'].sum()
    feb_total = optimal_filter['Spend - February 2025'].sum()
    excluded_count = len(csv_campaigns) - len(optimal_filter)
    
    jan_diff = abs(excel_jan_total - jan_total)
    feb_diff = abs(excel_feb_total - feb_total)
    jan_rel_diff = (jan_diff / excel_jan_total * 100) if excel_jan_total != 0 else 0
    feb_rel_diff = (feb_diff / excel_feb_total * 100) if excel_feb_total != 0 else 0
    
    print(f'\n📋 OPTIMAL RULE: Exclude prefixes + zero-spend')
    print(f'  Campaigns excluded: {excluded_count}')
    print(f'  Campaigns remaining: {len(optimal_filter)}')
    print(f'  January total: ${jan_total:,.2f} (diff: ${jan_diff:,.2f}, {jan_rel_diff:.3f}%)')
    print(f'  February total: ${feb_total:,.2f} (diff: ${feb_diff:,.2f}, {feb_rel_diff:.3f}%)')
    
    # Final assessment
    print(f'\n🎯 ASSESSMENT:')
    if jan_rel_diff < 0.01 and feb_rel_diff < 0.01:
        print(f'  ✅ MATCH FOUND! This filtering rule makes totals match within 0.01%')
    elif jan_rel_diff < 0.1 and feb_rel_diff < 0.1:
        print(f'  ⚠️  Close match - within 0.1% tolerance')
    else:
        print(f'  ❌ No exact match found with campaign name filtering alone')
    
    # Show what campaigns would be included with the optimal rule
    print(f'\n📝 CAMPAIGNS THAT WOULD BE INCLUDED:')
    included_campaigns = optimal_filter['Campaign'].tolist()
    print(f'  Total campaigns: {len(included_campaigns)}')
    print(f'  Sample campaigns:')
    for i, campaign in enumerate(included_campaigns[:5]):
        jan_spend = optimal_filter.iloc[i]['Spend - January 2025']
        feb_spend = optimal_filter.iloc[i]['Spend - February 2025']
        print(f'    {campaign[:50]:<50} Jan: ${jan_spend:>8.2f} Feb: ${feb_spend:>8.2f}')

if __name__ == "__main__":
    main()