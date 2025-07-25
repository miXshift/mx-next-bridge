"""
MixRate Bridge with Infinity Error handling calculator implementation.

Used for metrics like ACoS and Total ACoS that can produce infinity errors
when denominators are zero. Uses inverse methodology (e.g., ROAS for ACoS).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from .base import BaseBridgeCalculator
from ...models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit
from ...config.bridge_mappings import get_metric_formula
from ...common.logger import get_logger

logger = get_logger(__name__)


class MixRateInfinityCalculator(BaseBridgeCalculator):
    """
    MixRate Bridge calculator with Infinity Error handling.
    
    For metrics that can produce infinity errors (like ACoS = Spend / Sales),
    this calculator uses the inverse metric (like ROAS = Sales / Spend) to
    calculate contributions, then transforms them back.
    
    Process:
    1. Calculate inverse metric values (e.g., ROAS)
    2. Apply standard MixRate Bridge to inverse metric
    3. Transform contributions back to original metric (e.g., ACoS)
    
    The transformation uses relative impact methodology to ensure stable
    attribution despite denominator shifts.
    """
    
    def __init__(self, configuration: BridgeConfiguration, precision: int = 12):
        """Initialize MixRate Infinity calculator."""
        if configuration.bridge_type != BridgeType.MIXRATE_INFINITY:
            raise ValueError(f"Invalid bridge type for MixRateInfinityCalculator: {configuration.bridge_type}")
        if not configuration.inverse_metric:
            raise ValueError("MixRate Infinity requires an inverse_metric")
        if not configuration.mix_determinant:
            raise ValueError("MixRate Infinity requires a mix_determinant")
        super().__init__(configuration, precision)
    
    def calculate_contributions(self,
                              campaign_data: pd.DataFrame,
                              total_row: pd.DataFrame,
                              metric: str,
                              p1_suffix: str = "January 2025",
                              p2_suffix: str = "February 2025") -> np.ndarray:
        """
        Calculate MixRate contributions using inverse methodology.
        
        Args:
            campaign_data: Campaign-level data
            total_row: Total row with aggregate values
            metric: Original metric name (e.g., "ACoS")
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Array of contribution values in basis points
        """
        # Step 1: Calculate inverse metric values
        inverse_data = self._calculate_inverse_values(
            campaign_data, total_row, self.config.inverse_metric, p1_suffix, p2_suffix
        )
        
        # Step 2: Calculate inverse metric contributions using MixRate Bridge
        inverse_contributions = self._calculate_inverse_contributions(
            inverse_data["campaign_data"],
            inverse_data["total_row"],
            self.config.inverse_metric,
            p1_suffix,
            p2_suffix
        )
        
        # Step 3: Transform inverse contributions back to original metric
        original_contributions = self._transform_to_original_metric(
            inverse_contributions,
            total_row,
            metric,
            self.config.inverse_metric,
            p1_suffix,
            p2_suffix
        )
        
        return original_contributions
    
    def _calculate_inverse_values(self,
                                campaign_data: pd.DataFrame,
                                total_row: pd.DataFrame,
                                inverse_metric: str,
                                p1_suffix: str,
                                p2_suffix: str) -> Dict[str, pd.DataFrame]:
        """
        Calculate inverse metric values for all campaigns and totals.
        
        Args:
            campaign_data: Original campaign data
            total_row: Original total row
            inverse_metric: Name of inverse metric (e.g., "ROAS")
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Dictionary with updated campaign_data and total_row including inverse values
        """
        # Get formula for inverse metric
        formula = get_metric_formula(inverse_metric)
        if not formula:
            raise ValueError(f"No formula found for inverse metric: {inverse_metric}")
        
        # Copy dataframes to avoid modifying originals
        campaign_data = campaign_data.copy()
        total_row = total_row.copy()
        
        # Calculate inverse values for both periods
        for period in [p1_suffix, p2_suffix]:
            num_col = f"{formula.numerator} - {period}"
            denom_col = f"{formula.denominator} - {period}"
            inverse_col = f"{inverse_metric} - {period}"
            
            # Calculate for campaigns
            campaign_data[inverse_col] = campaign_data.apply(
                lambda row: formula.calculate(row[num_col], row[denom_col]),
                axis=1
            )
            
            # Calculate for totals
            total_row[inverse_col] = formula.calculate(
                total_row[num_col].iloc[0],
                total_row[denom_col].iloc[0]
            )
        
        logger.debug(f"Calculated {inverse_metric} values for transformation")
        
        return {
            "campaign_data": campaign_data,
            "total_row": total_row
        }
    
    def _calculate_inverse_contributions(self,
                                       campaign_data: pd.DataFrame,
                                       total_row: pd.DataFrame,
                                       inverse_metric: str,
                                       p1_suffix: str,
                                       p2_suffix: str) -> np.ndarray:
        """
        Calculate contributions for the inverse metric using standard MixRate Bridge.
        
        Args:
            campaign_data: Campaign data with inverse metric values
            total_row: Total row with inverse metric values
            inverse_metric: Name of inverse metric
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Array of inverse metric contributions
        """
        # Get column names
        inverse_p1_col = f"{inverse_metric} - {p1_suffix}"
        inverse_p2_col = f"{inverse_metric} - {p2_suffix}"
        mix_p1_col = f"{self.config.mix_determinant} - {p1_suffix}"
        mix_p2_col = f"{self.config.mix_determinant} - {p2_suffix}"
        
        # Get total values
        total_mix_p1 = total_row[mix_p1_col].iloc[0]
        total_mix_p2 = total_row[mix_p2_col].iloc[0]
        total_inverse_p2 = total_row[inverse_p2_col].iloc[0]
        
        contributions = np.zeros(len(campaign_data))
        
        if total_mix_p1 == 0:
            logger.warning(f"Total {self.config.mix_determinant} for {p1_suffix} is zero")
            return contributions
        
        # Calculate MixRate Bridge for inverse metric
        for i, row in campaign_data.iterrows():
            # Get values
            campaign_mix_p1 = row[mix_p1_col]
            campaign_mix_p2 = row[mix_p2_col]
            campaign_inverse_p1 = row[inverse_p1_col]
            campaign_inverse_p2 = row[inverse_p2_col]
            
            # Calculate mix
            p1_mix = campaign_mix_p1 / total_mix_p1 if total_mix_p1 > 0 else 0
            p2_mix = campaign_mix_p2 / total_mix_p2 if total_mix_p2 > 0 else 0
            
            # MixRate Bridge components
            mix_impact = (p2_mix - p1_mix) * (campaign_inverse_p2 - total_inverse_p2)
            rate_impact = (campaign_inverse_p2 - campaign_inverse_p1) * p1_mix
            
            contributions[i] = mix_impact + rate_impact
        
        logger.debug(f"Calculated {inverse_metric} contributions: sum={contributions.sum():.4f}")
        
        return contributions
    
    def _transform_to_original_metric(self,
                                    inverse_contributions: np.ndarray,
                                    total_row: pd.DataFrame,
                                    original_metric: str,
                                    inverse_metric: str,
                                    p1_suffix: str,
                                    p2_suffix: str) -> np.ndarray:
        """
        Transform inverse metric contributions back to original metric.
        
        Uses relative impact methodology:
        1. Calculate total change in inverse metric
        2. Calculate total change in original metric
        3. For each campaign: (Inverse Contribution / Total Inverse Change) × Total Original Change
        
        Args:
            inverse_contributions: Contributions calculated for inverse metric
            total_row: Total row with original metric values
            original_metric: Original metric name (e.g., "ACoS")
            inverse_metric: Inverse metric name (e.g., "ROAS")
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Array of contributions for original metric in basis points
        """
        # Get total changes
        # For inverse metric (calculated values)
        inverse_formula = get_metric_formula(inverse_metric)
        total_inverse_p1 = inverse_formula.calculate(
            total_row[f"{inverse_formula.numerator} - {p1_suffix}"].iloc[0],
            total_row[f"{inverse_formula.denominator} - {p1_suffix}"].iloc[0]
        )
        total_inverse_p2 = inverse_formula.calculate(
            total_row[f"{inverse_formula.numerator} - {p2_suffix}"].iloc[0],
            total_row[f"{inverse_formula.denominator} - {p2_suffix}"].iloc[0]
        )
        total_inverse_change = total_inverse_p2 - total_inverse_p1
        
        # For original metric (from data)
        total_original_p1 = total_row[f"{original_metric} - {p1_suffix}"].iloc[0]
        total_original_p2 = total_row[f"{original_metric} - {p2_suffix}"].iloc[0]
        total_original_change = total_original_p2 - total_original_p1
        
        logger.debug(
            f"Total {inverse_metric} change: {total_inverse_change:.4f}, "
            f"Total {original_metric} change: {total_original_change:.4f}"
        )
        
        # Handle case where there's no inverse change
        if abs(total_inverse_change) < 1e-10:
            logger.info(f"No {inverse_metric} change detected, {original_metric} contributions will be zero")
            return np.zeros(len(inverse_contributions))
        
        # Handle infinity in original metric change
        if np.isinf(total_original_change):
            logger.warning(f"{original_metric} has infinite change, contributions set to zero")
            return np.zeros(len(inverse_contributions))
        
        # Transform each contribution
        original_contributions = np.zeros(len(inverse_contributions))
        
        for i, inverse_contrib in enumerate(inverse_contributions):
            # Calculate relative impact as percentage of total inverse change
            relative_impact = inverse_contrib / total_inverse_change
            
            # Apply to total original change
            original_contrib = relative_impact * total_original_change
            
            # Convert to basis points if configured
            if self.config.requires_percentage_conversion:
                original_contrib *= 100  # Convert percentage points to basis points
            
            original_contributions[i] = original_contrib
            
            logger.debug(
                f"Campaign {i}: {inverse_metric} contrib={inverse_contrib:.4f}, "
                f"Relative impact={relative_impact:.4f}, "
                f"{original_metric} contrib={original_contrib:.2f} bps"
            )
        
        # Validate transformation
        total_transformed = original_contributions.sum()
        expected_total = total_original_change * (100 if self.config.requires_percentage_conversion else 1)
        
        logger.info(
            f"{original_metric} contributions transformed: total={total_transformed:.2f} bps "
            f"(expected: {expected_total:.2f} bps)"
        )
        
        return original_contributions
    
    def generate_metadata(self,
                         campaign_data: pd.DataFrame,
                         total_row: pd.DataFrame,
                         metric: str,
                         contributions: np.ndarray,
                         p1_suffix: str,
                         p2_suffix: str) -> Dict[str, Any]:
        """
        Generate metadata specific to MixRate Infinity calculations.
        """
        # Get base metadata
        metadata = super().generate_metadata(
            campaign_data, total_row, metric, contributions, p1_suffix, p2_suffix
        )
        
        # Add infinity-specific metadata
        metadata["inverse_methodology"] = {
            "original_metric": metric,
            "inverse_metric": self.config.inverse_metric,
            "transformation_method": "relative_impact"
        }
        
        # Calculate inverse metric values and changes
        inverse_formula = get_metric_formula(self.config.inverse_metric)
        if inverse_formula:
            total_inverse_p1 = inverse_formula.calculate(
                total_row[f"{inverse_formula.numerator} - {p1_suffix}"].iloc[0],
                total_row[f"{inverse_formula.denominator} - {p1_suffix}"].iloc[0]
            )
            total_inverse_p2 = inverse_formula.calculate(
                total_row[f"{inverse_formula.numerator} - {p2_suffix}"].iloc[0],
                total_row[f"{inverse_formula.denominator} - {p2_suffix}"].iloc[0]
            )
            
            metadata["inverse_metric_analysis"] = {
                "p1_value": float(total_inverse_p1),
                "p2_value": float(total_inverse_p2),
                "change": float(total_inverse_p2 - total_inverse_p1)
            }
        
        return metadata