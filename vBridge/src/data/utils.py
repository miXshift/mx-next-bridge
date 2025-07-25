"""
Shared calculation utilities for MixBridge analysis.
Contains common mathematical operations and helper functions.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Tuple
import warnings

try:
    from ..config.constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
    from ..common.exceptions import CalculationError
    from ..common.logger import get_logger
except ImportError:
    # Backwards compatibility during migration
    try:
        from .constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
        from .exceptions import CalculationError
        from .logger import get_logger
    except ImportError:
        from constants import BASIS_POINTS_MULTIPLIER, ZERO_TOLERANCE
        from exceptions import CalculationError
        from logger import get_logger


logger = get_logger(__name__)


def safe_divide(
    numerator: Union[float, pd.Series, np.ndarray], 
    denominator: Union[float, pd.Series, np.ndarray],
    fill_value: float = 0.0,
    handle_inf: bool = True
) -> Union[float, pd.Series, np.ndarray]:
    """
    Perform safe division with zero and infinity handling.
    
    Args:
        numerator: Numerator values
        denominator: Denominator values
        fill_value: Value to use when denominator is zero
        handle_inf: Whether to replace infinite values with fill_value
        
    Returns:
        Division result with safe handling of edge cases
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        
        # Handle division by zero
        if isinstance(denominator, (pd.Series, np.ndarray)):
            result = np.divide(numerator, denominator, out=np.full_like(numerator, fill_value, dtype=float), where=denominator!=0)
        else:
            if abs(denominator) < ZERO_TOLERANCE:
                return fill_value
            result = numerator / denominator
        
        # Handle infinity values
        if handle_inf and isinstance(result, (pd.Series, np.ndarray)):
            result = np.where(np.isinf(result), fill_value, result)
        elif handle_inf and np.isinf(result):
            result = fill_value
            
        return result


def calculate_percentage_change(
    baseline: Union[float, pd.Series], 
    actual: Union[float, pd.Series],
    handle_zero_baseline: str = 'zero'
) -> Union[float, pd.Series]:
    """
    Calculate percentage change with zero baseline handling.
    
    Args:
        baseline: Baseline values
        actual: Actual values
        handle_zero_baseline: How to handle zero baseline ('zero', 'skip', 'error')
        
    Returns:
        Percentage change values
        
    Raises:
        CalculationError: If handle_zero_baseline='error' and zero baseline found
    """
    if handle_zero_baseline == 'error':
        if isinstance(baseline, (pd.Series, np.ndarray)):
            if (baseline == 0).any():
                raise CalculationError("Zero baseline values found")
        elif baseline == 0:
            raise CalculationError("Zero baseline value found")
    
    if handle_zero_baseline == 'skip':
        if isinstance(baseline, (pd.Series, np.ndarray)):
            mask = baseline != 0
            result = pd.Series(index=baseline.index, dtype=float)
            result[mask] = ((actual[mask] - baseline[mask]) / baseline[mask]) * 100
            result[~mask] = np.nan
            return result
        else:
            if baseline == 0:
                return np.nan
    
    # Default: return 0 for zero baseline
    return safe_divide(actual - baseline, baseline) * 100


def calculate_contribution_bps(
    campaign_baseline: Union[float, pd.Series],
    campaign_actual: Union[float, pd.Series], 
    total_baseline: float
) -> Union[float, pd.Series]:
    """
    Calculate contribution in basis points using standard Mix Bridge formula.
    
    Args:
        campaign_baseline: Campaign baseline values
        campaign_actual: Campaign actual values
        total_baseline: Total baseline value
        
    Returns:
        Contribution values in basis points
    """
    # Standard Mix Bridge calculation: (actual - baseline) / total_baseline * 10000
    return safe_divide(
        campaign_actual - campaign_baseline, 
        total_baseline,
        fill_value=0.0
    ) * BASIS_POINTS_MULTIPLIER


def calculate_rate_metric(
    numerator: Union[float, pd.Series],
    denominator: Union[float, pd.Series],
    as_percentage: bool = True,
    precision: int = 4
) -> Union[float, pd.Series]:
    """
    Calculate rate metrics (CTR, CVR, etc.) with proper formatting.
    
    Args:
        numerator: Numerator values (e.g., clicks, conversions)
        denominator: Denominator values (e.g., impressions, clicks)
        as_percentage: Whether to return as percentage (multiply by 100)
        precision: Decimal places to round to
        
    Returns:
        Calculated rate metric
    """
    rate = safe_divide(numerator, denominator, fill_value=0.0)
    
    if as_percentage:
        rate = rate * 100
    
    if isinstance(rate, (pd.Series, np.ndarray)):
        return np.round(rate, precision)
    else:
        return round(rate, precision)


def aggregate_weighted_metrics(
    values: pd.Series,
    weights: pd.Series,
    metric_type: str = 'rate'
) -> float:
    """
    Aggregate metrics with proper weighting.
    
    Args:
        values: Metric values to aggregate
        weights: Weight values for aggregation
        metric_type: Type of metric ('rate', 'absolute', 'average')
        
    Returns:
        Aggregated metric value
    """
    if len(values) == 0 or len(weights) == 0:
        return 0.0
    
    if metric_type == 'absolute':
        # For absolute metrics, just sum
        return values.sum()
    elif metric_type == 'rate':
        # For rate metrics, use weighted average
        total_weight = weights.sum()
        if total_weight == 0:
            return 0.0
        return (values * weights).sum() / total_weight
    elif metric_type == 'average':
        # Simple average
        return values.mean()
    else:
        logger.warning(f"Unknown metric_type '{metric_type}', using simple average")
        return values.mean()


def validate_calculation_inputs(
    baseline: Union[float, pd.Series],
    actual: Union[float, pd.Series],
    allow_negative: bool = True,
    check_consistency: bool = True
) -> Tuple[bool, str]:
    """
    Validate inputs for calculations.
    
    Args:
        baseline: Baseline values
        actual: Actual values
        allow_negative: Whether negative values are allowed
        check_consistency: Whether to check data consistency
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for NaN values
    if isinstance(baseline, (pd.Series, np.ndarray)):
        if baseline.isna().any():
            return False, "Baseline contains NaN values"
        if actual.isna().any():
            return False, "Actual contains NaN values"
    else:
        if pd.isna(baseline) or pd.isna(actual):
            return False, "Input contains NaN values"
    
    # Check for negative values if not allowed
    if not allow_negative:
        if isinstance(baseline, (pd.Series, np.ndarray)):
            if (baseline < 0).any() or (actual < 0).any():
                return False, "Negative values not allowed"
        else:
            if baseline < 0 or actual < 0:
                return False, "Negative values not allowed"
    
    # Check data consistency
    if check_consistency:
        if isinstance(baseline, (pd.Series, np.ndarray)):
            if len(baseline) != len(actual):
                return False, "Baseline and actual have different lengths"
    
    return True, ""


def format_metric_value(
    value: Union[float, int],
    metric_name: str,
    precision: int = 2
) -> str:
    """
    Format metric value for display based on metric type.
    
    Args:
        value: Value to format
        metric_name: Name of the metric
        precision: Decimal precision
        
    Returns:
        Formatted string representation
    """
    if pd.isna(value):
        return "N/A"
    
    # Percentage metrics
    if metric_name.lower() in ['acos', 'ctr', 'conversion rate', 'cvr']:
        return f"{value:.{precision}f}%"
    
    # Currency metrics
    elif metric_name.lower() in ['spend', 'sales', 'cpc'] or 'sales' in metric_name.lower():
        return f"${value:,.{precision}f}"
    
    # Count metrics
    elif metric_name.lower() in ['impressions', 'clicks', 'orders'] or 'orders' in metric_name.lower():
        return f"{value:,.0f}"
    
    # Ratio metrics
    elif metric_name.lower() in ['roas']:
        return f"{value:.{precision}f}x"
    
    # Default formatting
    else:
        return f"{value:.{precision}f}"


def detect_calculation_anomalies(
    values: pd.Series,
    metric_name: str,
    threshold_multiplier: float = 3.0
) -> pd.Series:
    """
    Detect anomalous values in calculations.
    
    Args:
        values: Values to check
        metric_name: Name of the metric
        threshold_multiplier: Z-score threshold for anomaly detection
        
    Returns:
        Boolean series indicating anomalies
    """
    if len(values) < 3:  # Need at least 3 values for meaningful statistics
        return pd.Series([False] * len(values), index=values.index)
    
    # Calculate z-scores
    mean_val = values.mean()
    std_val = values.std()
    
    if std_val == 0:  # All values are the same
        return pd.Series([False] * len(values), index=values.index)
    
    z_scores = np.abs((values - mean_val) / std_val)
    anomalies = z_scores > threshold_multiplier
    
    if anomalies.any():
        logger.warning(f"Detected {anomalies.sum()} anomalies in {metric_name}")
    
    return anomalies