"""
Abstract base class for all bridge calculators.
Defines the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from ...models.bridge_types import BridgeConfiguration, ContributionUnit
from ...common.logger import get_logger

logger = get_logger(__name__)


class BaseBridgeCalculator(ABC):
    """
    Abstract base class for bridge calculators.
    
    All bridge calculators must inherit from this class and implement
    the abstract methods for calculating contributions.
    """
    
    def __init__(self, configuration: BridgeConfiguration, precision: int = 12):
        """
        Initialize the bridge calculator.
        
        Args:
            configuration: Bridge configuration for this calculator
            precision: Decimal precision for calculations
        """
        self.config = configuration
        self.precision = precision
        logger.info(f"Initialized {self.__class__.__name__} with {configuration.bridge_type.name}")
    
    @abstractmethod
    def calculate_contributions(self, 
                              campaign_data: pd.DataFrame,
                              total_row: pd.DataFrame,
                              metric: str,
                              p1_suffix: str = "January 2025",
                              p2_suffix: str = "February 2025") -> np.ndarray:
        """
        Calculate contributions for a specific metric.
        
        This is the main method that each bridge type must implement.
        
        Args:
            campaign_data: DataFrame with campaign-level data
            total_row: DataFrame with total/aggregate values
            metric: The metric name to calculate contributions for
            p1_suffix: Period 1 column suffix
            p2_suffix: Period 2 column suffix
            
        Returns:
            Array of contribution values for each campaign
        """
        pass
    
    def validate_inputs(self, 
                       campaign_data: pd.DataFrame,
                       total_row: pd.DataFrame,
                       metric: str,
                       p1_suffix: str,
                       p2_suffix: str) -> bool:
        """
        Validate inputs before calculation.
        
        Args:
            campaign_data: Campaign data DataFrame
            total_row: Total row DataFrame
            metric: Metric name
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Check required columns exist
        p1_col = f"{metric} - {p1_suffix}"
        p2_col = f"{metric} - {p2_suffix}"
        
        for col in [p1_col, p2_col]:
            if col not in campaign_data.columns:
                raise ValueError(f"Missing column in campaign data: {col}")
            if col not in total_row.columns:
                raise ValueError(f"Missing column in total row: {col}")
        
        # Check total row structure
        if len(total_row) != 1:
            raise ValueError("Total row must contain exactly one row")
        
        # Check for negative values in absolute metrics
        if self.config.bridge_type.name == "MIX_BRIDGE":
            for col in [p1_col, p2_col]:
                if (campaign_data[col] < 0).any():
                    logger.warning(f"Negative values found in {col}")
        
        return True
    
    def format_contributions(self, contributions: np.ndarray) -> List[str]:
        """
        Format contribution values according to the contribution unit.
        
        Args:
            contributions: Array of contribution values
            
        Returns:
            List of formatted contribution strings
        """
        unit = self.config.contribution_unit
        
        if unit == ContributionUnit.CURRENCY:
            # Format as currency with +/- sign
            return [f"{'+' if c >= 0 else ''}{c:,.2f}" for c in contributions]
        
        elif unit == ContributionUnit.BASIS_POINTS:
            # Format as basis points
            return [f"{'+' if c >= 0 else ''}{c:,.0f} bps" for c in contributions]
        
        elif unit == ContributionUnit.PERCENTAGE:
            # Format as percentage
            return [f"{'+' if c >= 0 else ''}{c:,.2f}%" for c in contributions]
        
        elif unit == ContributionUnit.COUNT:
            # Format as integer count
            return [f"{'+' if c >= 0 else ''}{int(c):,}" for c in contributions]
        
        elif unit == ContributionUnit.RATIO:
            # Format as decimal ratio
            return [f"{'+' if c >= 0 else ''}{c:,.4f}" for c in contributions]
        
        else:
            # Default formatting
            return [f"{c:,.4f}" for c in contributions]
    
    def calculate_and_validate(self,
                              campaign_data: pd.DataFrame,
                              total_row: pd.DataFrame,
                              metric: str,
                              p1_suffix: str = "January 2025",
                              p2_suffix: str = "February 2025") -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calculate contributions with validation and metadata.
        
        Args:
            campaign_data: Campaign data DataFrame
            total_row: Total row DataFrame  
            metric: Metric name
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Tuple of (contributions array, metadata dict)
        """
        # Validate inputs
        self.validate_inputs(campaign_data, total_row, metric, p1_suffix, p2_suffix)
        
        # Calculate contributions
        contributions = self.calculate_contributions(
            campaign_data, total_row, metric, p1_suffix, p2_suffix
        )
        
        # Generate metadata
        metadata = self.generate_metadata(
            campaign_data, total_row, metric, contributions, p1_suffix, p2_suffix
        )
        
        # Validate results
        self.validate_results(contributions, metadata)
        
        return contributions, metadata
    
    def generate_metadata(self,
                         campaign_data: pd.DataFrame,
                         total_row: pd.DataFrame,
                         metric: str,
                         contributions: np.ndarray,
                         p1_suffix: str,
                         p2_suffix: str) -> Dict[str, Any]:
        """
        Generate metadata about the calculation.
        
        Args:
            campaign_data: Campaign data
            total_row: Total row
            metric: Metric name
            contributions: Calculated contributions
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Dictionary with calculation metadata
        """
        p1_col = f"{metric} - {p1_suffix}"
        p2_col = f"{metric} - {p2_suffix}"
        
        # Calculate totals and changes
        total_p1 = total_row[p1_col].iloc[0]
        total_p2 = total_row[p2_col].iloc[0]
        total_change = total_p2 - total_p1
        
        # Sum contributions
        total_contributions = contributions.sum()
        
        metadata = {
            "metric": metric,
            "bridge_type": self.config.bridge_type.name,
            "contribution_unit": self.config.contribution_unit.name,
            "period_1": p1_suffix,
            "period_2": p2_suffix,
            "total_p1_value": float(total_p1),
            "total_p2_value": float(total_p2),
            "total_change": float(total_change),
            "total_contributions": float(total_contributions),
            "contribution_count": len(contributions),
            "mathematical_consistency": abs(total_contributions - total_change) < 0.01
        }
        
        # Add bridge-specific metadata
        if self.config.mix_determinant:
            metadata["mix_determinant"] = self.config.mix_determinant
        if self.config.inverse_metric:
            metadata["inverse_metric"] = self.config.inverse_metric
        
        return metadata
    
    def validate_results(self, contributions: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """
        Validate calculation results.
        
        Args:
            contributions: Calculated contributions
            metadata: Calculation metadata
            
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Check for NaN or infinite values
        if np.any(np.isnan(contributions)):
            raise ValueError("Contributions contain NaN values")
        if np.any(np.isinf(contributions)):
            raise ValueError("Contributions contain infinite values")
        
        # Log warning if mathematical consistency is off
        if not metadata.get("mathematical_consistency", True):
            logger.warning(
                f"Mathematical consistency check failed for {metadata['metric']}: "
                f"Total contributions ({metadata['total_contributions']:.4f}) != "
                f"Total change ({metadata['total_change']:.4f})"
            )
        
        return True