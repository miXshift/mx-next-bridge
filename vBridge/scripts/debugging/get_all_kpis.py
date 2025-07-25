import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Read the Excel file to get all KPIs
file_path = 'data/HydrapakUS_SPABridge_MoM_February 2025vsJanuary 2025.xlsx'

# Read the header row to get all KPIs
header_df = pd.read_excel(file_path, sheet_name='Campaign', nrows=12, header=None)
kpi_row = header_df.iloc[11]

# Get all KPI names and their column positions
kpi_positions = []
for i, kpi in enumerate(kpi_row.values):
    if pd.notna(kpi) and str(kpi).strip() and str(kpi) != 'KPIs':
        kpi_positions.append((i, str(kpi)))

print("All KPIs found in the file:")
print("=" * 80)
for pos, kpi in kpi_positions:
    print(f"Column {pos}: {kpi}")

# Now get the campaign data
df = pd.read_excel(file_path, sheet_name='Campaign', skiprows=12)
campaign_data = df[df['Campaign'] == '1000-CONQ-NONBRAND-ASIN-Skyflask']

if not campaign_data.empty:
    campaign_row = campaign_data.iloc[0]
    
    print("\n\nComplete metrics for campaign '1000-CONQ-NONBRAND-ASIN-Skyflask':")
    print("=" * 80)
    
    # For each KPI, show the values in the next 5 columns (typically: Jan, Feb, Net Change, % Change, Contribution)
    col_names = df.columns.tolist()
    
    for kpi_idx, (kpi_col, kpi_name) in enumerate(kpi_positions):
        print(f"\n{kpi_name}:")
        print("-" * 50)
        
        # Show the next 5 columns after each KPI header
        start_col = kpi_col
        for offset in range(5):
            if start_col + offset < len(col_names):
                col_name = col_names[start_col + offset]
                value = campaign_row[col_name]
                
                # Determine what type of column this is based on pattern
                if 'January' in col_name:
                    label = "January 2025"
                elif 'February' in col_name:
                    label = "February 2025"
                elif 'Net Change' in col_name:
                    label = "Net Change"
                elif '% Change' in col_name:
                    label = "% Change"
                elif 'Contribution' in col_name:
                    label = "Contribution"
                elif 'Pts Change' in col_name:
                    label = "Points Change"
                else:
                    label = col_name
                    
                print(f"  {label}: {value}")
                
    # Also display any columns we might have missed
    print("\n\nAdditional columns (if any):")
    print("-" * 50)
    displayed_cols = set()
    for kpi_col, _ in kpi_positions:
        for offset in range(5):
            if kpi_col + offset < len(col_names):
                displayed_cols.add(col_names[kpi_col + offset])
    
    for col in col_names:
        if col not in displayed_cols and col != 'Campaign':
            value = campaign_row[col]
            if pd.notna(value):
                print(f"{col}: {value}")