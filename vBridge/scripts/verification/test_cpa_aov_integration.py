#!/usr/bin/env python3
"""
Test script to verify CPA and AOV KPI integration
"""

import sys
sys.path.append('src')

def test_cpa_aov_integration():
    """Test that CPA and AOV are properly integrated into the bridge system"""
    
    print("🔍 TESTING CPA AND AOV INTEGRATION")
    print("=" * 80)
    
    # Test 1: Import bridge mappings
    try:
        from src.config.bridge_mappings import KPI_BRIDGE_MAPPINGS, METRIC_FORMULAS
        print("✅ Successfully imported bridge mappings")
    except ImportError as e:
        print(f"❌ Failed to import bridge mappings: {e}")
        return False
    
    # Test 2: Check CPA and AOV exist in mappings
    expected_metrics = ['CPA', 'AOV']
    missing_metrics = []
    
    for metric in expected_metrics:
        if metric in KPI_BRIDGE_MAPPINGS:
            print(f"✅ {metric} found in KPI_BRIDGE_MAPPINGS")
        else:
            print(f"❌ {metric} missing from KPI_BRIDGE_MAPPINGS") 
            missing_metrics.append(metric)
    
    if missing_metrics:
        return False
    
    # Test 3: Check metric formulas
    for metric in expected_metrics:
        if metric in METRIC_FORMULAS:
            formula = METRIC_FORMULAS[metric]
            print(f"✅ {metric} formula: {formula.numerator} / {formula.denominator}")
        else:
            print(f"❌ {metric} missing from METRIC_FORMULAS")
            return False
    
    # Test 4: Verify configurations
    print("\n📊 Configuration Details:")
    print("-" * 40)
    
    for metric in expected_metrics:
        config = KPI_BRIDGE_MAPPINGS[metric]
        formula = METRIC_FORMULAS[metric]
        
        print(f"\n{metric}:")
        print(f"  Bridge Type: {config.bridge_type}")
        print(f"  Mix Determinant: {config.mix_determinant}")
        print(f"  Contribution Unit: {config.contribution_unit}")
        print(f"  Formula: {formula.numerator} / {formula.denominator}")
        
        # Verify expected values
        expected_values = {
            'CPA': {
                'numerator': 'Spend',
                'denominator': 'Total Ad Orders',
                'mix_determinant': 'Total Ad Orders'
            },
            'AOV': {
                'numerator': 'Total Ad Sales', 
                'denominator': 'Total Ad Orders',
                'mix_determinant': 'Total Ad Orders'
            }
        }
        
        expected = expected_values[metric]
        success = (formula.numerator == expected['numerator'] and
                  formula.denominator == expected['denominator'] and
                  config.mix_determinant == expected['mix_determinant'])
        
        if success:
            print(f"  ✅ Configuration matches specification")
        else:
            print(f"  ❌ Configuration mismatch")
            return False
    
    # Test 5: Test compatibility layer
    try:
        from src.core.bridge_calculator import BridgeCalculator
        metrics = BridgeCalculator.get_metric_list()
        
        cpa_found = 'CPA' in metrics
        aov_found = 'AOV' in metrics
        
        print(f"\n📈 Compatibility Layer Test:")
        print(f"  CPA in metric list: {'✅' if cpa_found else '❌'}")
        print(f"  AOV in metric list: {'✅' if aov_found else '❌'}")
        
        if not (cpa_found and aov_found):
            return False
            
    except ImportError as e:
        print(f"❌ Failed to test compatibility layer: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS: CPA and AOV integration test passed!")
    print("   - Both metrics are properly configured")
    print("   - Formulas match specifications")
    print("   - Bridge mappings are correct")
    print("   - Compatibility layer works")
    
    return True

if __name__ == "__main__":
    success = test_cpa_aov_integration()
    sys.exit(0 if success else 1)