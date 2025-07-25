"""
KPI to Bridge Type mappings for the MixBridge v2 system.

This module defines which bridge calculation type should be used for each KPI,
along with all necessary configuration for proper calculation and display.
"""

from typing import Dict, List
from ..models.bridge_types import BridgeConfiguration, BridgeType, ContributionUnit, MetricFormula


# Define formulas for calculated metrics
METRIC_FORMULAS: Dict[str, MetricFormula] = {
    # Rate metrics with percentage display
    "ACoS": MetricFormula(
        numerator="Spend",
        denominator="Total Ad Sales",
        is_percentage=True
    ),
    "CTR": MetricFormula(
        numerator="Clicks", 
        denominator="Impressions",
        is_percentage=True
    ),
    "Conversion Rate": MetricFormula(
        numerator="Total Ad Orders",
        denominator="Clicks", 
        is_percentage=True
    ),
    "Buy Box %": MetricFormula(
        numerator="Buy Box",
        denominator="Page Views",
        is_percentage=True
    ),
    
    # Rate metrics with currency/ratio display
    "ROAS": MetricFormula(
        numerator="Total Ad Sales",
        denominator="Spend"
    ),
    "CPC": MetricFormula(
        numerator="Spend",
        denominator="Clicks"
    ),
    "CPA": MetricFormula(
        numerator="Spend",
        denominator="Total Ad Orders"
    ),
    "Average Order Value": MetricFormula(
        numerator="Total Ad Sales",
        denominator="Total Ad Orders"
    ),
    "Total ROAS": MetricFormula(
        numerator="Total OPS",
        denominator="Spend"
    ),
    "Total ACoS": MetricFormula(
        numerator="Spend",
        denominator="Total OPS",
        is_percentage=True
    ),
    
    # Calculated absolute metrics
    "ASP": MetricFormula(
        numerator="OPS",
        denominator="Units"
    ),
    "Unit Session %": MetricFormula(  # Alias for Conversion Rate
        numerator="Units",
        denominator="Sessions",
        is_percentage=True
    ),
    "Ad ConvR": MetricFormula(
        numerator="Orders",
        denominator="Clicks",
        is_percentage=True
    )
}


# KPI to Bridge Configuration mappings
KPI_BRIDGE_MAPPINGS: Dict[str, BridgeConfiguration] = {
    # Type 1: Traditional Mix Bridge (absolute metrics)
    "OPS": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Spend": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Units": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Sessions": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Page Views": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Ad Spend": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Ad Sales": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Total Ad Sales": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Impressions": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Clicks": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Same SKU Ad Sales": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Other SKU Ad Sales": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Other SKU Sales": BridgeConfiguration(  # Alternative name
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Ad Orders": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Total Ad Orders": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Same SKU Ad Orders": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    "Other SKU Ad Orders": BridgeConfiguration(
        bridge_type=BridgeType.MIX_BRIDGE,
        contribution_unit=ContributionUnit.COUNT
    ),
    
    # Type 2: Standard MixRate Bridge
    "ASP": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Units",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Conversion Rate": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Sessions",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    ),
    "Unit Session %": BridgeConfiguration(  # Alias for Conversion Rate
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Sessions", 
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    ),
    "Buy Box %": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Page Views",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    ),
    "ROAS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Spend",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Ad ConvR": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Clicks",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    ),
    "CTR": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Impressions",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        requires_percentage_conversion=True
    ),
    "CPC": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Clicks",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "CPA": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Total Ad Orders",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Average Order Value": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Total Ad Orders",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    "Total ROAS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_BRIDGE,
        mix_determinant="Spend",
        contribution_unit=ContributionUnit.CURRENCY
    ),
    
    # Type 3: MixRate Bridge with Infinity Error handling
    "ACoS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_INFINITY,
        mix_determinant="Spend",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        inverse_metric="ROAS",
        requires_percentage_conversion=True
    ),
    "Total ACoS": BridgeConfiguration(
        bridge_type=BridgeType.MIXRATE_INFINITY,
        mix_determinant="Spend",
        contribution_unit=ContributionUnit.BASIS_POINTS,
        inverse_metric="Total ROAS",
        requires_percentage_conversion=True
    )
}


def get_bridge_configuration(metric: str) -> BridgeConfiguration:
    """
    Get the bridge configuration for a specific metric.
    
    Args:
        metric: The metric name
        
    Returns:
        BridgeConfiguration for the metric
        
    Raises:
        KeyError: If metric is not found in mappings
    """
    if metric not in KPI_BRIDGE_MAPPINGS:
        raise KeyError(f"No bridge configuration found for metric: {metric}")
    return KPI_BRIDGE_MAPPINGS[metric]


def get_metrics_by_bridge_type(bridge_type: BridgeType) -> List[str]:
    """
    Get all metrics that use a specific bridge type.
    
    Args:
        bridge_type: The bridge type to filter by
        
    Returns:
        List of metric names using that bridge type
    """
    return [
        metric for metric, config in KPI_BRIDGE_MAPPINGS.items()
        if config.bridge_type == bridge_type
    ]


def get_metric_formula(metric: str) -> MetricFormula:
    """
    Get the calculation formula for a metric.
    
    Args:
        metric: The metric name
        
    Returns:
        MetricFormula if the metric is calculated, None if it's a base metric
    """
    return METRIC_FORMULAS.get(metric)


def is_calculated_metric(metric: str) -> bool:
    """
    Check if a metric is calculated from other metrics.
    
    Args:
        metric: The metric name
        
    Returns:
        True if the metric has a formula, False if it's a base metric
    """
    return metric in METRIC_FORMULAS