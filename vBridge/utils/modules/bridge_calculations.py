"""
Mix Bridge calculation module.
Handles the 5 analytic points for each KPI with configurable zero baseline handling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from .config import AnalysisConfig, ABSOLUTE_METRICS, RATE_METRICS

class BridgeCalculator:
    """
    Calculator for Mix Bridge analytics.
    
    The 5 analytic points for each KPI:
    1. P1 Mix - Percentage of total in period 1
    2. Mix Rate - Growth rate between periods
    3. Contribution - Mix * Growth * Scale
    4. Delta - Change in absolute value (P2 - P1)
    5. Impact - Contribution to total change
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize calculator with configuration."""
        self.config = config or AnalysisConfig()
        
    def calculate_p1_mix(self, campaign_value: float, total_value: float) -> float:
        """
        Calculate P1 Mix percentage.
        
        Args:
            campaign_value: Value for specific campaign in P1
            total_value: Total value across all campaigns in P1
            
        Returns:
            Mix percentage (0-1 scale)
        """
        if total_value == 0:
            return 0.0
        return campaign_value / total_value
    
    def calculate_mix_rate(self, p1_value: float, p2_value: float, 
                          metric_name: Optional[str] = None) -> float:
        """
        Calculate growth rate between periods with zero baseline handling.
        
        Args:
            p1_value: Period 1 value
            p2_value: Period 2 value
            metric_name: Name of metric (for determining if rate metric)
            
        Returns:
            Growth rate
        """
        # Handle zero baseline based on configuration
        if p1_value == 0 and self.config.zero_baseline.enabled:
            if self.config.zero_baseline.strategy == "dummy_value":
                p1_value = self.config.zero_baseline.dummy_value
            elif self.config.zero_baseline.strategy == "skip":
                return 0.0
            elif self.config.zero_baseline.strategy == "zero":
                return 0.0 if p2_value == 0 else float('inf')
        
        if p1_value == 0:
            return 0.0
            
        # For rate metrics, use different calculation
        if metric_name and metric_name in RATE_METRICS:
            return (p2_value - p1_value) / 100  # Convert percentage point change
        else:
            return (p2_value - p1_value) / p1_value
    
    def calculate_contribution(self, p1_mix: float, mix_rate: float, 
                             scale: Optional[float] = None) -> float:
        """
        Calculate contribution (Mix * Growth * Scale).
        
        Args:
            p1_mix: P1 Mix value
            mix_rate: Growth rate
            scale: Scale factor (defaults to config value)
            
        Returns:
            Contribution value
        """
        if scale is None:
            scale = self.config.zero_baseline.dummy_value if hasattr(self.config, 'contribution_scale') else 10000
        
        return p1_mix * mix_rate * scale
    
    def calculate_delta(self, p1_value: float, p2_value: float) -> float:
        """
        Calculate absolute change between periods.
        
        Args:
            p1_value: Period 1 value
            p2_value: Period 2 value
            
        Returns:
            Delta (P2 - P1)
        """
        return p2_value - p1_value
    
    def calculate_impact(self, contribution: float, total_contribution: float) -> float:
        """
        Calculate impact as percentage of total contribution.
        
        Args:
            contribution: Individual contribution
            total_contribution: Sum of all contributions
            
        Returns:
            Impact percentage (0-1 scale)
        """
        if total_contribution == 0:
            return 0.0
        return contribution / total_contribution
    
    def calculate_all_analytics(self, p1_campaign: float, p1_total: float,
                               p2_campaign: float, p2_total: float,
                               metric_name: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate all 5 analytic points for a campaign/metric combination.
        
        Args:
            p1_campaign: Campaign value in period 1
            p1_total: Total value in period 1
            p2_campaign: Campaign value in period 2
            p2_total: Total value in period 2
            metric_name: Name of the metric
            
        Returns:
            Dictionary with all 5 analytic values
        """
        # Calculate each analytic point
        p1_mix = self.calculate_p1_mix(p1_campaign, p1_total)
        mix_rate = self.calculate_mix_rate(p1_campaign, p2_campaign, metric_name)
        contribution = self.calculate_contribution(p1_mix, mix_rate)
        delta = self.calculate_delta(p1_campaign, p2_campaign)
        
        return {
            "p1_mix": p1_mix,
            "mix_rate": mix_rate,
            "contribution": contribution,
            "delta": delta,
            "impact": 0.0  # Will be calculated after all contributions are known
        }
    
    def process_dataframe(self, df: pd.DataFrame, 
                         p1_columns: Dict[str, str],
                         p2_columns: Dict[str, str],
                         campaign_column: str = "Campaign") -> pd.DataFrame:
        """
        Process a dataframe to calculate all Mix Bridge analytics.
        
        Args:
            df: Input dataframe with P1 and P2 data
            p1_columns: Mapping of metric names to P1 column names
            p2_columns: Mapping of metric names to P2 column names
            campaign_column: Name of campaign column
            
        Returns:
            DataFrame with all analytic calculations added
        """
        result_df = df.copy()
        
        # Calculate totals for each metric
        totals = {}
        for metric in p1_columns:
            totals[f"{metric}_p1_total"] = df[p1_columns[metric]].sum()
            totals[f"{metric}_p2_total"] = df[p2_columns[metric]].sum()
        
        # Calculate analytics for each metric
        for metric in p1_columns:
            p1_col = p1_columns[metric]
            p2_col = p2_columns[metric]
            
            # Initialize columns
            analytics_data = []
            
            # Calculate for each row
            for idx, row in df.iterrows():
                analytics = self.calculate_all_analytics(
                    row[p1_col],
                    totals[f"{metric}_p1_total"],
                    row[p2_col],
                    totals[f"{metric}_p2_total"],
                    metric
                )
                analytics_data.append(analytics)
            
            # Add columns to dataframe
            analytics_df = pd.DataFrame(analytics_data)
            
            # Calculate impact after getting all contributions
            total_contribution = analytics_df['contribution'].sum()
            analytics_df['impact'] = analytics_df['contribution'].apply(
                lambda x: self.calculate_impact(x, total_contribution)
            )
            
            # Add to result with metric prefix
            for col in analytics_df.columns:
                result_df[f"{metric}_{col}"] = analytics_df[col]
        
        return result_df
    
    def validate_calculations(self, df: pd.DataFrame, 
                            metrics: List[str],
                            tolerance: Optional[float] = None) -> Dict[str, bool]:
        """
        Validate that calculations are internally consistent.
        
        Args:
            df: DataFrame with calculated analytics
            metrics: List of metric names to validate
            tolerance: Comparison tolerance (defaults to config value)
            
        Returns:
            Dictionary of validation results
        """
        if tolerance is None:
            tolerance = self.config.comparison.tolerance
            
        validations = {}
        
        for metric in metrics:
            # Check that impacts sum to ~1.0
            impact_col = f"{metric}_impact"
            if impact_col in df.columns:
                impact_sum = df[impact_col].sum()
                validations[f"{metric}_impact_sum"] = abs(impact_sum - 1.0) < tolerance
            
            # Check that mix values sum to ~1.0
            mix_col = f"{metric}_p1_mix"
            if mix_col in df.columns:
                mix_sum = df[mix_col].sum()
                validations[f"{metric}_mix_sum"] = abs(mix_sum - 1.0) < tolerance
        
        return validations

def create_bridge_summary(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """
    Create a summary of Mix Bridge calculations.
    
    Args:
        df: DataFrame with Mix Bridge calculations
        metrics: List of metrics to summarize
        
    Returns:
        Summary DataFrame
    """
    summary_data = []
    
    for metric in metrics:
        # Get relevant columns
        contribution_col = f"{metric}_contribution"
        impact_col = f"{metric}_impact"
        delta_col = f"{metric}_delta"
        
        if all(col in df.columns for col in [contribution_col, impact_col, delta_col]):
            summary_data.append({
                "Metric": metric,
                "Total Contribution": df[contribution_col].sum(),
                "Total Delta": df[delta_col].sum(),
                "Max Impact Campaign": df.loc[df[impact_col].idxmax(), 'Campaign'] if 'Campaign' in df.columns else "N/A",
                "Max Impact %": df[impact_col].max() * 100
            })
    
    return pd.DataFrame(summary_data)