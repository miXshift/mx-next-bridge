"""
DataFrame operations module for CSV handling and data transformation.
Optimized for Mix Bridge data processing with caching support.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
from .config import AnalysisConfig, PERCENTAGE_FORMAT_METRICS

class DataFrameCache:
    """Simple in-memory cache for DataFrames."""
    
    def __init__(self):
        self._cache: Dict[str, pd.DataFrame] = {}
        
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Get DataFrame from cache."""
        return self._cache.get(key)
        
    def set(self, key: str, df: pd.DataFrame) -> None:
        """Store DataFrame in cache."""
        self._cache[key] = df.copy()
        
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        
    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

# Global cache instance
_df_cache = DataFrameCache()

def read_csv_with_multiheaders(file_path: Union[str, Path], 
                              use_cache: bool = True) -> pd.DataFrame:
    """
    Read CSV file with multi-tier headers (KPI/Dimension structure).
    
    Args:
        file_path: Path to CSV file
        use_cache: Whether to use caching
        
    Returns:
        DataFrame with processed headers
    """
    file_path = str(file_path)
    
    if use_cache and _df_cache.has(file_path):
        return _df_cache.get(file_path)
    
    # Read first few rows to detect structure
    preview = pd.read_csv(file_path, nrows=5)
    
    # Check if first row contains "KPI" - indicates multi-header
    if 'KPI' in str(preview.iloc[0].values):
        # Read with multi-index
        df = pd.read_csv(file_path, header=[0, 1])
        
        # Flatten column names
        df.columns = ['_'.join(col).strip() if col[0] != 'Unnamed' else col[1] 
                      for col in df.columns.values]
    else:
        # Standard single header
        df = pd.read_csv(file_path)
    
    if use_cache:
        _df_cache.set(file_path, df)
        
    return df

def safe_numeric_conversion(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to numeric, handling various formats.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Numeric value
    """
    if pd.isna(value):
        return default
        
    if isinstance(value, (int, float)):
        return float(value)
        
    if isinstance(value, str):
        # Remove common formatting
        value = value.strip()
        value = value.replace(',', '')
        value = value.replace('$', '')
        value = value.replace('%', '')
        
        try:
            return float(value)
        except ValueError:
            return default
            
    return default

def aggregate_by_campaign(df: pd.DataFrame, 
                         metrics_config: Dict[str, str],
                         campaign_column: str = "Campaign") -> pd.DataFrame:
    """
    Aggregate metrics by campaign with proper handling of rate vs absolute metrics.
    
    Args:
        df: Input DataFrame
        metrics_config: Dict mapping metric names to aggregation methods
        campaign_column: Name of campaign column
        
    Returns:
        Aggregated DataFrame
    """
    # Ensure campaign column exists
    if campaign_column not in df.columns:
        raise ValueError(f"Campaign column '{campaign_column}' not found")
    
    # Group by campaign
    grouped = df.groupby(campaign_column)
    
    # Build aggregation dict
    agg_dict = {}
    for col in df.columns:
        if col == campaign_column:
            continue
            
        # Check if column matches any metric pattern
        metric_type = None
        for metric, agg_type in metrics_config.items():
            if metric in col:
                metric_type = agg_type
                break
        
        # Default aggregation based on column content
        if metric_type is None:
            if any(rate in col for rate in ['Rate', 'ACoS', 'ROAS', 'CTR', 'CPC']):
                metric_type = 'mean'
            else:
                metric_type = 'sum'
                
        agg_dict[col] = metric_type
    
    # Perform aggregation
    result = grouped.agg(agg_dict).reset_index()
    
    return result

def safe_divide(numerator: Union[float, pd.Series], 
                denominator: Union[float, pd.Series], 
                default: float = 0.0) -> Union[float, pd.Series]:
    """
    Safely divide values, handling division by zero.
    
    Args:
        numerator: Numerator value(s)
        denominator: Denominator value(s)
        default: Default value for division by zero
        
    Returns:
        Result of division
    """
    if isinstance(numerator, pd.Series) and isinstance(denominator, pd.Series):
        return numerator.div(denominator).fillna(default).replace([np.inf, -np.inf], default)
    elif isinstance(denominator, (int, float)):
        return numerator / denominator if denominator != 0 else default
    else:
        # Handle mixed types
        result = pd.Series(numerator) / pd.Series(denominator)
        return result.fillna(default).replace([np.inf, -np.inf], default)

def calculate_rate_metrics(df: pd.DataFrame, 
                          metric_configs: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Calculate rate metrics from absolute values.
    
    Args:
        df: DataFrame with absolute metrics
        metric_configs: List of metric calculation configurations
            Each config should have: name, numerator, denominator, scale
            
    Returns:
        DataFrame with calculated rate metrics
    """
    result = df.copy()
    
    for config in metric_configs:
        metric_name = config['name']
        numerator_col = config['numerator']
        denominator_col = config['denominator']
        scale = config.get('scale', 1.0)
        
        if numerator_col in df.columns and denominator_col in df.columns:
            result[metric_name] = safe_divide(
                df[numerator_col] * scale,
                df[denominator_col]
            )
            
    return result

def prepare_for_excel_export(df: pd.DataFrame, 
                            percentage_metrics: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Prepare DataFrame for Excel export with proper formatting.
    
    Args:
        df: Input DataFrame
        percentage_metrics: List of metric names that should be percentages
        
    Returns:
        DataFrame ready for Excel export
    """
    result = df.copy()
    
    if percentage_metrics is None:
        percentage_metrics = PERCENTAGE_FORMAT_METRICS
    
    # Convert percentage columns to decimal format for Excel
    for col in result.columns:
        if any(metric in col for metric in percentage_metrics):
            if result[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                # Assuming values are in percentage (0-100), convert to decimal
                if result[col].max() > 1:  # Likely in percentage format
                    result[col] = result[col] / 100
                    
    return result

def export_to_csv(df: pd.DataFrame, 
                 file_path: Union[str, Path],
                 config: Optional[AnalysisConfig] = None) -> None:
    """
    Export DataFrame to CSV with Mix Bridge formatting.
    
    Args:
        df: DataFrame to export
        file_path: Output file path
        config: Analysis configuration
    """
    if config is None:
        config = AnalysisConfig()
        
    # Prepare for export
    export_df = prepare_for_excel_export(df)
    
    # Add metadata if configured
    if config.comparison.include_metadata:
        # Create metadata row
        metadata = {
            col: '' for col in export_df.columns
        }
        metadata[export_df.columns[0]] = f"Generated with Mix Bridge Analysis v0.1.0"
        
        # Create new dataframe with metadata
        metadata_df = pd.DataFrame([metadata])
        export_df = pd.concat([metadata_df, export_df], ignore_index=True)
    
    # Export to CSV
    export_df.to_csv(file_path, index=False)

def merge_period_data(p1_df: pd.DataFrame, 
                     p2_df: pd.DataFrame,
                     join_column: str = "Campaign",
                     p1_suffix: str = "_P1",
                     p2_suffix: str = "_P2") -> pd.DataFrame:
    """
    Merge two period DataFrames for comparison.
    
    Args:
        p1_df: Period 1 DataFrame
        p2_df: Period 2 DataFrame
        join_column: Column to join on
        p1_suffix: Suffix for P1 columns
        p2_suffix: Suffix for P2 columns
        
    Returns:
        Merged DataFrame
    """
    # Rename columns to avoid conflicts
    p1_renamed = p1_df.rename(columns={
        col: f"{col}{p1_suffix}" if col != join_column else col
        for col in p1_df.columns
    })
    
    p2_renamed = p2_df.rename(columns={
        col: f"{col}{p2_suffix}" if col != join_column else col
        for col in p2_df.columns
    })
    
    # Merge dataframes
    merged = pd.merge(
        p1_renamed,
        p2_renamed,
        on=join_column,
        how='outer',
        indicator=True
    )
    
    # Fill NaN values with 0 for numeric columns
    numeric_columns = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_columns] = merged[numeric_columns].fillna(0)
    
    return merged

def clear_dataframe_cache() -> None:
    """Clear the DataFrame cache."""
    _df_cache.clear()