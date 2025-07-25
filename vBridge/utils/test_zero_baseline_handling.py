#!/usr/bin/env python3
"""
Comprehensive Testing for Zero Baseline Handling
Tests all three strategies with various scenarios
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

from enhanced_mixbridge_calculator import EnhancedMixBridgeCalculator
from mixbridge_config import MixBridgeConfig
from mixbridge_validator import ContributionValidator


class ZeroBaselineTestSuite:
    """Comprehensive testing for zero baseline scenarios"""
    
    def __init__(self):
        """Initialize test suite"""
        self.test_cases = self._generate_test_cases()
        self.strategies = ['dummy_value', 'delta_assignment', 'hybrid']
        self.results = {}
    
    def _generate_test_cases(self) -> Dict[str, Dict]:
        """Generate test scenarios for zero baseline handling"""
        return {
            'simple_zero_baseline': {
                'description': 'Simple scenario with one zero baseline campaign',
                'campaigns': [
                    {'name': 'New_Campaign', 'spend_p1': 0, 'spend_p2': 100, 'sales_p1': 0, 'sales_p2': 150},
                    {'name': 'Existing_Campaign', 'spend_p1': 50, 'spend_p2': 75, 'sales_p1': 200, 'sales_p2': 250}
                ],
                'expected_behavior': 'delta_assignment_accurate'
            },
            
            'multiple_zero_baseline': {
                'description': 'Multiple new campaigns starting from zero',
                'campaigns': [
                    {'name': 'New_A', 'spend_p1': 0, 'spend_p2': 80, 'sales_p1': 0, 'sales_p2': 120},
                    {'name': 'New_B', 'spend_p1': 0, 'spend_p2': 120, 'sales_p1': 0, 'sales_p2': 200},
                    {'name': 'Existing', 'spend_p1': 100, 'spend_p2': 150, 'sales_p1': 300, 'sales_p2': 400}
                ],
                'expected_behavior': 'proportional_assignment'
            },
            
            'mixed_scenarios': {
                'description': 'Mix of new, growing, and declining campaigns',
                'campaigns': [
                    {'name': 'New_Campaign', 'spend_p1': 0, 'spend_p2': 200, 'sales_p1': 0, 'sales_p2': 400},
                    {'name': 'Growing_Campaign', 'spend_p1': 100, 'spend_p2': 150, 'sales_p1': 300, 'sales_p2': 500},
                    {'name': 'Declining_Campaign', 'spend_p1': 100, 'spend_p2': 50, 'sales_p1': 200, 'sales_p2': 100},
                    {'name': 'Stable_Campaign', 'spend_p1': 80, 'spend_p2': 82, 'sales_p1': 240, 'sales_p2': 245}
                ],
                'expected_behavior': 'mathematical_consistency'
            },
            
            'edge_cases': {
                'description': 'Edge cases and boundary conditions',
                'campaigns': [
                    {'name': 'Zero_Both', 'spend_p1': 0, 'spend_p2': 0, 'sales_p1': 0, 'sales_p2': 0},
                    {'name': 'Tiny_P1', 'spend_p1': 1e-10, 'spend_p2': 100, 'sales_p1': 1e-8, 'sales_p2': 200},
                    {'name': 'Discontinued', 'spend_p1': 50, 'spend_p2': 0, 'sales_p1': 150, 'sales_p2': 0},
                    {'name': 'Massive_Growth', 'spend_p1': 1, 'spend_p2': 1000, 'sales_p1': 2, 'sales_p2': 3000}
                ],
                'expected_behavior': 'graceful_handling'
            },
            
            'real_world_simulation': {
                'description': 'Realistic campaign portfolio simulation',
                'campaigns': [
                    # Established campaigns
                    {'name': 'Brand_Core', 'spend_p1': 1000, 'spend_p2': 1200, 'sales_p1': 4000, 'sales_p2': 5000},
                    {'name': 'Product_A', 'spend_p1': 500, 'spend_p2': 450, 'sales_p1': 2000, 'sales_p2': 1800},
                    {'name': 'Product_B', 'spend_p1': 300, 'spend_p2': 350, 'sales_p1': 1200, 'sales_p2': 1400},
                    # New launches
                    {'name': 'New_Product_X', 'spend_p1': 0, 'spend_p2': 200, 'sales_p1': 0, 'sales_p2': 600},
                    {'name': 'New_Product_Y', 'spend_p1': 0, 'spend_p2': 150, 'sales_p1': 0, 'sales_p2': 400},
                    # Seasonal campaigns
                    {'name': 'Holiday_Special', 'spend_p1': 0, 'spend_p2': 800, 'sales_p1': 0, 'sales_p2': 3200},
                    # Underperforming
                    {'name': 'Legacy_Product', 'spend_p1': 200, 'spend_p2': 50, 'sales_p1': 400, 'sales_p2': 100}
                ],
                'expected_behavior': 'realistic_portfolio_analysis'
            }
        }
    
    def _create_test_dataframe(self, campaigns: List[Dict]) -> pd.DataFrame:
        """
        Create test dataframe from campaign specifications
        
        Args:
            campaigns: List of campaign dictionaries
            
        Returns:
            DataFrame formatted for bridge calculation
        """
        data = []
        for campaign in campaigns:
            # Create merged data structure similar to bridge_calculator input
            row = {
                'CampaignName': campaign['name'],
                'Spend - January 2025': campaign['spend_p1'],
                'Spend - February 2025': campaign['spend_p2'],
                'Total Ad Sales - January 2025': campaign['sales_p1'],
                'Total Ad Sales - February 2025': campaign['sales_p2'],
                'Impressions - January 2025': campaign['spend_p1'] * 1000,  # Simulated impressions
                'Impressions - February 2025': campaign['spend_p2'] * 1000,
                'Clicks - January 2025': campaign['spend_p1'] * 10,  # Simulated clicks
                'Clicks - February 2025': campaign['spend_p2'] * 10,
                'Same SKU Ad Sales - January 2025': campaign['sales_p1'] * 0.8,  # 80% same SKU
                'Same SKU Ad Sales - February 2025': campaign['sales_p2'] * 0.8,
                'Other SKU Sales - January 2025': campaign['sales_p1'] * 0.2,  # 20% other SKU
                'Other SKU Sales - February 2025': campaign['sales_p2'] * 0.2,
                'Same SKU Ad Orders - January 2025': campaign['sales_p1'] / 50,  # Avg order value $50
                'Same SKU Ad Orders - February 2025': campaign['sales_p2'] / 50,
                'Other SKU Ad Orders - January 2025': campaign['sales_p1'] / 100,  # Lower conversion
                'Other SKU Ad Orders - February 2025': campaign['sales_p2'] / 100,
                'Total Ad Orders - January 2025': campaign['sales_p1'] / 40,  # Combined
                'Total Ad Orders - February 2025': campaign['sales_p2'] / 40
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _create_totals_row(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create totals row for test data"""
        metrics = ['Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
                  'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
                  'Other SKU Ad Orders', 'Total Ad Orders']
        
        totals_data = {'Campaign': 'Total'}
        
        for metric in metrics:
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            
            totals_data[jan_col] = df[jan_col].sum()
            totals_data[feb_col] = df[feb_col].sum()
            
            # Calculate changes
            if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                totals_data[f'{metric} - Pts Change'] = 0  # Will be calculated
            else:
                totals_data[f'{metric} - Net Change'] = totals_data[feb_col] - totals_data[jan_col]
            
            # Calculate percentage change
            if totals_data[jan_col] > 0:
                totals_data[f'{metric} - % Change'] = (
                    (totals_data[feb_col] - totals_data[jan_col]) / totals_data[jan_col]
                ) * 100
            else:
                totals_data[f'{metric} - % Change'] = 0
            
            # Initialize contribution
            totals_data[f'{metric} - Contribution'] = 0
        
        return pd.DataFrame([totals_data])
    
    def run_strategy_comparison(self) -> Dict[str, Any]:
        """
        Run comprehensive comparison of all strategies across test cases
        
        Returns:
            Dictionary with detailed comparison results
        """
        results = {}
        
        print("="*80)
        print("ZERO BASELINE HANDLING - STRATEGY COMPARISON")
        print("="*80)
        
        for test_name, test_case in self.test_cases.items():
            print(f"\n{'='*20} {test_name.upper()} {'='*20}")
            print(f"Description: {test_case['description']}")
            
            # Create test data
            test_df = self._create_test_dataframe(test_case['campaigns'])
            totals_row = self._create_totals_row(test_df)
            
            test_results = {}
            
            # Test each strategy
            for strategy in self.strategies:
                print(f"\n--- Testing {strategy.upper()} Strategy ---")
                
                try:
                    # Run calculation
                    config = MixBridgeConfig(
                        zero_baseline_strategy=strategy,
                        precision_decimals=6,  # Reduced for cleaner output
                        mathematical_validation=True
                    )
                    
                    calculator = EnhancedMixBridgeCalculator(
                        strategy=strategy, 
                        precision=config.precision_decimals
                    )
                    
                    result_df = calculator.calculate_contributions_enhanced(
                        test_df.copy(), totals_row.copy(), strategy
                    )
                    
                    # Validate results
                    validator = ContributionValidator(config)
                    is_valid = validator.validate_contributions(result_df, totals_row)
                    
                    # Calculate summary statistics
                    summary = calculator.get_calculation_summary(result_df, totals_row)
                    
                    # Analyze zero baseline handling
                    zero_baseline_analysis = self._analyze_zero_baseline_handling(
                        result_df, test_case['campaigns'], strategy
                    )
                    
                    test_results[strategy] = {
                        'validation_passed': is_valid,
                        'calculation_summary': summary,
                        'zero_baseline_analysis': zero_baseline_analysis,
                        'result_dataframe': result_df,
                        'validation_details': validator.get_validation_report()
                    }
                    
                    # Print key results
                    print(f"Validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
                    print(f"Zero baseline campaigns handled: {zero_baseline_analysis['campaigns_handled']}")
                    print(f"Total contribution assigned: {zero_baseline_analysis['total_contribution']:.2f} bps")
                    
                except Exception as e:
                    print(f"❌ ERROR: {str(e)}")
                    test_results[strategy] = {
                        'error': str(e),
                        'validation_passed': False
                    }
            
            results[test_name] = test_results
            
            # Strategy comparison for this test case
            self._print_strategy_comparison(test_name, test_results)
        
        return results
    
    def _analyze_zero_baseline_handling(self, result_df: pd.DataFrame, 
                                      campaigns: List[Dict], strategy: str) -> Dict[str, Any]:
        """Analyze how zero baseline campaigns were handled"""
        analysis = {
            'strategy': strategy,
            'campaigns_handled': 0,
            'total_contribution': 0,
            'campaign_details': []
        }
        
        for campaign in campaigns:
            if campaign['spend_p1'] == 0 and campaign['spend_p2'] > 0:
                # Find this campaign in results
                campaign_row = result_df[result_df['CampaignName'] == campaign['name']]
                if len(campaign_row) > 0:
                    spend_contrib = campaign_row['Spend - Contribution'].iloc[0]
                    analysis['campaigns_handled'] += 1
                    analysis['total_contribution'] += spend_contrib
                    analysis['campaign_details'].append({
                        'name': campaign['name'],
                        'p2_spend': campaign['spend_p2'],
                        'contribution': spend_contrib
                    })
        
        return analysis
    
    def _print_strategy_comparison(self, test_name: str, results: Dict[str, Any]):
        """Print comparison table for strategies"""
        print(f"\n--- STRATEGY COMPARISON: {test_name} ---")
        print(f"{'Strategy':<15} {'Validation':<12} {'Zero Handled':<12} {'Total Contrib':<15}")
        print("-" * 60)
        
        for strategy in self.strategies:
            if strategy in results and 'error' not in results[strategy]:
                result = results[strategy]
                validation = "✅ PASS" if result['validation_passed'] else "❌ FAIL"
                handled = result['zero_baseline_analysis']['campaigns_handled']
                contrib = result['zero_baseline_analysis']['total_contribution']
                print(f"{strategy:<15} {validation:<12} {handled:<12} {contrib:<15.2f}")
            else:
                print(f"{strategy:<15} {'❌ ERROR':<12} {'-':<12} {'-':<15}")
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("="*80)
        report.append("COMPREHENSIVE ZERO BASELINE HANDLING TEST REPORT")
        report.append("="*80)
        
        # Summary statistics
        total_tests = len(results)
        strategy_success_rates = {strategy: 0 for strategy in self.strategies}
        
        for test_name, test_results in results.items():
            for strategy in self.strategies:
                if (strategy in test_results and 
                    'validation_passed' in test_results[strategy] and
                    test_results[strategy]['validation_passed']):
                    strategy_success_rates[strategy] += 1
        
        report.append("\nOVERALL STRATEGY PERFORMANCE:")
        report.append("-" * 40)
        for strategy, successes in strategy_success_rates.items():
            success_rate = (successes / total_tests) * 100
            report.append(f"{strategy:<20}: {successes}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Detailed test results
        report.append("\nDETAILED TEST RESULTS:")
        report.append("-" * 40)
        
        for test_name, test_results in results.items():
            report.append(f"\n{test_name.upper()}:")
            for strategy in self.strategies:
                if strategy in test_results and 'error' not in test_results[strategy]:
                    result = test_results[strategy]
                    validation = "PASS" if result['validation_passed'] else "FAIL"
                    report.append(f"  {strategy}: {validation}")
                else:
                    report.append(f"  {strategy}: ERROR")
        
        # Recommendations
        report.append("\nRECOMMENDations:")
        report.append("-" * 20)
        
        best_strategy = max(strategy_success_rates.items(), key=lambda x: x[1])
        report.append(f"• Best performing strategy: {best_strategy[0]} ({best_strategy[1]}/{total_tests} tests)")
        
        if strategy_success_rates['hybrid'] == max(strategy_success_rates.values()):
            report.append("• Hybrid strategy recommended for balanced accuracy and consistency")
        elif strategy_success_rates['delta_assignment'] > strategy_success_rates['dummy_value']:
            report.append("• Delta assignment strategy provides higher accuracy for zero baseline scenarios")
        else:
            report.append("• Dummy value strategy provides good mathematical consistency")
        
        return "\n".join(report)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate report"""
        print("Starting comprehensive zero baseline handling tests...")
        
        results = self.run_strategy_comparison()
        
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80)
        
        report = self.generate_comprehensive_report(results)
        print(report)
        
        return {
            'test_results': results,
            'report': report,
            'summary': {
                'total_test_cases': len(self.test_cases),
                'strategies_tested': len(self.strategies),
                'recommendation': 'hybrid'  # Based on design analysis
            }
        }


def main():
    """Main execution function"""
    print("Zero Baseline Handling Test Suite")
    print("="*50)
    
    # Run comprehensive tests
    test_suite = ZeroBaselineTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    try:
        import json
        output_file = 'utils/test_results_zero_baseline.json'
        
        # Convert DataFrames to dict for JSON serialization
        serializable_results = {}
        for test_name, test_results in results['test_results'].items():
            serializable_results[test_name] = {}
            for strategy, strategy_results in test_results.items():
                if 'result_dataframe' in strategy_results:
                    # Convert DataFrame to dict
                    strategy_results_copy = strategy_results.copy()
                    strategy_results_copy['result_dataframe'] = strategy_results['result_dataframe'].to_dict()
                    serializable_results[test_name][strategy] = strategy_results_copy
                else:
                    serializable_results[test_name][strategy] = strategy_results
        
        results['test_results'] = serializable_results
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed test results saved to: {output_file}")
        
    except Exception as e:
        print(f"Warning: Could not save results to file: {e}")
    
    print("\nTest suite completed!")


if __name__ == "__main__":
    main()