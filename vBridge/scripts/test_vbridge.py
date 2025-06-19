#!/usr/bin/env python3
"""
Test script for the modular vBridge implementation.

This script tests the modular structure and ensures all components work together correctly.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the scripts directory to the path so we can import vBridge
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vBridge import VBridge, ConfigManager, DataProcessor


def test_config_manager():
    """Test the ConfigManager class"""
    print("Testing ConfigManager...")
    config = ConfigManager()
    
    # Test basic functionality
    assert hasattr(config, 'CAMPAIGN_NAME_COL')
    assert hasattr(config, 'DATE_COL')
    assert hasattr(config, 'kpi_format')
    
    # Test KPI name mapping
    display_name = config.get_kpi_display_name('CTR')
    assert display_name == 'Clickthrough Rate'
    
    internal_name = config.get_kpi_internal_name('Clickthrough Rate')
    assert internal_name == 'CTR'
    
    print("✓ ConfigManager tests passed")


def test_data_processor():
    """Test the DataProcessor class"""
    print("Testing DataProcessor...")
    config = ConfigManager()
    processor = DataProcessor(config)
    
    # Create sample data for testing
    sample_data = {
        'CampaignName': ['Campaign A', 'Campaign B', 'Campaign A', 'Campaign B'],
        'DateKey': ['20250101', '20250101', '20250102', '20250102'],
        'Cost': [100, 200, 150, 250],
        'Clicks': [10, 20, 15, 25],
        'Impressions': [1000, 2000, 1500, 2500],
        'AttributedSales7day': [500, 1000, 750, 1250],
        'AttributedConversions7day': [5, 10, 7, 12],
        'AttributedSalesSameSKU7day': [400, 800, 600, 1000],
        'AttributedConversionsSameSKU7day': [4, 8, 6, 10]
    }
    
    # Create a temporary CSV file
    test_df = pd.DataFrame(sample_data)
    test_csv_path = 'test_data.csv'
    test_df.to_csv(test_csv_path, index=False)
    
    try:
        # Test data loading
        loaded_df = processor.load_and_preprocess_data(test_csv_path)
        assert loaded_df is not None
        assert len(loaded_df) == 4
        assert config.DATE_COL in loaded_df.columns
        
        # Test data aggregation
        start_date = pd.to_datetime('2025-01-01')
        end_date = pd.to_datetime('2025-01-02')
        aggregated = processor.aggregate_data_for_period(loaded_df, start_date, end_date)
        assert len(aggregated) == 2  # Two campaigns
        
        print("✓ DataProcessor tests passed")
        
    finally:
        # Clean up test file
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


def test_vbridge_initialization():
    """Test VBridge initialization"""
    print("Testing VBridge initialization...")
    
    vbridge = VBridge(output_dir='test_output')
    
    # Test that all components are initialized
    assert hasattr(vbridge, 'config')
    assert hasattr(vbridge, 'data_processor')
    assert hasattr(vbridge, 'step1')
    assert hasattr(vbridge, 'step2')
    assert hasattr(vbridge, 'step3')
    assert hasattr(vbridge, 'step4')
    assert hasattr(vbridge, 'summary_generator')
    
    # Test that output directory is created
    assert os.path.exists('test_output')
    
    print("✓ VBridge initialization tests passed")
    
    # Clean up test directory
    import shutil
    if os.path.exists('test_output'):
        shutil.rmtree('test_output')


def test_step_classes():
    """Test that all step classes can be instantiated"""
    print("Testing step class instantiation...")
    
    from vBridge import (Step1KPICalculation, Step2AbsoluteContributions, 
                        Step3MixRateContributions, Step4AcosRoasInfinityHandling,
                        SummaryReportGenerator)
    
    config = ConfigManager()
    output_dir = 'test_steps'
    
    try:
        # Test instantiation of all step classes
        step1 = Step1KPICalculation(config, output_dir)
        step2 = Step2AbsoluteContributions(config, output_dir)
        step3 = Step3MixRateContributions(config, output_dir)
        step4 = Step4AcosRoasInfinityHandling(config, output_dir)
        summary = SummaryReportGenerator(config, output_dir)
        
        # Test that they all inherit from AnalysisStep
        assert hasattr(step1, 'execute')
        assert hasattr(step2, 'execute')
        assert hasattr(step3, 'execute')
        assert hasattr(step4, 'execute')
        assert hasattr(summary, 'execute')
        
        print("✓ Step class instantiation tests passed")
        
    finally:
        # Clean up test directory
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("RUNNING VBRIDGE MODULAR TESTS")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_data_processor()
        test_vbridge_initialization()
        test_step_classes()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("The modular vBridge implementation is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_all_tests() 