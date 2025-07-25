"""Tests for the MixBridge validator module."""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.data.validator import MixBridgeValidator
    from src.common.exceptions import ValidationError
except ImportError:
    # Handle relative imports when run as module or legacy structure
    try:
        from src.mixbridge_validator import MixBridgeValidator
        from src.exceptions import ValidationError
    except ImportError:
        from mixbridge_validator import MixBridgeValidator
        from exceptions import ValidationError


class TestMixBridgeValidator(unittest.TestCase):
    """Test cases for MixBridgeValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = MixBridgeValidator()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Campaign Name': ['Campaign A', 'Campaign A', 'Campaign B'],
            'spend': [100.0, 150.0, 200.0],
            'clicks': [50, 75, 100],
            'impressions': [1000, 1500, 2000],
            'CTR': [5.0, 5.0, 5.0]
        })
        
        self.bridge_data = pd.DataFrame({
            'Campaign Name': ['Campaign A', 'Campaign B'],
            'baseline_spend': [100.0, 200.0],
            'actual_spend': [150.0, 200.0],
            'baseline_clicks': [50, 100],
            'actual_clicks': [75, 100]
        })
    
    def test_validate_required_columns_success(self):
        """Test validation passes with all required columns."""
        required_columns = ['Date', 'Campaign Name', 'spend']
        # Should not raise exception
        self.validator.validate_required_columns(self.sample_data, required_columns)
    
    def test_validate_required_columns_missing(self):
        """Test validation fails with missing columns."""
        required_columns = ['Date', 'Campaign Name', 'spend', 'missing_column']
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_required_columns(self.sample_data, required_columns)
        self.assertIn("missing_column", str(context.exception))
    
    def test_validate_numeric_columns(self):
        """Test numeric column validation."""
        # Create data with non-numeric values
        bad_data = self.sample_data.copy()
        bad_data.loc[0, 'spend'] = 'not_a_number'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_numeric_columns(bad_data, ['spend'])
        self.assertIn("spend", str(context.exception))
    
    def test_validate_date_column(self):
        """Test date column validation."""
        # Should not raise exception with valid dates
        self.validator.validate_date_column(self.sample_data, 'Date')
        
        # Test with invalid dates
        bad_data = self.sample_data.copy()
        bad_data.loc[0, 'Date'] = 'invalid_date'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_date_column(bad_data, 'Date')
        self.assertIn("Date", str(context.exception))
    
    def test_validate_metric_calculations(self):
        """Test metric calculation validation."""
        # CTR should equal clicks/impressions * 100
        valid_data = self.sample_data.copy()
        # Should not raise exception
        self.validator.validate_metric_calculations(valid_data)
        
        # Create data with incorrect CTR
        invalid_data = self.sample_data.copy()
        invalid_data.loc[0, 'CTR'] = 10.0  # Should be 5.0
        
        with self.assertRaises(ValidationError):
            self.validator.validate_metric_calculations(invalid_data)
    
    def test_validate_bridge_totals(self):
        """Test bridge total validation."""
        # Create bridge data where totals match
        bridge_data = pd.DataFrame({
            'metric': ['spend', 'clicks'],
            'baseline_total': [300.0, 150],
            'actual_total': [350.0, 175],
            'incremental_total': [50.0, 25]
        })
        
        # Should not raise exception
        self.validator.validate_bridge_totals(bridge_data)
        
        # Create data with incorrect totals
        bad_bridge_data = bridge_data.copy()
        bad_bridge_data.loc[0, 'incremental_total'] = 100.0  # Should be 50.0
        
        with self.assertRaises(ValidationError):
            self.validator.validate_bridge_totals(bad_bridge_data)
    
    def test_validate_percentage_bounds(self):
        """Test percentage bounds validation."""
        # Create data with valid percentages
        data = pd.DataFrame({
            'CTR': [5.0, 10.0, 0.0],
            'CVR': [2.5, 5.0, 0.0]
        })
        
        # Should not raise exception
        self.validator.validate_percentage_bounds(data, ['CTR', 'CVR'])
        
        # Create data with invalid percentages
        bad_data = data.copy()
        bad_data.loc[0, 'CTR'] = 150.0  # Over 100%
        
        with self.assertRaises(ValidationError):
            self.validator.validate_percentage_bounds(bad_data, ['CTR', 'CVR'])
    
    def test_validate_non_negative_values(self):
        """Test non-negative value validation."""
        # Should not raise exception with positive values
        self.validator.validate_non_negative_values(self.sample_data, ['spend', 'clicks'])
        
        # Create data with negative values
        bad_data = self.sample_data.copy()
        bad_data.loc[0, 'spend'] = -100.0
        
        with self.assertRaises(ValidationError):
            self.validator.validate_non_negative_values(bad_data, ['spend'])
    
    def test_detect_outliers(self):
        """Test outlier detection."""
        # Create data with outliers
        data = pd.DataFrame({
            'spend': [100, 100, 100, 100, 1000000],  # Last value is outlier
            'clicks': [50, 50, 50, 50, 50]
        })
        
        outliers = self.validator.detect_outliers(data, 'spend', threshold=3.0)
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers.iloc[0], 1000000)
    
    def test_validate_campaign_consistency(self):
        """Test campaign consistency validation."""
        # Create data with consistent campaigns
        consistent_data = pd.DataFrame({
            'Campaign Name': ['Campaign A', 'Campaign A', 'Campaign B', 'Campaign B'],
            'Date': ['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02']
        })
        
        # Should not raise exception
        self.validator.validate_campaign_consistency(
            consistent_data, 
            consistent_data[['Campaign Name']].drop_duplicates()
        )
        
        # Test with inconsistent campaigns
        bridge_campaigns = pd.DataFrame({
            'Campaign Name': ['Campaign A', 'Campaign C']  # Campaign C not in raw data
        })
        
        with self.assertRaises(ValidationError):
            self.validator.validate_campaign_consistency(consistent_data, bridge_campaigns)


if __name__ == '__main__':
    unittest.main()