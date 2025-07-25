import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Read the Excel file to understand the header structure
file_path = 'data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx'

# Read the header rows
header_df = pd.read_excel(file_path, sheet_name='Campaign', nrows=12, header=None)

print("Header Structure:")
print("=" * 80)

# Display the header rows to understand the KPIs
for i in range(12):
    row = header_df.iloc[i]
    non_nan = [(j, str(v)) for j, v in enumerate(row.values) if pd.notna(v) and str(v).strip()]
    if non_nan:
        print(f"\nRow {i}:")
        for col_idx, value in non_nan[:15]:  # Show first 15 non-empty values
            print(f"  Col {col_idx}: {value}")

# Now read with proper headers and show the KPI mappings
print("\n\nKPI Headers from Row 11:")
print("=" * 80)
kpi_row = header_df.iloc[11]
for i, kpi in enumerate(kpi_row.values):
    if pd.notna(kpi) and str(kpi).strip() and str(kpi) != 'KPIs':
        print(f"Column {i}: {kpi}")

# Get the campaign data with full understanding
df = pd.read_excel(file_path, sheet_name='Campaign', skiprows=12)
campaign_data = df[df['Campaign'] == '1000-CONQ-NONBRAND-ASIN-Skyflask'].iloc[0]

print("\n\nCampaign Metrics for '1000-CONQ-NONBRAND-ASIN-Skyflask':")
print("=" * 80)

# Map the KPIs to the values
kpi_mapping = {
    'Spend': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution'],
    'Total Ad Sales': ['January 2025.1', 'February 2025.1', 'Net Change.1', '% Change.1', 'Contribution.1'],
    'ACoS': ['January 2025.2', 'February 2025.2', 'Pts Change', '% Change.2', 'Contribution.2'],
    'ROAS': ['January 2025.3', 'February 2025.3', 'Net Change.2', '% Change.3', 'Contribution.3'],
    'CPC': ['January 2025.4', 'February 2025.4', 'Pts Change.1', '% Change.4', 'Contribution.4'],
    'Clicks': ['January 2025.5', 'February 2025.5', 'Net Change.3', '% Change.5', 'Contribution.5'],
    'Orders': ['January 2025.6', 'February 2025.6', 'Net Change.4', '% Change.6', 'Contribution.6'],
    'CVR': ['January 2025.7', 'February 2025.7', 'Pts Change.2', '% Change.7', 'Contribution.7'],
    'CPA': ['January 2025.8', 'February 2025.8', 'Net Change.5', '% Change.8', 'Contribution.8'],
    'Impress': ['January 2025.9', 'February 2025.9', 'Net Change.6', '% Change.9', 'Contribution.9'],
    'New-to-brand Orders': ['January 2025.10', 'February 2025.10', 'Net Change.7', '% Change.10', 'Contribution.10'],
    'Units': ['January 2025.11', 'February 2025.11', 'Net Change.8', '% Change.11', 'Contribution.11'],
    '% of Orders NTB': ['January 2025.12', 'February 2025.12', 'Net Change.9', '% Change.12', 'Contribution.12'],
    'Total Units': ['January 2025.13', 'February 2025.13', 'Net Change.10', '% Change.13', 'Contribution.13']
}

for kpi, cols in kpi_mapping.items():
    print(f"\n{kpi}:")
    print("-" * 40)
    if len(cols) >= 2:
        jan_val = campaign_data[cols[0]]
        feb_val = campaign_data[cols[1]]
        print(f"  January 2025: {jan_val}")
        print(f"  February 2025: {feb_val}")
        if len(cols) >= 3:
            change = campaign_data[cols[2]]
            print(f"  Net Change: {change}")
        if len(cols) >= 4:
            pct_change = campaign_data[cols[3]]
            print(f"  % Change: {pct_change}")
        if len(cols) >= 5:
            contrib = campaign_data[cols[4]]
            print(f"  Contribution: {contrib}")