#!/usr/bin/env python3
"""
Manual comparison of Excel vs CSV with proper handling of duplicate column names
"""

import pandas as pd
import numpy as np

def main():
    print("🔍 MANUAL MIXBRIDGE COMPARISON (FILTERED)")
    print("=" * 80)
    
    # Load files
    print("\n📊 Loading files...")
    excel_df = pd.read_excel('../data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx', 
                             sheet_name='Campaign', header=12)
    csv_df = pd.read_csv('../output/analyses/mixbridge_jan2025-feb2025_delta_20250718_153220.csv')
    
    print(f"✅ Excel loaded: {len(excel_df)} rows, {len(excel_df.columns)} columns")
    print(f"✅ CSV loaded (original): {len(csv_df)} rows, {len(csv_df.columns)} columns")
    
    # Filter CSV to only include campaigns that exist in Excel
    excel_campaigns = set(excel_df['Campaign'].unique())
    csv_df_filtered = csv_df[csv_df['Campaign'].isin(excel_campaigns)].copy()
    
    print(f"✅ CSV filtered to Excel campaigns: {len(csv_df_filtered)} rows")
    print(f"📊 Filtering removed {len(csv_df) - len(csv_df_filtered)} campaigns from CSV")
    
    # Now use the filtered CSV for all comparisons
    csv_df = csv_df_filtered
    
    # Recalculate totals for filtered CSV data
    print("\n📊 Recalculating totals for filtered CSV data...")
    
    # Remove existing Total row from filtered data
    csv_df_no_total = csv_df[csv_df['Campaign'] != 'Total'].copy()
    
    # Calculate new totals for numeric columns
    numeric_columns = csv_df_no_total.select_dtypes(include=[np.number]).columns
    csv_totals = {}
    
    for col in numeric_columns:
        if 'contribution' in col.lower():
            # Contribution columns should sum to 0 or near 0
            csv_totals[col] = csv_df_no_total[col].sum()
        elif '%' in col or 'rate' in col.lower() or 'ctr' in col.lower() or 'acos' in col.lower() or 'roas' in col.lower():
            # These are rates/percentages - calculate weighted average or specific logic
            if 'Spend - % Change' in col:
                jan_spend = csv_df_no_total['Spend - January 2025'].sum()
                feb_spend = csv_df_no_total['Spend - February 2025'].sum()
                csv_totals[col] = ((feb_spend - jan_spend) / jan_spend * 100) if jan_spend != 0 else 0
            elif 'ACoS' in col:
                if 'January' in col:
                    spend = csv_df_no_total['Spend - January 2025'].sum()
                    sales = csv_df_no_total['Total Ad Sales - January 2025'].sum()
                    csv_totals[col] = (spend / sales * 100) if sales != 0 else 0
                elif 'February' in col:
                    spend = csv_df_no_total['Spend - February 2025'].sum()
                    sales = csv_df_no_total['Total Ad Sales - February 2025'].sum()
                    csv_totals[col] = (spend / sales * 100) if sales != 0 else 0
            else:
                # For other rates, use mean for now
                csv_totals[col] = csv_df_no_total[col].mean()
        else:
            # Regular numeric columns - sum them
            csv_totals[col] = csv_df_no_total[col].sum()
    
    # Create a total row series
    csv_total = pd.Series(csv_totals)
    csv_total['Campaign'] = 'Total'
    
    # Get Excel total
    excel_total = excel_df[excel_df['Campaign'] == 'Total'].iloc[0]
    
    # Metrics comparison
    print("\n🎯 TOTAL ROW COMPARISON")
    print("-" * 80)
    
    # Define metrics to compare (Excel column -> CSV column mapping)
    metrics_map = [
        ('Spend - January 2025', 'January 2025', 'Spend - January 2025'),
        ('Spend - February 2025', 'February 2025', 'Spend - February 2025'),
        ('Spend - Net Change', 'Net Change', 'Spend - Net Change'),
        ('Spend - % Change', '% Change', 'Spend - % Change'),
        ('Total Ad Sales - January 2025', 'January 2025.1', 'Total Ad Sales - January 2025'),
        ('Total Ad Sales - February 2025', 'February 2025.1', 'Total Ad Sales - February 2025'),
        ('ACoS - January 2025', 'January 2025.2', 'ACoS - January 2025'),
        ('ACoS - February 2025', 'February 2025.2', 'ACoS - February 2025'),
    ]
    
    results = []
    for metric_name, excel_col, csv_col in metrics_map:
        if excel_col in excel_total.index and csv_col in csv_total.index:
            excel_val = excel_total[excel_col]
            csv_val = csv_total[csv_col]
            
            # Handle numeric conversion
            try:
                excel_val = float(excel_val)
                csv_val = float(csv_val)
                
                diff = csv_val - excel_val
                if excel_val != 0:
                    rel_diff = abs(diff / excel_val * 100)
                else:
                    rel_diff = 0 if csv_val == 0 else 100
                
                # Grade
                if rel_diff < 0.01:
                    grade = '🎯 PERFECT'
                elif rel_diff < 0.1:
                    grade = '✅ EXCELLENT'
                elif rel_diff < 1.0:
                    grade = '✅ GOOD'  
                elif rel_diff < 5.0:
                    grade = '⚠️ FAIR'
                else:
                    grade = '❌ POOR'
                
                print(f"\n📊 {metric_name}:")
                print(f"   Excel: {excel_val:,.2f}")
                print(f"   CSV:   {csv_val:,.2f}")
                print(f"   Diff:  {diff:,.2f} ({rel_diff:.2f}%)")
                print(f"   Grade: {grade}")
                
                results.append({
                    'metric': metric_name,
                    'excel': excel_val,
                    'csv': csv_val,
                    'diff': diff,
                    'rel_diff': rel_diff,
                    'grade': grade
                })
            except:
                print(f"\n❌ Could not compare {metric_name}")
    
    # Sample campaigns comparison
    print("\n\n🔍 SAMPLE CAMPAIGN COMPARISON")
    print("-" * 80)
    
    # Find common campaigns
    common_campaigns = list(set(excel_df['Campaign']) & set(csv_df['Campaign']))
    common_campaigns = [c for c in common_campaigns if c != 'Total'][:5]
    
    for campaign in common_campaigns:
        excel_row = excel_df[excel_df['Campaign'] == campaign].iloc[0]
        csv_row = csv_df[csv_df['Campaign'] == campaign].iloc[0]
        
        print(f"\n📋 Campaign: {campaign}")
        
        # Compare Spend metrics
        excel_spend_jan = excel_row['January 2025']
        csv_spend_jan = csv_row['Spend - January 2025']
        
        try:
            excel_spend_jan = float(excel_spend_jan)
            csv_spend_jan = float(csv_spend_jan)
            
            diff = abs(csv_spend_jan - excel_spend_jan)
            rel_diff = (diff / excel_spend_jan * 100) if excel_spend_jan != 0 else 0
            
            status = "✅ PASS" if rel_diff < 1.0 else "⚠️ REVIEW"
            
            print(f"   January Spend: Excel={excel_spend_jan:.2f}, CSV={csv_spend_jan:.2f}")
            print(f"   Difference: {rel_diff:.2f}% {status}")
        except:
            print(f"   ❌ Could not compare January Spend")
    
    # Summary
    print("\n\n📊 SUMMARY")
    print("=" * 80)
    
    # Show campaigns that were filtered out
    original_csv = pd.read_csv('../output/analyses/mixbridge_jan2025-feb2025_delta_20250718_153220.csv')
    all_csv_campaigns = set(original_csv['Campaign'].unique())
    filtered_out = all_csv_campaigns - excel_campaigns
    filtered_out.discard('Total')  # Remove Total from the list
    
    print(f"\n📋 Filtering Information:")
    print(f"   Original CSV campaigns: {len(all_csv_campaigns) - 1}")  # -1 for Total
    print(f"   Excel campaigns: {len(excel_campaigns) - 1}")  # -1 for Total
    print(f"   Filtered out: {len(filtered_out)} campaigns")
    if len(filtered_out) > 0:
        print(f"   Examples of filtered campaigns: {list(filtered_out)[:5]}")
    
    if results:
        avg_error = np.mean([r['rel_diff'] for r in results])
        max_error = max([r['rel_diff'] for r in results])
        
        print(f"\n📈 Comparison Results (after filtering):")
        print(f"   Average Error: {avg_error:.2f}%")
        print(f"   Maximum Error: {max_error:.2f}%")
        
        if avg_error < 0.1:
            overall = "🎯 EXCELLENT - Ready for production"
        elif avg_error < 1.0:
            overall = "✅ GOOD - Generally acceptable"
        elif avg_error < 5.0:
            overall = "⚠️ FAIR - Review recommended"
        else:
            overall = "❌ POOR - Investigation required"
        
        print(f"\n🎯 Overall Assessment: {overall}")
    
    print("\n" + "=" * 80)
    print("✅ Comparison complete!")

if __name__ == "__main__":
    main()