import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Read the Excel file with proper header row
file_path = 'data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx'
df = pd.read_excel(file_path, sheet_name='Campaign', skiprows=12)

# Remove the Total row
df = df[df['Campaign'] != 'Total']

# Display all campaign names
print('All campaign names in the file:')
print('-' * 80)
campaigns = df['Campaign'].dropna().unique()
for i, campaign in enumerate(campaigns):
    print(f'{i+1}. {campaign}')
    
print(f'\nTotal campaigns: {len(campaigns)}')

# Check if our specific campaign exists
campaign_name = '1000-CONQ-NONBRAND-ASIN-Skyflask'
if campaign_name in campaigns:
    print(f'\n✓ Found exact match: {campaign_name}')
    
    # Get the data for this campaign
    campaign_data = df[df['Campaign'] == campaign_name].iloc[0]
    
    print('\nAll metrics and values for this campaign:')
    print('=' * 80)
    
    # Display all columns and their values
    for col in df.columns:
        value = campaign_data[col]
        if pd.notna(value):
            print(f'{col}: {value}')
        else:
            print(f'{col}: NaN')
else:
    print(f'\n✗ Exact match not found for: {campaign_name}')
    
    # Search for partial matches
    skyflask_matches = [c for c in campaigns if 'skyflask' in c.lower()]
    if skyflask_matches:
        print('\nCampaigns containing "skyflask":')
        for match in skyflask_matches:
            print(f'  - {match}')