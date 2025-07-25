#!/usr/bin/env python3
"""
Campaign Bridge Analysis Tool
Replicates the campaign tab of the Excel bridge report using CSV source data
"""

import pandas as pd
import numpy as np
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')


class CampaignBridge:
    def __init__(self, csv_path):
        """Initialize with path to source CSV data"""
        self.csv_path = csv_path
        self.df = None
        self.jan_data = None
        self.feb_data = None
        self.bridge_data = None
        
    def load_data(self):
        """Load and filter the source CSV data"""
        print(f"Loading data from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        
        # Convert DateKey to datetime
        self.df['Date'] = pd.to_datetime(self.df['DateKey'], format='%Y%m%d')
        
        # Filter for January 2025 and February 2025
        self.jan_data = self.df[
            (self.df['Date'] >= '2025-01-01') & 
            (self.df['Date'] <= '2025-01-31')
        ].copy()
        
        self.feb_data = self.df[
            (self.df['Date'] >= '2025-02-01') & 
            (self.df['Date'] <= '2025-02-28')
        ].copy()
        
        print(f"January 2025 records: {len(self.jan_data)}")
        print(f"February 2025 records: {len(self.feb_data)}")
        
    def aggregate_period_data(self, period_df):
        """Aggregate data by campaign for a given period"""
        # Group by CampaignName and aggregate metrics
        agg_dict = {
            'Cost': 'sum',
            'Sales': 'sum',
            'Impressions': 'sum',
            'Clicks': 'sum',
            'AttributedSalesSameSKU14day': 'sum',
            'AttributedConversionsSameSKU14day': 'sum',
            'AttributedConversions14day': 'sum'
        }
        
        grouped = period_df.groupby('CampaignName').agg(agg_dict).reset_index()
        
        # Calculate derived metrics
        grouped['Other SKU Sales'] = grouped['Sales'] - grouped['AttributedSalesSameSKU14day']
        grouped['Other SKU Ad Orders'] = (
            grouped['AttributedConversions14day'] - 
            grouped['AttributedConversionsSameSKU14day']
        )
        
        # Calculate rate metrics with safe division (as decimals)
        grouped['ACoS'] = np.where(
            grouped['Sales'] > 0,
            grouped['Cost'] / grouped['Sales'],
            0
        )
        
        grouped['ROAS'] = np.where(
            grouped['Cost'] > 0,
            grouped['Sales'] / grouped['Cost'],
            0
        )
        
        grouped['Conversion Rate'] = np.where(
            grouped['Clicks'] > 0,
            grouped['AttributedConversions14day'] / grouped['Clicks'],
            0
        )
        
        grouped['CTR'] = np.where(
            grouped['Impressions'] > 0,
            grouped['Clicks'] / grouped['Impressions'],
            0
        )
        
        grouped['CPC'] = np.where(
            grouped['Clicks'] > 0,
            grouped['Cost'] / grouped['Clicks'],
            0
        )
        
        # Rename columns to match Excel format
        grouped = grouped.rename(columns={
            'Cost': 'Spend',
            'Sales': 'Total Ad Sales',
            'Clicks': 'Clicks',
            'Impressions': 'Impressions',
            'AttributedSalesSameSKU14day': 'Same SKU Ad Sales',
            'AttributedConversionsSameSKU14day': 'Same SKU Ad Orders',
            'AttributedConversions14day': 'Total Ad Orders'
        })
        
        return grouped
    
    def calculate_bridge(self):
        """Calculate the bridge between January and February data"""
        print("\nAggregating January data...")
        jan_agg = self.aggregate_period_data(self.jan_data)
        
        print("Aggregating February data...")
        feb_agg = self.aggregate_period_data(self.feb_data)
        
        # Get all unique campaigns from both periods
        all_campaigns = pd.concat([
            jan_agg[['CampaignName']], 
            feb_agg[['CampaignName']]
        ]).drop_duplicates()
        
        # Merge data for both periods
        bridge = all_campaigns.merge(
            jan_agg, on='CampaignName', how='left', suffixes=('', '_jan')
        ).merge(
            feb_agg, on='CampaignName', how='left', suffixes=('_jan', '_feb')
        )
        
        # Fill NaN values with 0 for campaigns that don't exist in one period
        numeric_cols = bridge.select_dtypes(include=[np.number]).columns
        bridge[numeric_cols] = bridge[numeric_cols].fillna(0)
        
        # Calculate metrics for each metric group
        metrics = [
            'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
            'Impressions', 'Clicks', 'CTR', 'CPC', 'Same SKU Ad Sales',
            'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders',
            'Total Ad Orders'
        ]
        
        # Create output dataframe
        output_columns = ['Campaign']
        
        for metric in metrics:
            jan_col = metric if metric + '_jan' not in bridge.columns else metric + '_jan'
            feb_col = metric if metric + '_feb' not in bridge.columns else metric + '_feb'
            
            # Ensure columns exist
            if jan_col not in bridge.columns:
                bridge[jan_col] = bridge[metric]
            if feb_col not in bridge.columns:
                bridge[feb_col] = bridge[metric]
            
            # Add columns for each metric group
            output_columns.extend([
                f'{metric} - January 2025',
                f'{metric} - February 2025',
                f'{metric} - {"Pts" if metric in ["ACoS", "CTR", "Conversion Rate"] else "Net"} Change',
                f'{metric} - % Change',
                f'{metric} - Contribution'
            ])
        
        # Initialize output dataframe
        output_df = pd.DataFrame(columns=output_columns)
        output_df['Campaign'] = bridge['CampaignName']
        
        # Calculate values for each metric
        for metric in metrics:
            jan_col = metric if metric + '_jan' not in bridge.columns else metric + '_jan'
            feb_col = metric if metric + '_feb' not in bridge.columns else metric + '_feb'
            
            # Period values
            output_df[f'{metric} - January 2025'] = bridge[jan_col]
            output_df[f'{metric} - February 2025'] = bridge[feb_col]
            
            # Net/Points change
            if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                output_df[f'{metric} - Pts Change'] = bridge[feb_col] - bridge[jan_col]
            else:
                output_df[f'{metric} - Net Change'] = bridge[feb_col] - bridge[jan_col]
            
            # % Change (as decimal, not percentage)
            output_df[f'{metric} - % Change'] = np.where(
                bridge[jan_col] != 0,
                (bridge[feb_col] - bridge[jan_col]) / bridge[jan_col],
                0
            )
            
            # Contribution will be calculated after we have totals
            output_df[f'{metric} - Contribution'] = 0
        
        # Add Total row
        total_row = pd.DataFrame([['Total'] + [0] * (len(output_columns) - 1)], 
                                columns=output_columns)
        
        # Calculate totals for absolute metrics
        absolute_metrics = [
            'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
            'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
            'Other SKU Ad Orders', 'Total Ad Orders'
        ]
        
        for metric in absolute_metrics:
            total_row.at[0, f'{metric} - January 2025'] = output_df[f'{metric} - January 2025'].sum()
            total_row.at[0, f'{metric} - February 2025'] = output_df[f'{metric} - February 2025'].sum()
            total_row.at[0, f'{metric} - Net Change'] = (
                total_row.at[0, f'{metric} - February 2025'] - 
                total_row.at[0, f'{metric} - January 2025']
            )
            
            if total_row.at[0, f'{metric} - January 2025'] != 0:
                total_row.at[0, f'{metric} - % Change'] = (
                    total_row.at[0, f'{metric} - Net Change'] / 
                    total_row.at[0, f'{metric} - January 2025']
                )
        
        # Calculate totals for rate metrics (as decimals)
        if total_row.at[0, 'Total Ad Sales - January 2025'] > 0:
            total_row.at[0, 'ACoS - January 2025'] = (
                total_row.at[0, 'Spend - January 2025'] / 
                total_row.at[0, 'Total Ad Sales - January 2025']
            )
        
        if total_row.at[0, 'Total Ad Sales - February 2025'] > 0:
            total_row.at[0, 'ACoS - February 2025'] = (
                total_row.at[0, 'Spend - February 2025'] / 
                total_row.at[0, 'Total Ad Sales - February 2025']
            )
        
        total_row.at[0, 'ACoS - Pts Change'] = (
            total_row.at[0, 'ACoS - February 2025'] - 
            total_row.at[0, 'ACoS - January 2025']
        )
        
        # Similar calculations for other rate metrics (all as decimals)
        for metric_config in [
            ('ROAS', 'Total Ad Sales', 'Spend'),
            ('CTR', 'Clicks', 'Impressions'),
            ('CPC', 'Spend', 'Clicks'),
            ('Conversion Rate', 'Total Ad Orders', 'Clicks')
        ]:
            metric, numerator, denominator = metric_config
            
            for period in ['January 2025', 'February 2025']:
                if total_row.at[0, f'{denominator} - {period}'] > 0:
                    value = (
                        total_row.at[0, f'{numerator} - {period}'] / 
                        total_row.at[0, f'{denominator} - {period}']
                    )
                    total_row.at[0, f'{metric} - {period}'] = value
            
            if metric in ['CTR', 'Conversion Rate']:
                total_row.at[0, f'{metric} - Pts Change'] = (
                    total_row.at[0, f'{metric} - February 2025'] - 
                    total_row.at[0, f'{metric} - January 2025']
                )
            else:
                total_row.at[0, f'{metric} - Net Change'] = (
                    total_row.at[0, f'{metric} - February 2025'] - 
                    total_row.at[0, f'{metric} - January 2025']
                )
        
        # Calculate contributions based on Mix Bridge formula BEFORE adding total row
        # Define metric categories first
        absolute_metrics_only = [
            'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
            'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
            'Other SKU Ad Orders', 'Total Ad Orders'
        ]
        
        rate_metrics = ['ACoS', 'ROAS', 'Conversion Rate', 'CTR', 'CPC']
        
        # Include both absolute and rate metrics for contribution calculation
        all_metrics = [
            'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
            'Impressions', 'Clicks', 'CTR', 'CPC', 'Same SKU Ad Sales',
            'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders'
        ]
        
        # Calculate campaign contributions first
        for i, row in output_df.iterrows():
            for metric in all_metrics:
                jan_total = total_row.at[0, f'{metric} - January 2025']
                if jan_total > 0:
                    p1_mix = row[f'{metric} - January 2025'] / jan_total
                    jan_value = row[f'{metric} - January 2025']
                    feb_value = row[f'{metric} - February 2025']
                    
                    # Handle edge case: P1 is 0 but P2 is not 0 for Spend and related metrics
                    if jan_value == 0 and feb_value != 0 and metric in absolute_metrics_only:
                        # Use dummy value to enable valid calculation
                        jan_value = 0.0000001
                    
                    if jan_value > 0:
                        growth_rate = (feb_value / jan_value) - 1
                        contribution = p1_mix * growth_rate * 10000
                        output_df.at[i, f'{metric} - Contribution'] = contribution
        
        # Calculate total row contributions 
        # Only for ABSOLUTE metrics (additive) - rate metrics get 0 by design
        # Calculate contributions for absolute metrics only
        for metric in absolute_metrics_only:
            # Sum the individual campaign contributions for this metric
            total_contribution = output_df[f'{metric} - Contribution'].sum()
            total_row.at[0, f'{metric} - Contribution'] = total_contribution
        
        # Set rate metrics contributions to 0 (correct for Mix Bridge methodology)
        for metric in rate_metrics:
            total_row.at[0, f'{metric} - Contribution'] = 0
        
        # Combine total row with campaign data
        output_df = pd.concat([total_row, output_df], ignore_index=True)
        
        self.bridge_data = output_df
        
        return output_df
    
    def format_output_to_excel_structure(self):
        """Format the output with two-tier header structure"""
        # Get the metrics in the exact order from Excel
        metric_groups = [
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
        
        # Create two-tier header structure
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
        
        # Create dataframe with campaign data
        data_df = pd.DataFrame()
        data_df['Campaign Name'] = self.bridge_data['Campaign']
        
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
                data_df[f'{metric}_Jan'] = self.bridge_data[jan_col].round(12)
                data_df[f'{metric}_Feb'] = self.bridge_data[feb_col].round(12)
                data_df[f'{metric}_Change'] = self.bridge_data[change_col].round(12)
            elif format_type == '%':
                if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                    data_df[f'{metric}_Jan'] = self.bridge_data[jan_col].round(12)
                    data_df[f'{metric}_Feb'] = self.bridge_data[feb_col].round(12)
                    data_df[f'{metric}_Change'] = self.bridge_data[change_col].round(12)
                else:
                    data_df[f'{metric}_Jan'] = self.bridge_data[jan_col].round(12)
                    data_df[f'{metric}_Feb'] = self.bridge_data[feb_col].round(12)
                    data_df[f'{metric}_Change'] = self.bridge_data[change_col].round(12)
            else:  # '#' format for counts
                data_df[f'{metric}_Jan'] = self.bridge_data[jan_col].round(0).astype('Int64')
                data_df[f'{metric}_Feb'] = self.bridge_data[feb_col].round(0).astype('Int64')
                data_df[f'{metric}_Change'] = self.bridge_data[change_col].round(0).astype('Int64')
            
            # % Change and Contribution formatting
            data_df[f'{metric}_PctChange'] = self.bridge_data[pct_change_col].round(12)
            data_df[f'{metric}_Contribution'] = self.bridge_data[contrib_col].round(12)
        
        return data_df, top_headers, sub_headers
    
    def save_to_csv(self, output_path):
        """Save the bridge data to CSV format with unique filename"""
        if self.bridge_data is None:
            raise ValueError("No bridge data to save. Run calculate_bridge() first.")
        
        # Use unique output manager for better file management
        try:
            from ..output.unique_manager import get_unique_output_manager
            unique_manager = get_unique_output_manager()
            
            # Format to get data and headers
            data_df, top_headers, sub_headers = self.format_output_to_excel_structure()
            
            # Extract analysis type and periods from existing data
            analysis_type = 'mixbridge'
            periods = None
            
            # Try to extract periods from data if columns exist
            date_cols = [col for col in data_df.columns if ' - ' in col and any(month in col for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])]
            if len(date_cols) >= 2:
                # Extract periods from column names
                period_names = list(set([col.split(' - ')[1] for col in date_cols]))
                if len(period_names) >= 2:
                    period_names.sort()  # Sort to ensure consistent ordering
                    periods = {'p1': period_names[0], 'p2': period_names[1]}
            
            # Save using unique manager
            unique_path, latest_path, previous_path = unique_manager.save_analysis(
                data=data_df,
                analysis_type=analysis_type,
                periods=periods,
                strategy='campaign_bridge',
                metadata={
                    'original_output_path': output_path,
                    'total_campaigns': len(data_df) - 1 if len(data_df) > 0 and 'Total' in str(data_df.iloc[-1, 0]) else len(data_df),
                    'metrics_count': len([col for col in data_df.columns if col != 'Campaign']),
                    'has_two_tier_headers': True
                }
            )
            
            print(f"✅ Analysis saved with unique filename:")
            print(f"   Unique file: {Path(unique_path).name}")
            print(f"   Latest file: {Path(latest_path).name}")
            if previous_path:
                print(f"   Previous file: {Path(previous_path).name}")
            
            return unique_path
            
        except ImportError:
            # Fallback to original timestamp-based naming
            timestamp = datetime.now().strftime("%H%M")  # Military time format HHMM
            base_path = output_path.rsplit('.', 1)[0]  # Remove extension
            extension = output_path.rsplit('.', 1)[1] if '.' in output_path else 'csv'
            timestamped_path = f"{base_path}_{timestamp}.{extension}"
        
        # Format to get data and headers
        data_df, top_headers, sub_headers = self.format_output_to_excel_structure()
        
        # Write CSV manually to handle two-tier headers
        with open(timestamped_path, 'w', newline='') as f:
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
        
        print(f"\nBridge data saved to: {timestamped_path}")
        return timestamped_path


def main():
    # Initialize the bridge calculator
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    
    # Load and process data
    bridge.load_data()
    
    # Calculate bridge
    print("\nCalculating bridge metrics...")
    bridge_df = bridge.calculate_bridge()
    
    # Save to CSV
    output_filename = 'output/period_comparison.csv'
    actual_filename = bridge.save_to_csv(output_filename)
    
    print(f"\nTotal campaigns analyzed: {len(bridge_df) - 1}")
    print("Bridge calculation complete!")


if __name__ == "__main__":
    main()