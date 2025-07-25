"""
Standard MixRate Bridge calculator implementation.

Used for rate metrics like ROAS, CTR, CPC, Conversion Rate, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base import BaseBridgeCalculator
from ...models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit
from ...common.logger import get_logger

logger = get_logger(__name__)


class MixRateBridgeCalculator(BaseBridgeCalculator):
    """
    Standard MixRate Bridge calculator for rate metrics.
    
    Formula:
    - Mix Impact = (P2 Mix - P1 Mix) × (P2 Rate - P2 Total Rate)
    - Rate Impact = (P2 Rate - P1 Rate) × P1 Mix
    - Total Contribution = Mix Impact + Rate Impact
    
    The mix is determined by a specific denominator (e.g., Spend for ROAS,
    Clicks for Conversion Rate, Impressions for CTR).
    
    Contributions are shown in the appropriate unit (currency or basis points).
    """
    
    def __init__(self, configuration: BridgeConfiguration, precision: int = 12):
        """Initialize MixRate Bridge calculator."""
        if configuration.bridge_type != BridgeType.MIXRATE_BRIDGE:
            raise ValueError(f"Invalid bridge type for MixRateBridgeCalculator: {configuration.bridge_type}")
        if not configuration.mix_determinant:
            raise ValueError("MixRate Bridge requires a mix_determinant")
        super().__init__(configuration, precision)
    
    def calculate_contributions(self,
                              campaign_data: pd.DataFrame,
                              total_row: pd.DataFrame,
                              metric: str,
                              p1_suffix: str = "January 2025",
                              p2_suffix: str = "February 2025") -> np.ndarray:
        """
        Calculate MixRate Bridge contributions for rate metrics.
        
        Args:
            campaign_data: Campaign-level data
            total_row: Total row with aggregate values
            metric: Metric name (e.g., "ROAS", "CTR")
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Array of contribution values
        """
        # Get column names
        metric_p1_col = f"{metric} - {p1_suffix}"
        metric_p2_col = f"{metric} - {p2_suffix}"
        mix_p1_col = f"{self.config.mix_determinant} - {p1_suffix}"
        mix_p2_col = f"{self.config.mix_determinant} - {p2_suffix}"
        
        # Get total values
        total_mix_p1 = total_row[mix_p1_col].iloc[0]
        total_mix_p2 = total_row[mix_p2_col].iloc[0]
        total_metric_p1 = total_row[metric_p1_col].iloc[0]
        total_metric_p2 = total_row[metric_p2_col].iloc[0]
        
        # Initialize contributions array
        contributions = np.zeros(len(campaign_data))
        
        # Handle case where total mix determinant is zero
        if total_mix_p1 == 0:
            logger.warning(
                f"Total {self.config.mix_determinant} for {p1_suffix} is zero, "
                f"cannot calculate {metric} contributions"
            )
            return contributions
        
        # Calculate contributions for each campaign
        for i, row in campaign_data.iterrows():
            # Get campaign values
            campaign_mix_p1 = row[mix_p1_col]
            campaign_mix_p2 = row[mix_p2_col]
            campaign_metric_p1 = row[metric_p1_col]
            campaign_metric_p2 = row[metric_p2_col]
            
            # Calculate mix percentages
            p1_mix = campaign_mix_p1 / total_mix_p1 if total_mix_p1 > 0 else 0
            p2_mix = campaign_mix_p2 / total_mix_p2 if total_mix_p2 > 0 else 0
            
            # Calculate MixRate Bridge components
            # Mix Impact: (P2 Mix - P1 Mix) × (P2 Rate - P2 Total Rate)
            mix_impact = (p2_mix - p1_mix) * (campaign_metric_p2 - total_metric_p2)
            
            # Rate Impact: (P2 Rate - P1 Rate) × P1 Mix
            rate_impact = (campaign_metric_p2 - campaign_metric_p1) * p1_mix
            
            # Total contribution
            contribution = mix_impact + rate_impact
            
            # Apply percentage conversion if needed (for basis points)
            if self.config.requires_percentage_conversion:
                contribution *= 10000  # Convert to basis points
            
            contributions[i] = contribution
            
            logger.debug(
                f"Campaign {i} {metric}: Mix Impact={mix_impact:.4f}, "
                f"Rate Impact={rate_impact:.4f}, Total={contribution:.4f}"
            )
        
        # Log summary
        total_contribution = contributions.sum()
        logger.info(
            f"{metric} MixRate Bridge: Total contribution={total_contribution:.4f} "
            f"({self.config.contribution_unit.name})"
        )
        
        return contributions
    
    def validate_inputs(self,
                       campaign_data: pd.DataFrame,
                       total_row: pd.DataFrame,
                       metric: str,
                       p1_suffix: str,
                       p2_suffix: str) -> bool:
        """
        Validate inputs for MixRate Bridge calculation.
        
        Extends base validation to check mix determinant columns.
        """
        # Base validation
        super().validate_inputs(campaign_data, total_row, metric, p1_suffix, p2_suffix)
        
        # Check mix determinant columns
        mix_p1_col = f"{self.config.mix_determinant} - {p1_suffix}"
        mix_p2_col = f"{self.config.mix_determinant} - {p2_suffix}"
        
        for col in [mix_p1_col, mix_p2_col]:
            if col not in campaign_data.columns:
                raise ValueError(f"Missing mix determinant column in campaign data: {col}")
            if col not in total_row.columns:
                raise ValueError(f"Missing mix determinant column in total row: {col}")
        
        # Check for negative mix determinant values
        if (campaign_data[mix_p1_col] < 0).any() or (campaign_data[mix_p2_col] < 0).any():
            logger.warning(f"Negative values found in mix determinant {self.config.mix_determinant}")
        
        return True
    
    def generate_metadata(self,
                         campaign_data: pd.DataFrame,
                         total_row: pd.DataFrame,
                         metric: str,
                         contributions: np.ndarray,
                         p1_suffix: str,
                         p2_suffix: str) -> Dict[str, Any]:
        """
        Generate metadata specific to MixRate Bridge calculations.
        """
        # Get base metadata
        metadata = super().generate_metadata(
            campaign_data, total_row, metric, contributions, p1_suffix, p2_suffix
        )
        
        # Add MixRate specific metadata
        mix_p1_col = f"{self.config.mix_determinant} - {p1_suffix}"
        mix_p2_col = f"{self.config.mix_determinant} - {p2_suffix}"
        
        # Mix determinant totals
        metadata["mix_determinant_totals"] = {
            "p1": float(total_row[mix_p1_col].iloc[0]),
            "p2": float(total_row[mix_p2_col].iloc[0])
        }
        
        # Calculate mix and rate impact breakdowns
        mix_impacts = []
        rate_impacts = []
        
        total_mix_p1 = total_row[mix_p1_col].iloc[0]
        total_mix_p2 = total_row[mix_p2_col].iloc[0]
        total_metric_p2 = total_row[f"{metric} - {p2_suffix}"].iloc[0]
        
        for i, row in campaign_data.iterrows():
            if total_mix_p1 > 0:
                p1_mix = row[mix_p1_col] / total_mix_p1
                p2_mix = row[mix_p2_col] / total_mix_p2 if total_mix_p2 > 0 else 0
                
                campaign_metric_p1 = row[f"{metric} - {p1_suffix}"]
                campaign_metric_p2 = row[f"{metric} - {p2_suffix}"]
                
                mix_impact = (p2_mix - p1_mix) * (campaign_metric_p2 - total_metric_p2)
                rate_impact = (campaign_metric_p2 - campaign_metric_p1) * p1_mix
                
                if self.config.requires_percentage_conversion:
                    mix_impact *= 10000
                    rate_impact *= 10000
                
                mix_impacts.append(mix_impact)
                rate_impacts.append(rate_impact)
        
        if mix_impacts:
            metadata["impact_breakdown"] = {
                "total_mix_impact": float(sum(mix_impacts)),
                "total_rate_impact": float(sum(rate_impacts)),
                "mix_contribution_pct": float(sum(mix_impacts) / contributions.sum() * 100) if contributions.sum() != 0 else 0,
                "rate_contribution_pct": float(sum(rate_impacts) / contributions.sum() * 100) if contributions.sum() != 0 else 0
            }
        
        return metadata