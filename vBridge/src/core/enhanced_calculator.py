#!/usr/bin/env python3
"""
Enhanced MixBridge Calculator Module
Handles zero baseline scenarios using delta assignment strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union

try:
    from ..config.bridge_mappings import KPI_BRIDGE_MAPPINGS
    from ..common.logger import get_logger
    from ..common.exceptions import CalculationError, ConfigurationError, ValidationError
    from ..config.constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
except ImportError:
    # Backwards compatibility during migration
    try:
        from .bridge_mappings import KPI_BRIDGE_MAPPINGS
        from .logger import get_logger
        from .exceptions import CalculationError, ConfigurationError, ValidationError
        from .constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
    except ImportError:
        from bridge_mappings import KPI_BRIDGE_MAPPINGS
        from logger import get_logger
        from exceptions import CalculationError, ConfigurationError, ValidationError
        from constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE


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


class EnhancedMixBridgeCalculator:
    """
    Advanced Mix Bridge calculator using delta assignment for zero baseline handling.
    
    Delta assignment provides mathematically consistent contribution calculations
    by proportionally assigning total period changes based on Period 2 mix.
    """
    
    def __init__(self, precision: int = 12):
        """
        Initialize enhanced calculator with delta assignment strategy.
        
        Args:
            precision: Decimal precision for calculations
        """
        self.precision = precision
        self.validation_enabled = True
        logger.info("EnhancedMixBridgeCalculator initialized with delta assignment strategy")
    
    def get_absolute_metrics(self) -> List[str]:
        """Get list of absolute (summable) metrics"""
        return MetricDefinitions.get_absolute_metrics()
    
    def calculate_contributions_enhanced(self, output_df: pd.DataFrame, 
                                       total_row: pd.DataFrame) -> pd.DataFrame:
        """
        Enhanced contribution calculation using delta assignment for zero baseline handling.
        
        Delta Assignment Method:
        1. Calculate standard contributions for campaigns with P1 > 0
        2. Calculate the delta (understated amount) between total change and standard contributions
        3. Distribute delta proportionally to zero baseline campaigns based on their P2 mix
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            DataFrame with calculated contributions using delta assignment method
            
        Raises:
            CalculationError: If calculation fails
        """
        try:
            logger.info("Starting delta assignment contribution calculation")
            return self._calculate_delta_assignment_method(output_df, total_row)
        except Exception as e:
            error_msg = f"Delta assignment calculation failed: {str(e)}"
            logger.error(error_msg)
            raise CalculationError(error_msg) from e
    
    def _calculate_delta_assignment_method(self, output_df: pd.DataFrame, 
                                         total_row: pd.DataFrame) -> pd.DataFrame:
        """
        Delta assignment method for zero baseline handling.
        
        This method ensures mathematical consistency by:
        1. Calculating standard Mix Bridge contributions for campaigns with baseline values
        2. Determining the "delta" (difference between total change and sum of standard contributions)
        3. Proportionally assigning this delta to zero baseline campaigns based on their Period 2 mix
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            DataFrame with calculated contributions
        """
        output_df = output_df.copy()
        
        for metric in self.get_absolute_metrics():
            logger.debug(f"Processing metric: {metric}")
            
            # Step 1: Calculate standard contributions for campaigns with P1 > 0
            total_standard_contribution = 0
            
            for i, row in output_df.iterrows():
                jan_total = total_row.at[0, f'{metric} - January 2025']
                jan_campaign = row[f'{metric} - January 2025']
                feb_campaign = row[f'{metric} - February 2025']
                
                if jan_total > ZERO_TOLERANCE and jan_campaign > ZERO_TOLERANCE:
                    # Standard Mix Bridge calculation: P1_mix * growth_rate * 10000
                    p1_mix = jan_campaign / jan_total
                    growth_rate = (feb_campaign / jan_campaign) - 1
                    contribution = p1_mix * growth_rate * BASIS_POINTS_MULTIPLIER
                    output_df.at[i, f'{metric} - Contribution'] = round(contribution, self.precision)
                    total_standard_contribution += contribution
                    
                    logger.debug(f"Campaign {i}: Standard contribution = {contribution:.2f} bps")
                else:
                    # Initialize to 0, will be calculated in step 3 for zero baseline campaigns
                    output_df.at[i, f'{metric} - Contribution'] = 0
            
            # Step 2: Calculate delta (understated amount)
            total_change_bps = self._calculate_total_change_bps(total_row, metric)
            delta_bps = total_change_bps - total_standard_contribution
            
            logger.debug(f"Total change: {total_change_bps:.2f} bps, "
                        f"Standard contributions: {total_standard_contribution:.2f} bps, "
                        f"Delta: {delta_bps:.2f} bps")
            
            # Step 3: Distribute delta based on P2 mix for zero baseline campaigns
            zero_baseline_campaigns = output_df[
                (output_df[f'{metric} - January 2025'] == 0) & 
                (output_df[f'{metric} - February 2025'] > 0)
            ]
            
            if len(zero_baseline_campaigns) > 0 and abs(delta_bps) > ZERO_TOLERANCE:
                # Calculate P2 total for zero baseline campaigns
                total_p2_zero_baseline = zero_baseline_campaigns[f'{metric} - February 2025'].sum()
                
                if total_p2_zero_baseline > ZERO_TOLERANCE:
                    logger.debug(f"Distributing {delta_bps:.2f} bps among "
                               f"{len(zero_baseline_campaigns)} zero baseline campaigns")
                    
                    # Assign contributions proportionally to P2 mix
                    for i in zero_baseline_campaigns.index:
                        campaign_p2 = output_df.at[i, f'{metric} - February 2025']
                        p2_proportion = campaign_p2 / total_p2_zero_baseline
                        assigned_contribution = delta_bps * p2_proportion
                        output_df.at[i, f'{metric} - Contribution'] = round(assigned_contribution, self.precision)
                        
                        logger.debug(f"Zero baseline campaign {i}: "
                                   f"P2 proportion = {p2_proportion:.4f}, "
                                   f"Assigned contribution = {assigned_contribution:.2f} bps")
        
        logger.info("Delta assignment calculation completed successfully")
        return output_df
    
    def _calculate_total_change_bps(self, total_row: pd.DataFrame, metric: str) -> float:
        """
        Calculate total change in basis points for a metric.
        
        Args:
            total_row: Totals row dataframe
            metric: Metric name
            
        Returns:
            Total change in basis points
        """
        jan_total = total_row.at[0, f'{metric} - January 2025']
        feb_total = total_row.at[0, f'{metric} - February 2025']
        
        if jan_total > ZERO_TOLERANCE:
            change_bps = ((feb_total - jan_total) / jan_total) * BASIS_POINTS_MULTIPLIER
            logger.debug(f"Total change for {metric}: {change_bps:.2f} bps")
            return change_bps
        else:
            logger.warning(f"Zero total baseline for {metric}, returning 0 bps change")
            return 0.0
    
    def get_calculation_summary(self, output_df: pd.DataFrame, total_row: pd.DataFrame) -> Dict:
        """
        Generate summary of calculation results using delta assignment.
        
        Args:
            output_df: Campaign data with contributions
            total_row: Totals row
            
        Returns:
            Dictionary with calculation summary
        """
        summary = {
            'strategy_used': 'delta_assignment',
            'total_campaigns': len(output_df),
            'metrics_processed': len(self.get_absolute_metrics()),
            'zero_baseline_campaigns': {},
            'contribution_totals': {},
            'mathematical_consistency': {}
        }
        
        for metric in self.get_absolute_metrics():
            # Count zero baseline campaigns
            zero_baseline_mask = (
                (output_df[f'{metric} - January 2025'] == 0) & 
                (output_df[f'{metric} - February 2025'] > 0)
            )
            zero_baseline_count = zero_baseline_mask.sum()
            summary['zero_baseline_campaigns'][metric] = zero_baseline_count
            
            # Calculate contribution totals
            total_contribution = output_df[f'{metric} - Contribution'].sum()
            summary['contribution_totals'][metric] = round(total_contribution, 2)
            
            # Check mathematical consistency
            expected_total = self._calculate_total_change_bps(total_row, metric)
            consistency_check = abs(total_contribution - expected_total) < 0.01  # 0.01 bps tolerance
            summary['mathematical_consistency'][metric] = {
                'expected_total_bps': round(expected_total, 2),
                'actual_total_bps': round(total_contribution, 2),
                'difference_bps': round(total_contribution - expected_total, 4),
                'is_consistent': consistency_check
            }
        
        # Overall consistency
        all_consistent = all(
            summary['mathematical_consistency'][metric]['is_consistent'] 
            for metric in self.get_absolute_metrics()
        )
        summary['overall_mathematical_consistency'] = all_consistent
        
        logger.info(f"Calculation summary generated: {summary['total_campaigns']} campaigns, "
                   f"mathematical consistency: {all_consistent}")
        
        return summary
    
    def validate_inputs(self, output_df: pd.DataFrame, total_row: pd.DataFrame) -> bool:
        """
        Validate inputs for delta assignment calculation.
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            True if inputs are valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Check required columns exist
            required_metrics = self.get_absolute_metrics()
            
            for metric in required_metrics:
                jan_col = f'{metric} - January 2025'
                feb_col = f'{metric} - February 2025'
                
                if jan_col not in output_df.columns:
                    raise ValidationError(f"Missing column: {jan_col}")
                if feb_col not in output_df.columns:
                    raise ValidationError(f"Missing column: {feb_col}")
                
                # Check for non-negative values
                if (output_df[jan_col] < 0).any():
                    raise ValidationError(f"Negative values found in {jan_col}")
                if (output_df[feb_col] < 0).any():
                    raise ValidationError(f"Negative values found in {feb_col}")
            
            # Check totals row
            if len(total_row) != 1:
                raise ValidationError("Total row must contain exactly one row")
            
            logger.debug("Input validation passed for delta assignment calculation")
            return True
            
        except Exception as e:
            error_msg = f"Input validation failed: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e