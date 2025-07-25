#!/usr/bin/env python3
"""
Comprehensive test suite for the refactored bridge calculator architecture.
Tests all three bridge types and the orchestrator.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.bridge_types import (
    BridgeType, ContributionUnit, BridgeConfiguration, MetricFormula
)
from src.config.bridge_mappings import (
    get_bridge_configuration, get_metrics_by_bridge_type,
    get_metric_formula, is_calculated_metric
)
from src.core.bridges import (
    MixBridgeCalculator, MixRateBridgeCalculator, MixRateInfinityCalculator
)
from src.core.orchestrator import BridgeOrchestrator


class TestBridgeTypes(unittest.TestCase):
    """Test the bridge type definitions and configurations."""
    
    def test_bridge_configuration_validation(self):
        """Test that bridge configurations validate correctly."""
        # Valid Mix Bridge config
        config = BridgeConfiguration(
            bridge_type=BridgeType.MIX_BRIDGE,
            contribution_unit=ContributionUnit.CURRENCY
        )
        self.assertEqual(config.bridge_type, BridgeType.MIX_BRIDGE)
        
        # Invalid MixRate config (missing mix_determinant)
        with self.assertRaises(ValueError):
            BridgeConfiguration(
                bridge_type=BridgeType.MIXRATE_BRIDGE,
                contribution_unit=ContributionUnit.CURRENCY
                # Missing mix_determinant
            )
        
        # Invalid MixRate Infinity config (missing inverse_metric)
        with self.assertRaises(ValueError):
            BridgeConfiguration(
                bridge_type=BridgeType.MIXRATE_INFINITY,
                mix_determinant="Spend",
                contribution_unit=ContributionUnit.BASIS_POINTS
                # Missing inverse_metric
            )
    
    def test_metric_formula(self):
        """Test metric formula calculations."""
        formula = MetricFormula(
            numerator="Sales",
            denominator="Spend",
            is_percentage=False
        )
        
        # Normal calculation
        result = formula.calculate(1000, 200)
        self.assertEqual(result, 5.0)
        
        # Zero denominator
        result = formula.calculate(1000, 0)
        self.assertEqual(result, 0.0)
        
        # Percentage calculation
        formula_pct = MetricFormula(
            numerator="Clicks",
            denominator="Impressions",
            is_percentage=True
        )
        result = formula_pct.calculate(100, 10000)
        self.assertEqual(result, 1.0)  # 1%


class TestBridgeMappings(unittest.TestCase):
    """Test the bridge mapping configurations."""
    
    def test_get_bridge_configuration(self):
        """Test retrieving bridge configurations."""
        # Test Mix Bridge metric
        config = get_bridge_configuration("Spend")
        self.assertEqual(config.bridge_type, BridgeType.MIX_BRIDGE)
        self.assertEqual(config.contribution_unit, ContributionUnit.CURRENCY)
        
        # Test MixRate Bridge metric
        config = get_bridge_configuration("ROAS")
        self.assertEqual(config.bridge_type, BridgeType.MIXRATE_BRIDGE)
        self.assertEqual(config.mix_determinant, "Spend")
        
        # Test MixRate Infinity metric
        config = get_bridge_configuration("ACoS")
        self.assertEqual(config.bridge_type, BridgeType.MIXRATE_INFINITY)
        self.assertEqual(config.inverse_metric, "ROAS")
        
        # Test invalid metric
        with self.assertRaises(KeyError):
            get_bridge_configuration("InvalidMetric")
    
    def test_get_metrics_by_bridge_type(self):
        """Test grouping metrics by bridge type."""
        mix_metrics = get_metrics_by_bridge_type(BridgeType.MIX_BRIDGE)
        self.assertIn("Spend", mix_metrics)
        self.assertIn("Impressions", mix_metrics)
        
        mixrate_metrics = get_metrics_by_bridge_type(BridgeType.MIXRATE_BRIDGE)
        self.assertIn("ROAS", mixrate_metrics)
        self.assertIn("CTR", mixrate_metrics)
        
        infinity_metrics = get_metrics_by_bridge_type(BridgeType.MIXRATE_INFINITY)
        self.assertIn("ACoS", infinity_metrics)
    
    def test_metric_formulas(self):
        """Test metric formula retrieval."""
        # Test calculated metric
        formula = get_metric_formula("ROAS")
        self.assertIsNotNone(formula)
        self.assertEqual(formula.numerator, "Total Ad Sales")
        self.assertEqual(formula.denominator, "Spend")
        
        # Test base metric (no formula)
        formula = get_metric_formula("Spend")
        self.assertIsNone(formula)
        
        # Test is_calculated_metric
        self.assertTrue(is_calculated_metric("ROAS"))
        self.assertFalse(is_calculated_metric("Spend"))


class TestBridgeCalculators(unittest.TestCase):
    """Test individual bridge calculator implementations."""
    
    def setUp(self):
        """Create test data for calculators."""
        self.campaign_data = pd.DataFrame({
            'Campaign': ['A', 'B', 'C'],
            'Spend - January 2025': [1000, 2000, 1500],
            'Spend - February 2025': [1200, 1800, 2000],
            'Total Ad Sales - January 2025': [5000, 8000, 4500],
            'Total Ad Sales - February 2025': [6000, 7500, 6000],
            'Clicks - January 2025': [100, 200, 150],
            'Clicks - February 2025': [120, 180, 200],
            'Impressions - January 2025': [10000, 15000, 12000],
            'Impressions - February 2025': [12000, 14000, 16000],
        })
        
        # Calculate rate metrics
        for period in ['January 2025', 'February 2025']:
            self.campaign_data[f'ROAS - {period}'] = (
                self.campaign_data[f'Total Ad Sales - {period}'] / 
                self.campaign_data[f'Spend - {period}']
            )
            self.campaign_data[f'CTR - {period}'] = (
                self.campaign_data[f'Clicks - {period}'] / 
                self.campaign_data[f'Impressions - {period}'] * 100
            )
            self.campaign_data[f'ACoS - {period}'] = (
                self.campaign_data[f'Spend - {period}'] / 
                self.campaign_data[f'Total Ad Sales - {period}'] * 100
            )
        
        # Create total row
        self.total_row = pd.DataFrame([{
            'Campaign': 'Total',
            'Spend - January 2025': self.campaign_data['Spend - January 2025'].sum(),
            'Spend - February 2025': self.campaign_data['Spend - February 2025'].sum(),
            'Total Ad Sales - January 2025': self.campaign_data['Total Ad Sales - January 2025'].sum(),
            'Total Ad Sales - February 2025': self.campaign_data['Total Ad Sales - February 2025'].sum(),
            'Clicks - January 2025': self.campaign_data['Clicks - January 2025'].sum(),
            'Clicks - February 2025': self.campaign_data['Clicks - February 2025'].sum(),
            'Impressions - January 2025': self.campaign_data['Impressions - January 2025'].sum(),
            'Impressions - February 2025': self.campaign_data['Impressions - February 2025'].sum(),
        }])
        
        # Calculate total rate metrics
        for period in ['January 2025', 'February 2025']:
            self.total_row[f'ROAS - {period}'] = (
                self.total_row[f'Total Ad Sales - {period}'] / 
                self.total_row[f'Spend - {period}']
            )
            self.total_row[f'CTR - {period}'] = (
                self.total_row[f'Clicks - {period}'] / 
                self.total_row[f'Impressions - {period}'] * 100
            )
            self.total_row[f'ACoS - {period}'] = (
                self.total_row[f'Spend - {period}'] / 
                self.total_row[f'Total Ad Sales - {period}'] * 100
            )
    
    def test_mix_bridge_calculator(self):
        """Test Mix Bridge calculator."""
        config = BridgeConfiguration(
            bridge_type=BridgeType.MIX_BRIDGE,
            contribution_unit=ContributionUnit.CURRENCY
        )
        calculator = MixBridgeCalculator(config)
        
        # Calculate contributions
        contributions = calculator.calculate_contributions(
            self.campaign_data, self.total_row, "Spend"
        )
        
        # Verify results
        self.assertEqual(len(contributions), 3)
        
        # Check mathematical consistency
        total_change = (
            self.total_row['Spend - February 2025'].iloc[0] - 
            self.total_row['Spend - January 2025'].iloc[0]
        )
        self.assertAlmostEqual(contributions.sum(), total_change, places=2)
        
        # Test formatting
        formatted = calculator.format_contributions(contributions)
        self.assertTrue(all('$' in f or '+' in f or '-' in f for f in formatted))
    
    def test_mixrate_bridge_calculator(self):
        """Test MixRate Bridge calculator."""
        config = BridgeConfiguration(
            bridge_type=BridgeType.MIXRATE_BRIDGE,
            mix_determinant="Impressions",
            contribution_unit=ContributionUnit.BASIS_POINTS,
            requires_percentage_conversion=True
        )
        calculator = MixRateBridgeCalculator(config)
        
        # Calculate CTR contributions
        contributions = calculator.calculate_contributions(
            self.campaign_data, self.total_row, "CTR"
        )
        
        # Verify results
        self.assertEqual(len(contributions), 3)
        
        # Test formatting (should be in basis points)
        formatted = calculator.format_contributions(contributions)
        self.assertTrue(all('bps' in f for f in formatted))
    
    def test_mixrate_infinity_calculator(self):
        """Test MixRate Infinity calculator."""
        config = BridgeConfiguration(
            bridge_type=BridgeType.MIXRATE_INFINITY,
            mix_determinant="Spend",
            contribution_unit=ContributionUnit.BASIS_POINTS,
            inverse_metric="ROAS",
            requires_percentage_conversion=True
        )
        calculator = MixRateInfinityCalculator(config)
        
        # Calculate ACoS contributions
        contributions = calculator.calculate_contributions(
            self.campaign_data, self.total_row, "ACoS"
        )
        
        # Verify results
        self.assertEqual(len(contributions), 3)
        
        # Test that contributions are in basis points
        formatted = calculator.format_contributions(contributions)
        self.assertTrue(all('bps' in f for f in formatted))


class TestOrchestrator(unittest.TestCase):
    """Test the Bridge Orchestrator."""
    
    def setUp(self):
        """Set up test data."""
        # Use same test data as calculator tests
        self.campaign_data = pd.DataFrame({
            'Campaign': ['A', 'B', 'C'],
            'Spend - January 2025': [1000, 2000, 1500],
            'Spend - February 2025': [1200, 1800, 2000],
            'Total Ad Sales - January 2025': [5000, 8000, 4500],
            'Total Ad Sales - February 2025': [6000, 7500, 6000],
            'Clicks - January 2025': [100, 200, 150],
            'Clicks - February 2025': [120, 180, 200],
            'Impressions - January 2025': [10000, 15000, 12000],
            'Impressions - February 2025': [12000, 14000, 16000],
        })
        
        # Calculate rate metrics
        for period in ['January 2025', 'February 2025']:
            self.campaign_data[f'ROAS - {period}'] = (
                self.campaign_data[f'Total Ad Sales - {period}'] / 
                self.campaign_data[f'Spend - {period}']
            )
            self.campaign_data[f'CTR - {period}'] = (
                self.campaign_data[f'Clicks - {period}'] / 
                self.campaign_data[f'Impressions - {period}'] * 100
            )
            self.campaign_data[f'ACoS - {period}'] = (
                self.campaign_data[f'Spend - {period}'] / 
                self.campaign_data[f'Total Ad Sales - {period}'] * 100
            )
        
        # Create total row
        totals = {
            'Campaign': 'Total',
            'Spend - January 2025': self.campaign_data['Spend - January 2025'].sum(),
            'Spend - February 2025': self.campaign_data['Spend - February 2025'].sum(),
            'Total Ad Sales - January 2025': self.campaign_data['Total Ad Sales - January 2025'].sum(),
            'Total Ad Sales - February 2025': self.campaign_data['Total Ad Sales - February 2025'].sum(),
            'Clicks - January 2025': self.campaign_data['Clicks - January 2025'].sum(),
            'Clicks - February 2025': self.campaign_data['Clicks - February 2025'].sum(),
            'Impressions - January 2025': self.campaign_data['Impressions - January 2025'].sum(),
            'Impressions - February 2025': self.campaign_data['Impressions - February 2025'].sum(),
        }
        self.total_row = pd.DataFrame([totals])
        
        # Calculate total rate metrics
        for period in ['January 2025', 'February 2025']:
            self.total_row[f'ROAS - {period}'] = (
                self.total_row[f'Total Ad Sales - {period}'].iloc[0] / 
                self.total_row[f'Spend - {period}'].iloc[0]
            )
            self.total_row[f'CTR - {period}'] = (
                self.total_row[f'Clicks - {period}'].iloc[0] / 
                self.total_row[f'Impressions - {period}'].iloc[0] * 100
            )
            self.total_row[f'ACoS - {period}'] = (
                self.total_row[f'Spend - {period}'].iloc[0] / 
                self.total_row[f'Total Ad Sales - {period}'].iloc[0] * 100
            )
        
        self.orchestrator = BridgeOrchestrator()
    
    def test_calculate_single_metric(self):
        """Test calculating a single metric."""
        # Test Mix Bridge metric
        results = self.orchestrator.calculate_metric(
            self.campaign_data, self.total_row, "Spend"
        )
        
        self.assertIn("contributions", results)
        self.assertIn("formatted_contributions", results)
        self.assertIn("metadata", results)
        
        # Verify contributions
        contributions = results["contributions"]
        self.assertEqual(len(contributions), 3)
        
        # Check metadata
        metadata = results["metadata"]
        self.assertEqual(metadata["metric"], "Spend")
        self.assertEqual(metadata["bridge_type"], "MIX_BRIDGE")
    
    def test_calculate_all_metrics(self):
        """Test batch processing of multiple metrics."""
        metrics = ["Spend", "ROAS", "CTR", "ACoS"]
        results = self.orchestrator.calculate_all_metrics(
            self.campaign_data, self.total_row, metrics
        )
        
        # Check structure
        self.assertIn("contributions", results)
        self.assertIn("metadata", results)
        self.assertIn("summary", results)
        
        # Verify all metrics calculated
        for metric in metrics:
            self.assertIn(metric, results["contributions"])
            self.assertIn(metric, results["metadata"])
        
        # Check summary
        summary = results["summary"]
        self.assertEqual(summary["total_metrics"], 4)
        self.assertEqual(summary["successful_calculations"], 4)
    
    def test_apply_to_dataframe(self):
        """Test applying calculations to output dataframe."""
        # Create output dataframe structure
        output_df = self.campaign_data.copy()
        for metric in ["Spend", "ROAS", "ACoS"]:
            output_df[f"{metric} - Contribution"] = 0.0
        
        # Apply calculations
        updated_df = self.orchestrator.apply_to_dataframe(
            output_df, self.total_row, ["Spend", "ROAS", "ACoS"]
        )
        
        # Verify contributions were updated
        self.assertFalse((updated_df["Spend - Contribution"] == 0).all())
        self.assertFalse((updated_df["ROAS - Contribution"] == 0).all())
        self.assertFalse((updated_df["ACoS - Contribution"] == 0).all())
    
    def test_validation(self):
        """Test contribution validation."""
        # Apply calculations
        output_df = self.campaign_data.copy()
        for metric in ["Spend", "ROAS"]:
            output_df[f"{metric} - Contribution"] = 0.0
        
        output_df = self.orchestrator.apply_to_dataframe(
            output_df, self.total_row, ["Spend", "ROAS"]
        )
        
        # Add total contributions
        for metric in ["Spend", "ROAS"]:
            self.total_row[f"{metric} - Contribution"] = output_df[f"{metric} - Contribution"].sum()
        
        # Validate
        validation = self.orchestrator.validate_all_contributions(
            output_df, self.total_row, tolerance=0.01
        )
        
        # Check validation passed for calculated metrics
        self.assertTrue(validation.get("Spend", False))
        self.assertTrue(validation.get("ROAS", False))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_zero_baseline_handling(self):
        """Test handling of zero baseline values."""
        # Create data with zero baseline
        campaign_data = pd.DataFrame({
            'Campaign': ['A', 'B'],
            'Spend - January 2025': [0, 1000],  # Campaign A has zero baseline
            'Spend - February 2025': [500, 1200],
        })
        
        total_row = pd.DataFrame([{
            'Campaign': 'Total',
            'Spend - January 2025': 1000,
            'Spend - February 2025': 1700,
        }])
        
        config = get_bridge_configuration("Spend")
        calculator = MixBridgeCalculator(config)
        
        # Should not raise error
        contributions = calculator.calculate_contributions(
            campaign_data, total_row, "Spend"
        )
        
        # Campaign A should have contribution despite zero baseline
        self.assertNotEqual(contributions[0], 0)
    
    def test_missing_columns(self):
        """Test handling of missing columns."""
        campaign_data = pd.DataFrame({
            'Campaign': ['A', 'B'],
            'Spend - January 2025': [1000, 2000],
            # Missing February column
        })
        
        total_row = pd.DataFrame([{
            'Campaign': 'Total',
            'Spend - January 2025': 3000,
        }])
        
        orchestrator = BridgeOrchestrator()
        
        # Should handle error gracefully
        results = orchestrator.calculate_metric(
            campaign_data, total_row, "Spend"
        )
        
        # Should have error in metadata
        self.assertIn("error", results["metadata"])
    
    def test_infinity_error_prevention(self):
        """Test that infinity errors are prevented in ACoS calculation."""
        # Create data where sales go to zero (would cause infinity in ACoS)
        campaign_data = pd.DataFrame({
            'Campaign': ['A'],
            'Spend - January 2025': [1000],
            'Spend - February 2025': [1200],
            'Total Ad Sales - January 2025': [5000],
            'Total Ad Sales - February 2025': [0],  # Would cause infinity
        })
        
        # Calculate ACoS values
        campaign_data['ACoS - January 2025'] = 20.0  # 1000/5000 * 100
        campaign_data['ACoS - February 2025'] = float('inf')  # Would be infinity
        
        total_row = pd.DataFrame([{
            'Campaign': 'Total',
            'Spend - January 2025': 1000,
            'Spend - February 2025': 1200,
            'Total Ad Sales - January 2025': 5000,
            'Total Ad Sales - February 2025': 0,
            'ACoS - January 2025': 20.0,
            'ACoS - February 2025': float('inf'),
        }])
        
        config = get_bridge_configuration("ACoS")
        calculator = MixRateInfinityCalculator(config)
        
        # Should handle infinity gracefully through inverse method
        contributions = calculator.calculate_contributions(
            campaign_data, total_row, "ACoS"
        )
        
        # Should not have infinity or NaN
        self.assertFalse(np.any(np.isinf(contributions)))
        self.assertFalse(np.any(np.isnan(contributions)))


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    test_classes = [
        TestBridgeTypes,
        TestBridgeMappings,
        TestBridgeCalculators,
        TestOrchestrator,
        TestEdgeCases
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
                print(f"- {test}: {error_msg}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                error_line = traceback.split('\n')[-2]
                print(f"- {test}: {error_line}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)