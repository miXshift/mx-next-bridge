#!/usr/bin/env python3
"""
MixRate Bridge Calculator Module
Handles rate metric contributions using inverse methodology to avoid infinity errors
Specifically designed for ACoS using ROAS as the inverse calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging

try:
    from ..config.bridge_mappings import KPI_BRIDGE_MAPPINGS
    from ..common.logger import get_logger
    from ..common.exceptions import CalculationError, ValidationError
    from ..config.constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
except ImportError:
    # Backwards compatibility during migration
    try:
        from .bridge_mappings import KPI_BRIDGE_MAPPINGS
        from .logger import get_logger
        from .exceptions import CalculationError, ValidationError
        from .constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
    except ImportError:
        from bridge_mappings import KPI_BRIDGE_MAPPINGS
        from logger import get_logger
        from exceptions import CalculationError, ValidationError
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


class MixRateBridgeCalculator:
    """
    MixRate Bridge calculator for rate metrics using inverse methodology.
    
    Prevents infinity errors in rate metrics (like ACoS) by calculating through
    their inverse (like ROAS) and transforming contributions back.
    
    Formula Implementation:
    1. Calculate ROAS Mix and Rate impacts using Ad Spend as mix determinant
    2. Transform ROAS contributions back to ACoS contributions
    3. Use relative impact methodology to ensure stable attribution
    """
    
    def __init__(self, precision: int = 12):
        """
        Initialize MixRate Bridge calculator.
        
        Args:
            precision: Decimal precision for calculations
        """
        self.precision = precision
        logger.info("MixRateBridgeCalculator initialized with inverse methodology")
    
    def calculate_all_rate_metric_contributions(self, output_df: pd.DataFrame, 
                                               total_row: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all rate metric contributions using appropriate MixRate Bridge methodologies.
        
        This method handles:
        1. MixRate Bridge with Infinity Error: ACoS (via ROAS inverse)
        2. Standard MixRate Bridge: ROAS, Conversion Rate, CTR, CPC
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            DataFrame with calculated rate metric contributions
            
        Raises:
            CalculationError: If calculation fails
        """
        try:
            logger.info("Starting rate metric contributions calculation")
            
            # Import metric definitions for proper routing
            from metric_definitions import MetricDefinitions
            
            # 1. Handle MixRate Bridge with Infinity Error (ACoS via ROAS inverse)
            if 'ACoS - January 2025' in output_df.columns:
                logger.info("Calculating ACoS contributions via ROAS inverse methodology")
                output_df = self._calculate_acos_via_roas_inverse(output_df, total_row)
            
            # 2. Handle Standard MixRate Bridge (ROAS, Conversion Rate, CTR, CPC)
            mixrate_standard_metrics = MetricDefinitions.get_mixrate_standard_metrics()
            for metric in mixrate_standard_metrics:
                if f'{metric} - January 2025' in output_df.columns:
                    logger.info(f"Calculating {metric} contributions via standard MixRate Bridge")
                    output_df = self._calculate_standard_mixrate_contributions(
                        output_df, total_row, metric
                    )
            
            logger.info(f"Rate metric contributions calculated for {len(output_df)} campaigns")
            return output_df
            
        except Exception as e:
            error_msg = f"Rate metric contribution calculation failed: {str(e)}"
            logger.error(error_msg)
            raise CalculationError(error_msg) from e
    
    def _calculate_acos_via_roas_inverse(self, output_df: pd.DataFrame, 
                                        total_row: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ACoS contributions using ROAS inverse methodology (Infinity Error handling).
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            DataFrame with calculated ACoS contributions
        """
        # Validate required columns exist
        self._validate_acos_roas_columns(output_df, total_row)
        
        # Calculate ROAS values for all campaigns
        output_df = self._calculate_campaign_roas_values(output_df)
        
        # Calculate total ROAS values
        total_row = self._calculate_total_roas_values(total_row)
        
        # Calculate ROAS contributions (Mix + Rate impacts)
        roas_contributions = self._calculate_roas_contributions(output_df, total_row)
        
        # Transform ROAS contributions to ACoS contributions
        acos_contributions = self._transform_roas_to_acos_contributions(
            roas_contributions, total_row
        )
        
        # Apply ACoS contributions to output dataframe
        output_df['ACoS - Contribution'] = acos_contributions
        
        return output_df
    
    def _calculate_standard_mixrate_contributions(self, output_df: pd.DataFrame,
                                                 total_row: pd.DataFrame,
                                                 metric: str) -> pd.DataFrame:
        """
        Calculate contributions for standard MixRate Bridge metrics.
        
        These metrics (ROAS, Conversion Rate, CTR, CPC) use direct MixRate Bridge
        calculations without infinity error handling.
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            metric: The metric name to calculate contributions for
            
        Returns:
            DataFrame with calculated contributions for the metric
        """
        try:
            logger.debug(f"Calculating standard MixRate contributions for {metric}")
            
            # Get the appropriate mix determinant for each metric
            mix_determinant = self._get_mix_determinant_for_metric(metric)
            
            # Calculate contributions using MixRate Bridge formula
            contributions = self._calculate_mixrate_contributions(
                output_df, total_row, metric, mix_determinant
            )
            
            # Apply contributions to output dataframe
            contribution_col = f'{metric} - Contribution'
            output_df[contribution_col] = contributions
            
            logger.debug(f"{metric} contributions calculated: {contributions.sum():.4f}")
            return output_df
            
        except Exception as e:
            logger.error(f"Standard MixRate calculation failed for {metric}: {str(e)}")
            # Set contributions to zero on failure
            output_df[f'{metric} - Contribution'] = 0.0
            return output_df
    
    def _validate_acos_roas_columns(self, output_df: pd.DataFrame, 
                                   total_row: pd.DataFrame) -> None:
        """Validate required columns for ACoS/ROAS calculations exist."""
        required_cols = [
            'Spend - January 2025', 'Spend - February 2025',
            'Total Ad Sales - January 2025', 'Total Ad Sales - February 2025'
        ]
        
        for col in required_cols:
            if col not in output_df.columns:
                raise ValidationError(f"Missing required column: {col}")
            if col not in total_row.columns:
                raise ValidationError(f"Missing required column in total row: {col}")
    
    def _calculate_campaign_roas_values(self, output_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ROAS values for all campaigns."""
        output_df = output_df.copy()
        
        # Calculate ROAS for January and February
        for period in ['January 2025', 'February 2025']:
            spend_col = f'Spend - {period}'
            sales_col = f'Total Ad Sales - {period}'
            roas_col = f'ROAS - {period}'
            
            # ROAS = Ad Sales / Ad Spend, handle division by zero
            output_df[roas_col] = np.where(
                output_df[spend_col] > ZERO_TOLERANCE,
                output_df[sales_col] / output_df[spend_col],
                0.0
            )
        
        logger.debug(f"Campaign ROAS values calculated for {len(output_df)} campaigns")
        return output_df
    
    def _calculate_total_roas_values(self, total_row: pd.DataFrame) -> pd.DataFrame:
        """Calculate total ROAS values."""
        total_row = total_row.copy()
        
        # Calculate total ROAS for January and February
        for period in ['January 2025', 'February 2025']:
            spend_col = f'Spend - {period}'
            sales_col = f'Total Ad Sales - {period}'
            roas_col = f'ROAS - {period}'
            
            total_spend = total_row.at[0, spend_col]
            total_sales = total_row.at[0, sales_col]
            
            if total_spend > ZERO_TOLERANCE:
                total_row.at[0, roas_col] = total_sales / total_spend
            else:
                total_row.at[0, roas_col] = 0.0
        
        logger.debug("Total ROAS values calculated")
        return total_row
    
    def _calculate_roas_contributions(self, output_df: pd.DataFrame, 
                                    total_row: pd.DataFrame) -> np.ndarray:
        """
        Calculate ROAS contributions using MixRate Bridge methodology.
        
        Formula:
        1. Mix Impact = (P2 Mix – P1 Mix) * (P2 ROAS – P2 Total ROAS)
        2. Rate Impact = (P2 ROAS – P1 ROAS) * P1 Mix
        
        Where Mix is determined by Ad Spend (not Sales as in traditional Mix Bridge)
        """
        contributions = np.zeros(len(output_df))
        
        # Get total values
        total_p1_spend = total_row.at[0, 'Spend - January 2025']
        total_p2_spend = total_row.at[0, 'Spend - February 2025']
        total_p2_roas = total_row.at[0, 'ROAS - February 2025']
        
        if total_p1_spend <= ZERO_TOLERANCE:
            logger.warning("Total P1 spend is zero, cannot calculate ROAS contributions")
            return contributions
        
        for i, row in output_df.iterrows():
            # Get campaign values
            p1_spend = row['Spend - January 2025']
            p2_spend = row['Spend - February 2025']
            p1_roas = row['ROAS - January 2025']
            p2_roas = row['ROAS - February 2025']
            
            # Calculate spend mix (using Ad Spend as mix determinant)
            p1_mix = p1_spend / total_p1_spend if total_p1_spend > ZERO_TOLERANCE else 0
            p2_mix = p2_spend / total_p2_spend if total_p2_spend > ZERO_TOLERANCE else 0
            
            # Calculate Mix Impact: (P2 Mix – P1 Mix) * (P2 ROAS – P2 Total ROAS)
            mix_impact = (p2_mix - p1_mix) * (p2_roas - total_p2_roas)
            
            # Calculate Rate Impact: (P2 ROAS – P1 ROAS) * P1 Mix
            rate_impact = (p2_roas - p1_roas) * p1_mix
            
            # Total ROAS contribution (in currency units, e.g., dollars)
            total_contribution = mix_impact + rate_impact
            contributions[i] = total_contribution
            
            logger.debug(f"Campaign {i}: Mix={mix_impact:.4f}, Rate={rate_impact:.4f}, "
                        f"Total ROAS contribution={total_contribution:.4f}")
        
        logger.info(f"ROAS contributions calculated: total={contributions.sum():.4f}")
        return contributions
    
    def _transform_roas_to_acos_contributions(self, roas_contributions: np.ndarray, 
                                            total_row: pd.DataFrame) -> np.ndarray:
        """
        Transform ROAS contributions to ACoS contributions using relative impact methodology.
        
        Formula:
        1. Calculate total ROAS change
        2. Calculate total ACoS change  
        3. For each campaign: (Campaign ROAS Contribution / Total ROAS Change) * Total ACoS Change
        
        This ensures stable attribution despite denominator shifts.
        """
        # Calculate total changes
        total_roas_p1 = total_row.at[0, 'ROAS - January 2025']
        total_roas_p2 = total_row.at[0, 'ROAS - February 2025']
        total_roas_change = total_roas_p2 - total_roas_p1
        
        total_acos_p1 = total_row.at[0, 'ACoS - January 2025']
        total_acos_p2 = total_row.at[0, 'ACoS - February 2025']
        total_acos_change_pts = total_acos_p2 - total_acos_p1  # In percentage points
        
        logger.debug(f"Total ROAS change: {total_roas_change:.4f}")
        logger.debug(f"Total ACoS change: {total_acos_change_pts:.4f} pts")
        
        # Handle case where there's no ROAS change
        if abs(total_roas_change) <= ZERO_TOLERANCE:
            logger.info("No total ROAS change detected, ACoS contributions will be zero")
            return np.zeros(len(roas_contributions))
        
        # Transform each ROAS contribution to ACoS contribution
        acos_contributions = np.zeros(len(roas_contributions))
        
        for i, roas_contrib in enumerate(roas_contributions):
            # Relative impact as percentage of total ROAS change
            relative_impact_pct = roas_contrib / total_roas_change
            
            # Apply to total ACoS change and convert to basis points
            acos_contrib_pts = relative_impact_pct * total_acos_change_pts
            acos_contrib_bps = acos_contrib_pts * 100  # Convert to basis points
            
            acos_contributions[i] = acos_contrib_bps
            
            logger.debug(f"Campaign {i}: ROAS contrib={roas_contrib:.4f}, "
                        f"Relative impact={relative_impact_pct:.4f}, "
                        f"ACoS contrib={acos_contrib_bps:.2f} bps")
        
        total_acos_contrib = acos_contributions.sum()
        expected_total = total_acos_change_pts * 100  # Expected total in bps
        
        logger.info(f"ACoS contributions transformed: total={total_acos_contrib:.2f} bps "
                   f"(expected: {expected_total:.2f} bps)")
        
        return acos_contributions
    
    def calculate_mixrate_summary(self, output_df: pd.DataFrame, 
                                 total_row: pd.DataFrame) -> Dict:
        """
        Generate summary of MixRate Bridge calculations.
        
        Args:
            output_df: Campaign data with contributions
            total_row: Totals row
            
        Returns:
            Dictionary with calculation summary
        """
        summary = {
            'methodology': 'mixrate_bridge_inverse',
            'rate_metric': 'ACoS',
            'inverse_metric': 'ROAS',
            'mix_determinant': 'Ad Spend',
            'total_campaigns': len(output_df),
            'calculation_components': {},
            'mathematical_consistency': {}
        }
        
        # ROAS analysis
        total_roas_p1 = total_row.at[0, 'ROAS - January 2025']
        total_roas_p2 = total_row.at[0, 'ROAS - February 2025']
        total_roas_change = total_roas_p2 - total_roas_p1
        
        # ACoS analysis
        total_acos_p1 = total_row.at[0, 'ACoS - January 2025']
        total_acos_p2 = total_row.at[0, 'ACoS - February 2025']
        total_acos_change = total_acos_p2 - total_acos_p1
        
        summary['calculation_components'] = {
            'roas_january': round(total_roas_p1, 4),
            'roas_february': round(total_roas_p2, 4),
            'roas_change': round(total_roas_change, 4),
            'acos_january': round(total_acos_p1, 2),
            'acos_february': round(total_acos_p2, 2),
            'acos_change_pts': round(total_acos_change, 2)
        }
        
        # Check mathematical consistency
        if 'ACoS - Contribution' in output_df.columns:
            total_acos_contrib = output_df['ACoS - Contribution'].sum()
            expected_total = total_acos_change * 100  # Convert to bps
            difference = abs(total_acos_contrib - expected_total)
            
            summary['mathematical_consistency'] = {
                'total_contributions_bps': round(total_acos_contrib, 2),
                'expected_total_bps': round(expected_total, 2),
                'difference_bps': round(difference, 4),
                'is_consistent': difference < 1.0  # 1 bps tolerance
            }
        
        logger.info(f"MixRate Bridge summary generated: {summary['total_campaigns']} campaigns")
        return summary
    
    def validate_mixrate_inputs(self, output_df: pd.DataFrame, 
                               total_row: pd.DataFrame) -> bool:
        """
        Validate inputs for MixRate Bridge calculation.
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            
        Returns:
            True if inputs are valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Check required columns
            required_spend_sales = [
                'Spend - January 2025', 'Spend - February 2025',
                'Total Ad Sales - January 2025', 'Total Ad Sales - February 2025'
            ]
            
            for col in required_spend_sales:
                if col not in output_df.columns:
                    raise ValidationError(f"Missing column in campaigns: {col}")
                if col not in total_row.columns:
                    raise ValidationError(f"Missing column in totals: {col}")
            
            # Check for non-negative values
            for col in required_spend_sales:
                if (output_df[col] < 0).any():
                    raise ValidationError(f"Negative values found in campaign {col}")
                if total_row.at[0, col] < 0:
                    raise ValidationError(f"Negative value found in total {col}")
            
            # Check totals row structure
            if len(total_row) != 1:
                raise ValidationError("Total row must contain exactly one row")
            
            logger.debug("MixRate Bridge input validation passed")
            return True
            
        except Exception as e:
            error_msg = f"MixRate Bridge input validation failed: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e
    
    def _get_mix_determinant_for_metric(self, metric: str) -> str:
        """
        Get the appropriate mix determinant for a given metric.
        
        Different metrics use different denominators to determine campaign mix:
        - ROAS: Uses Ad Spend as mix determinant
        - Conversion Rate: Uses Clicks as mix determinant  
        - CTR: Uses Impressions as mix determinant
        - CPC: Uses Clicks as mix determinant
        
        Args:
            metric: The metric name
            
        Returns:
            The column name (without period) to use as mix determinant
        """
        mix_determinant_map = {
            'ROAS': 'Spend',
            'Conversion Rate': 'Clicks', 
            'CTR': 'Impressions',
            'CPC': 'Clicks'
        }
        
        return mix_determinant_map.get(metric, 'Spend')  # Default to Spend
    
    def _calculate_mixrate_contributions(self, output_df: pd.DataFrame,
                                       total_row: pd.DataFrame, 
                                       metric: str,
                                       mix_determinant: str) -> np.ndarray:
        """
        Calculate MixRate Bridge contributions for a specific metric.
        
        Standard MixRate Bridge Formula:
        1. Mix Impact = (P2 Mix – P1 Mix) × (P2 Metric – P2 Total Metric)
        2. Rate Impact = (P2 Metric – P1 Metric) × P1 Mix
        
        Args:
            output_df: Campaign data dataframe
            total_row: Totals row dataframe
            metric: The metric to calculate contributions for
            mix_determinant: The column to use for determining campaign mix
            
        Returns:
            Array of contributions for each campaign
        """
        contributions = np.zeros(len(output_df))
        
        # Get total values for mix determinant
        total_p1_mix_base = total_row.at[0, f'{mix_determinant} - January 2025']
        total_p2_mix_base = total_row.at[0, f'{mix_determinant} - February 2025']
        
        # Get total metric values
        total_p1_metric = total_row.at[0, f'{metric} - January 2025']
        total_p2_metric = total_row.at[0, f'{metric} - February 2025']
        
        if total_p1_mix_base <= ZERO_TOLERANCE:
            logger.warning(f"Total P1 {mix_determinant} is zero, cannot calculate {metric} contributions")
            return contributions
        
        for i, row in output_df.iterrows():
            # Get campaign values for mix determinant
            p1_mix_base = row[f'{mix_determinant} - January 2025']
            p2_mix_base = row[f'{mix_determinant} - February 2025']
            
            # Get campaign metric values
            p1_metric = row[f'{metric} - January 2025']
            p2_metric = row[f'{metric} - February 2025']
            
            # Calculate mix percentages
            p1_mix = p1_mix_base / total_p1_mix_base if total_p1_mix_base > ZERO_TOLERANCE else 0
            p2_mix = p2_mix_base / total_p2_mix_base if total_p2_mix_base > ZERO_TOLERANCE else 0
            
            # Calculate MixRate Bridge components
            # Mix Impact: (P2 Mix – P1 Mix) × (P2 Metric – P2 Total Metric)
            mix_impact = (p2_mix - p1_mix) * (p2_metric - total_p2_metric)
            
            # Rate Impact: (P2 Metric – P1 Metric) × P1 Mix  
            rate_impact = (p2_metric - p1_metric) * p1_mix
            
            # Total contribution
            total_contribution = mix_impact + rate_impact
            contributions[i] = total_contribution
            
            logger.debug(f"Campaign {i} {metric}: Mix={mix_impact:.4f}, Rate={rate_impact:.4f}, "
                        f"Total={total_contribution:.4f}")
        
        logger.info(f"{metric} MixRate contributions calculated: total={contributions.sum():.4f}")
        return contributions