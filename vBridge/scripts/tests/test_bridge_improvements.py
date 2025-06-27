"""
Test Suite for Improved Bridge Calculations
Tests edge cases, numerical stability, and mathematical accuracy
"""

import pandas as pd
import numpy as np
import unittest
import sys
import os

# Add the parent scripts directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bridge_calculations_improved import (
    BridgeCalculationUtils,
    ImprovedMixBridgeCalculator,
    ImprovedMixRateCalculator,
    ImprovedInfinityHandler,
    BridgeValidation
)


class TestBridgeCalculationUtils(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.utils = BridgeCalculationUtils()
    
    def test_safe_divide_scalar(self):
        """Test safe division with scalar values"""
        # Normal division
        self.assertEqual(self.utils.safe_divide(10, 2), 5)
        
        # Zero division
        self.assertEqual(self.utils.safe_divide(10, 0), 0)
        
        # Near-zero division
        self.assertEqual(self.utils.safe_divide(10, 1e-11), 0)
        
        # Custom default
        self.assertEqual(self.utils.safe_divide(10, 0, default=-1), -1)
    
    def test_safe_divide_series(self):
        """Test safe division with pandas Series"""
        numerator = pd.Series([10, 20, 30, 40])
        denominator = pd.Series([2, 0, 1e-11, 5])
        
        result = self.utils.safe_divide(numerator, denominator)
        
        self.assertEqual(result[0], 5)  # 10/2
        self.assertEqual(result[1], 0)  # 20/0
        self.assertEqual(result[2], 0)  # 30/near-zero
        self.assertEqual(result[3], 8)  # 40/5
    
    def test_to_basis_points(self):
        """Test basis points conversion"""
        # Raw value to BPS
        self.assertEqual(self.utils.to_basis_points(0.01), 100)
        self.assertEqual(self.utils.to_basis_points(0.0001), 1)
        
        # Percentage to BPS
        self.assertEqual(self.utils.to_basis_points(0.01, is_already_percentage=True), 1)
        self.assertEqual(self.utils.to_basis_points(0.10, is_already_percentage=True), 10)
        
        # Series conversion
        series = pd.Series([0.01, 0.02, 0.03])
        result = self.utils.to_basis_points(series)
        expected = pd.Series([100.0, 200.0, 300.0])
        pd.testing.assert_series_equal(result, expected)


class TestImprovedMixBridge(unittest.TestCase):
    """Test improved Mix Bridge calculations"""
    
    def setUp(self):
        self.calculator = ImprovedMixBridgeCalculator()
    
    def test_basic_mix_bridge(self):
        """Test basic mix bridge calculation"""
        p1_values = pd.Series({
            'Campaign A': 1000,
            'Campaign B': 2000,
            'Campaign C': 500
        })
        p2_values = pd.Series({
            'Campaign A': 1200,
            'Campaign B': 1800,
            'Campaign C': 600
        })
        
        p1_total = p1_values.sum()  # 3500
        p2_total = p2_values.sum()  # 3600
        
        result = self.calculator.calculate_mix_bridge(
            p1_values, p2_values, p1_total, p2_total, "Test Metric"
        )
        
        # Check that contributions sum to total change
        total_change_bps = (p2_total - p1_total) / p1_total * 10000
        contribution_sum = result['Total Contribution (BPS)'].sum()
        
        self.assertAlmostEqual(contribution_sum, total_change_bps, places=1)
        
        # Verify volume and mix effects sum to total
        for idx in result.index:
            self.assertAlmostEqual(
                result.loc[idx, 'Volume Effect (BPS)'] + result.loc[idx, 'Mix Effect (BPS)'],
                result.loc[idx, 'Total Contribution (BPS)'],
                places=6
            )
    
    def test_new_campaign_handling(self):
        """Test handling of new campaigns in P2"""
        p1_values = pd.Series({
            'Campaign A': 1000,
            'Campaign B': 2000
        })
        p2_values = pd.Series({
            'Campaign A': 1200,
            'Campaign B': 1800,
            'Campaign C': 300  # New campaign
        })
        
        result = self.calculator.calculate_mix_bridge(
            p1_values, p2_values, 
            p1_values.sum(), p2_values.sum(),
            "Test with New Campaign"
        )
        
        # Campaign C should have zero P1 share but positive P2 share
        self.assertEqual(result.loc['Campaign C', 'P1 Share'], 0)
        self.assertGreater(result.loc['Campaign C', 'P2 Share'], 0)
        
        # Campaign C should have only mix effect (no volume effect)
        self.assertEqual(result.loc['Campaign C', 'Volume Effect (BPS)'], 0)
        self.assertGreater(result.loc['Campaign C', 'Mix Effect (BPS)'], 0)
    
    def test_discontinued_campaign_handling(self):
        """Test handling of discontinued campaigns"""
        p1_values = pd.Series({
            'Campaign A': 1000,
            'Campaign B': 2000,
            'Campaign C': 500  # Will be discontinued
        })
        p2_values = pd.Series({
            'Campaign A': 1200,
            'Campaign B': 1800
        })
        
        result = self.calculator.calculate_mix_bridge(
            p1_values, p2_values,
            p1_values.sum(), p2_values.sum(),
            "Test with Discontinued Campaign"
        )
        
        # Campaign C should have negative contribution
        self.assertLess(result.loc['Campaign C', 'Total Contribution (BPS)'], 0)
        
        # Campaign C should have P1 share but zero P2 share
        self.assertGreater(result.loc['Campaign C', 'P1 Share'], 0)
        self.assertEqual(result.loc['Campaign C', 'P2 Share'], 0)
    
    def test_zero_total_handling(self):
        """Test handling when P1 total is zero"""
        p1_values = pd.Series({
            'Campaign A': 0,
            'Campaign B': 0
        })
        p2_values = pd.Series({
            'Campaign A': 100,
            'Campaign B': 200
        })
        
        # Should not raise an error
        result = self.calculator.calculate_mix_bridge(
            p1_values, p2_values, 0, 300, "Zero Total Test"
        )
        
        # All contributions should be zero (can't calculate relative change from zero)
        self.assertTrue((result['Total Contribution (BPS)'] == 0).all())


class TestImprovedMixRate(unittest.TestCase):
    """Test improved Mix/Rate calculations"""
    
    def setUp(self):
        self.calculator = ImprovedMixRateCalculator()
    
    def test_ctr_mix_rate(self):
        """Test CTR mix/rate calculation"""
        # Campaign data
        campaigns = ['Campaign A', 'Campaign B', 'Campaign C']
        
        # P1 data
        p1_clicks = pd.Series([100, 200, 50], index=campaigns)
        p1_impressions = pd.Series([10000, 15000, 5000], index=campaigns)
        p1_ctr = p1_clicks / p1_impressions
        
        # P2 data (Campaign A improves CTR, B decreases, C stays same)
        p2_clicks = pd.Series([150, 180, 50], index=campaigns)
        p2_impressions = pd.Series([12000, 16000, 5000], index=campaigns)
        p2_ctr = p2_clicks / p2_impressions
        
        result = self.calculator.calculate_mix_rate_contribution(
            p1_kpi_values=p1_ctr,
            p2_kpi_values=p2_ctr,
            p1_mix_driver=p1_impressions,
            p2_mix_driver=p2_impressions,
            kpi_name="CTR",
            is_percentage_metric=True
        )
        
        # Check that mix + rate = total for all campaigns
        for campaign in campaigns:
            self.assertAlmostEqual(
                result.loc[campaign, 'Mix Impact'] + result.loc[campaign, 'Rate Impact'],
                result.loc[campaign, 'Total Contribution'],
                places=6
            )
    
    def test_zero_mix_driver_handling(self):
        """Test handling of zero mix driver values"""
        campaigns = ['Campaign A', 'Campaign B', 'Campaign C']
        
        # Campaign C has zero impressions in both periods
        p1_impressions = pd.Series([10000, 15000, 0], index=campaigns)
        p2_impressions = pd.Series([12000, 16000, 0], index=campaigns)
        
        # CTR values (Campaign C will be 0/0)
        p1_ctr = pd.Series([0.01, 0.02, 0], index=campaigns)
        p2_ctr = pd.Series([0.015, 0.018, 0], index=campaigns)
        
        result = self.calculator.calculate_mix_rate_contribution(
            p1_kpi_values=p1_ctr,
            p2_kpi_values=p2_ctr,
            p1_mix_driver=p1_impressions,
            p2_mix_driver=p2_impressions,
            kpi_name="CTR",
            is_percentage_metric=True
        )
        
        # Campaign C should be flagged as having zero driver
        self.assertTrue(result.loc['Campaign C', 'Has Zero Driver'])
        
        # Campaign C should have zero contributions
        self.assertEqual(result.loc['Campaign C', 'Mix Impact'], 0)
        self.assertEqual(result.loc['Campaign C', 'Rate Impact'], 0)
    
    def test_new_campaign_in_mix_rate(self):
        """Test new campaign handling in mix/rate"""
        # P1 data (only A and B)
        p1_spend = pd.Series({'Campaign A': 1000, 'Campaign B': 2000})
        p1_sales = pd.Series({'Campaign A': 5000, 'Campaign B': 8000})
        p1_roas = p1_sales / p1_spend
        
        # P2 data (includes new Campaign C)
        p2_spend = pd.Series({'Campaign A': 1200, 'Campaign B': 1800, 'Campaign C': 500})
        p2_sales = pd.Series({'Campaign A': 6000, 'Campaign B': 7500, 'Campaign C': 3000})
        p2_roas = p2_sales / p2_spend
        
        result = self.calculator.calculate_mix_rate_contribution(
            p1_kpi_values=p1_roas,
            p2_kpi_values=p2_roas,
            p1_mix_driver=p1_spend,
            p2_mix_driver=p2_spend,
            kpi_name="ROAS",
            is_percentage_metric=False
        )
        
        # Campaign C should be flagged as new
        self.assertTrue(result.loc['Campaign C', 'Is New Campaign'])
        
        # Campaign C should have P1 KPI = 0 and P1 Mix Share = 0
        self.assertEqual(result.loc['Campaign C', 'P1 KPI'], 0)
        self.assertEqual(result.loc['Campaign C', 'P1 Mix Share'], 0)


class TestInfinityHandling(unittest.TestCase):
    """Test infinity handling for ACoS/ROAS"""
    
    def setUp(self):
        self.handler = ImprovedInfinityHandler()
    
    def test_acos_infinity_handling(self):
        """Test ACoS infinity scenarios"""
        campaigns = ['Campaign A', 'Campaign B', 'Campaign C', 'Campaign D']
        
        # Original contributions (some will be infinity)
        contributions = pd.Series([100, np.inf, -np.inf, 50], index=campaigns)
        
        # Spend data
        p1_spend = pd.Series([1000, 500, 800, 1200], index=campaigns)
        p2_spend = pd.Series([1200, 600, 900, 1000], index=campaigns)
        
        # Sales data with edge cases
        p1_sales = pd.Series([5000, 2000, 0, 4000], index=campaigns)  # C has no P1 sales
        p2_sales = pd.Series([6000, 0, 1000, 0], index=campaigns)      # B,D have no P2 sales
        
        result = self.handler.handle_acos_roas_infinity(
            contributions=contributions,
            p1_spend=p1_spend,
            p2_spend=p2_spend,
            p1_sales=p1_sales,
            p2_sales=p2_sales,
            metric_type='ACoS'
        )
        
        # Check flags
        self.assertEqual(result.loc['Campaign B', 'Flag'], 'P2_Sales_Zero')
        self.assertEqual(result.loc['Campaign C', 'Flag'], 'P1_Sales_Zero')
        self.assertEqual(result.loc['Campaign D', 'Flag'], 'P2_Sales_Zero')
        
        # Check handled values
        self.assertEqual(result.loc['Campaign B', 'Handled Contribution'], 10000)
        self.assertEqual(result.loc['Campaign C', 'Handled Contribution'], -10000)
    
    def test_roas_infinity_handling(self):
        """Test ROAS infinity scenarios"""
        campaigns = ['Campaign A', 'Campaign B', 'Campaign C']
        
        contributions = pd.Series([100, np.inf, 200], index=campaigns)
        
        # Spend data with edge cases
        p1_spend = pd.Series([1000, 0, 800], index=campaigns)     # B has no P1 spend
        p2_spend = pd.Series([1200, 500, 0], index=campaigns)     # C has no P2 spend
        
        # Sales data
        p1_sales = pd.Series([5000, 2000, 4000], index=campaigns)
        p2_sales = pd.Series([6000, 3000, 5000], index=campaigns)
        
        result = self.handler.handle_acos_roas_infinity(
            contributions=contributions,
            p1_spend=p1_spend,
            p2_spend=p2_spend,
            p1_sales=p1_sales,
            p2_sales=p2_sales,
            metric_type='ROAS'
        )
        
        # Check flags
        self.assertEqual(result.loc['Campaign B', 'Flag'], 'P1_Spend_Zero_With_Sales')
        self.assertEqual(result.loc['Campaign C', 'Flag'], 'P2_Spend_Zero_With_Sales')
        
        # Check handled values
        self.assertEqual(result.loc['Campaign B', 'Handled Contribution'], -10000)
        self.assertEqual(result.loc['Campaign C', 'Handled Contribution'], 10000)


class TestBridgeValidation(unittest.TestCase):
    """Test validation functions"""
    
    def setUp(self):
        self.validator = BridgeValidation()
    
    def test_contribution_sum_validation(self):
        """Test contribution sum validation"""
        # Valid case
        contributions = pd.Series([100, 200, -50, 150])  # Sum = 400
        is_valid = self.validator.validate_contribution_sum(
            contributions=contributions,
            expected_total_change=400,
            metric_name="Test Metric"
        )
        self.assertTrue(is_valid)
        
        # Invalid case
        is_valid = self.validator.validate_contribution_sum(
            contributions=contributions,
            expected_total_change=500,  # Wrong expected value
            metric_name="Test Metric"
        )
        self.assertFalse(is_valid)
        
        # Zero expected change
        zero_contributions = pd.Series([50, -30, -20])  # Sum = 0
        is_valid = self.validator.validate_contribution_sum(
            contributions=zero_contributions,
            expected_total_change=0,
            metric_name="Zero Change"
        )
        self.assertTrue(is_valid)
    
    def test_mix_rate_decomposition_validation(self):
        """Test mix/rate decomposition validation"""
        # Valid case
        mix_impact = pd.Series([50, 30, -20])
        rate_impact = pd.Series([100, -50, 40])
        total_contribution = pd.Series([150, -20, 20])
        
        is_valid = self.validator.validate_mix_rate_decomposition(
            mix_impact=mix_impact,
            rate_impact=rate_impact,
            total_contribution=total_contribution,
            metric_name="Test KPI"
        )
        self.assertTrue(is_valid)
        
        # Invalid case (totals don't match)
        total_contribution_wrong = pd.Series([151, -20, 25])  # Wrong values
        
        is_valid = self.validator.validate_mix_rate_decomposition(
            mix_impact=mix_impact,
            rate_impact=rate_impact,
            total_contribution=total_contribution_wrong,
            metric_name="Test KPI"
        )
        self.assertFalse(is_valid)


class TestIntegration(unittest.TestCase):
    """Integration tests with realistic data"""
    
    def test_complete_bridge_analysis(self):
        """Test complete bridge analysis workflow"""
        # Create realistic campaign data
        np.random.seed(42)
        n_campaigns = 20
        campaign_names = [f'Campaign_{i}' for i in range(n_campaigns)]
        
        # P1 data
        p1_spend = pd.Series(np.random.uniform(100, 5000, n_campaigns), index=campaign_names)
        p1_sales = p1_spend * np.random.uniform(2, 8, n_campaigns)  # ROAS between 2-8
        p1_impressions = p1_spend * np.random.uniform(100, 1000, n_campaigns)
        p1_clicks = p1_impressions * np.random.uniform(0.001, 0.05, n_campaigns)
        
        # P2 data with some changes
        p2_spend = p1_spend * np.random.uniform(0.7, 1.3, n_campaigns)
        p2_sales = p2_spend * np.random.uniform(1.5, 9, n_campaigns)
        p2_impressions = p2_spend * np.random.uniform(80, 1200, n_campaigns)
        p2_clicks = p2_impressions * np.random.uniform(0.001, 0.06, n_campaigns)
        
        # Add some edge cases
        p1_sales.iloc[5] = 0  # Zero sales for campaign 5 in P1
        p2_spend.iloc[10] = 0  # Zero spend for campaign 10 in P2
        
        # Initialize calculators
        mix_bridge_calc = ImprovedMixBridgeCalculator()
        mix_rate_calc = ImprovedMixRateCalculator()
        infinity_handler = ImprovedInfinityHandler()
        validator = BridgeValidation()
        
        # 1. Calculate Mix Bridge for Spend
        spend_bridge = mix_bridge_calc.calculate_mix_bridge(
            p1_values=p1_spend,
            p2_values=p2_spend,
            p1_total=p1_spend.sum(),
            p2_total=p2_spend.sum(),
            metric_name="Spend"
        )
        
        # Validate spend bridge
        spend_change_bps = (p2_spend.sum() - p1_spend.sum()) / p1_spend.sum() * 10000
        is_valid = validator.validate_contribution_sum(
            contributions=spend_bridge['Total Contribution (BPS)'],
            expected_total_change=spend_change_bps,
            metric_name="Spend"
        )
        self.assertTrue(is_valid)
        
        # 2. Calculate CTR Mix/Rate
        p1_ctr = p1_clicks / p1_impressions
        p2_ctr = p2_clicks / p2_impressions
        
        ctr_mix_rate = mix_rate_calc.calculate_mix_rate_contribution(
            p1_kpi_values=p1_ctr,
            p2_kpi_values=p2_ctr,
            p1_mix_driver=p1_impressions,
            p2_mix_driver=p2_impressions,
            kpi_name="CTR",
            is_percentage_metric=True
        )
        
        # 3. Calculate ACoS with infinity handling
        p1_acos = p1_spend / p1_sales.replace(0, np.nan)
        p2_acos = p2_spend / p2_sales.replace(0, np.nan)
        
        # Create dummy contributions for testing
        acos_contributions = (p2_acos - p1_acos).fillna(0) * 10000
        
        acos_handled = infinity_handler.handle_acos_roas_infinity(
            contributions=acos_contributions,
            p1_spend=p1_spend,
            p2_spend=p2_spend,
            p1_sales=p1_sales,
            p2_sales=p2_sales,
            metric_type='ACoS'
        )
        
        # Check that all calculations completed without errors
        self.assertIsNotNone(spend_bridge)
        self.assertIsNotNone(ctr_mix_rate)
        self.assertIsNotNone(acos_handled)
        
        # Check that no NaN or infinity values remain
        self.assertFalse(spend_bridge['Total Contribution (BPS)'].isna().any())
        self.assertFalse(ctr_mix_rate['Total Contribution'].isna().any())
        self.assertFalse(acos_handled['Handled Contribution'].isna().any())
        self.assertFalse(np.isinf(acos_handled['Handled Contribution']).any())


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)