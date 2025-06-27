"""
Improved Bridge Calculations Module
Implements mathematically robust bridge analysis with proper edge case handling
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BridgeCalculationUtils:
    """Utility functions for robust bridge calculations"""
    
    @staticmethod
    def safe_divide(numerator: Union[float, np.ndarray, pd.Series], 
                   denominator: Union[float, np.ndarray, pd.Series], 
                   default: float = 0.0,
                   epsilon: float = 1e-10) -> Union[float, np.ndarray, pd.Series]:
        """
        Safely divide with zero/near-zero handling
        
        Args:
            numerator: The numerator value(s)
            denominator: The denominator value(s)
            default: Default value when denominator is zero/near-zero
            epsilon: Threshold for near-zero detection
            
        Returns:
            Result of division or default value
        """
        if isinstance(denominator, (pd.Series, np.ndarray)):
            mask = np.abs(denominator) > epsilon
            result = pd.Series(default, index=denominator.index if isinstance(denominator, pd.Series) else None)
            if mask.any():
                result[mask] = numerator[mask] / denominator[mask]
            return result
        else:
            if abs(denominator) <= epsilon:
                return default
            return numerator / denominator
    
    @staticmethod
    def to_basis_points(value: Union[float, np.ndarray, pd.Series], 
                       is_already_percentage: bool = False) -> Union[float, np.ndarray, pd.Series]:
        """
        Convert value to basis points with clear logic
        
        Args:
            value: The value to convert
            is_already_percentage: If True, value is already in percentage form (e.g., 0.01 = 1%)
            
        Returns:
            Value in basis points
        """
        if is_already_percentage:
            return value * 100  # 0.01 (1%) -> 100 BPS
        else:
            return value * 10000  # 0.01 (raw) -> 100 BPS
    
    @staticmethod
    def validate_data_alignment(p1_data: pd.DataFrame, p2_data: pd.DataFrame) -> pd.Index:
        """
        Validate and align data between periods
        
        Returns:
            Union index of all campaigns across both periods
        """
        all_campaigns = p1_data.index.union(p2_data.index)
        
        # Log new and discontinued campaigns
        new_campaigns = p2_data.index.difference(p1_data.index)
        discontinued_campaigns = p1_data.index.difference(p2_data.index)
        
        if len(new_campaigns) > 0:
            logger.info(f"New campaigns in P2: {len(new_campaigns)}")
        if len(discontinued_campaigns) > 0:
            logger.info(f"Discontinued campaigns from P1: {len(discontinued_campaigns)}")
            
        return all_campaigns


class ImprovedMixBridgeCalculator:
    """
    Implements improved Mix Bridge calculation with proper volume/mix decomposition
    """
    
    def __init__(self, utils: BridgeCalculationUtils = None):
        self.utils = utils or BridgeCalculationUtils()
    
    def calculate_mix_bridge(self, 
                           p1_values: pd.Series,
                           p2_values: pd.Series,
                           p1_total: float,
                           p2_total: float,
                           metric_name: str = "metric") -> pd.DataFrame:
        """
        Calculate Mix Bridge with volume and mix effects decomposition
        
        Args:
            p1_values: Period 1 values by campaign
            p2_values: Period 2 values by campaign
            p1_total: Period 1 total
            p2_total: Period 2 total
            metric_name: Name of the metric for logging
            
        Returns:
            DataFrame with columns: Volume Effect, Mix Effect, Total Contribution (all in BPS)
        """
        # Align data
        all_campaigns = self.utils.validate_data_alignment(
            p1_values.to_frame(), p2_values.to_frame()
        )
        
        # Reindex with zeros for missing campaigns
        p1_aligned = p1_values.reindex(all_campaigns, fill_value=0)
        p2_aligned = p2_values.reindex(all_campaigns, fill_value=0)
        
        # Calculate shares (handle zero totals)
        p1_share = self.utils.safe_divide(p1_aligned, p1_total, default=0)
        p2_share = self.utils.safe_divide(p2_aligned, p2_total, default=0)
        
        # Volume Effect: How much did the total market change, applied to P1 share
        volume_effect = (p2_total - p1_total) * p1_share
        
        # Mix Effect: How much did this campaign's share change, applied to P2 total
        mix_effect = (p2_share - p1_share) * p2_total
        
        # Total contribution
        total_contribution = volume_effect + mix_effect
        
        # Convert to basis points (relative to P1 total)
        volume_effect_bps = self.utils.safe_divide(volume_effect, p1_total, default=0) * 10000
        mix_effect_bps = self.utils.safe_divide(mix_effect, p1_total, default=0) * 10000
        total_contribution_bps = self.utils.safe_divide(total_contribution, p1_total, default=0) * 10000
        
        # Validate the decomposition
        expected_total_change_bps = self.utils.safe_divide(p2_total - p1_total, p1_total, default=0) * 10000
        
        # Handle the case where total_contribution_bps might be a scalar
        if isinstance(total_contribution_bps, pd.Series):
            actual_total_bps = total_contribution_bps.sum()
        else:
            actual_total_bps = total_contribution_bps
        
        if not np.isclose(actual_total_bps, expected_total_change_bps, rtol=0.001):
            logger.warning(
                f"{metric_name}: Contribution sum ({actual_total_bps:.2f} BPS) "
                f"!= expected change ({expected_total_change_bps:.2f} BPS)"
            )
        
        # Create result DataFrame
        result = pd.DataFrame({
            'Volume Effect (BPS)': volume_effect_bps,
            'Mix Effect (BPS)': mix_effect_bps,
            'Total Contribution (BPS)': total_contribution_bps,
            'P1 Value': p1_aligned,
            'P2 Value': p2_aligned,
            'P1 Share': p1_share,
            'P2 Share': p2_share
        }, index=all_campaigns)
        
        return result


class ImprovedMixRateCalculator:
    """
    Implements improved Mix/Rate calculation with numerical stability
    """
    
    def __init__(self, utils: BridgeCalculationUtils = None):
        self.utils = utils or BridgeCalculationUtils()
    
    def calculate_mix_rate_contribution(self,
                                      p1_kpi_values: pd.Series,
                                      p2_kpi_values: pd.Series,
                                      p1_mix_driver: pd.Series,
                                      p2_mix_driver: pd.Series,
                                      kpi_name: str,
                                      is_percentage_metric: bool = False) -> pd.DataFrame:
        """
        Calculate Mix/Rate contributions with improved numerical stability
        
        Args:
            p1_kpi_values: Period 1 KPI values by campaign
            p2_kpi_values: Period 2 KPI values by campaign
            p1_mix_driver: Period 1 mix driver values (e.g., impressions for CTR)
            p2_mix_driver: Period 2 mix driver values
            kpi_name: Name of the KPI
            is_percentage_metric: Whether the KPI is a percentage metric
            
        Returns:
            DataFrame with Mix Impact, Rate Impact, and Total Contribution
        """
        # Align all data
        all_campaigns = self.utils.validate_data_alignment(
            p1_kpi_values.to_frame(), p2_kpi_values.to_frame()
        )
        
        # Reindex all series
        p1_kpi = p1_kpi_values.reindex(all_campaigns, fill_value=0)
        p2_kpi = p2_kpi_values.reindex(all_campaigns, fill_value=0)
        p1_driver = p1_mix_driver.reindex(all_campaigns, fill_value=0)
        p2_driver = p2_mix_driver.reindex(all_campaigns, fill_value=0)
        
        # Calculate mix shares with safe division
        p1_total_driver = p1_driver.sum()
        p2_total_driver = p2_driver.sum()
        
        p1_mix = self.utils.safe_divide(p1_driver, p1_total_driver, default=0)
        p2_mix = self.utils.safe_divide(p2_driver, p2_total_driver, default=0)
        
        # Calculate weighted average KPI for P2
        p2_weighted_kpi = self._calculate_weighted_kpi(p2_kpi, p2_driver, kpi_name)
        
        # Mix Impact: Change in mix share × (Campaign KPI - Overall KPI)
        mix_impact = (p2_mix - p1_mix) * (p2_kpi - p2_weighted_kpi)
        
        # Rate Impact: Change in KPI × P1 mix share
        rate_impact = (p2_kpi - p1_kpi) * p1_mix
        
        # Total contribution
        total_contribution = mix_impact + rate_impact
        
        # Convert to basis points if percentage metric
        if is_percentage_metric:
            mix_impact = self.utils.to_basis_points(mix_impact, is_already_percentage=True)
            rate_impact = self.utils.to_basis_points(rate_impact, is_already_percentage=True)
            total_contribution = self.utils.to_basis_points(total_contribution, is_already_percentage=True)
        
        # Handle special cases
        result = pd.DataFrame({
            'Mix Impact': mix_impact,
            'Rate Impact': rate_impact,
            'Total Contribution': total_contribution,
            'P1 KPI': p1_kpi,
            'P2 KPI': p2_kpi,
            'P1 Mix Share': p1_mix,
            'P2 Mix Share': p2_mix
        }, index=all_campaigns)
        
        # Flag campaigns with edge cases
        result['Is New Campaign'] = ~result.index.isin(p1_kpi_values.index)
        result['Is Discontinued'] = ~result.index.isin(p2_kpi_values.index)
        result['Has Zero Driver'] = (p1_driver == 0) | (p2_driver == 0)
        
        return result
    
    def _calculate_weighted_kpi(self, kpi_values: pd.Series, weights: pd.Series, kpi_name: str) -> float:
        """
        Calculate weighted average KPI with proper handling
        
        Args:
            kpi_values: KPI values by campaign
            weights: Weight values (mix driver)
            kpi_name: Name of KPI for logging
            
        Returns:
            Weighted average KPI value
        """
        total_weight = weights.sum()
        
        if total_weight == 0 or np.isclose(total_weight, 0):
            logger.warning(f"{kpi_name}: Total weight is zero, returning simple average")
            return kpi_values.mean() if len(kpi_values) > 0 else 0
        
        # For ratio KPIs, we need to sum numerators and denominators separately
        # This is a simplified version - in practice, you'd need the original components
        weighted_avg = (kpi_values * weights).sum() / total_weight
        
        return weighted_avg


class ImprovedInfinityHandler:
    """
    Handles infinity values in ACoS/ROAS with context awareness
    """
    
    def __init__(self, utils: BridgeCalculationUtils = None):
        self.utils = utils or BridgeCalculationUtils()
    
    def handle_acos_roas_infinity(self,
                                 contributions: pd.Series,
                                 p1_spend: pd.Series,
                                 p2_spend: pd.Series,
                                 p1_sales: pd.Series,
                                 p2_sales: pd.Series,
                                 metric_type: str = 'ACoS') -> pd.DataFrame:
        """
        Handle infinity values with context-aware logic
        
        Args:
            contributions: Original contribution values
            p1_spend: Period 1 spend by campaign
            p2_spend: Period 2 spend by campaign
            p1_sales: Period 1 sales by campaign
            p2_sales: Period 2 sales by campaign
            metric_type: 'ACoS' or 'ROAS'
            
        Returns:
            DataFrame with handled contributions and flags
        """
        # Align all data
        all_campaigns = contributions.index
        
        # Create masks for different scenarios
        p1_zero_sales = (p1_sales == 0) | np.isclose(p1_sales, 0)
        p2_zero_sales = (p2_sales == 0) | np.isclose(p2_sales, 0)
        p1_zero_spend = (p1_spend == 0) | np.isclose(p1_spend, 0)
        p2_zero_spend = (p2_spend == 0) | np.isclose(p2_spend, 0)
        
        # Initialize handled contributions
        handled_contributions = contributions.copy()
        flags = pd.DataFrame(index=all_campaigns)
        
        if metric_type == 'ACoS':
            # ACoS = Spend / Sales (infinity when sales = 0)
            
            # Case 1: P1 has sales, P2 has no sales (ACoS goes to infinity)
            mask1 = ~p1_zero_sales & p2_zero_sales & ~p2_zero_spend
            handled_contributions[mask1] = 10000  # Large positive contribution
            flags.loc[mask1, 'Flag'] = 'P2_Sales_Zero'
            
            # Case 2: P1 has no sales, P2 has sales (ACoS comes down from infinity)
            mask2 = p1_zero_sales & ~p2_zero_sales & ~p1_zero_spend
            handled_contributions[mask2] = -10000  # Large negative contribution
            flags.loc[mask2, 'Flag'] = 'P1_Sales_Zero'
            
            # Case 3: Both periods have no sales
            mask3 = p1_zero_sales & p2_zero_sales
            handled_contributions[mask3] = 0
            flags.loc[mask3, 'Flag'] = 'Both_Sales_Zero'
            
        else:  # ROAS
            # ROAS = Sales / Spend (infinity when spend = 0)
            
            # Case 1: P1 has spend, P2 has no spend (ROAS goes to infinity if sales > 0)
            mask1 = ~p1_zero_spend & p2_zero_spend & (p2_sales > 0)
            handled_contributions[mask1] = 10000  # Large positive contribution
            flags.loc[mask1, 'Flag'] = 'P2_Spend_Zero_With_Sales'
            
            # Case 2: P1 has no spend, P2 has spend (ROAS comes down from infinity)
            mask2 = p1_zero_spend & ~p2_zero_spend & (p1_sales > 0)
            handled_contributions[mask2] = -10000  # Large negative contribution
            flags.loc[mask2, 'Flag'] = 'P1_Spend_Zero_With_Sales'
            
            # Case 3: No spend in either period
            mask3 = p1_zero_spend & p2_zero_spend
            handled_contributions[mask3] = 0
            flags.loc[mask3, 'Flag'] = 'Both_Spend_Zero'
        
        # Replace any remaining infinity/NaN values
        handled_contributions = handled_contributions.replace([np.inf, -np.inf], 0)
        handled_contributions = handled_contributions.fillna(0)
        
        # Create result DataFrame
        result = pd.DataFrame({
            'Original Contribution': contributions,
            'Handled Contribution': handled_contributions,
            'P1 Spend': p1_spend,
            'P2 Spend': p2_spend,
            'P1 Sales': p1_sales,
            'P2 Sales': p2_sales
        }, index=all_campaigns)
        
        # Add flags
        result = result.join(flags)
        
        # Log summary of handling
        if 'Flag' in flags.columns:
            flag_counts = flags['Flag'].value_counts()
            logger.info(f"{metric_type} infinity handling summary:\n{flag_counts}")
        
        return result


class BridgeValidation:
    """Validation functions for bridge calculations"""
    
    @staticmethod
    def validate_contribution_sum(contributions: pd.Series,
                                expected_total_change: float,
                                metric_name: str,
                                tolerance: float = 0.01) -> bool:
        """
        Validate that contributions sum to the expected total change
        
        Args:
            contributions: Series of contribution values
            expected_total_change: Expected total change
            metric_name: Name of metric for logging
            tolerance: Relative tolerance for validation
            
        Returns:
            True if validation passes
        """
        actual_sum = contributions.sum()
        
        if expected_total_change == 0:
            is_valid = np.isclose(actual_sum, 0, atol=1e-10)
        else:
            relative_diff = abs(actual_sum - expected_total_change) / abs(expected_total_change)
            is_valid = relative_diff <= tolerance
        
        if not is_valid:
            logger.warning(
                f"{metric_name}: Contribution sum validation failed. "
                f"Sum={actual_sum:.2f}, Expected={expected_total_change:.2f}, "
                f"Diff={actual_sum - expected_total_change:.2f}"
            )
        
        return is_valid
    
    @staticmethod
    def validate_mix_rate_decomposition(mix_impact: pd.Series,
                                      rate_impact: pd.Series,
                                      total_contribution: pd.Series,
                                      metric_name: str) -> bool:
        """
        Validate that mix + rate = total for all campaigns
        
        Returns:
            True if all validations pass
        """
        calculated_total = mix_impact + rate_impact
        diff = abs(calculated_total - total_contribution)
        
        # Check if all differences are small
        max_diff = diff.max()
        problem_campaigns = diff[diff > 1e-10].index.tolist()
        
        if len(problem_campaigns) > 0:
            logger.warning(
                f"{metric_name}: Mix+Rate != Total for {len(problem_campaigns)} campaigns. "
                f"Max difference: {max_diff:.6f}"
            )
            return False
        
        return True


# Example usage function
def example_usage():
    """Example of how to use the improved bridge calculators"""
    
    # Initialize calculators
    utils = BridgeCalculationUtils()
    mix_bridge_calc = ImprovedMixBridgeCalculator(utils)
    mix_rate_calc = ImprovedMixRateCalculator(utils)
    infinity_handler = ImprovedInfinityHandler(utils)
    validator = BridgeValidation()
    
    # Example data
    p1_data = pd.Series({'Campaign A': 1000, 'Campaign B': 2000, 'Campaign C': 500})
    p2_data = pd.Series({'Campaign A': 1200, 'Campaign B': 1800, 'Campaign D': 300})
    
    # Calculate Mix Bridge
    mix_bridge_result = mix_bridge_calc.calculate_mix_bridge(
        p1_values=p1_data,
        p2_values=p2_data,
        p1_total=p1_data.sum(),
        p2_total=p2_data.sum(),
        metric_name="Spend"
    )
    
    print("Mix Bridge Results:")
    print(mix_bridge_result)
    
    # Validate
    is_valid = validator.validate_contribution_sum(
        contributions=mix_bridge_result['Total Contribution (BPS)'],
        expected_total_change=(p2_data.sum() - p1_data.sum()) / p1_data.sum() * 10000,
        metric_name="Spend"
    )
    print(f"Validation passed: {is_valid}")


if __name__ == "__main__":
    example_usage()