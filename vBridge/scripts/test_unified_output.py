#!/usr/bin/env python3
"""
Test script to demonstrate unified output functionality

This script shows how to use VBridge with both individual files and unified output modes.
"""

import os
import sys
from vbridge_main import VBridge

def test_unified_output():
    """Test the unified output functionality"""
    print("=" * 80)
    print("TESTING VBRIDGE UNIFIED OUTPUT")
    print("=" * 80)
    
    # Test data file path (adjust as needed)
    csv_file_path = 'Hydrapak YTD - campaign.csv'
    
    # Check if test data exists
    if not os.path.exists(csv_file_path):
        print(f"⚠️  Test data file not found: {csv_file_path}")
        print("Please ensure you have the test data file in the current directory.")
        return
    
    # Define test periods
    p1_start_date = '2025-01-01'
    p1_end_date = '2025-01-31'
    p2_start_date = '2025-02-01'
    p2_end_date = '2025-02-28'
    
    print("\n1. Testing UNIFIED OUTPUT mode...")
    print("-" * 50)
    
    # Test unified output
    vbridge_unified = VBridge(output_dir='output_unified', unified_output=True)
    results_unified = vbridge_unified.run_complete_analysis(
        csv_file_path, p1_start_date, p1_end_date, p2_start_date, p2_end_date
    )
    
    print("\n2. Testing INDIVIDUAL FILES mode...")
    print("-" * 50)
    
    # Test individual files output
    vbridge_individual = VBridge(output_dir='output_individual', unified_output=False)
    results_individual = vbridge_individual.run_complete_analysis(
        csv_file_path, p1_start_date, p1_end_date, p2_start_date, p2_end_date
    )
    
    print("\n" + "=" * 80)
    print("COMPARISON OF OUTPUT MODES")
    print("=" * 80)
    
    # Compare outputs
    unified_file = 'output_unified/vbridge_unified_analysis.csv'
    individual_dir = 'output_individual'
    
    if os.path.exists(unified_file):
        file_size = os.path.getsize(unified_file) / 1024  # KB
        print(f"✓ Unified output: {unified_file} ({file_size:.1f} KB)")
    else:
        print("✗ Unified output file not found")
    
    if os.path.exists(individual_dir):
        # Count files in individual output
        total_files = 0
        total_size = 0
        for root, dirs, files in os.walk(individual_dir):
            for file in files:
                if file.endswith('.csv'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
        
        total_size_kb = total_size / 1024
        print(f"✓ Individual files: {total_files} CSV files ({total_size_kb:.1f} KB total)")
        
        # List directory structure
        print(f"\nIndividual files structure:")
        for root, dirs, files in os.walk(individual_dir):
            level = root.replace(individual_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.csv'):
                    print(f"{subindent}📄 {file}")
    else:
        print("✗ Individual output directory not found")
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"   • Use unified_output=True for single-file convenience")
    print(f"   • Use unified_output=False for step-by-step analysis")
    print(f"   • Both modes produce identical analytical results")

if __name__ == '__main__':
    test_unified_output() 