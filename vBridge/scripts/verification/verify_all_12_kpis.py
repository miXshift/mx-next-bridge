#!/usr/bin/env python3
"""
Comprehensive verification of all 12 KPIs implementation
"""

import pandas as pd
from src.config.metrics import MetricDefinitions

def verify_all_kpis():
    """Verify all 12 KPIs are properly implemented"""
    print('🎯 ALL 12 KPIS VERIFICATION')
    print('='*80)
    
    # Read the latest results
    df = pd.read_csv('output/current/LATEST_mixbridge.csv')
    total_row = df[df['Campaign'] == 'Total'].iloc[0]
    campaign_rows = df[df['Campaign'] != 'Total']
    
    # Get all metric categories
    categories = MetricDefinitions.get_metrics_by_category()
    
    print('📊 METRIC CATEGORIZATION:')
    print('-'*80)
    for category, metrics in categories.items():
        if category != 'percentage':  # Skip percentage as it's a formatting category
            print(f'{category.upper().replace("_", " ")}: {len(metrics)} metrics')
            for metric in metrics:
                methodology = MetricDefinitions.get_calculation_methodology(metric)
                print(f'  • {metric:<20} | {methodology}')
    
    print('\n🔍 KPI ANALYSIS BY METHODOLOGY:')
    print('='*80)
    
    # 1. Traditional Mix Bridge (Absolute Metrics)
    print('\n1. TRADITIONAL MIX BRIDGE (9 Metrics):')
    print('-'*60)
    absolute_metrics = MetricDefinitions.get_absolute_metrics()
    for metric in absolute_metrics:
        jan_val = total_row[f'{metric} - January 2025']
        feb_val = total_row[f'{metric} - February 2025']
        net_change = total_row[f'{metric} - Net Change']
        pct_change = total_row[f'{metric} - % Change']
        contribution = total_row[f'{metric} - Contribution']
        
        # Count campaigns with non-zero contributions
        non_zero_campaigns = (abs(campaign_rows[f'{metric} - Contribution']) > 0.01).sum()
        
        print(f'  {metric:<20} | P1: {jan_val:>10.2f} | P2: {feb_val:>10.2f} | '
              f'Net: {net_change:>10.2f} | %: {pct_change:>8.2f}% | '
              f'Contrib: {contribution:>10.2f} | Campaigns: {non_zero_campaigns:>3d}')
    
    # 2. MixRate Bridge with Infinity Error (ACoS)
    print('\n2. MIXRATE BRIDGE WITH INFINITY ERROR (1 Metric):')
    print('-'*60)
    infinity_metrics = MetricDefinitions.get_mixrate_infinity_metrics()
    for metric in infinity_metrics:
        jan_val = total_row[f'{metric} - January 2025']
        feb_val = total_row[f'{metric} - February 2025']
        pts_change = total_row[f'{metric} - Pts Change']
        pct_change = total_row[f'{metric} - % Change']
        contribution = total_row[f'{metric} - Contribution']
        
        non_zero_campaigns = (abs(campaign_rows[f'{metric} - Contribution']) > 0.01).sum()
        
        print(f'  {metric:<20} | P1: {jan_val:>10.2f}% | P2: {feb_val:>10.2f}% | '
              f'Pts: {pts_change:>10.2f} | %: {pct_change:>8.2f}% | '
              f'Contrib: {contribution:>10.2f} bps | Campaigns: {non_zero_campaigns:>3d}')
        
        print(f'    → Calculated via ROAS inverse to prevent infinity errors')
    
    # 3. Standard MixRate Bridge (ROAS, Conversion Rate, CTR, CPC)
    print('\n3. STANDARD MIXRATE BRIDGE (4 Metrics):')
    print('-'*60)
    standard_metrics = MetricDefinitions.get_mixrate_standard_metrics()
    for metric in standard_metrics:
        jan_val = total_row[f'{metric} - January 2025']
        feb_val = total_row[f'{metric} - February 2025']
        
        # Check if it's a percentage metric for proper formatting
        if metric in ['Conversion Rate', 'CTR']:
            change_col = f'{metric} - Pts Change'
            change_val = total_row[change_col]
            print(f'  {metric:<20} | P1: {jan_val:>10.2f}% | P2: {feb_val:>10.2f}% | '
                  f'Pts: {change_val:>10.2f}', end='')
        else:
            change_col = f'{metric} - Net Change' 
            change_val = total_row[change_col]
            print(f'  {metric:<20} | P1: {jan_val:>10.4f} | P2: {feb_val:>10.4f} | '
                  f'Net: {change_val:>10.4f}', end='')
        
        pct_change = total_row[f'{metric} - % Change']
        contribution = total_row[f'{metric} - Contribution']
        non_zero_campaigns = (abs(campaign_rows[f'{metric} - Contribution']) > 0.01).sum()
        
        print(f' | %: {pct_change:>8.2f}% | '
              f'Contrib: {contribution:>10.4f} | Campaigns: {non_zero_campaigns:>3d}')
        
        # Show mix determinant
        from src.core.mixrate_calculator import MixRateBridgeCalculator
        calculator = MixRateBridgeCalculator()
        mix_determinant = calculator._get_mix_determinant_for_metric(metric)
        print(f'    → Mix determinant: {mix_determinant}')
    
    print('\n📈 CONTRIBUTION SUMMARY:')
    print('='*80)
    
    # Summary statistics
    all_metrics = MetricDefinitions.get_all_metrics()
    total_metrics = len(all_metrics)
    metrics_with_contributions = 0
    total_campaigns_with_contributions = 0
    
    for metric in all_metrics:
        contribution_col = f'{metric} - Contribution'
        total_contrib = total_row[contribution_col]
        non_zero_campaigns = (abs(campaign_rows[contribution_col]) > 0.01).sum()
        
        if abs(total_contrib) > 0.01 or non_zero_campaigns > 0:
            metrics_with_contributions += 1
            total_campaigns_with_contributions += non_zero_campaigns
    
    print(f'✅ Total KPIs: {total_metrics}')
    print(f'✅ KPIs with contributions: {metrics_with_contributions}')
    print(f'✅ Campaign-KPI combinations with contributions: {total_campaigns_with_contributions}')
    print(f'✅ Average campaigns per KPI: {total_campaigns_with_contributions/metrics_with_contributions:.1f}')
    
    # Validation checks
    print(f'\n🔍 VALIDATION CHECKS:')
    print('='*80)
    
    validation_results = []
    
    # Check 1: All metrics have P1, P2, change, % change, contribution columns
    missing_columns = []
    for metric in all_metrics:
        required_cols = [
            f'{metric} - January 2025',
            f'{metric} - February 2025', 
            f'{metric} - % Change',
            f'{metric} - Contribution'
        ]
        
        # Add appropriate change column
        if metric in ['ACoS', 'CTR', 'Conversion Rate']:
            required_cols.append(f'{metric} - Pts Change')
        else:
            required_cols.append(f'{metric} - Net Change')
        
        for col in required_cols:
            if col not in df.columns:
                missing_columns.append(col)
    
    check1_pass = len(missing_columns) == 0
    validation_results.append(('All required columns present', check1_pass))
    if not check1_pass:
        print(f'❌ Missing columns: {missing_columns[:5]}{"..." if len(missing_columns) > 5 else ""}')
    else:
        print('✅ All required columns present')
    
    # Check 2: Mathematical consistency - campaign contributions sum to totals
    consistency_issues = []
    for metric in all_metrics:
        contribution_col = f'{metric} - Contribution'
        campaign_sum = campaign_rows[contribution_col].sum()
        total_contrib = total_row[contribution_col]
        difference = abs(campaign_sum - total_contrib)
        
        if difference > 0.01:  # 0.01 tolerance
            consistency_issues.append((metric, difference))
    
    check2_pass = len(consistency_issues) == 0
    validation_results.append(('Mathematical consistency', check2_pass))
    if not check2_pass:
        print(f'❌ Mathematical inconsistencies in: {[issue[0] for issue in consistency_issues[:3]]}')
    else:
        print('✅ Mathematical consistency verified')
    
    # Check 3: Rate metrics have non-zero contributions
    rate_metrics = MetricDefinitions.get_rate_metrics()
    rate_metrics_with_contributions = 0
    for metric in rate_metrics:
        if abs(total_row[f'{metric} - Contribution']) > 0.01:
            rate_metrics_with_contributions += 1
    
    check3_pass = rate_metrics_with_contributions == len(rate_metrics)
    validation_results.append(('All rate metrics have contributions', check3_pass))
    if not check3_pass:
        missing_rate_metrics = len(rate_metrics) - rate_metrics_with_contributions
        print(f'⚠️  {missing_rate_metrics} rate metrics still have zero contributions')
    else:
        print('✅ All rate metrics have contributions')
    
    # Overall success
    all_checks_pass = all(result[1] for result in validation_results)
    
    print(f'\n🎯 OVERALL IMPLEMENTATION STATUS:')
    print('='*80)
    print(f'Status: {"✅ SUCCESS" if all_checks_pass else "⚠️  PARTIAL SUCCESS"}')
    print(f'Validation Score: {sum(result[1] for result in validation_results)}/{len(validation_results)} checks passed')
    
    if all_checks_pass:
        print('\n🎉 ALL 12 KPIS SUCCESSFULLY IMPLEMENTED!')
        print('   • Traditional Mix Bridge: 9 metrics')
        print('   • MixRate Bridge with Infinity Error: 1 metric (ACoS)')  
        print('   • Standard MixRate Bridge: 4 metrics (ROAS, Conversion Rate, CTR, CPC)')
        print('   • All metrics have P1, P2, change, % change, and contribution values')
        print('   • Mathematical consistency verified across all methodologies')
    
    return {
        'total_kpis': total_metrics,
        'kpis_with_contributions': metrics_with_contributions,
        'validation_results': validation_results,
        'all_checks_pass': all_checks_pass
    }

if __name__ == "__main__":
    results = verify_all_kpis()