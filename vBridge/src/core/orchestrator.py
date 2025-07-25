"""
Bridge Orchestrator - Central controller for bridge calculations.

This module automatically selects and applies the correct bridge calculator
based on metric configuration, handling all three bridge types seamlessly.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from ..models.bridge_types import BridgeType, BridgeConfiguration
from ..config.bridge_mappings import get_bridge_configuration, get_metrics_by_bridge_type
from .bridges import (
    MixBridgeCalculator,
    MixRateBridgeCalculator, 
    MixRateInfinityCalculator
)
from ..common.logger import get_logger
from ..common.exceptions import CalculationError, ValidationError

logger = get_logger(__name__)


class BridgeOrchestrator:
    """
    Orchestrates bridge calculations across all metrics.
    
    This class is the main entry point for bridge calculations. It:
    1. Determines which bridge type to use for each metric
    2. Instantiates the appropriate calculator
    3. Manages the calculation process
    4. Aggregates results and metadata
    """
    
    def __init__(self, precision: int = 12):
        """
        Initialize the Bridge Orchestrator.
        
        Args:
            precision: Decimal precision for calculations
        """
        self.precision = precision
        self.calculators = {}
        self._initialize_calculators()
        logger.info("BridgeOrchestrator initialized")
    
    def _initialize_calculators(self):
        """Initialize calculator instances for each bridge type."""
        # Create a calculator instance for each unique configuration
        # This allows reuse and better performance
        self.calculator_cache = {}
    
    def get_calculator(self, configuration: BridgeConfiguration):
        """
        Get or create a calculator for the given configuration.
        
        Args:
            configuration: Bridge configuration
            
        Returns:
            Appropriate bridge calculator instance
        """
        # Create a cache key from configuration
        cache_key = (
            configuration.bridge_type,
            configuration.mix_determinant,
            configuration.inverse_metric
        )
        
        # Check cache
        if cache_key in self.calculator_cache:
            return self.calculator_cache[cache_key]
        
        # Create new calculator
        if configuration.bridge_type == BridgeType.MIX_BRIDGE:
            calculator = MixBridgeCalculator(configuration, self.precision)
        elif configuration.bridge_type == BridgeType.MIXRATE_BRIDGE:
            calculator = MixRateBridgeCalculator(configuration, self.precision)
        elif configuration.bridge_type == BridgeType.MIXRATE_INFINITY:
            calculator = MixRateInfinityCalculator(configuration, self.precision)
        else:
            raise ValueError(f"Unknown bridge type: {configuration.bridge_type}")
        
        # Cache and return
        self.calculator_cache[cache_key] = calculator
        return calculator
    
    def calculate_all_metrics(self,
                            campaign_data: pd.DataFrame,
                            total_row: pd.DataFrame,
                            metrics: Optional[List[str]] = None,
                            p1_suffix: str = "January 2025",
                            p2_suffix: str = "February 2025") -> Dict[str, Any]:
        """
        Calculate contributions for all specified metrics.
        
        Args:
            campaign_data: Campaign-level data
            total_row: Total row with aggregate values
            metrics: List of metrics to calculate (None for all)
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Dictionary with results and metadata
        """
        # Get metrics to calculate
        if metrics is None:
            # Get all configured metrics
            from ..config.bridge_mappings import KPI_BRIDGE_MAPPINGS
            metrics = list(KPI_BRIDGE_MAPPINGS.keys())
        
        results = {
            "contributions": {},
            "metadata": {},
            "summary": {}
        }
        
        # Group metrics by bridge type for efficient processing
        metrics_by_type = self._group_metrics_by_type(metrics)
        
        # Process each bridge type
        for bridge_type, metric_list in metrics_by_type.items():
            logger.info(f"Processing {len(metric_list)} metrics with {bridge_type.name}")
            
            for metric in metric_list:
                try:
                    # Calculate contributions for this metric
                    metric_results = self.calculate_metric(
                        campaign_data, total_row, metric, p1_suffix, p2_suffix
                    )
                    
                    # Store results
                    results["contributions"][metric] = metric_results["contributions"]
                    results["metadata"][metric] = metric_results["metadata"]
                    
                except Exception as e:
                    logger.error(f"Failed to calculate {metric}: {str(e)}")
                    # Store error information
                    results["contributions"][metric] = np.zeros(len(campaign_data))
                    results["metadata"][metric] = {
                        "error": str(e),
                        "bridge_type": bridge_type.name if 'bridge_type' in locals() else "UNKNOWN"
                    }
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def calculate_metric(self,
                       campaign_data: pd.DataFrame,
                       total_row: pd.DataFrame,
                       metric: str,
                       p1_suffix: str = "January 2025",
                       p2_suffix: str = "February 2025") -> Dict[str, Any]:
        """
        Calculate contributions for a single metric.
        
        Args:
            campaign_data: Campaign-level data
            total_row: Total row with aggregate values
            metric: Metric name
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Dictionary with contributions and metadata
        """
        try:
            # Get configuration for this metric
            configuration = get_bridge_configuration(metric)
            
            # Get appropriate calculator
            calculator = self.get_calculator(configuration)
            
            # Calculate contributions with validation
            contributions, metadata = calculator.calculate_and_validate(
                campaign_data, total_row, metric, p1_suffix, p2_suffix
            )
            
            # Format contributions
            formatted_contributions = calculator.format_contributions(contributions)
            
            return {
                "contributions": contributions,
                "formatted_contributions": formatted_contributions,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate {metric}: {str(e)}")
            # Return error result
            zero_contributions = np.zeros(len(campaign_data))
            return {
                "contributions": zero_contributions,
                "formatted_contributions": ["0.0"] * len(campaign_data),
                "metadata": {
                    "error": str(e),
                    "metric": metric,
                    "bridge_type": "UNKNOWN"
                }
            }
    
    def apply_to_dataframe(self,
                         output_df: pd.DataFrame,
                         total_row: pd.DataFrame,
                         metrics: Optional[List[str]] = None,
                         p1_suffix: str = "January 2025",
                         p2_suffix: str = "February 2025") -> pd.DataFrame:
        """
        Apply bridge calculations directly to an output dataframe.
        
        This method updates the contribution columns in the provided dataframe.
        
        Args:
            output_df: Output dataframe to update
            total_row: Total row with aggregate values
            metrics: List of metrics to calculate (None for all)
            p1_suffix: Period 1 suffix
            p2_suffix: Period 2 suffix
            
        Returns:
            Updated output dataframe
        """
        # Calculate all metrics
        results = self.calculate_all_metrics(
            output_df, total_row, metrics, p1_suffix, p2_suffix
        )
        
        # Apply contributions to dataframe
        for metric, contributions in results["contributions"].items():
            contribution_col = f"{metric} - Contribution"
            if contribution_col in output_df.columns:
                output_df[contribution_col] = contributions
            else:
                logger.warning(f"Column {contribution_col} not found in output dataframe")
        
        # Log summary
        successful = sum(1 for m in results["metadata"].values() if "error" not in m)
        total = len(results["metadata"])
        logger.info(f"Applied contributions for {successful}/{total} metrics")
        
        return output_df
    
    def _group_metrics_by_type(self, metrics: List[str]) -> Dict[BridgeType, List[str]]:
        """Group metrics by their bridge type for efficient processing."""
        grouped = {}
        
        for metric in metrics:
            try:
                config = get_bridge_configuration(metric)
                bridge_type = config.bridge_type
                
                if bridge_type not in grouped:
                    grouped[bridge_type] = []
                grouped[bridge_type].append(metric)
                
            except KeyError:
                logger.warning(f"No configuration found for metric: {metric}")
        
        return grouped
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the calculation results."""
        summary = {
            "total_metrics": len(results["contributions"]),
            "successful_calculations": 0,
            "failed_calculations": 0,
            "metrics_by_type": {},
            "consistency_check": {}
        }
        
        # Count successes and failures
        for metric, metadata in results["metadata"].items():
            if "error" in metadata:
                summary["failed_calculations"] += 1
            else:
                summary["successful_calculations"] += 1
                
                # Group by bridge type
                bridge_type = metadata.get("bridge_type", "UNKNOWN")
                if bridge_type not in summary["metrics_by_type"]:
                    summary["metrics_by_type"][bridge_type] = []
                summary["metrics_by_type"][bridge_type].append(metric)
                
                # Check mathematical consistency
                if metadata.get("mathematical_consistency", False):
                    summary["consistency_check"][metric] = "PASS"
                else:
                    summary["consistency_check"][metric] = "FAIL"
        
        # Calculate success rate
        if summary["total_metrics"] > 0:
            summary["success_rate"] = (
                summary["successful_calculations"] / summary["total_metrics"] * 100
            )
        else:
            summary["success_rate"] = 0.0
        
        return summary
    
    def validate_all_contributions(self,
                                 output_df: pd.DataFrame,
                                 total_row: pd.DataFrame,
                                 tolerance: float = 0.01) -> Dict[str, bool]:
        """
        Validate that contributions sum correctly for all metrics.
        
        Args:
            output_df: Output dataframe with contributions
            total_row: Total row
            tolerance: Tolerance for mathematical consistency
            
        Returns:
            Dictionary mapping metrics to validation results
        """
        validation_results = {}
        
        from ..config.bridge_mappings import KPI_BRIDGE_MAPPINGS
        
        for metric in KPI_BRIDGE_MAPPINGS.keys():
            contribution_col = f"{metric} - Contribution"
            
            if contribution_col not in output_df.columns:
                validation_results[metric] = False
                continue
            
            # Sum campaign contributions
            campaign_sum = output_df[contribution_col].sum()
            
            # Get total contribution
            if contribution_col in total_row.columns:
                total_contribution = total_row[contribution_col].iloc[0]
            else:
                total_contribution = 0
            
            # Check consistency
            difference = abs(campaign_sum - total_contribution)
            validation_results[metric] = difference < tolerance
            
            if not validation_results[metric]:
                logger.warning(
                    f"{metric} validation failed: Campaign sum={campaign_sum:.4f}, "
                    f"Total={total_contribution:.4f}, Difference={difference:.4f}"
                )
        
        return validation_results