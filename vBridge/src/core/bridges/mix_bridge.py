"""
Traditional Mix Bridge calculator implementation.

Used for absolute/summable metrics like Spend, Units, Sessions, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import BaseBridgeCalculator
from ...models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit
from ...common.logger import get_logger

logger = get_logger(__name__)


class MixBridgeCalculator(BaseBridgeCalculator):
    """
    Traditional Mix Bridge calculator for absolute metrics.
    
    Formula:
    - P1 Mix = Campaign P1 Value / Total P1 Value
    - Growth Rate = (Campaign P2 Value / Campaign P1 Value) - 1
    - Contribution = P1 Mix × Growth Rate × Total P1 Value
    
    This is used for metrics that can be summed across campaigns,
    such as Spend, Units, Sales, Impressions, etc.
    """
    
    def __init__(self, configuration: BridgeConfiguration, precision: int = 12):
        """Initialize Mix Bridge calculator."""
        if configuration.bridge_type != BridgeType.MIX_BRIDGE:
            raise ValueError(f"Invalid bridge type for MixBridgeCalculator: {configuration.bridge_type}")
        super().__init__(configuration, precision)
    
    def calculate_contributions(self,
                              campaign_data: pd.DataFrame,
                              total_row: pd.DataFrame,
                              metric: str,
                              p1_suffix: str = "January 2025",
                              p2_suffix: str = "February 2025") -> np.ndarray:
        """
        Calculate Mix Bridge contributions for absolute metrics.
        
        Args:
            campaign_data: Campaign-level data
            total_row: Total row with aggregate values
            metric: Metric name
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Array of contribution values
        """
        # Get column names
        p1_col = f"{metric} - {p1_suffix}"
        p2_col = f"{metric} - {p2_suffix}"
        
        # Get total values
        total_p1 = total_row[p1_col].iloc[0]
        total_p2 = total_row[p2_col].iloc[0]
        
        # Initialize contributions array
        contributions = np.zeros(len(campaign_data))
        
        # Handle case where total P1 is zero
        if total_p1 == 0:
            logger.warning(f"Total {metric} for {p1_suffix} is zero, all contributions will be zero")
            return contributions
        
        # Calculate contributions for each campaign
        for i, row in campaign_data.iterrows():
            p1_value = row[p1_col]
            p2_value = row[p2_col]
            
            # Calculate P1 mix (campaign's share of total)
            p1_mix = p1_value / total_p1
            
            # Calculate growth rate and contribution
            if p1_value > 0:
                growth_rate = (p2_value / p1_value) - 1
                # Traditional formula: P1 Mix × Growth Rate × Total P1 Value
                contribution = p1_mix * growth_rate * total_p1
            else:
                # Handle zero baseline with delta assignment
                # When P1 is zero, assign the full P2 value as contribution
                growth_rate = float('inf') if p2_value > 0 else 0.0
                contribution = p2_value
            
            contributions[i] = contribution
            
            logger.debug(
                f"Campaign {i}: P1={p1_value:.2f}, P2={p2_value:.2f}, "
                f"Mix={p1_mix:.4f}, Growth={growth_rate}, "
                f"Contribution={contribution:.4f}"
            )
        
        # Log summary
        total_contribution = contributions.sum()
        expected_change = total_p2 - total_p1
        logger.info(
            f"{metric} Mix Bridge: Total contribution={total_contribution:.4f}, "
            f"Expected change={expected_change:.4f}, "
            f"Difference={abs(total_contribution - expected_change):.4f}"
        )
        
        return contributions
    
    def generate_metadata(self,
                         campaign_data: pd.DataFrame,
                         total_row: pd.DataFrame,
                         metric: str,
                         contributions: np.ndarray,
                         p1_suffix: str,
                         p2_suffix: str) -> Dict[str, Any]:
        """
        Generate metadata specific to Mix Bridge calculations.
        
        Extends base metadata with Mix Bridge specific information.
        """
        # Get base metadata
        metadata = super().generate_metadata(
            campaign_data, total_row, metric, contributions, p1_suffix, p2_suffix
        )
        
        # Add Mix Bridge specific metadata
        p1_col = f"{metric} - {p1_suffix}"
        p2_col = f"{metric} - {p2_suffix}"
        
        # Calculate mix statistics
        total_p1 = total_row[p1_col].iloc[0]
        if total_p1 > 0:
            p1_mixes = campaign_data[p1_col] / total_p1
            metadata["mix_statistics"] = {
                "min_mix": float(p1_mixes.min()),
                "max_mix": float(p1_mixes.max()),
                "mean_mix": float(p1_mixes.mean()),
                "std_mix": float(p1_mixes.std())
            }
        
        # Count zero baseline campaigns
        zero_baseline_count = (campaign_data[p1_col] == 0).sum()
        metadata["zero_baseline_campaigns"] = int(zero_baseline_count)
        
        # Growth rate statistics
        growth_rates = []
        for i, row in campaign_data.iterrows():
            p1_value = row[p1_col]
            p2_value = row[p2_col]
            if p1_value > 0:
                growth_rate = (p2_value / p1_value) - 1
                growth_rates.append(growth_rate)
        
        if growth_rates:
            metadata["growth_statistics"] = {
                "min_growth": float(np.min(growth_rates)),
                "max_growth": float(np.max(growth_rates)),
                "mean_growth": float(np.mean(growth_rates)),
                "positive_growth_count": sum(1 for g in growth_rates if g > 0),
                "negative_growth_count": sum(1 for g in growth_rates if g < 0)
            }
        
        return metadata