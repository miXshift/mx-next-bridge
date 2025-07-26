#!/usr/bin/env python3
"""
Bridge Calculator Module for Campaign Bridge Analysis
Handles bridge calculations and metric computations
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
try:
    from ..config.bridge_mappings import KPI_BRIDGE_MAPPINGS
    from ..common.logger import get_logger
    from ..common.exceptions import CalculationError, DataProcessingError
except ImportError:
    # Backwards compatibility during migration
    try:
        from .bridge_mappings import KPI_BRIDGE_MAPPINGS
        from .logger import get_logger
        from .exceptions import CalculationError, DataProcessingError
    except ImportError:
        from bridge_mappings import KPI_BRIDGE_MAPPINGS
        from logger import get_logger
        from exceptions import CalculationError, DataProcessingError


# Compatibility layer for legacy MetricDefinitions usage
class MetricDefinitions:
    """Compatibility layer using bridge mappings"""
    
    @staticmethod
    def get_all_metrics():
        return list(KPI_BRIDGE_MAPPINGS.keys())
    
    @staticmethod
    def get_absolute_metrics():
        from ..models.bridge_types import BridgeType
        return [metric for metric, config in KPI_BRIDGE_MAPPINGS.items() 
                if config.bridge_type == BridgeType.MIX_BRIDGE]
    
    @staticmethod
    def get_rate_metrics():
        from ..models.bridge_types import BridgeType
        return [metric for metric, config in KPI_BRIDGE_MAPPINGS.items() 
                if config.bridge_type in [BridgeType.MIXRATE_BRIDGE, BridgeType.MIXRATE_INFINITY]]


logger = get_logger(__name__)


class BridgeCalculator:
    """Handles bridge calculations and metric computations"""
    
    @staticmethod
    def get_metric_list() -> List[str]:
        """Get list of metrics for calculation"""
        return MetricDefinitions.get_all_metrics()
    
    @staticmethod
    def get_absolute_metrics() -> List[str]:
        """Get list of absolute (summable) metrics"""
        return MetricDefinitions.get_absolute_metrics()
    
    @staticmethod
    def create_output_dataframe(bridge_data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Create initial output dataframe with proper column structure"""
        try:
            metrics = MetricDefinitions.get_all_metrics()
            
            # Create output columns
            output_columns = ['Campaign']
            
            for metric in metrics:
                # Use centralized method to determine if percentage metric
                change_suffix = "Pts" if MetricDefinitions.is_percentage_metric(metric) else "Net"
                
                # Add columns for each metric group
                output_columns.extend([
                    f'{metric} - January 2025',
                    f'{metric} - February 2025',
                    f'{metric} - {change_suffix} Change',
                    f'{metric} - % Change',
                    f'{metric} - Contribution'
                ])
            
            # Initialize output dataframe
            output_df = pd.DataFrame(columns=output_columns)
            output_df['Campaign'] = bridge_data['CampaignName']
            
            logger.debug(f"Created output structure with {len(output_columns)} columns")
            return output_df, output_columns
            
        except Exception as e:
            error_msg = f"Failed to create output dataframe: {str(e)}"
            logger.error(error_msg)
            raise DataProcessingError(error_msg) from e
    
    @staticmethod
    def calculate_period_values(output_df: pd.DataFrame, bridge_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate period values and changes for all metrics.
        
        Args:
            output_df: Output dataframe to populate
            bridge_data: Bridge data with period values
            
        Returns:
            Updated output dataframe with period calculations
            
        Raises:
            DataProcessingError: If calculation fails
        """
        try:
            metrics = MetricDefinitions.get_all_metrics()
            
            for metric in metrics:
                jan_col = metric if metric + '_jan' not in bridge_data.columns else metric + '_jan'
                feb_col = metric if metric + '_feb' not in bridge_data.columns else metric + '_feb'
                
                logger.debug(f"Processing metric {metric}: {jan_col} -> {feb_col}")
                
                if jan_col not in bridge_data.columns or feb_col not in bridge_data.columns:
                    logger.warning(f"Missing columns for metric {metric}, skipping")
                    continue
                
                # Ensure columns exist
                if jan_col not in bridge_data.columns:
                    bridge_data[jan_col] = bridge_data[metric]
                if feb_col not in bridge_data.columns:
                    bridge_data[feb_col] = bridge_data[metric]
                
                # Period values
                output_df[f'{metric} - January 2025'] = bridge_data[jan_col]
                output_df[f'{metric} - February 2025'] = bridge_data[feb_col]
                
                # Net/Points change
                if metric in ['ACoS', 'CTR', 'Conversion Rate']:
                    output_df[f'{metric} - Pts Change'] = bridge_data[feb_col] - bridge_data[jan_col]
                else:
                    output_df[f'{metric} - Net Change'] = bridge_data[feb_col] - bridge_data[jan_col]
                
                # % Change
                output_df[f'{metric} - % Change'] = np.where(
                    bridge_data[jan_col] != 0,
                    ((bridge_data[feb_col] - bridge_data[jan_col]) / bridge_data[jan_col]) * 100,
                    0
                )
                
                # Initialize contribution (will be calculated later)
                output_df[f'{metric} - Contribution'] = 0
        
            return output_df
            
        except Exception as e:
            logger.error(f"Error calculating period values: {str(e)}")
            raise DataProcessingError(f"Failed to calculate period values: {str(e)}")
    
    @staticmethod
    def create_total_row(output_df, output_columns):
        """Create and calculate total row"""
        total_row = pd.DataFrame([['Total'] + [0] * (len(output_columns) - 1)], 
                                columns=output_columns)
        
        absolute_metrics = BridgeCalculator.get_absolute_metrics()
        
        # Calculate totals for absolute metrics
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
                ) * 100
        
        return total_row
    
    @staticmethod
    def calculate_rate_metrics_totals(total_row):
        """Calculate rate metrics for totals row"""
        # ACoS calculation
        if total_row.at[0, 'Total Ad Sales - January 2025'] > 0:
            total_row.at[0, 'ACoS - January 2025'] = (
                total_row.at[0, 'Spend - January 2025'] / 
                total_row.at[0, 'Total Ad Sales - January 2025']
            ) * 100
        
        if total_row.at[0, 'Total Ad Sales - February 2025'] > 0:
            total_row.at[0, 'ACoS - February 2025'] = (
                total_row.at[0, 'Spend - February 2025'] / 
                total_row.at[0, 'Total Ad Sales - February 2025']
            ) * 100
        
        total_row.at[0, 'ACoS - Pts Change'] = (
            total_row.at[0, 'ACoS - February 2025'] - 
            total_row.at[0, 'ACoS - January 2025']
        )
        
        # Calculate ACoS % Change (fix for missing calculation)
        if total_row.at[0, 'ACoS - January 2025'] > 0:
            total_row.at[0, 'ACoS - % Change'] = (
                (total_row.at[0, 'ACoS - February 2025'] - 
                 total_row.at[0, 'ACoS - January 2025']) /
                total_row.at[0, 'ACoS - January 2025']
            ) * 100
        else:
            total_row.at[0, 'ACoS - % Change'] = 0
        
        # Other rate metrics
        rate_metrics = [
            ('ROAS', 'Total Ad Sales', 'Spend', False),
            ('CTR', 'Clicks', 'Impressions', True),
            ('CPC', 'Spend', 'Clicks', False),
            ('Conversion Rate', 'Total Ad Orders', 'Clicks', True)
        ]
        
        for metric, numerator, denominator, is_percentage in rate_metrics:
            for period in ['January 2025', 'February 2025']:
                if total_row.at[0, f'{denominator} - {period}'] > 0:
                    value = (
                        total_row.at[0, f'{numerator} - {period}'] / 
                        total_row.at[0, f'{denominator} - {period}']
                    )
                    if is_percentage:
                        value *= 100
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
            
            # Calculate % Change for all rate metrics (fix for missing calculations)
            if total_row.at[0, f'{metric} - January 2025'] > 0:
                total_row.at[0, f'{metric} - % Change'] = (
                    (total_row.at[0, f'{metric} - February 2025'] - 
                     total_row.at[0, f'{metric} - January 2025']) /
                    total_row.at[0, f'{metric} - January 2025']
                ) * 100
            else:
                total_row.at[0, f'{metric} - % Change'] = 0
        
        return total_row
    
    @staticmethod
    def calculate_contributions(output_df, total_row):
        """
        Calculate contributions based on Mix Bridge formula with delta assignment zero baseline handling
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            DataFrame with calculated contributions
        """
        # Import enhanced calculator (lazy import to avoid circular dependencies)
        try:
            from enhanced_mixbridge_calculator import EnhancedMixBridgeCalculator
            from mixbridge_config import get_config
            
            config = get_config()
            calculator = EnhancedMixBridgeCalculator(precision=config.precision_decimals)
            return calculator.calculate_contributions_enhanced(output_df, total_row)
            
        except ImportError:
            # Fallback to original implementation if enhanced modules not available
            return BridgeCalculator._calculate_contributions_original(output_df, total_row)
    
    @staticmethod
    def _calculate_contributions_original(output_df, total_row):
        """Original contribution calculation method (fallback)"""
        absolute_metrics = BridgeCalculator.get_absolute_metrics()
        
        for i, row in output_df.iterrows():
            for metric in absolute_metrics:
                jan_total = total_row.at[0, f'{metric} - January 2025']
                if jan_total > 0:
                    p1_mix = row[f'{metric} - January 2025'] / jan_total
                    if row[f'{metric} - January 2025'] > 0:
                        growth_rate = (
                            (row[f'{metric} - February 2025'] / 
                             row[f'{metric} - January 2025']) - 1
                        )
                        contribution = p1_mix * growth_rate * 10000
                        output_df.at[i, f'{metric} - Contribution'] = contribution
        
        return output_df
    
    @staticmethod
    def sum_contributions_to_total(output_df: pd.DataFrame, total_row: pd.DataFrame) -> pd.DataFrame:
        """
        Sum individual campaign contributions into the total row.
        
        This method fixes the issue where all contribution totals show 0.0
        by properly aggregating individual campaign contributions.
        
        Args:
            output_df: DataFrame with calculated campaign contributions
            total_row: Total row DataFrame to update
            
        Returns:
            Updated total_row with summed contribution values
        """
        # Get all metrics (both absolute and rate metrics)
        all_metrics = MetricDefinitions.get_all_metrics()
        
        # Sum contributions for each metric
        for metric in all_metrics:
            contribution_col = f'{metric} - Contribution'
            if contribution_col in output_df.columns:
                # Sum the contributions from all campaigns
                total_contribution = output_df[contribution_col].sum()
                # Update the total row with the summed value
                total_row.at[0, contribution_col] = total_contribution
                
                logger.debug(f"Total contribution for {metric}: {total_contribution:.4f}")
        
        logger.info("Campaign contributions summed into total row")
        return total_row
    
    @staticmethod
    def calculate_rate_metric_contributions(output_df: pd.DataFrame, 
                                          total_row: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculate rate metric contributions using MixRate Bridge methodology.
        
        This method calculates contributions for rate metrics (ACoS, ROAS, etc.) 
        using the inverse methodology to prevent infinity errors.
        
        Args:
            output_df: DataFrame with calculated campaign data
            total_row: Total row DataFrame
            
        Returns:
            Tuple of (updated output_df, updated total_row)
        """
        try:
            # Import MixRate Bridge calculator
            from mixrate_bridge_calculator import MixRateBridgeCalculator
            
            # Initialize calculator
            calculator = MixRateBridgeCalculator()
            
            # Validate inputs
            calculator.validate_mixrate_inputs(output_df, total_row)
            
            # Calculate all rate metric contributions using appropriate methodologies
            output_df = calculator.calculate_all_rate_metric_contributions(output_df, total_row)
            
            logger.info("Rate metric contributions calculated using MixRate Bridge methodology")
            
            # Generate calculation summary for logging
            summary = calculator.calculate_mixrate_summary(output_df, total_row)
            logger.debug(f"MixRate Bridge summary: {summary}")
            
            return output_df, total_row
            
        except ImportError:
            # Fallback: Rate metrics keep zero contributions (existing behavior)
            logger.warning("MixRate Bridge calculator not available, rate metrics will have zero contributions")
            return output_df, total_row
            
        except Exception as e:
            logger.error(f"MixRate Bridge calculation failed: {str(e)}")
            logger.warning("Falling back to zero contributions for rate metrics")
            return output_df, total_row
    
    @staticmethod
    def calculate_bridge(bridge_data, validate=True):
        """
        Main bridge calculation method with delta assignment zero baseline handling
        
        Args:
            bridge_data: Campaign data for analysis
            validate: Enable validation checks
            
        Returns:
            DataFrame with calculated contributions
        """
        # Create output dataframe
        output_df, output_columns = BridgeCalculator.create_output_dataframe(bridge_data)
        
        # Calculate period values and changes
        output_df = BridgeCalculator.calculate_period_values(output_df, bridge_data)
        
        # Create total row
        total_row = BridgeCalculator.create_total_row(output_df, output_columns)
        
        # Calculate rate metrics for totals
        total_row = BridgeCalculator.calculate_rate_metrics_totals(total_row)
        
        # Calculate contributions with delta assignment handling
        output_df = BridgeCalculator.calculate_contributions(output_df, total_row)
        
        # Calculate rate metric contributions using MixRate Bridge methodology
        output_df, total_row = BridgeCalculator.calculate_rate_metric_contributions(output_df, total_row)
        
        # Sum up campaign contributions into total row
        total_row = BridgeCalculator.sum_contributions_to_total(output_df, total_row)
        
        # Validation if enabled and available
        if validate:
            try:
                from mixbridge_validator import ContributionValidator
                validator = ContributionValidator()
                is_valid = validator.validate_contributions(output_df, total_row)
                if not is_valid:
                    print("⚠️  Warning: Validation failed - check calculation accuracy")
                    if hasattr(validator, 'print_validation_report'):
                        validator.print_validation_report()
            except ImportError:
                print("ℹ️  Validation module not available, skipping validation")
        
        # Combine total row with campaign data
        final_df = pd.concat([total_row, output_df], ignore_index=True)
        
        return final_df
    
    @staticmethod
    def save_bridge_analysis(result_df, periods=None, filename=None, subdirectory='analyses', metadata=None):
        """
        Save bridge analysis with improved file management and easy latest file identification
        
        Args:
            result_df: Analysis results dataframe
            periods: Dictionary with period information (e.g., {'p1': 'jan2025', 'p2': 'feb2025'})
            filename: Optional explicit filename (for backward compatibility)
            subdirectory: Target subdirectory (ignored in new system)
            metadata: Additional metadata to include
            
        Returns:
            Tuple of (latest_path, timestamped_path, previous_path)
        """
        try:
            # Try new improved output manager first
            from improved_output_manager import get_output_manager
            
            # If explicit filename provided, use legacy saving for compatibility
            if filename:
                return BridgeCalculator._save_traditional(result_df, filename)
            
            # Default periods if not provided
            if periods is None:
                periods = {'p1': 'jan2025', 'p2': 'feb2025'}
            
            # Prepare metadata
            analysis_metadata = {
                'strategy_used': 'delta_assignment',
                'total_campaigns': len(result_df) - 1,  # Exclude total row
                'metrics_analyzed': len(BridgeCalculator.get_metric_list()),
                'data_source': 'bridge_analysis'
            }
            
            if metadata:
                analysis_metadata.update(metadata)
            
            # Use improved output manager
            output_manager = get_output_manager()
            latest_path, timestamped_path, previous_path = output_manager.save_analysis(
                data=result_df,
                analysis_type='mixbridge',
                periods=periods,
                strategy='delta_assignment',
                metadata=analysis_metadata
            )
            
            print(f"✅ Analysis saved:")
            print(f"   📄 Latest file: {latest_path}")
            print(f"   📅 Timestamped: {timestamped_path}")
            if previous_path:
                print(f"   📋 Previous: {previous_path}")
            
            return latest_path, timestamped_path, previous_path
            
        except ImportError:
            # Fallback to enhanced formatter
            try:
                from enhanced_output_formatter import get_global_formatter
                
                formatter = get_global_formatter()
                periods = periods or {'p1': 'jan2025', 'p2': 'feb2025'}
                
                csv_path, meta_path = formatter.save_analysis(
                    data=result_df,
                    analysis_type='mixbridge',
                    periods=periods,
                    strategy='delta_assignment',
                    metadata=metadata or {},
                    subdirectory=subdirectory
                )
                
                return csv_path, meta_path, None
                
            except ImportError:
                # Final fallback to traditional saving
                return BridgeCalculator._save_traditional(result_df, filename or 'output/period_comparison.csv')
    
    @staticmethod
    def _save_traditional(result_df, filename):
        """Traditional save method for backward compatibility"""
        import os
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save CSV
        result_df.to_csv(filename, index=False)
        print(f"✅ Analysis saved (traditional): {filename}")
        
        return filename, None
    
