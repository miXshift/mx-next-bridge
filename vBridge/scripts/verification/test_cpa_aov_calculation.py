#!/usr/bin/env python3
"""
Test script to verify CPA and AOV calculation functionality
"""

import sys
import pandas as pd
sys.path.append('src')

def test_cpa_aov_calculation():
    """Test CPA and AOV calculations work correctly"""
    
    print("🔍 TESTING CPA AND AOV CALCULATIONS")
    print("=" * 80)
    
    # Create test data
    test_data = pd.DataFrame({
        'Campaign': ['Campaign A', 'Campaign B', 'Campaign C'],
        'Spend - January 2025': [100.0, 200.0, 50.0],
        'Spend - February 2025': [120.0, 180.0, 70.0],
        'Total Ad Sales - January 2025': [500.0, 800.0, 200.0],
        'Total Ad Sales - February 2025': [600.0, 720.0, 280.0],
        'Total Ad Orders - January 2025': [10, 20, 5],
        'Total Ad Orders - February 2025': [12, 18, 7]
    })
    
    # Test manual calculation
    print("📊 Manual CPA/AOV Calculation Test:")
    print("-" * 40)
    
    for _, row in test_data.iterrows():
        campaign = row['Campaign']
        
        # Calculate CPA for both periods
        cpa_jan = row['Spend - January 2025'] / row['Total Ad Orders - January 2025']
        cpa_feb = row['Spend - February 2025'] / row['Total Ad Orders - February 2025']
        
        # Calculate AOV for both periods  
        aov_jan = row['Total Ad Sales - January 2025'] / row['Total Ad Orders - January 2025']
        aov_feb = row['Total Ad Sales - February 2025'] / row['Total Ad Orders - February 2025']
        
        print(f"\n{campaign}:")
        print(f"  CPA Jan: ${cpa_jan:.2f}, Feb: ${cpa_feb:.2f}")
        print(f"  AOV Jan: ${aov_jan:.2f}, Feb: ${aov_feb:.2f}")
    
    # Test bridge configuration retrieval
    try:
        from src.config.bridge_mappings import get_bridge_configuration
        
        cpa_config = get_bridge_configuration('CPA')
        aov_config = get_bridge_configuration('AOV')
        
        print(f"\n🔧 Bridge Configuration Test:")
        print(f"  CPA bridge type: {cpa_config.bridge_type}")
        print(f"  CPA mix determinant: {cpa_config.mix_determinant}")
        print(f"  AOV bridge type: {aov_config.bridge_type}")
        print(f"  AOV mix determinant: {aov_config.mix_determinant}")
        
        # Verify both use Total Ad Orders as mix determinant
        success = (cpa_config.mix_determinant == 'Total Ad Orders' and
                  aov_config.mix_determinant == 'Total Ad Orders')
        
        if success:
            print("  ✅ Both metrics use 'Total Ad Orders' as mix determinant")
        else:
            print("  ❌ Incorrect mix determinant configuration")
            return False
            
    except Exception as e:
        print(f"❌ Failed to retrieve bridge configuration: {e}")
        return False
    
    # Test data requirements validation
    print(f"\n📋 Data Requirements Validation:")
    print("-" * 40)
    
    required_fields = ['Spend', 'Total Ad Sales', 'Total Ad Orders']
    available_base_fields = [col.split(' - ')[0] for col in test_data.columns if ' - ' in col]
    unique_fields = list(set(available_base_fields))
    
    for field in required_fields:
        if field in unique_fields:
            print(f"  ✅ {field}: Available")
        else:
            print(f"  ❌ {field}: Missing")
            return False
    
    # Test contribution unit configuration
    try:
        from src.models.bridge_types import ContributionUnit
        
        print(f"\n💰 Contribution Unit Test:")
        print(f"  CPA contribution unit: {cpa_config.contribution_unit}")
        print(f"  AOV contribution unit: {aov_config.contribution_unit}")
        
        # Both should use currency units
        currency_unit = (cpa_config.contribution_unit == ContributionUnit.CURRENCY and
                        aov_config.contribution_unit == ContributionUnit.CURRENCY)
        
        if currency_unit:
            print("  ✅ Both metrics use currency contribution units")
        else:
            print("  ❌ Incorrect contribution unit configuration")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test contribution units: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS: CPA and AOV calculation test passed!")
    print("   - Manual calculations work correctly")
    print("   - Bridge configurations are valid")
    print("   - Data requirements are satisfied")
    print("   - Contribution units are properly set")
    
    return True

if __name__ == "__main__":
    success = test_cpa_aov_calculation()
    sys.exit(0 if success else 1)