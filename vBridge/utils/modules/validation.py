"""
Validation module for Mix Bridge analysis.
Provides data validation utilities and consistency checks.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from .config import AnalysisConfig, ABSOLUTE_METRICS, RATE_METRICS

class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []
        self.is_valid: bool = True
        
    def add_error(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add validation error."""
        self.errors.append({
            "message": message,
            "details": details or {},
            "severity": "error"
        })
        self.is_valid = False
        
    def add_warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add validation warning."""
        self.warnings.append({
            "message": message,
            "details": details or {},
            "severity": "warning"
        })
        
    def add_info(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Add validation info."""
        self.info.append({
            "message": message,
            "details": details or {},
            "severity": "info"
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
            "total_issues": len(self.errors) + len(self.warnings)
        }
        
    def print_summary(self) -> None:
        """Print validation summary to console."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY".center(60))
        print("=" * 60)
        
        summary = self.get_summary()
        print(f"Overall Status: {'VALID' if summary['is_valid'] else 'INVALID'}")
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        print(f"Info: {summary['info_count']}")
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error['message']}")
                
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning['message']}")
                
        print("=" * 60)

class DataValidator:
    """Validator for Mix Bridge data."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize validator with configuration."""
        self.config = config or AnalysisConfig()
        
    def validate_required_columns(self, df: pd.DataFrame, 
                                 required_cols: List[str]) -> ValidationResult:
        """
        Validate that required columns exist in DataFrame.
        
        Args:
            df: DataFrame to validate
            required_cols: List of required column names
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            result.add_error(
                f"Missing required columns: {', '.join(missing_cols)}",
                {"missing_columns": missing_cols, "available_columns": list(df.columns)}
            )
        else:
            result.add_info(f"All {len(required_cols)} required columns found")
            
        return result
        
    def validate_numeric_columns(self, df: pd.DataFrame, 
                                numeric_cols: List[str]) -> ValidationResult:
        """
        Validate that specified columns contain numeric data.
        
        Args:
            df: DataFrame to validate
            numeric_cols: List of columns that should be numeric
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        for col in numeric_cols:
            if col not in df.columns:
                result.add_error(f"Column '{col}' not found in DataFrame")
                continue
                
            # Check if column is numeric
            if not pd.api.types.is_numeric_dtype(df[col]):
                # Try to convert to numeric
                try:
                    pd.to_numeric(df[col], errors='raise')
                    result.add_warning(f"Column '{col}' is not numeric but can be converted")
                except (ValueError, TypeError):
                    # Count non-numeric values
                    non_numeric = df[col][pd.to_numeric(df[col], errors='coerce').isna()].count()
                    result.add_error(
                        f"Column '{col}' contains {non_numeric} non-numeric values",
                        {"non_numeric_count": non_numeric, "total_rows": len(df)}
                    )
            else:
                result.add_info(f"Column '{col}' is properly numeric")
                
        return result
        
    def validate_data_consistency(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate data consistency (no NaN, reasonable ranges, etc.).
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        # Check for NaN values
        nan_summary = df.isnull().sum()
        columns_with_nan = nan_summary[nan_summary > 0]
        
        if not columns_with_nan.empty:
            for col, nan_count in columns_with_nan.items():
                percentage = (nan_count / len(df)) * 100
                if percentage > 50:
                    result.add_error(
                        f"Column '{col}' has {nan_count} NaN values ({percentage:.1f}% of data)",
                        {"nan_count": nan_count, "percentage": percentage}
                    )
                elif percentage > 10:
                    result.add_warning(
                        f"Column '{col}' has {nan_count} NaN values ({percentage:.1f}% of data)",
                        {"nan_count": nan_count, "percentage": percentage}
                    )
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            result.add_warning(
                f"Found {duplicate_count} duplicate rows",
                {"duplicate_count": duplicate_count}
            )
            
        # Check for negative values in metrics that should be positive
        positive_metrics = ABSOLUTE_METRICS + ['ROAS', 'Conversion Rate']
        for col in df.columns:
            if any(metric in col for metric in positive_metrics):
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        result.add_warning(
                            f"Column '{col}' has {negative_count} negative values",
                            {"negative_count": negative_count}
                        )
        
        return result
        
    def validate_calculation_consistency(self, calculated: pd.Series, 
                                       expected: pd.Series,
                                       tolerance: Optional[float] = None) -> ValidationResult:
        """
        Validate that calculated values match expected values within tolerance.
        
        Args:
            calculated: Calculated values
            expected: Expected values
            tolerance: Tolerance for comparison
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        if tolerance is None:
            tolerance = self.config.comparison.tolerance
            
        # Check series lengths
        if len(calculated) != len(expected):
            result.add_error(
                f"Series length mismatch: calculated={len(calculated)}, expected={len(expected)}"
            )
            return result
            
        # Calculate differences
        diff = abs(calculated - expected)
        relative_diff = diff / np.maximum(abs(expected), 1e-10)  # Avoid division by zero
        
        # Count mismatches
        mismatches = (diff > tolerance).sum()
        large_mismatches = (relative_diff > tolerance).sum()
        
        if mismatches > 0:
            max_diff = diff.max()
            max_rel_diff = relative_diff.max()
            
            result.add_error(
                f"Found {mismatches} values outside tolerance ({tolerance})",
                {
                    "mismatch_count": mismatches,
                    "max_difference": max_diff,
                    "max_relative_difference": max_rel_diff,
                    "tolerance": tolerance
                }
            )
        else:
            result.add_info(f"All {len(calculated)} values within tolerance")
            
        return result
        
    def validate_contribution_sum(self, individual_contribs: pd.Series, 
                                 total_contrib: float,
                                 tolerance: Optional[float] = None) -> ValidationResult:
        """
        Validate that individual contributions sum to total contribution.
        
        Args:
            individual_contribs: Series of individual contributions
            total_contrib: Expected total contribution
            tolerance: Tolerance for comparison
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        if tolerance is None:
            tolerance = self.config.comparison.tolerance
            
        calculated_total = individual_contribs.sum()
        difference = abs(calculated_total - total_contrib)
        relative_difference = difference / max(abs(total_contrib), 1e-10)
        
        if difference > tolerance:
            result.add_error(
                f"Contribution sum mismatch: calculated={calculated_total:.6f}, expected={total_contrib:.6f}",
                {
                    "calculated_total": calculated_total,
                    "expected_total": total_contrib,
                    "difference": difference,
                    "relative_difference": relative_difference
                }
            )
        else:
            result.add_info("Contribution sum validation passed")
            
        return result
        
    def validate_mix_bridge_structure(self, df: pd.DataFrame,
                                     metrics: List[str]) -> ValidationResult:
        """
        Validate Mix Bridge DataFrame structure and calculations.
        
        Args:
            df: DataFrame with Mix Bridge calculations
            metrics: List of metrics to validate
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        # Check for required columns for each metric
        for metric in metrics:
            required_cols = [
                f"{metric}_p1_mix",
                f"{metric}_mix_rate", 
                f"{metric}_contribution",
                f"{metric}_delta",
                f"{metric}_impact"
            ]
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                result.add_error(
                    f"Missing Mix Bridge columns for {metric}: {', '.join(missing_cols)}",
                    {"metric": metric, "missing_columns": missing_cols}
                )
            else:
                result.add_info(f"All Mix Bridge columns found for {metric}")
                
                # Validate that impacts sum to ~1.0
                impact_col = f"{metric}_impact"
                if impact_col in df.columns:
                    impact_sum = df[impact_col].sum()
                    if abs(impact_sum - 1.0) > self.config.comparison.tolerance:
                        result.add_warning(
                            f"Impact sum for {metric} is {impact_sum:.6f}, expected ~1.0",
                            {"metric": metric, "impact_sum": impact_sum}
                        )
                
                # Validate that mix values sum to ~1.0
                mix_col = f"{metric}_p1_mix"
                if mix_col in df.columns:
                    mix_sum = df[mix_col].sum()
                    if abs(mix_sum - 1.0) > self.config.comparison.tolerance:
                        result.add_warning(
                            f"Mix sum for {metric} is {mix_sum:.6f}, expected ~1.0",
                            {"metric": metric, "mix_sum": mix_sum}
                        )
        
        return result
        
    def validate_complete_dataset(self, df: pd.DataFrame,
                                 required_columns: List[str],
                                 numeric_columns: List[str],
                                 metrics: Optional[List[str]] = None) -> ValidationResult:
        """
        Perform complete validation of a dataset.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required columns
            numeric_columns: List of columns that should be numeric
            metrics: List of metrics for Mix Bridge validation
            
        Returns:
            Combined ValidationResult
        """
        combined_result = ValidationResult()
        
        # Validate required columns
        cols_result = self.validate_required_columns(df, required_columns)
        combined_result.errors.extend(cols_result.errors)
        combined_result.warnings.extend(cols_result.warnings)
        combined_result.info.extend(cols_result.info)
        
        # Validate numeric columns
        numeric_result = self.validate_numeric_columns(df, numeric_columns)
        combined_result.errors.extend(numeric_result.errors)
        combined_result.warnings.extend(numeric_result.warnings)
        combined_result.info.extend(numeric_result.info)
        
        # Validate data consistency
        consistency_result = self.validate_data_consistency(df)
        combined_result.errors.extend(consistency_result.errors)
        combined_result.warnings.extend(consistency_result.warnings)
        combined_result.info.extend(consistency_result.info)
        
        # Validate Mix Bridge structure if metrics provided
        if metrics:
            bridge_result = self.validate_mix_bridge_structure(df, metrics)
            combined_result.errors.extend(bridge_result.errors)
            combined_result.warnings.extend(bridge_result.warnings)
            combined_result.info.extend(bridge_result.info)
        
        # Update overall validity
        combined_result.is_valid = len(combined_result.errors) == 0
        
        return combined_result

def validate_excel_file_structure(file_path: str, 
                                 expected_sheets: List[str]) -> ValidationResult:
    """
    Validate Excel file structure.
    
    Args:
        file_path: Path to Excel file
        expected_sheets: List of expected sheet names
        
    Returns:
        ValidationResult object
    """
    result = ValidationResult()
    
    try:
        from .excel_operations import get_sheet_names
        
        actual_sheets = get_sheet_names(file_path)
        
        # Check for missing sheets
        missing_sheets = [sheet for sheet in expected_sheets if sheet not in actual_sheets]
        if missing_sheets:
            result.add_error(
                f"Missing expected sheets: {', '.join(missing_sheets)}",
                {"missing_sheets": missing_sheets, "available_sheets": actual_sheets}
            )
        
        # Check for extra sheets
        extra_sheets = [sheet for sheet in actual_sheets if sheet not in expected_sheets]
        if extra_sheets:
            result.add_info(
                f"Found additional sheets: {', '.join(extra_sheets)}",
                {"extra_sheets": extra_sheets}
            )
        
        if not missing_sheets:
            result.add_info(f"All {len(expected_sheets)} expected sheets found")
            
    except Exception as e:
        result.add_error(f"Error reading Excel file: {str(e)}")
        
    return result

def create_validation_report(validation_results: List[ValidationResult],
                           report_name: str = "Validation Report") -> str:
    """
    Create a comprehensive validation report.
    
    Args:
        validation_results: List of ValidationResult objects
        report_name: Name for the report
        
    Returns:
        Formatted report string
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(report_name.center(80))
    lines.append("=" * 80)
    
    # Summary
    total_errors = sum(len(result.errors) for result in validation_results)
    total_warnings = sum(len(result.warnings) for result in validation_results)
    total_info = sum(len(result.info) for result in validation_results)
    
    lines.append(f"\nOVERALL SUMMARY:")
    lines.append(f"Total Validations: {len(validation_results)}")
    lines.append(f"Total Errors: {total_errors}")
    lines.append(f"Total Warnings: {total_warnings}")
    lines.append(f"Total Info: {total_info}")
    
    # Individual results
    for i, result in enumerate(validation_results, 1):
        lines.append(f"\n{'-' * 60}")
        lines.append(f"VALIDATION {i}")
        lines.append(f"{'-' * 60}")
        
        if result.errors:
            lines.append("\nERRORS:")
            for error in result.errors:
                lines.append(f"  - {error['message']}")
                
        if result.warnings:
            lines.append("\nWARNINGS:")
            for warning in result.warnings:
                lines.append(f"  - {warning['message']}")
                
        if result.info:
            lines.append("\nINFO:")
            for info in result.info:
                lines.append(f"  - {info['message']}")
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)