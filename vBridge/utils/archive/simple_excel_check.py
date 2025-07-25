#!/usr/bin/env python3
"""
Simple check of Excel structure to understand column naming
"""

import pandas as pd

def check_excel_structure():
    """Check Excel structure to understand the issue"""
    
    print("EXCEL STRUCTURE CHECK")
    print("=" * 80)
    
    excel_path = "data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx"
    
    # Read with different approaches
    print("1. Reading with header=[12, 13]:")
    try:
        df1 = pd.read_excel(excel_path, sheet_name='Campaign', header=[12, 13])
        print(f"   Shape: {df1.shape}")
        print(f"   Columns: {list(df1.columns[:15])}")
        
        # Check first row
        print(f"   First cell: '{df1.iloc[0, 0]}'")
        
        # Look for Spend columns differently
        spend_cols = [i for i, col in enumerate(df1.columns) if isinstance(col, tuple) and 'Spend' in str(col)]
        print(f"   Spend column indices: {spend_cols}")
        
        if spend_cols:
            for idx in spend_cols[:3]:
                print(f"   Column {idx}: {df1.columns[idx]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Reading with header=12:")
    try:
        df2 = pd.read_excel(excel_path, sheet_name='Campaign', header=12)
        print(f"   Shape: {df2.shape}")
        print(f"   Columns: {list(df2.columns[:15])}")
        
        # Look for Spend
        spend_cols = [col for col in df2.columns if 'Spend' in str(col)]
        print(f"   Spend columns: {spend_cols}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Reading raw data (no header):")
    try:
        df3 = pd.read_excel(excel_path, sheet_name='Campaign', header=None)
        print(f"   Shape: {df3.shape}")
        
        # Check rows 12-14 which should contain headers
        print(f"   Row 12: {list(df3.iloc[12, :10])}")
        print(f"   Row 13: {list(df3.iloc[13, :10])}")
        print(f"   Row 14: {list(df3.iloc[14, :10])}")
        
        # Look for "Total" in the data
        for row_idx in range(15, min(20, len(df3))):
            first_cell = str(df3.iloc[row_idx, 0]) if pd.notna(df3.iloc[row_idx, 0]) else ""
            if 'Total' in first_cell:
                print(f"   Found potential totals row at {row_idx}: '{first_cell}'")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    check_excel_structure()