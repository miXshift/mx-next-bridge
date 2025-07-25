#!/usr/bin/env python3
"""
Output Formatting Module for Campaign Bridge Analysis
Handles CSV output formatting with two-tier headers
"""

import pandas as pd


class OutputFormatter:
    """Handles output formatting and CSV generation"""
    
    @staticmethod
    def get_metric_groups():
        """Get the metrics in the exact order from Excel"""
        return [
            ('Spend', '$'),
            ('Total Ad Sales', '$'),
            ('ACoS', '%'),
            ('ROAS', '$'),
            ('Conversion Rate', '%'),
            ('Impressions', '#'),
            ('Clicks', '#'),
            ('CTR', '%'),
            ('CPC', '$'),
            ('Same SKU Ad Sales', '$'),
            ('Other SKU Sales', '$'),
            ('Same SKU Ad Orders', '#'),
            ('Other SKU Ad Orders', '#'),
            ('Total Ad Orders', '#')
        ]
    
    @staticmethod
    def create_two_tier_headers():
        """Create two-tier header structure"""
        metric_groups = OutputFormatter.get_metric_groups()
        
        top_headers = ['Campaign Name']
        sub_headers = ['']
        
        for metric, format_type in metric_groups:
            if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                change_label = 'Pts Change'
            else:
                change_label = 'Net Change'
            
            # Add 5 columns for each metric (top header repeats metric name)
            top_headers.extend([metric] * 5)
            sub_headers.extend([
                'Jan 2025',
                'Feb 2025', 
                change_label,
                '% Change',
                'Contribution'
            ])
        
        return top_headers, sub_headers
    
    @staticmethod
    def format_bridge_data(bridge_data):
        """Format the bridge data with proper column structure"""
        metric_groups = OutputFormatter.get_metric_groups()
        
        # Create dataframe with campaign data
        data_df = pd.DataFrame()
        data_df['Campaign Name'] = bridge_data['Campaign']
        
        # Map the data to columns
        for metric, format_type in metric_groups:
            # Map old column names to new names
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            
            if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                change_col = f'{metric} - Pts Change'
            else:
                change_col = f'{metric} - Net Change'
            
            pct_change_col = f'{metric} - % Change'
            contrib_col = f'{metric} - Contribution'
            
            # Copy data with proper formatting
            if format_type == '$':
                data_df[f'{metric}_Jan'] = bridge_data[jan_col].round(2)
                data_df[f'{metric}_Feb'] = bridge_data[feb_col].round(2)
                data_df[f'{metric}_Change'] = bridge_data[change_col].round(2)
            elif format_type == '%':
                if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                    data_df[f'{metric}_Jan'] = bridge_data[jan_col].round(1)
                    data_df[f'{metric}_Feb'] = bridge_data[feb_col].round(1)
                    data_df[f'{metric}_Change'] = bridge_data[change_col].round(1)
                else:
                    data_df[f'{metric}_Jan'] = bridge_data[jan_col].round(2)
                    data_df[f'{metric}_Feb'] = bridge_data[feb_col].round(2)
                    data_df[f'{metric}_Change'] = bridge_data[change_col].round(2)
            else:  # '#' format for counts
                data_df[f'{metric}_Jan'] = bridge_data[jan_col].round(0).astype('Int64')
                data_df[f'{metric}_Feb'] = bridge_data[feb_col].round(0).astype('Int64')
                data_df[f'{metric}_Change'] = bridge_data[change_col].round(0).astype('Int64')
            
            # % Change and Contribution formatting
            data_df[f'{metric}_PctChange'] = bridge_data[pct_change_col].round(1)
            data_df[f'{metric}_Contribution'] = bridge_data[contrib_col].round(0).astype('Int64')
        
        return data_df
    
    @staticmethod
    def save_to_csv(bridge_data, output_path):
        """Save the bridge data to CSV format with two-tier headers"""
        if bridge_data is None:
            raise ValueError("No bridge data to save.")
        
        # Create headers and format data
        top_headers, sub_headers = OutputFormatter.create_two_tier_headers()
        data_df = OutputFormatter.format_bridge_data(bridge_data)
        
        # Write CSV manually to handle two-tier headers
        with open(output_path, 'w', newline='') as f:
            # Write top header row
            f.write(','.join(top_headers) + '\n')
            # Write sub header row
            f.write(','.join(sub_headers) + '\n')
            
            # Write data rows
            for _, row in data_df.iterrows():
                # Build row data in correct order
                row_data = [str(row['Campaign Name'])]
                
                # Add data for each metric in order
                metric_groups = [
                    'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
                    'Impressions', 'Clicks', 'CTR', 'CPC', 'Same SKU Ad Sales',
                    'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders'
                ]
                
                for metric in metric_groups:
                    row_data.extend([
                        str(row[f'{metric}_Jan']),
                        str(row[f'{metric}_Feb']),
                        str(row[f'{metric}_Change']),
                        str(row[f'{metric}_PctChange']),
                        str(row[f'{metric}_Contribution'])
                    ])
                
                f.write(','.join(row_data) + '\n')
        
        print(f"\nBridge data saved to: {output_path}")