#!/usr/bin/env python3
"""
Check current contribution totals in the enhanced output
"""

import pandas as pd

# Load current enhanced output
df = pd.read_csv('output/analyses/mixbridge_jan2025-feb2025_delta_20250718_153220.csv')

# Check totals
total_row = df[df['Campaign'] == 'Total']
print('Current Spend Contribution in Total row:', total_row['Spend - Contribution'].iloc[0])

# Sum individual contributions
campaigns = df[df['Campaign'] != 'Total']
spend_sum = campaigns['Spend - Contribution'].sum()
print('Sum of individual Spend Contributions:', spend_sum)
print('Difference:', abs(total_row['Spend - Contribution'].iloc[0] - spend_sum))