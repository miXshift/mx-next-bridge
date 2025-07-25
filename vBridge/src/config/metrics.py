"""
Centralized metric definitions and utilities for MixBridge calculations.
"""

from typing import Dict, List, Set
try:
    from .constants import VOLUME_METRICS, RATE_METRICS, COST_METRICS
except ImportError:
    from constants import VOLUME_METRICS, RATE_METRICS, COST_METRICS


class MetricDefinitions:
    """Centralized metric definitions and category management."""
    
    @staticmethod
    def get_absolute_metrics() -> List[str]:
        """
        Get list of absolute (summable) metrics that use traditional Mix Bridge.
        
        Returns:
            List of metric names that can be summed across campaigns
        """
        return [
            'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
            'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
            'Other SKU Ad Orders', 'Total Ad Orders'
        ]
    
    @staticmethod
    def get_mixrate_infinity_metrics() -> List[str]:
        """
        Get list of rate metrics that use MixRate Bridge with Infinity Error handling.
        
        These metrics can produce infinity errors when denominators are zero,
        so they use inverse methodology (e.g., ACoS calculated via ROAS inverse).
        
        Returns:
            List of metric names using MixRate Bridge with Infinity Error handling
        """
        return ['ACoS']
    
    @staticmethod
    def get_mixrate_standard_metrics() -> List[str]:
        """
        Get list of rate metrics that use standard MixRate Bridge.
        
        These metrics use MixRate Bridge methodology but don't have infinity error issues.
        
        Returns:
            List of metric names using standard MixRate Bridge
        """
        return ['ROAS', 'Conversion Rate', 'CTR', 'CPC']
    
    @staticmethod
    def get_rate_metrics() -> List[str]:
        """
        Get list of all rate/ratio metrics.
        
        Returns:
            List of all metric names that are calculated as ratios
        """
        return (MetricDefinitions.get_mixrate_infinity_metrics() + 
                MetricDefinitions.get_mixrate_standard_metrics())
    
    @staticmethod
    def get_all_metrics() -> List[str]:
        """
        Get complete list of all metrics.
        
        Returns:
            List of all metric names
        """
        return MetricDefinitions.get_absolute_metrics() + MetricDefinitions.get_rate_metrics()
    
    @staticmethod
    def get_percentage_metrics() -> List[str]:
        """
        Get list of metrics that are expressed as percentages.
        
        Returns:
            List of metric names that use percentage format
        """
        return ['ACoS', 'CTR', 'Conversion Rate']
    
    @staticmethod
    def is_absolute_metric(metric: str) -> bool:
        """
        Check if a metric is an absolute (summable) metric.
        
        Args:
            metric: Metric name to check
            
        Returns:
            True if metric is absolute, False otherwise
        """
        return metric in MetricDefinitions.get_absolute_metrics()
    
    @staticmethod
    def is_rate_metric(metric: str) -> bool:
        """
        Check if a metric is a rate/ratio metric.
        
        Args:
            metric: Metric name to check
            
        Returns:
            True if metric is a rate, False otherwise
        """
        return metric in MetricDefinitions.get_rate_metrics()
    
    @staticmethod
    def is_mixrate_infinity_metric(metric: str) -> bool:
        """
        Check if a metric uses MixRate Bridge with Infinity Error handling.
        
        Args:
            metric: Metric name to check
            
        Returns:
            True if metric uses MixRate Bridge with Infinity Error handling
        """
        return metric in MetricDefinitions.get_mixrate_infinity_metrics()
    
    @staticmethod
    def is_mixrate_standard_metric(metric: str) -> bool:
        """
        Check if a metric uses standard MixRate Bridge.
        
        Args:
            metric: Metric name to check
            
        Returns:
            True if metric uses standard MixRate Bridge
        """
        return metric in MetricDefinitions.get_mixrate_standard_metrics()
    
    @staticmethod
    def is_percentage_metric(metric: str) -> bool:
        """
        Check if a metric is expressed as a percentage.
        
        Args:
            metric: Metric name to check
            
        Returns:
            True if metric uses percentage format, False otherwise
        """
        return metric in MetricDefinitions.get_percentage_metrics()
    
    @staticmethod
    def get_metric_category(metric: str) -> str:
        """
        Get the category of a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            Category name ('absolute', 'mixrate_infinity', 'mixrate_standard', 'unknown')
        """
        if MetricDefinitions.is_absolute_metric(metric):
            return 'absolute'
        elif MetricDefinitions.is_mixrate_infinity_metric(metric):
            return 'mixrate_infinity'
        elif MetricDefinitions.is_mixrate_standard_metric(metric):
            return 'mixrate_standard'
        else:
            return 'unknown'
    
    @staticmethod
    def get_calculation_methodology(metric: str) -> str:
        """
        Get the calculation methodology for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            Calculation methodology description
        """
        if MetricDefinitions.is_absolute_metric(metric):
            return 'Traditional Mix Bridge (summable values)'
        elif MetricDefinitions.is_mixrate_infinity_metric(metric):
            return 'MixRate Bridge with Infinity Error handling (inverse methodology)'
        elif MetricDefinitions.is_mixrate_standard_metric(metric):
            return 'Standard MixRate Bridge (direct rate calculations)'
        else:
            return 'Unknown methodology'
    
    @staticmethod
    def get_metrics_by_category() -> Dict[str, List[str]]:
        """
        Get metrics organized by category.
        
        Returns:
            Dictionary with categories as keys and metric lists as values
        """
        return {
            'absolute': MetricDefinitions.get_absolute_metrics(),
            'mixrate_infinity': MetricDefinitions.get_mixrate_infinity_metrics(),
            'mixrate_standard': MetricDefinitions.get_mixrate_standard_metrics(),
            'all_rate': MetricDefinitions.get_rate_metrics(),
            'percentage': MetricDefinitions.get_percentage_metrics()
        }
    
    @staticmethod
    def validate_metric(metric: str) -> bool:
        """
        Validate that a metric is recognized.
        
        Args:
            metric: Metric name to validate
            
        Returns:
            True if metric is valid, False otherwise
        """
        return metric in MetricDefinitions.get_all_metrics()
    
    @staticmethod
    def get_metric_display_unit(metric: str) -> str:
        """
        Get the display unit for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            Display unit string
        """
        if metric in ['Spend', 'Total Ad Sales', 'Same SKU Ad Sales', 'Other SKU Sales', 'CPC']:
            return '$'
        elif metric in ['ACoS', 'CTR', 'Conversion Rate']:
            return '%'
        elif metric in ['Impressions', 'Clicks', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders']:
            return 'count'
        elif metric == 'ROAS':
            return 'ratio'
        else:
            return ''
    
    @staticmethod
    def should_format_as_percentage(metric: str) -> bool:
        """
        Check if metric should be formatted as percentage in output.
        
        Args:
            metric: Metric name
            
        Returns:
            True if should format as percentage
        """
        return metric in MetricDefinitions.get_percentage_metrics()


# Convenience functions for backward compatibility
def get_metric_list() -> List[str]:
    """Get complete metric list - backward compatibility function."""
    return MetricDefinitions.get_all_metrics()


def get_absolute_metrics() -> List[str]:
    """Get absolute metrics list - backward compatibility function."""
    return MetricDefinitions.get_absolute_metrics()


def get_rate_metrics() -> List[str]:
    """Get rate metrics list - backward compatibility function."""
    return MetricDefinitions.get_rate_metrics()