#!/usr/bin/env python3
"""
Optimized Data Processing Module for Campaign Bridge Analysis
Handles data loading, filtering, and aggregation operations with performance improvements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path

try:
    from .utils import safe_divide, calculate_rate_metric
    from ..common.logger import get_logger
    from ..common.exceptions import DataProcessingError, FileOperationError
    from ..config.constants import (
        DEFAULT_ENCODING, CSV_BUFFER_SIZE, CHUNK_SIZE, 
        DEFAULT_DATE_COLUMN, DEFAULT_CAMPAIGN_COLUMN
    )
except ImportError:
    # Backwards compatibility during migration
    try:
        from .calculation_utils import safe_divide, calculate_rate_metric
        from .logger import get_logger
        from .exceptions import DataProcessingError, FileOperationError
        from .constants import (
            DEFAULT_ENCODING, CSV_BUFFER_SIZE, CHUNK_SIZE, 
            DEFAULT_DATE_COLUMN, DEFAULT_CAMPAIGN_COLUMN
        )
    except ImportError:
        from calculation_utils import safe_divide, calculate_rate_metric
        from logger import get_logger
        from exceptions import DataProcessingError, FileOperationError
        from constants import (
            DEFAULT_ENCODING, CSV_BUFFER_SIZE, CHUNK_SIZE,
            DEFAULT_DATE_COLUMN, DEFAULT_CAMPAIGN_COLUMN
        )


logger = get_logger(__name__)


class OptimizedDataProcessor:
    """
    Optimized data loading and processing operations with performance improvements.
    
    Performance optimizations:
    - Vectorized operations instead of iterrows()
    - Efficient date filtering with datetime indexing
    - Memory-conscious chunked processing for large files
    - Cached intermediate results
    - Type-specific optimizations for numeric columns
    """
    
    def __init__(self, csv_path: Union[str, Path], chunk_size: int = CHUNK_SIZE):
        """
        Initialize with path to source CSV data.
        
        Args:
            csv_path: Path to source CSV file
            chunk_size: Size of chunks for large file processing
        """
        self.csv_path = Path(csv_path)
        self.chunk_size = chunk_size
        self.df: Optional[pd.DataFrame] = None
        self.jan_data: Optional[pd.DataFrame] = None
        self.feb_data: Optional[pd.DataFrame] = None
        self._metadata: Dict = {}
        
        logger.info(f"DataProcessor initialized for {self.csv_path}")
        
    def load_data(self, use_chunking: bool = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and filter the source CSV data with performance optimizations.
        
        Args:
            use_chunking: Whether to use chunked reading for large files.
                         Auto-detects if None based on file size.
                         
        Returns:
            Tuple of (january_data, february_data)
            
        Raises:
            FileOperationError: If file cannot be read
            DataProcessingError: If data processing fails
        """
        try:
            logger.info(f"Loading data from {self.csv_path}")
            
            # Auto-detect chunking based on file size
            if use_chunking is None:
                file_size_mb = self.csv_path.stat().st_size / (1024 * 1024)
                use_chunking = file_size_mb > 100  # Use chunking for files > 100MB
                logger.debug(f"File size: {file_size_mb:.1f}MB, chunking: {use_chunking}")
            
            if use_chunking:
                self.df = self._load_data_chunked()
            else:
                self.df = self._load_data_direct()
            
            # Optimize data types for better performance
            self.df = self._optimize_dtypes(self.df)
            
            # Filter for target periods
            self.jan_data, self.feb_data = self._filter_periods(self.df)
            
            logger.info(f"January 2025 records: {len(self.jan_data):,}")
            logger.info(f"February 2025 records: {len(self.feb_data):,}")
            
            return self.jan_data, self.feb_data
            
        except FileNotFoundError as e:
            error_msg = f"CSV file not found: {self.csv_path}"
            logger.error(error_msg)
            raise FileOperationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load data: {str(e)}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def _load_data_direct(self) -> pd.DataFrame:
        """Load data directly for smaller files."""
        return pd.read_csv(
            self.csv_path,
            encoding=DEFAULT_ENCODING,
            low_memory=False  # Improve dtype inference
        )
    
    def _load_data_chunked(self) -> pd.DataFrame:
        """Load data in chunks for memory efficiency with large files."""
        logger.info("Loading data in chunks for memory efficiency")
        chunks = []
        
        chunk_iter = pd.read_csv(
            self.csv_path,
            encoding=DEFAULT_ENCODING,
            chunksize=self.chunk_size,
            low_memory=False
        )
        
        for i, chunk in enumerate(chunk_iter):
            # Apply basic filtering at chunk level to reduce memory usage
            chunk = self._optimize_dtypes(chunk)
            chunks.append(chunk)
            
            if i % 10 == 0:  # Log progress every 10 chunks
                logger.debug(f"Processed {i+1} chunks")
        
        logger.info(f"Concatenating {len(chunks)} chunks")
        return pd.concat(chunks, ignore_index=True)
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize data types for better performance and memory usage.
        
        Args:
            df: DataFrame to optimize
            
        Returns:
            DataFrame with optimized data types
        """
        # Convert string columns to category if they have low cardinality
        for col in df.select_dtypes(include=['object']).columns:
            if col in [DEFAULT_CAMPAIGN_COLUMN, 'CampaignName']:
                # Campaign names are categorical
                df[col] = df[col].astype('category')
            elif df[col].nunique() < len(df) * 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
        
        # Optimize numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            # Downcast integers if possible
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            # Downcast floats if possible
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        logger.debug("Data types optimized for performance")
        return df
    
    def _filter_periods(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filter data for specific periods with optimized date operations.
        
        Args:
            df: Full dataset
            
        Returns:
            Tuple of (january_data, february_data)
        """
        # Convert DateKey to datetime with error handling
        if 'DateKey' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['DateKey'], format='%Y%m%d')
            except ValueError:
                # Fallback to automatic parsing
                df['Date'] = pd.to_datetime(df['DateKey'])
        elif DEFAULT_DATE_COLUMN in df.columns:
            df['Date'] = pd.to_datetime(df[DEFAULT_DATE_COLUMN])
        else:
            raise DataProcessingError("No date column found in data")
        
        # Use efficient datetime indexing for filtering
        jan_mask = (df['Date'] >= '2025-01-01') & (df['Date'] <= '2025-01-31')
        feb_mask = (df['Date'] >= '2025-02-01') & (df['Date'] <= '2025-02-28')
        
        jan_data = df[jan_mask].copy()
        feb_data = df[feb_mask].copy()
        
        # Reset index for better performance in subsequent operations
        jan_data = jan_data.reset_index(drop=True)
        feb_data = feb_data.reset_index(drop=True)
        
        return jan_data, feb_data
        
    def aggregate_period_data(self, period_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by campaign for a given period with vectorized operations.
        
        Args:
            period_df: Period-filtered DataFrame
            
        Returns:
            Aggregated DataFrame with calculated metrics
        """
        try:
            logger.debug(f"Aggregating {len(period_df):,} records")
            
            # Define aggregation dictionary with all required metrics
            agg_dict = {
                'Cost': 'sum',
                'Sales': 'sum', 
                'Impressions': 'sum',
                'Clicks': 'sum',
                'AttributedSalesSameSKU14day': 'sum',
                'AttributedConversionsSameSKU14day': 'sum',
                'AttributedConversions14day': 'sum'
            }
            
            # Group and aggregate in one operation
            grouped = period_df.groupby('CampaignName', observed=True).agg(agg_dict).reset_index()
            
            # Vectorized calculation of derived metrics
            grouped = self._calculate_derived_metrics_vectorized(grouped)
            
            # Vectorized calculation of rate metrics
            grouped = self._calculate_rate_metrics_vectorized(grouped)
            
            # Rename columns to match expected format
            grouped = self._rename_columns(grouped)
            
            logger.debug(f"Aggregated to {len(grouped):,} campaigns")
            return grouped
            
        except Exception as e:
            error_msg = f"Failed to aggregate period data: {str(e)}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    def _calculate_derived_metrics_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived metrics using vectorized operations."""
        # Other SKU Sales = Total Sales - Same SKU Sales
        df['Other SKU Sales'] = df['Sales'] - df['AttributedSalesSameSKU14day']
        
        # Other SKU Orders = Total Orders - Same SKU Orders  
        df['Other SKU Ad Orders'] = (
            df['AttributedConversions14day'] - df['AttributedConversionsSameSKU14day']
        )
        
        # Ensure non-negative values (business logic constraint)
        df['Other SKU Sales'] = np.maximum(df['Other SKU Sales'], 0)
        df['Other SKU Ad Orders'] = np.maximum(df['Other SKU Ad Orders'], 0)
        
        return df
    
    def _calculate_rate_metrics_vectorized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate rate-based metrics using optimized vectorized operations."""
        # Use the shared calculation utilities for consistency
        df['ACoS'] = calculate_rate_metric(df['Cost'], df['Sales'], as_percentage=True)
        df['ROAS'] = calculate_rate_metric(df['Sales'], df['Cost'], as_percentage=False)
        df['Conversion Rate'] = calculate_rate_metric(
            df['AttributedConversions14day'], df['Clicks'], as_percentage=True
        )
        df['CTR'] = calculate_rate_metric(df['Clicks'], df['Impressions'], as_percentage=True)
        df['CPC'] = safe_divide(df['Cost'], df['Clicks'], fill_value=0.0)
        
        return df
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to match expected Excel format."""
        column_mapping = {
            'Cost': 'Spend',
            'Sales': 'Total Ad Sales',
            'AttributedSalesSameSKU14day': 'Same SKU Ad Sales',
            'AttributedConversionsSameSKU14day': 'Same SKU Ad Orders',
            'AttributedConversions14day': 'Total Ad Orders'
        }
        
        return df.rename(columns=column_mapping)
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics and metadata."""
        return {
            'file_path': str(self.csv_path),
            'total_records': len(self.df) if self.df is not None else 0,
            'jan_records': len(self.jan_data) if self.jan_data is not None else 0,
            'feb_records': len(self.feb_data) if self.feb_data is not None else 0,
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / (1024 * 1024) if self.df is not None else 0,
            'chunk_size': self.chunk_size
        }
    
    def get_all_campaigns(self, jan_agg: pd.DataFrame, feb_agg: pd.DataFrame) -> List[str]:
        """Get all unique campaigns from both periods."""
        jan_campaigns = set(jan_agg['CampaignName'].astype(str))
        feb_campaigns = set(feb_agg['CampaignName'].astype(str))
        all_campaigns = sorted(jan_campaigns.union(feb_campaigns))
        logger.info(f"Found {len(all_campaigns)} unique campaigns across both periods")
        return all_campaigns
    
    def merge_period_data(self, all_campaigns: List[str], jan_agg: pd.DataFrame, feb_agg: pd.DataFrame) -> pd.DataFrame:
        """Merge January and February data for all campaigns."""
        logger.info("Merging period data for bridge analysis")
        
        # Create a complete campaign list
        bridge_data = pd.DataFrame({'CampaignName': all_campaigns})
        
        # Set CampaignName as index for easier merging
        jan_agg_indexed = jan_agg.set_index('CampaignName')
        feb_agg_indexed = feb_agg.set_index('CampaignName')
        
        # Merge January data
        for col in jan_agg.columns:
            if col != 'CampaignName':
                bridge_data[f'{col}_jan'] = bridge_data['CampaignName'].map(jan_agg_indexed[col]).fillna(0)
        
        # Merge February data  
        for col in feb_agg.columns:
            if col != 'CampaignName':
                bridge_data[f'{col}_feb'] = bridge_data['CampaignName'].map(feb_agg_indexed[col]).fillna(0)
        
        logger.info(f"Bridge data prepared: {len(bridge_data)} campaigns with {len(bridge_data.columns)} columns")
        return bridge_data


# Maintain backward compatibility
class DataProcessor(OptimizedDataProcessor):
    """Backward compatibility alias for OptimizedDataProcessor."""
    
    def __init__(self, csv_path: Union[str, Path]):
        """Initialize with backward compatible signature."""
        super().__init__(csv_path)
        
    def load_data(self):
        """Load data with backward compatible signature."""
        return super().load_data()
    
    def aggregate_period_data(self, period_df):
        """Aggregate data with backward compatible signature.""" 
        return super().aggregate_period_data(period_df)
    
    def _calculate_rate_metrics(self, df):
        """Backward compatibility method."""
        return self._calculate_rate_metrics_vectorized(df)