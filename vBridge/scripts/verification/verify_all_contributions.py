#!/usr/bin/env python3
"""
Comprehensive verification that all KPI contributions are correctly summed.
This script tests the fix across all metrics to ensure contributions are properly calculated.
"""

import pandas as pd
import numpy as np
from src.core.bridge_calculator import BridgeCalculator
from src.config.metrics import MetricDefinitions

def create_comprehensive_test_data():
    """Create test data with various scenarios for all metrics"""
    # Create diverse campaign data
    campaigns = []
    
    # Campaign 1: Positive growth across all metrics
    campaigns.append({
        'CampaignName': 'Growth Campaign',
        'Spend': 1000, 'Spend_feb': 1200,
        'Total Ad Sales': 5000, 'Total Ad Sales_feb': 6000,
        'Impressions': 100000, 'Impressions_feb': 120000,
        'Clicks': 1000, 'Clicks_feb': 1200,
        'Total Ad Orders': 50, 'Total Ad Orders_feb': 60,
        'Ad Sales 7 Day': 3500, 'Ad Sales 7 Day_feb': 4200,
        'Ad Sales 14 Day': 4500, 'Ad Sales 14 Day_feb': 5400,
        'Ad Orders 7 Day': 35, 'Ad Orders 7 Day_feb': 42,
        'Ad Orders 14 Day': 45, 'Ad Orders 14 Day_feb': 54
    })
    
    # Campaign 2: Negative growth (declining performance)
    campaigns.append({
        'CampaignName': 'Declining Campaign',
        'Spend': 800, 'Spend_feb': 600,
        'Total Ad Sales': 4000, 'Total Ad Sales_feb': 3000,
        'Impressions': 80000, 'Impressions_feb': 60000,
        'Clicks': 800, 'Clicks_feb': 600,
        'Total Ad Orders': 40, 'Total Ad Orders_feb': 30,
        'Ad Sales 7 Day': 2800, 'Ad Sales 7 Day_feb': 2100,
        'Ad Sales 14 Day': 3600, 'Ad Sales 14 Day_feb': 2700,
        'Ad Orders 7 Day': 28, 'Ad Orders 7 Day_feb': 21,
        'Ad Orders 14 Day': 36, 'Ad Orders 14 Day_feb': 27
    })
    
    # Campaign 3: Zero baseline (new campaign)
    campaigns.append({
        'CampaignName': 'New Campaign',
        'Spend': 0, 'Spend_feb': 500,
        'Total Ad Sales': 0, 'Total Ad Sales_feb': 2500,
        'Impressions': 0, 'Impressions_feb': 50000,
        'Clicks': 0, 'Clicks_feb': 500,
        'Total Ad Orders': 0, 'Total Ad Orders_feb': 25,
        'Ad Sales 7 Day': 0, 'Ad Sales 7 Day_feb': 1750,
        'Ad Sales 14 Day': 0, 'Ad Sales 14 Day_feb': 2250,
        'Ad Orders 7 Day': 0, 'Ad Orders 7 Day_feb': 18,
        'Ad Orders 14 Day': 0, 'Ad Orders 14 Day_feb': 23
    })
    
    # Campaign 4: Mixed performance
    campaigns.append({
        'CampaignName': 'Mixed Campaign',
        'Spend': 1500, 'Spend_feb': 1800,
        'Total Ad Sales': 7500, 'Total Ad Sales_feb': 7000,
        'Impressions': 150000, 'Impressions_feb': 180000,
        'Clicks': 1500, 'Clicks_feb': 1400,
        'Total Ad Orders': 75, 'Total Ad Orders_feb': 70,
        'Ad Sales 7 Day': 5250, 'Ad Sales 7 Day_feb': 4900,
        'Ad Sales 14 Day': 6750, 'Ad Sales 14 Day_feb': 6300,
        'Ad Orders 7 Day': 53, 'Ad Orders 7 Day_feb': 49,
        'Ad Orders 14 Day': 68, 'Ad Orders 14 Day_feb': 63
    })
    
    return pd.DataFrame(campaigns)

def verify_contribution_calculations(result_df):
    """Verify that all contributions are properly calculated"""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE CONTRIBUTION VERIFICATION")
    print("="*80)
    
    # Get all metrics
    all_metrics = MetricDefinitions.get_all_metrics()
    
    # Separate total row from campaign rows
    total_row = result_df[result_df['Campaign'] == 'Total'].iloc[0]
    campaign_rows = result_df[result_df['Campaign'] != 'Total']
    
    verification_results = []
    
    for metric in all_metrics:
        contribution_col = f'{metric} - Contribution'
        if contribution_col in result_df.columns:
            # Sum individual campaign contributions
            campaign_sum = campaign_rows[contribution_col].sum()
            
            # Get total row contribution
            total_contribution = total_row[contribution_col]
            
            # Check if they match
            difference = abs(campaign_sum - total_contribution)
            matches = difference < 0.01  # Allow small floating point differences
            
            result = {
                'metric': metric,
                'campaign_sum': campaign_sum,
                'total_row': total_contribution,
                'difference': difference,
                'matches': matches
            }
            verification_results.append(result)
            
            # Print result
            status = "✅ PASS" if matches else "❌ FAIL"
            print(f"\n{status} {metric}:")
            print(f"  Campaign Sum: {campaign_sum:,.4f}")
            print(f"  Total Row:    {total_contribution:,.4f}")
            if not matches:
                print(f"  Difference:   {difference:,.4f}")
    
    # Summary
    print("\n" + "-"*80)
    passed = sum(1 for r in verification_results if r['matches'])
    total = len(verification_results)
    print(f"\n📊 VERIFICATION SUMMARY: {passed}/{total} metrics passed")
    
    if passed == total:
        print("\n✅ SUCCESS: All KPI contributions are correctly summed!")
    else:
        print("\n❌ FAILURE: Some KPI contributions have issues")
        failed_metrics = [r['metric'] for r in verification_results if not r['matches']]
        print(f"Failed metrics: {', '.join(failed_metrics)}")
    
    return verification_results

def display_contribution_details(result_df):
    """Display detailed contribution information for each metric"""
    print("\n" + "="*80)
    print("📈 CONTRIBUTION DETAILS BY METRIC")
    print("="*80)
    
    # Get metrics that have contributions
    all_metrics = MetricDefinitions.get_all_metrics()
    campaign_rows = result_df[result_df['Campaign'] != 'Total']
    
    for metric in all_metrics:
        contribution_col = f'{metric} - Contribution'
        if contribution_col in result_df.columns:
            print(f"\n{metric}:")
            print("-" * 40)
            
            # Show individual campaign contributions
            for _, row in campaign_rows.iterrows():
                contribution = row[contribution_col]
                if abs(contribution) > 0.01:  # Only show non-zero contributions
                    print(f"  {row['Campaign']:.<30} {contribution:>10.2f} bps")
            
            # Show total
            total_contribution = result_df[result_df['Campaign'] == 'Total'].iloc[0][contribution_col]
            print(f"  {'TOTAL':.<30} {total_contribution:>10.2f} bps")

def main():
    """Run comprehensive verification test"""
    print("🚀 Running comprehensive contribution verification...")
    
    # Create test data
    test_data = create_comprehensive_test_data()
    
    print("\n📊 Test Data Summary:")
    print(f"  - {len(test_data)} campaigns")
    print(f"  - Mix of growth patterns: positive, negative, zero baseline, mixed")
    print(f"  - Testing all {len(MetricDefinitions.get_all_metrics())} metrics")
    
    # Calculate bridge with contributions
    print("\n🔧 Calculating bridge with contributions...")
    result_df = BridgeCalculator.calculate_bridge(test_data, validate=False)
    
    # Verify contributions
    verification_results = verify_contribution_calculations(result_df)
    
    # Display detailed results
    display_contribution_details(result_df)
    
    # Check specific examples
    print("\n" + "="*80)
    print("🔍 SPECIFIC EXAMPLES")
    print("="*80)
    
    total_row = result_df[result_df['Campaign'] == 'Total'].iloc[0]
    
    # Show a few key metrics
    key_metrics = ['Spend', 'Total Ad Sales', 'Impressions']
    for metric in key_metrics:
        print(f"\n{metric}:")
        print(f"  January Total:  ${total_row[f'{metric} - January 2025']:,.2f}")
        print(f"  February Total: ${total_row[f'{metric} - February 2025']:,.2f}")
        print(f"  Net Change:     ${total_row[f'{metric} - Net Change']:,.2f}")
        print(f"  % Change:       {total_row[f'{metric} - % Change']:.2f}%")
        print(f"  Contribution:   {total_row[f'{metric} - Contribution']:.2f} bps")
    
    # Save results for inspection
    output_file = 'output/contribution_verification_results.csv'
    result_df.to_csv(output_file, index=False)
    print(f"\n💾 Full results saved to: {output_file}")
    
    return all(r['matches'] for r in verification_results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)