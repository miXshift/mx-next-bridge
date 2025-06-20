import pandas as pd
import json
import os

def clean_currency(value):
    """Remove currency symbols and commas, and convert to numeric."""
    if isinstance(value, str):
        # Remove currency symbols and commas
        value = value.replace('$', '').replace(',', '')
        try:
            # Convert to numeric, coercing errors to NaN
            return pd.to_numeric(value, errors='coerce')
        except (ValueError, TypeError):
            # Return original value if conversion fails
            return value
    return value

def main():
    # Define paths relative to the script location
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    csv_path = os.path.join(project_root, 'output', 'kpi_calculation', 'period_comparison.csv')
    kpi_format_path = os.path.join(project_root, 'kpi_format.py')

    # Load KPI formatting rules
    with open(kpi_format_path, 'r') as f:
        kpi_formats = json.load(f)

    # Read the CSV with a two-level header and index
    df = pd.read_csv(csv_path, header=[0, 1], index_col=0)

    # Iterate over columns and apply cleaning logic
    for col_name_tuple in df.columns:
        kpi, sub_metric = col_name_tuple
        
        # Clean up kpi name from file if it has extra characters from merging
        kpi = kpi.split('.')[0]

        if kpi in kpi_formats:
            formats = kpi_formats[kpi].get('formats', {})
            
            is_period_value = '202' in sub_metric
            is_net_change = 'net change' in sub_metric.lower()
            is_contribution = 'contribution' in sub_metric.lower()
            
            if is_period_value:
                if formats.get('period_values', {}).get('type') == 'currency':
                    df[col_name_tuple] = df[col_name_tuple].apply(clean_currency)
            
            if is_net_change:
                if formats.get('net_change', {}).get('type') == 'currency':
                    df[col_name_tuple] = df[col_name_tuple].apply(clean_currency)
            
            if is_contribution:
                 if formats.get('contribution', {}).get('type') == 'currency':
                    df[col_name_tuple] = df[col_name_tuple].apply(clean_currency)

    # Save the cleaned data back to the CSV, preserving the index
    df.to_csv(csv_path, index=True)
    print(f"Cleaned currency formatting from {csv_path}")

if __name__ == "__main__":
    main() 