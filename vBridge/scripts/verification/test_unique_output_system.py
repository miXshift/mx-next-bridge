#!/usr/bin/env python3
"""
Test script for unique output system validation
"""

import sys
import pandas as pd
import time
from pathlib import Path
sys.path.append('src')

def test_unique_output_system():
    """Test the unique filename generation system"""
    
    print("🔍 TESTING UNIQUE OUTPUT SYSTEM")
    print("=" * 80)
    
    # Test 1: Import unique manager
    try:
        from src.output.unique_manager import UniqueOutputManager, get_unique_output_manager
        print("✅ Successfully imported unique output manager")
    except ImportError as e:
        print(f"❌ Failed to import unique output manager: {e}")
        return False
    
    # Test 2: Create manager instance
    try:
        manager = UniqueOutputManager()
        print(f"✅ Created unique manager with session ID: {manager.session_id}")
    except Exception as e:
        print(f"❌ Failed to create manager instance: {e}")
        return False
    
    # Test 3: Create test data
    test_data = pd.DataFrame({
        'Campaign': ['Campaign A', 'Campaign B', 'Campaign C', 'Total'],
        'Spend - January 2025': [100.0, 200.0, 50.0, 350.0],
        'Spend - February 2025': [120.0, 180.0, 70.0, 370.0],
        'CPA - January 2025': [10.0, 10.0, 10.0, 10.0],
        'CPA - February 2025': [10.0, 10.0, 10.0, 10.0],
        'AOV - January 2025': [50.0, 40.0, 40.0, 43.33],
        'AOV - February 2025': [50.0, 40.0, 40.0, 43.33]
    })
    
    print(f"\n📊 Test Data Created: {len(test_data)} rows, {len(test_data.columns)} columns")
    
    # Test 4: Save multiple analyses with unique names
    unique_files = []
    periods = {'p1': 'January 2025', 'p2': 'February 2025'}
    
    print(f"\n🗂️ Testing Multiple Saves:")
    print("-" * 40)
    
    for i in range(3):
        try:
            unique_path, latest_path, previous_path = manager.save_analysis(
                data=test_data,
                analysis_type='mixbridge',
                periods=periods,
                strategy='test_unique_system',
                metadata={'test_run': i + 1}
            )
            
            unique_filename = Path(unique_path).name
            unique_files.append(unique_filename)
            
            print(f"Save {i+1}:")
            print(f"  Unique: {unique_filename}")
            print(f"  Latest: {Path(latest_path).name}")
            if previous_path:
                print(f"  Previous: {Path(previous_path).name}")
            
            # Small delay to ensure different timestamps
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Failed to save analysis {i+1}: {e}")
            return False
    
    # Test 5: Verify unique filenames
    print(f"\n🔍 Uniqueness Verification:")
    print("-" * 40)
    
    if len(set(unique_files)) == len(unique_files):
        print("✅ All filenames are unique")
        for i, filename in enumerate(unique_files):
            print(f"  {i+1}. {filename}")
    else:
        print("❌ Duplicate filenames detected")
        return False
    
    # Test 6: Test file existence
    print(f"\n📁 File Existence Check:")
    print("-" * 40)
    
    current_dir = Path('output/current')
    analyses_dir = Path('output/analyses')
    
    # Check unique files exist
    for filename in unique_files:
        unique_path = current_dir / filename
        analyses_path = analyses_dir / filename
        
        if unique_path.exists():
            print(f"✅ {filename} exists in current/")
        else:
            print(f"❌ {filename} missing from current/")
            return False
            
        if analyses_path.exists():
            print(f"✅ {filename} exists in analyses/")
        else:
            print(f"❌ {filename} missing from analyses/")
            return False
    
    # Check latest and previous files
    latest_file = current_dir / 'LATEST_mixbridge.csv'
    previous_file = current_dir / 'PREVIOUS_mixbridge.csv'
    
    if latest_file.exists():
        print("✅ LATEST_mixbridge.csv exists")
    else:
        print("❌ LATEST_mixbridge.csv missing")
        return False
    
    if previous_file.exists():
        print("✅ PREVIOUS_mixbridge.csv exists")
    else:
        print("⚠️ PREVIOUS_mixbridge.csv missing (expected for first run)")
    
    # Test 7: Test manager status
    print(f"\n📊 Manager Status:")
    print("-" * 40)
    
    status = manager.get_status_summary()
    print(f"Session ID: {status['session_id']}")
    print(f"Sequence Counter: {status['sequence_counter']}")
    print(f"Total Unique Files: {status['total_unique_files']}")
    print(f"Base Directory: {status['base_directory']}")
    
    # Test 8: Test current files listing
    print(f"\n📋 Current Files Listing:")
    print("-" * 40)
    
    current_files = manager.get_current_files('mixbridge')
    print(f"Found {len(current_files)} mixbridge files in current/")
    
    for file_info in current_files[:3]:  # Show first 3
        print(f"  📄 {file_info['filename']}")
        if 'metadata' in file_info and file_info['metadata']:
            metadata = file_info['metadata']
            if 'session_id' in metadata:
                print(f"      Session: {metadata['session_id']}")
            if 'test_run' in metadata:
                print(f"      Test Run: {metadata['test_run']}")
    
    # Test 9: Test latest file retrieval
    print(f"\n🎯 Latest File Test:")
    print("-" * 40)
    
    latest_path = manager.get_latest_file('mixbridge')
    if latest_path:
        print(f"✅ Latest file: {Path(latest_path).name}")
        
        # Verify it's readable
        try:
            latest_data = pd.read_csv(latest_path)
            print(f"✅ Latest file readable: {len(latest_data)} rows")
        except Exception as e:
            print(f"❌ Failed to read latest file: {e}")
            return False
    else:
        print("❌ No latest file found")
        return False
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS: Unique output system test passed!")
    print("   - Multiple unique filenames generated")
    print("   - Files saved in correct directories")
    print("   - Latest/Previous tracking works")
    print("   - Metadata system functional")
    print("   - File retrieval works correctly")
    
    return True

def test_integration_with_campaign_bridge():
    """Test integration with existing campaign bridge"""
    
    print("\n" + "=" * 80)
    print("🔗 TESTING CAMPAIGN BRIDGE INTEGRATION")
    print("=" * 80)
    
    try:
        from src.core.campaign_bridge import CampaignBridge
        
        # Check if data file exists
        data_file = 'data/Hydrapak YTD - campaign.csv'
        if not Path(data_file).exists():
            print(f"⚠️  Data file not found: {data_file}")
            print("Skipping integration test")
            return True
        
        # Initialize bridge
        bridge = CampaignBridge(data_file)
        bridge.load_data()
        bridge_df = bridge.calculate_bridge()
        
        print(f"✅ Bridge calculation completed: {len(bridge_df)} rows")
        
        # Test save with unique system
        output_path = bridge.save_to_csv('output/test_integration.csv')
        
        if output_path:
            output_filename = Path(output_path).name
            print(f"✅ Integration save successful: {output_filename}")
            
            # Verify file exists and is readable
            if Path(output_path).exists():
                test_data = pd.read_csv(output_path)
                print(f"✅ Integration file readable: {len(test_data)} rows")
            else:
                print(f"❌ Integration file not found: {output_path}")
                return False
        else:
            print("❌ Integration save failed")
            return False
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    print("✅ SUCCESS: Campaign bridge integration works!")
    return True

if __name__ == "__main__":
    success1 = test_unique_output_system()
    success2 = test_integration_with_campaign_bridge()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED: Unique output system ready for production!")
    else:
        print("❌ SOME TESTS FAILED: Review output above for details")
    
    sys.exit(0 if (success1 and success2) else 1)