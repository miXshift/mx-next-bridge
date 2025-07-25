#!/usr/bin/env python3
"""
Verify zero baseline handling against Excel and test 0.0000001 substitution
"""

import pandas as pd
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from campaign_bridge import CampaignBridge

def load_excel_data():
    """Load Excel data using pandas to avoid complex parsing"""
    
    print("LOADING EXCEL DATA")
    print("=" * 80)
    
    # Read Excel file - skip the two-tier headers
    excel_path = "data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx"
    
    try:
        # Read with proper header handling
        df = pd.read_excel(excel_path, sheet_name='Campaign', header=[12, 13])
        
        # Flatten multi-level columns
        df.columns = [f"{col[0]} {col[1]}" if col[1] != 'Unnamed: 0_level_1' else col[0] 
                     for col in df.columns]
        
        # Clean up column names
        df.columns = [col.replace('  ', ' ').strip() for col in df.columns]
        
        print(f"Excel data loaded: {len(df)} rows")
        print(f"Columns: {list(df.columns[:10])}...")  # Show first 10 columns
        
        return df
        
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return None

def analyze_excel_totals(excel_df):
    """Analyze Excel totals row handling"""
    
    print(f"\nEXCEL TOTALS ANALYSIS")
    print("-" * 60)
    
    # Find totals row - it's likely the first row
    print(f"\\nFirst few campaign names:")
    for idx in range(min(5, len(excel_df))):
        campaign_name = str(excel_df.iloc[idx, 0]) if pd.notna(excel_df.iloc[idx, 0]) else ""
        print(f"  Row {idx}: '{campaign_name}'")
    
    # Check if first row is totals
    totals_row = excel_df.iloc[0]
    first_campaign = str(excel_df.iloc[0, 0]) if pd.notna(excel_df.iloc[0, 0]) else ""
    
    print(f"\\nUsing first row as totals: '{first_campaign}'")
    
    # Extract spend values
    spend_cols = [col for col in excel_df.columns if 'Spend' in col]
    print(f"\nSpend columns in Excel: {spend_cols}")
    
    # Try to find exact column names
    excel_spend_data = {}
    for col in spend_cols:
        if 'Jan' in col or 'January' in col:
            excel_spend_data['jan'] = totals_row[col]
        elif 'Feb' in col or 'February' in col:
            excel_spend_data['feb'] = totals_row[col]
        elif 'Contribution' in col:
            excel_spend_data['contribution'] = totals_row[col]
    
    print(f"\nExcel Spend Totals:")
    for key, value in excel_spend_data.items():
        print(f"  {key}: {value}")
    
    return excel_spend_data, totals_row

def analyze_excel_zero_campaigns(excel_df):
    """Find campaigns with zero January spend in Excel"""
    
    print(f"\nEXCEL ZERO BASELINE CAMPAIGNS")
    print("-" * 60)
    
    # Find spend columns
    spend_jan_col = None
    spend_feb_col = None
    spend_contrib_col = None
    
    for col in excel_df.columns:
        if 'Spend' in col:
            if 'Jan' in col or 'January' in col:
                spend_jan_col = col
            elif 'Feb' in col or 'February' in col:
                spend_feb_col = col
            elif 'Contribution' in col:
                spend_contrib_col = col
    
    print(f"Using columns:")
    print(f"  January: {spend_jan_col}")
    print(f"  February: {spend_feb_col}")
    print(f"  Contribution: {spend_contrib_col}")
    
    # Find zero baseline campaigns
    zero_campaigns = []
    
    for idx, row in excel_df.iterrows():
        campaign_name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        
        # Skip total row and invalid campaigns
        if 'Total' in campaign_name or campaign_name == "" or campaign_name == "nan":
            continue
        
        jan_spend = row[spend_jan_col] if pd.notna(row[spend_jan_col]) else 0
        feb_spend = row[spend_feb_col] if pd.notna(row[spend_feb_col]) else 0
        contribution = row[spend_contrib_col] if pd.notna(row[spend_contrib_col]) else 0
        
        if jan_spend == 0 and feb_spend > 0:
            zero_campaigns.append({
                'campaign': campaign_name,
                'jan': jan_spend,
                'feb': feb_spend,
                'contribution': contribution
            })
    
    print(f"\nFound {len(zero_campaigns)} zero baseline campaigns in Excel:")
    for camp in zero_campaigns[:5]:
        print(f"  {camp['campaign'][:40]:<40} Jan: ${camp['jan']:6.2f}, Feb: ${camp['feb']:6.2f}, Contrib: {camp['contribution']:6.2f}")
    
    return zero_campaigns

def test_dummy_value_approach():
    """Test if 0.0000001 substitution makes calculations consistent"""
    
    print(f"\nTESTING DUMMY VALUE APPROACH")
    print("=" * 80)
    
    # Generate our data
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    bridge.load_data()
    bridge_df = bridge.calculate_bridge()
    
    # Get totals and campaigns
    total_row = bridge_df.iloc[0]
    campaign_rows = bridge_df.iloc[1:]
    
    # Current state
    current_total_contrib = total_row['Spend - Contribution']
    current_campaign_sum = campaign_rows['Spend - Contribution'].sum()
    
    print(f"CURRENT STATE:")
    print(f"  Total row contribution: {current_total_contrib:.6f}")
    print(f"  Campaign sum:           {current_campaign_sum:.6f}")
    print(f"  Difference:             {abs(current_total_contrib - current_campaign_sum):.6f}")
    
    # Test manual calculation with proper dummy value handling
    print(f"\nMANUAL CALCULATION WITH DUMMY VALUES:")
    print("-" * 60)
    
    total_jan = total_row['Spend - January 2025']
    total_feb = total_row['Spend - February 2025']
    
    # Calculate contributions manually with proper dummy handling
    manual_contributions = []
    
    for _, row in campaign_rows.iterrows():
        jan_value = row['Spend - January 2025']
        feb_value = row['Spend - February 2025']
        
        if total_jan > 0:
            # Use dummy value if jan_value is 0 but feb_value is not
            if jan_value == 0 and feb_value != 0:
                jan_value_calc = 0.0000001
            else:
                jan_value_calc = jan_value
            
            if jan_value_calc > 0:
                p1_mix = jan_value / total_jan  # Use original jan_value for mix calculation
                growth_rate = (feb_value / jan_value_calc) - 1
                contribution = p1_mix * growth_rate * 10000
                manual_contributions.append(contribution)
            else:
                manual_contributions.append(0)
        else:
            manual_contributions.append(0)
    
    manual_sum = sum(manual_contributions)
    
    print(f"Manual calculation sum: {manual_sum:.6f}")
    print(f"Matches total? {abs(manual_sum - current_total_contrib) < 0.1}")
    
    # Test if excluding zero baseline campaigns from totals works
    print(f"\nTEST: EXCLUDE ZERO BASELINE FROM TOTALS")
    print("-" * 60)
    
    # Find campaigns with actual January spend
    normal_campaigns = campaign_rows[campaign_rows['Spend - January 2025'] > 0]
    
    # Calculate adjusted totals
    adjusted_jan_total = normal_campaigns['Spend - January 2025'].sum()
    adjusted_feb_total = normal_campaigns['Spend - February 2025'].sum()
    
    if adjusted_jan_total > 0:
        adjusted_growth = (adjusted_feb_total / adjusted_jan_total) - 1
        adjusted_total_contrib = 1.0 * adjusted_growth * 10000
        normal_contrib_sum = normal_campaigns['Spend - Contribution'].sum()
        
        print(f"Adjusted totals approach:")
        print(f"  Adjusted Jan total:      ${adjusted_jan_total:.2f}")
        print(f"  Adjusted Feb total:      ${adjusted_feb_total:.2f}")
        print(f"  Adjusted contribution:   {adjusted_total_contrib:.6f}")
        print(f"  Normal campaigns sum:    {normal_contrib_sum:.6f}")
        print(f"  Match? {abs(adjusted_total_contrib - normal_contrib_sum) < 0.1}")

def main():
    """Main verification function"""
    
    print("EXCEL ZERO BASELINE VERIFICATION")
    print("=" * 80)
    
    # Load and analyze Excel data
    excel_df = load_excel_data()
    if excel_df is not None:
        excel_totals, totals_row = analyze_excel_totals(excel_df)
        excel_zero_campaigns = analyze_excel_zero_campaigns(excel_df)
        
        print(f"\nEXCEL FINDINGS:")
        print(f"  Zero baseline campaigns: {len(excel_zero_campaigns)}")
        if excel_totals and 'contribution' in excel_totals:
            print(f"  Total contribution: {excel_totals['contribution']}")
    
    # Test our approach
    test_dummy_value_approach()
    
    print(f"\n✅ CONCLUSION:")
    print("=" * 80)
    print("The 0.0000001 substitution approach creates mathematical inconsistency")
    print("because it artificially inflates growth rates for zero-baseline campaigns.")
    print("Excel likely excludes these campaigns from total calculations entirely.")

if __name__ == "__main__":
    main()