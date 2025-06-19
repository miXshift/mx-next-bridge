"""
Data Processing for vBridge KPI Analysis

This module handles data loading, preprocessing, and aggregation
for the KPI analysis system.
"""

import pandas as pd
from typing import Optional
from config_manager import ConfigManager


class DataProcessor:
    """Handles data loading, preprocessing, and aggregation"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def load_and_preprocess_data(self, csv_path: str) -> Optional[pd.DataFrame]:
        """
        Loads data from a CSV file and preprocesses it.
        - Converts DateKey to datetime objects.
        - Fills NaN values in key numeric columns with 0.
        - Dynamically selects 14-day attribution columns if available, otherwise falls back to 7-day.
        """
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"Error: The file {csv_path} was not found.")
            return None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

        # Convert DateKey to datetime
        df[self.config.DATE_COL] = pd.to_datetime(df[self.config.DATE_COL], format='%Y%m%d')

        # Dynamically select attribution columns
        self._select_attribution_columns(df)

        # Fill NaN values for key numeric columns
        numeric_cols_to_fill = [
            self.config.COST_COL, self.config.SALES_COL_ATTR, self.config.CLICKS_COL, 
            self.config.IMPRESSIONS_COL, self.config.ORDERS_COL_ATTR, 
            self.config.SALES_SAME_SKU_COL_ATTR, self.config.ORDERS_SAME_SKU_COL_ATTR
        ]
        
        for col in numeric_cols_to_fill:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                print(f"Warning: Expected column '{col}' not found in CSV. Adding with zeros.")
                df[col] = 0

        return df
    
    def _select_attribution_columns(self, df: pd.DataFrame):
        """Dynamically select attribution columns based on availability"""
        if 'AttributedSales14day' in df.columns:
            self.config.SALES_COL_ATTR = 'AttributedSales14day'
        else:
            self.config.SALES_COL_ATTR = 'AttributedSales7day'
            
        if 'AttributedConversions14day' in df.columns:
            self.config.ORDERS_COL_ATTR = 'AttributedConversions14day'
        else:
            self.config.ORDERS_COL_ATTR = 'AttributedConversions7day'
            
        if 'AttributedSalesSameSKU14day' in df.columns:
            self.config.SALES_SAME_SKU_COL_ATTR = 'AttributedSalesSameSKU14day'
        else:
            self.config.SALES_SAME_SKU_COL_ATTR = 'AttributedSalesSameSKU7day'
            
        if 'AttributedConversionsSameSKU14day' in df.columns:
            self.config.ORDERS_SAME_SKU_COL_ATTR = 'AttributedConversionsSameSKU14day'
        else:
            self.config.ORDERS_SAME_SKU_COL_ATTR = 'AttributedConversionsSameSKU7day'
    
    def aggregate_data_for_period(self, df: pd.DataFrame, start_date: pd.Timestamp, 
                                end_date: pd.Timestamp) -> pd.DataFrame:
        """Filters data for a given date range and aggregates key metrics by campaign"""
        period_df = df[(df[self.config.DATE_COL] >= start_date) & (df[self.config.DATE_COL] <= end_date)]

        if period_df.empty:
            print(f"Warning: No data found for the period {start_date} to {end_date}.")
            agg_cols = {
                self.config.COST_COL: 'sum', self.config.SALES_COL_ATTR: 'sum', 
                self.config.CLICKS_COL: 'sum', self.config.IMPRESSIONS_COL: 'sum', 
                self.config.ORDERS_COL_ATTR: 'sum', self.config.SALES_SAME_SKU_COL_ATTR: 'sum', 
                self.config.ORDERS_SAME_SKU_COL_ATTR: 'sum'
            }
            empty_data = {col: [] for col in agg_cols.keys()}
            empty_data[self.config.CAMPAIGN_NAME_COL] = []
            return pd.DataFrame(empty_data).set_index(self.config.CAMPAIGN_NAME_COL)

        agg_metrics = {
            self.config.COST_COL: 'sum',
            self.config.SALES_COL_ATTR: 'sum',
            self.config.CLICKS_COL: 'sum',
            self.config.IMPRESSIONS_COL: 'sum',
            self.config.ORDERS_COL_ATTR: 'sum',
            self.config.SALES_SAME_SKU_COL_ATTR: 'sum',
            self.config.ORDERS_SAME_SKU_COL_ATTR: 'sum'
        }
        
        # Check if all columns to aggregate exist
        for col in agg_metrics.keys():
            if col not in period_df.columns:
                print(f"Warning: Column '{col}' not found for aggregation. Filling with 0.")
                period_df[col] = 0
                
        campaign_period_data = period_df.groupby(self.config.CAMPAIGN_NAME_COL).agg(agg_metrics).reset_index()
        return campaign_period_data.set_index(self.config.CAMPAIGN_NAME_COL) 