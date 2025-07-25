#!/usr/bin/env python3
import pandas as pd

# Read the latest results
df = pd.read_csv('output/current/LATEST_mixbridge.csv')
total_row = df[df['Campaign'] == 'Total'].iloc[0]

print('🔍 ACOS ISSUE INVESTIGATION:')
print('ACoS Total Contribution:', total_row['ACoS - Contribution'])

# Check if any campaigns have ACoS contributions
campaign_rows = df[df['Campaign'] != 'Total']
acos_contribs = campaign_rows['ACoS - Contribution']
print('ACoS Campaign Contributions:')
print('  Non-zero contributions:', (abs(acos_contribs) > 0.01).sum())
print('  Sum:', acos_contribs.sum())
print('  Min/Max:', acos_contribs.min(), '/', acos_contribs.max())

# Check what happened to previous working ACoS contributions
print('\nComparing with expected:')
print('  Previous run had ACoS contribution: 111.43 bps')
print('  Current run has ACoS contribution:', total_row['ACoS - Contribution'], 'bps')
print('  Issue: ACoS contributions disappeared')