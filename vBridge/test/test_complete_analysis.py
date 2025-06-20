#!/usr/bin/env python3
"""
Test script to validate the complete 4-step analysis implementation
This script tests the modular vBridge system implementation.
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Add the scripts directory to the path so we can import vBridge modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from vBridge import VBridge
    from config_manager import ConfigManager
    from data_processor import DataProcessor
    from analysis_steps import (
        Step1KPICalculation,
        Step2AbsoluteContributions,
        Step3MixRateContributions,
        Step4AcosRoasInfinityHandling,
        SummaryReportGenerator
    )
    print("✓ Successfully imported all modules from vBridge system")
except ImportError as e:
    print(f"✗ Failed to import from vBridge system: {e}")
    sys.exit(1)

def create_test_data():
    """
    Create synthetic test data that mimics the expected CSV structure
    """
    print("\n=== CREATING TEST DATA ===")
    
    # Create synthetic campaign data
    campaigns = ['Campaign_A', 'Campaign_B', 'Campaign_C', 'Campaign_D', 'Campaign_E']
    dates = pd.date_range('2025-01-01', '2025-02-28', freq='D')
    
    data = []
    for date in dates:
        for i, campaign in enumerate(campaigns):
            # Create realistic but varied data for each campaign
            base_multiplier = (i + 1) * 0.5
            date_factor = 1.1 if date.month == 2 else 1.0  # P2 has 10% more activity
            
            row = {
                'CampaignID': f'ID_{i+1}',
                'CampaignName': campaign,
                'DateKey': date.strftime('%Y%m%d'),
                'Cost': np.random.uniform(100, 1000) * base_multiplier * date_factor,
                'Clicks': np.random.randint(10, 100) * base_multiplier * date_factor,
                'Impressions': np.random.randint(100, 1000) * base_multiplier * date_factor,
                'Sales': np.random.uniform(200, 2000) * base_multiplier * date_factor,
                'AttributedConversions7day': np.random.randint(1, 20) * base_multiplier * date_factor,
                'AttributedSalesSameSKU7day': np.random.uniform(100, 1500) * base_multiplier * date_factor,
                'AttributedConversionsSameSKU7day': np.random.randint(1, 15) * base_multiplier * date_factor,
            }
            data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save test data
    test_file = 'test_campaign_data.csv'
    df.to_csv(test_file, index=False)
    print(f"✓ Created test data with {len(df)} rows and saved to {test_file}")
    
    return test_file

def test_step1_kpi_calculation():
    """
    Test Step 1: Verify all 14 KPIs are calculated
    """
    print("\n=== TESTING STEP 1: KPI CALCULATION ===")
    
    expected_kpis = [
        'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
        'Impressions', 'Clicks', 'CTR', 'CPC', 'Same SKU Ad Sales',
        'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders'
    ]
    
    # Load test data using modular system
    test_file = create_test_data()
    
    # Initialize modular components
    config = ConfigManager()
    processor = DataProcessor(config)
    step1 = Step1KPICalculation(config, 'test_output')
    
    # Load and preprocess data
    full_df = processor.load_and_preprocess_data(test_file)
    
    if full_df is None:
        print("✗ Failed to load test data")
        return False
    
    # Test KPI calculation
    p1_start = pd.to_datetime('2025-01-01')
    p1_end = pd.to_datetime('2025-01-31')
    p2_start = pd.to_datetime('2025-02-01')
    p2_end = pd.to_datetime('2025-02-28')
    
    try:
        p1_kpis, p2_kpis, p1_totals, p2_totals = step1.execute(
            full_df, p1_start, p1_end, p2_start, p2_end
        )
    except Exception as e:
        print(f"✗ Step 1 execution failed: {e}")
        return False
    
    if p1_kpis is None:
        print("✗ Step 1 failed to return KPIs")
        return False
    
    # Check that all expected KPIs are present
    missing_kpis = []
    for kpi in expected_kpis:
        if kpi not in p1_kpis.columns:
            missing_kpis.append(kpi)
    
    if missing_kpis:
        print(f"✗ Missing KPIs: {missing_kpis}")
        return False
    
    print(f"✓ All {len(expected_kpis)} KPIs calculated successfully")
    print(f"✓ P1 KPIs shape: {p1_kpis.shape}")
    print(f"✓ P2 KPIs shape: {p2_kpis.shape}")
    
    # Clean up
    os.remove(test_file)
    
    return True

def test_step2_absolute_contributions():
    """
    Test Step 2: Verify all absolute metrics are processed
    """
    print("\n=== TESTING STEP 2: ABSOLUTE METRIC CONTRIBUTIONS ===")
    
    expected_absolute_metrics = [
        'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
        'Total Ad Orders', 'Same SKU Ad Sales', 'Other SKU Sales',
        'Same SKU Ad Orders', 'Other SKU Ad Orders'
    ]
    
    # Create test output directory
    test_output_dir = 'test_output'
    os.makedirs(test_output_dir, exist_ok=True)
    
    try:
        # Load test data and run step 1 using modular system
        test_file = create_test_data()
        
        # Initialize modular components
        config = ConfigManager()
        processor = DataProcessor(config)
        step1 = Step1KPICalculation(config, test_output_dir)
        step2 = Step2AbsoluteContributions(config, test_output_dir)
        
        # Load and preprocess data
        full_df = processor.load_and_preprocess_data(test_file)
        
        p1_start = pd.to_datetime('2025-01-01')
        p1_end = pd.to_datetime('2025-01-31')
        p2_start = pd.to_datetime('2025-02-01')
        p2_end = pd.to_datetime('2025-02-28')
        
        # Execute step 1
        p1_kpis, p2_kpis, p1_totals, p2_totals = step1.execute(
            full_df, p1_start, p1_end, p2_start, p2_end
        )
        
        # Execute step 2
        absolute_contributions = step2.execute(
            p1_kpis, p2_kpis, p1_totals, p2_totals
        )
        
        # Check that all expected files were created in the step2 subdirectory
        step2_dir = os.path.join(test_output_dir, 'absolute_contributions')
        missing_files = []
        for metric in expected_absolute_metrics:
            filename = f'{metric.lower().replace(" ", "_")}_absolute_contribution.csv'
            filepath = os.path.join(step2_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
        
        if missing_files:
            print(f"✗ Missing absolute contribution files: {missing_files}")
            return False
        
        # Check combined file
        combined_file = os.path.join(step2_dir, 'all_absolute_metric_contributions.csv')
        if not os.path.exists(combined_file):
            print("✗ Missing combined absolute contributions file")
            return False
        
        print(f"✓ All {len(expected_absolute_metrics)} absolute metric contributions calculated")
        print("✓ Combined absolute contributions file created")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_output_dir):
            import shutil
            shutil.rmtree(test_output_dir)

def test_step3_mix_rate_contributions():
    """
    Test Step 3: Verify all calculated KPIs are processed
    """
    print("\n=== TESTING STEP 3: MIX RATE CONTRIBUTIONS ===")
    
    expected_calculated_kpis = ['CTR', 'Conversion Rate', 'CPC', 'ROAS', 'ACoS']
    
    # Create test output directory
    test_output_dir = 'test_output'
    os.makedirs(test_output_dir, exist_ok=True)
    
    try:
        # Load test data and run steps 1 using modular system
        test_file = create_test_data()
        
        # Initialize modular components
        config = ConfigManager()
        processor = DataProcessor(config)
        step1 = Step1KPICalculation(config, test_output_dir)
        step3 = Step3MixRateContributions(config, test_output_dir)
        
        # Load and preprocess data
        full_df = processor.load_and_preprocess_data(test_file)
        
        p1_start = pd.to_datetime('2025-01-01')
        p1_end = pd.to_datetime('2025-01-31')
        p2_start = pd.to_datetime('2025-02-01')
        p2_end = pd.to_datetime('2025-02-28')
        
        # Execute step 1
        p1_kpis, p2_kpis, p1_totals, p2_totals = step1.execute(
            full_df, p1_start, p1_end, p2_start, p2_end
        )
        
        # Execute step 3
        mix_rate_contributions = step3.execute(
            p1_kpis, p2_kpis, p1_totals, p2_totals
        )
        
        # Check that all expected files were created in the step3 subdirectory
        step3_dir = os.path.join(test_output_dir, 'mix_rate_contributions')
        missing_files = []
        for kpi in expected_calculated_kpis:
            filename = f'{kpi.lower().replace(" ", "_")}_mix_rate_contributions.csv'
            filepath = os.path.join(step3_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
        
        if missing_files:
            print(f"✗ Missing mix rate contribution files: {missing_files}")
            return False
        
        print(f"✓ All {len(expected_calculated_kpis)} mix rate contributions calculated")
        
        # Verify file contents have expected columns
        test_file_path = os.path.join(step3_dir, 'ctr_mix_rate_contributions.csv')
        if os.path.exists(test_file_path):
            df = pd.read_csv(test_file_path)
            expected_columns = ['Mix Impact', 'Rate Impact', 'Total Contribution']
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                print(f"✗ Missing columns in CTR file: {missing_columns}")
                return False
            print("✓ Mix rate contribution files have expected columns")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_output_dir):
            import shutil
            shutil.rmtree(test_output_dir)

def test_step4_acos_roas_handling():
    """
    Test Step 4: Verify ACoS/ROAS infinity handling
    """
    print("\n=== TESTING STEP 4: ACOS/ROAS INFINITY HANDLING ===")
    
    # Create test output directory
    test_output_dir = 'test_output'
    os.makedirs(test_output_dir, exist_ok=True)
    
    try:
        # Load test data and run step 1 using modular system
        test_file = create_test_data()
        
        # Initialize modular components
        config = ConfigManager()
        processor = DataProcessor(config)
        step1 = Step1KPICalculation(config, test_output_dir)
        step4 = Step4AcosRoasInfinityHandling(config, test_output_dir)
        
        # Load and preprocess data
        full_df = processor.load_and_preprocess_data(test_file)
        
        p1_start = pd.to_datetime('2025-01-01')
        p1_end = pd.to_datetime('2025-01-31')
        p2_start = pd.to_datetime('2025-02-01')
        p2_end = pd.to_datetime('2025-02-28')
        
        # Execute step 1
        p1_kpis, p2_kpis, p1_totals, p2_totals = step1.execute(
            full_df, p1_start, p1_end, p2_start, p2_end
        )
        
        # Execute step 4
        final_acos_roas = step4.execute(
            p1_kpis, p2_kpis, p1_totals, p2_totals
        )
        
        if final_acos_roas is None:
            print("✗ Step 4 failed to return ACoS/ROAS contributions")
            return False
        
        # Check that the final file was created in the step4 subdirectory
        step4_dir = os.path.join(test_output_dir, 'acos_roas_final')
        final_file = os.path.join(step4_dir, 'acos_roas_final_contributions.csv')
        if not os.path.exists(final_file):
            print("✗ Missing final ACoS/ROAS contributions file")
            return False
        
        # Verify file contents
        df = pd.read_csv(final_file)
        expected_columns = ['ACoS_Contribution_BPS', 'ROAS_Contribution']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"✗ Missing columns in final ACoS/ROAS file: {missing_columns}")
            return False
        
        print("✓ ACoS/ROAS infinity handling completed successfully")
        print("✓ Final contributions file created with expected columns")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_output_dir):
            import shutil
            shutil.rmtree(test_output_dir)

def test_complete_integration():
    """
    Test the complete integrated analysis using the modular vBridge system
    """
    print("\n=== TESTING COMPLETE INTEGRATION ===")
    
    # Create test output directory
    test_output_dir = 'test_output'
    os.makedirs(test_output_dir, exist_ok=True)
    
    try:
        # Create test data
        test_file = create_test_data()
        
        # Test the complete analysis using vBridge
        p1_start = pd.to_datetime('2025-01-01')
        p1_end = pd.to_datetime('2025-01-31')
        p2_start = pd.to_datetime('2025-02-01')
        p2_end = pd.to_datetime('2025-02-28')
        
        # Initialize vBridge system
        vbridge = VBridge(output_dir=test_output_dir)
        
        # Run complete analysis
        results = vbridge.run_complete_analysis(
            csv_file_path=test_file,
            p1_start_date=p1_start.strftime('%Y-%m-%d'),
            p1_end_date=p1_end.strftime('%Y-%m-%d'),
            p2_start_date=p2_start.strftime('%Y-%m-%d'),
            p2_end_date=p2_end.strftime('%Y-%m-%d')
        )
        
        if results is None:
            print("✗ Complete analysis failed to return results")
            return False
        
        # Count generated files in organized subdirectories
        expected_subdirs = [
            'kpi_calculation',
            'absolute_contributions',
            'mix_rate_contributions',
            'acos_roas_final',
            'summary_reports'
        ]
        
        total_files = 0
        for subdir in expected_subdirs:
            subdir_path = os.path.join(test_output_dir, subdir)
            if os.path.exists(subdir_path):
                files = [f for f in os.listdir(subdir_path) if f.endswith('.csv')]
                total_files += len(files)
                print(f"✓ {subdir}: {len(files)} files")
            else:
                print(f"✗ Missing subdirectory: {subdir}")
                return False
        
        # Expected minimum files:
        # - 5 KPI calculation files (P1 campaigns, P2 campaigns, P1 totals, P2 totals, comparison) = 5
        # - 1 combined absolute metric contributions = 1
        # - 1 combined mix rate contributions = 1
        # - 1 final ACoS/ROAS contribution = 1
        # - 1 summary report file = 1
        # Total minimum: 9 files
        
        if total_files < 9:
            print(f"✗ Expected at least 9 files, but found {total_files}")
            return False
        
        print(f"✓ Complete integration test passed with {total_files} output files")
        print("✓ All analysis steps executed successfully")
        
        return True
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_output_dir):
            import shutil
            shutil.rmtree(test_output_dir)

def run_all_tests():
    """
    Run all tests to validate the implementation
    """
    print("=" * 60)
    print("RUNNING COMPREHENSIVE TESTS")
    print("=" * 60)
    print("Testing that all deviations from README have been addressed...")
    
    tests = [
        ("Step 1: KPI Calculation", test_step1_kpi_calculation),
        ("Step 2: Absolute Contributions", test_step2_absolute_contributions),
        ("Step 3: Mix Rate Contributions", test_step3_mix_rate_contributions),
        ("Step 4: ACoS/ROAS Handling", test_step4_acos_roas_handling),
        ("Complete Integration", test_complete_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("All deviations from the README have been successfully addressed.")
        print("The implementation now follows the proper 4-step sequential process.")
    else:
        print(f"\n❌ {total - passed} tests failed.")
        print("Some issues remain to be addressed.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 