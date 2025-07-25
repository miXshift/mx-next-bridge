"""
Data comparison module for Mix Bridge analysis.
Provides utilities for comparing datasets and generating reports.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
from .config import AnalysisConfig

class ComparisonResult:
    """Container for comparison results."""
    
    def __init__(self):
        self.matches: List[Dict[str, Any]] = []
        self.mismatches: List[Dict[str, Any]] = []
        self.missing_in_expected: List[str] = []
        self.missing_in_actual: List[str] = []
        self.summary: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        
    def add_match(self, item: str, expected: Any, actual: Any, difference: float = 0.0):
        """Add a matching comparison."""
        self.matches.append({
            "item": item,
            "expected": expected,
            "actual": actual,
            "difference": difference,
            "relative_difference": self._calculate_relative_difference(expected, actual)
        })
        
    def add_mismatch(self, item: str, expected: Any, actual: Any, difference: float, threshold: float):
        """Add a mismatching comparison."""
        self.mismatches.append({
            "item": item,
            "expected": expected,
            "actual": actual,
            "difference": difference,
            "relative_difference": self._calculate_relative_difference(expected, actual),
            "threshold": threshold
        })
        
    def _calculate_relative_difference(self, expected: Any, actual: Any) -> float:
        """Calculate relative difference as percentage."""
        if expected == 0:
            return 0.0 if actual == 0 else float('inf')
        return abs((actual - expected) / expected) * 100
        
    def generate_summary(self):
        """Generate summary statistics."""
        total_comparisons = len(self.matches) + len(self.mismatches)
        
        self.summary = {
            "total_comparisons": total_comparisons,
            "matches": len(self.matches),
            "mismatches": len(self.mismatches),
            "missing_in_expected": len(self.missing_in_expected),
            "missing_in_actual": len(self.missing_in_actual),
            "match_rate": len(self.matches) / total_comparisons if total_comparisons > 0 else 0.0,
            "max_difference": max([abs(m["difference"]) for m in self.mismatches]) if self.mismatches else 0.0,
            "avg_difference": np.mean([abs(m["difference"]) for m in self.mismatches]) if self.mismatches else 0.0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        self.generate_summary()
        return {
            "matches": self.matches,
            "mismatches": self.mismatches,
            "missing_in_expected": self.missing_in_expected,
            "missing_in_actual": self.missing_in_actual,
            "summary": self.summary,
            "metadata": self.metadata
        }

def compare_campaign_names(df1: pd.DataFrame, 
                          df2: pd.DataFrame,
                          campaign_column: str = "Campaign") -> Tuple[List[str], List[str], List[str]]:
    """
    Compare campaign names between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        campaign_column: Name of campaign column
        
    Returns:
        Tuple of (common_campaigns, missing_in_df1, missing_in_df2)
    """
    if campaign_column not in df1.columns or campaign_column not in df2.columns:
        raise ValueError(f"Campaign column '{campaign_column}' not found in one or both DataFrames")
        
    campaigns1 = set(df1[campaign_column].unique())
    campaigns2 = set(df2[campaign_column].unique())
    
    common = list(campaigns1.intersection(campaigns2))
    missing_in_df1 = list(campaigns2 - campaigns1)
    missing_in_df2 = list(campaigns1 - campaigns2)
    
    return common, missing_in_df1, missing_in_df2

def compare_numeric_values(val1: Union[float, int], 
                          val2: Union[float, int],
                          tolerance: float = 0.0001,
                          relative: bool = False) -> bool:
    """
    Compare two numeric values with tolerance.
    
    Args:
        val1: First value
        val2: Second value
        tolerance: Tolerance for comparison
        relative: Whether to use relative tolerance
        
    Returns:
        True if values are within tolerance
    """
    if pd.isna(val1) and pd.isna(val2):
        return True
    if pd.isna(val1) or pd.isna(val2):
        return False
        
    if relative:
        if val1 == 0:
            return abs(val2) <= tolerance
        return abs((val2 - val1) / val1) <= tolerance
    else:
        return abs(val2 - val1) <= tolerance

def compare_dataframes(expected_df: pd.DataFrame,
                      actual_df: pd.DataFrame,
                      join_column: str = "Campaign",
                      metrics_to_compare: Optional[List[str]] = None,
                      tolerance: float = 0.0001,
                      config: Optional[AnalysisConfig] = None) -> ComparisonResult:
    """
    Compare two DataFrames comprehensively.
    
    Args:
        expected_df: Expected/baseline DataFrame
        actual_df: Actual/comparison DataFrame
        join_column: Column to join on
        metrics_to_compare: List of metric columns to compare
        tolerance: Comparison tolerance
        config: Analysis configuration
        
    Returns:
        ComparisonResult object
    """
    result = ComparisonResult()
    
    if config is None:
        config = AnalysisConfig()
        tolerance = config.comparison.tolerance
    
    # Compare campaign names
    common, missing_expected, missing_actual = compare_campaign_names(
        expected_df, actual_df, join_column
    )
    
    result.missing_in_expected = missing_expected
    result.missing_in_actual = missing_actual
    
    # Merge dataframes on common campaigns
    merged = pd.merge(
        expected_df[expected_df[join_column].isin(common)],
        actual_df[actual_df[join_column].isin(common)],
        on=join_column,
        suffixes=('_expected', '_actual')
    )
    
    # Determine metrics to compare
    if metrics_to_compare is None:
        # Find numeric columns that exist in both dataframes
        expected_numeric = set(expected_df.select_dtypes(include=[np.number]).columns)
        actual_numeric = set(actual_df.select_dtypes(include=[np.number]).columns)
        metrics_to_compare = list(expected_numeric.intersection(actual_numeric))
        if join_column in metrics_to_compare:
            metrics_to_compare.remove(join_column)
    
    # Compare each metric
    for metric in metrics_to_compare:
        expected_col = f"{metric}_expected"
        actual_col = f"{metric}_actual"
        
        if expected_col in merged.columns and actual_col in merged.columns:
            for _, row in merged.iterrows():
                campaign = row[join_column]
                expected_val = row[expected_col]
                actual_val = row[actual_col]
                
                if compare_numeric_values(expected_val, actual_val, tolerance):
                    result.add_match(
                        f"{campaign}_{metric}",
                        expected_val,
                        actual_val,
                        actual_val - expected_val
                    )
                else:
                    result.add_mismatch(
                        f"{campaign}_{metric}",
                        expected_val,
                        actual_val,
                        actual_val - expected_val,
                        tolerance
                    )
    
    # Add metadata
    result.metadata = {
        "expected_campaigns": len(expected_df),
        "actual_campaigns": len(actual_df),
        "common_campaigns": len(common),
        "metrics_compared": metrics_to_compare,
        "tolerance": tolerance
    }
    
    return result

def calculate_differences(df1: pd.DataFrame,
                         df2: pd.DataFrame,
                         metrics_list: List[str],
                         join_column: str = "Campaign") -> pd.DataFrame:
    """
    Calculate differences between two DataFrames for specified metrics.
    
    Args:
        df1: First DataFrame (baseline)
        df2: Second DataFrame (comparison)
        metrics_list: List of metrics to calculate differences for
        join_column: Column to join on
        
    Returns:
        DataFrame with difference calculations
    """
    # Merge dataframes
    merged = pd.merge(df1, df2, on=join_column, suffixes=('_df1', '_df2'), how='outer')
    
    # Calculate differences
    result = merged[[join_column]].copy()
    
    for metric in metrics_list:
        col1 = f"{metric}_df1"
        col2 = f"{metric}_df2"
        
        if col1 in merged.columns and col2 in merged.columns:
            # Fill NaN with 0 for calculation
            val1 = merged[col1].fillna(0)
            val2 = merged[col2].fillna(0)
            
            # Calculate absolute difference
            result[f"{metric}_diff"] = val2 - val1
            
            # Calculate relative difference
            result[f"{metric}_rel_diff"] = np.where(
                val1 != 0,
                (val2 - val1) / val1 * 100,
                np.where(val2 != 0, float('inf'), 0)
            )
            
            # Add original values for reference
            result[f"{metric}_baseline"] = val1
            result[f"{metric}_comparison"] = val2
    
    return result

def generate_comparison_summary(comparison_result: ComparisonResult,
                               output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Generate a detailed comparison summary.
    
    Args:
        comparison_result: ComparisonResult object
        output_path: Optional path to save summary as JSON
        
    Returns:
        Summary dictionary
    """
    summary_dict = comparison_result.to_dict()
    
    # Add additional insights
    if comparison_result.mismatches:
        # Find campaigns with most mismatches
        campaign_mismatch_counts = {}
        for mismatch in comparison_result.mismatches:
            campaign = mismatch["item"].split("_")[0]  # Extract campaign name
            campaign_mismatch_counts[campaign] = campaign_mismatch_counts.get(campaign, 0) + 1
        
        summary_dict["top_mismatch_campaigns"] = sorted(
            campaign_mismatch_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find metrics with most mismatches
        metric_mismatch_counts = {}
        for mismatch in comparison_result.mismatches:
            metric = "_".join(mismatch["item"].split("_")[1:])  # Extract metric name
            metric_mismatch_counts[metric] = metric_mismatch_counts.get(metric, 0) + 1
        
        summary_dict["top_mismatch_metrics"] = sorted(
            metric_mismatch_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(summary_dict, f, indent=2, default=str)
    
    return summary_dict

def export_comparison_to_csv(comparison_result: ComparisonResult,
                            output_path: Union[str, Path]) -> None:
    """
    Export comparison results to CSV format.
    
    Args:
        comparison_result: ComparisonResult object
        output_path: Path to output CSV file
    """
    # Create comprehensive DataFrame
    all_comparisons = []
    
    # Add matches
    for match in comparison_result.matches:
        all_comparisons.append({
            "Item": match["item"],
            "Status": "Match",
            "Expected": match["expected"],
            "Actual": match["actual"],
            "Difference": match["difference"],
            "Relative_Difference_%": match["relative_difference"],
            "Threshold": "N/A"
        })
    
    # Add mismatches
    for mismatch in comparison_result.mismatches:
        all_comparisons.append({
            "Item": mismatch["item"],
            "Status": "Mismatch",
            "Expected": mismatch["expected"],
            "Actual": mismatch["actual"],
            "Difference": mismatch["difference"],
            "Relative_Difference_%": mismatch["relative_difference"],
            "Threshold": mismatch["threshold"]
        })
    
    # Create DataFrame and export
    df = pd.DataFrame(all_comparisons)
    df.to_csv(output_path, index=False)
    
    # Create summary sheet
    summary_path = str(output_path).replace('.csv', '_summary.csv')
    summary_data = [
        ["Metric", "Value"],
        ["Total Comparisons", comparison_result.summary.get("total_comparisons", 0)],
        ["Matches", comparison_result.summary.get("matches", 0)],
        ["Mismatches", comparison_result.summary.get("mismatches", 0)],
        ["Match Rate %", comparison_result.summary.get("match_rate", 0) * 100],
        ["Missing in Expected", len(comparison_result.missing_in_expected)],
        ["Missing in Actual", len(comparison_result.missing_in_actual)]
    ]
    
    summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
    summary_df.to_csv(summary_path, index=False)