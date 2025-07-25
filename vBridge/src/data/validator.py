#!/usr/bin/env python3
"""
Validation Framework for MixBridge Calculations
Comprehensive validation of contribution calculations and mathematical consistency
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from ..common.exceptions import (
        ValidationError, ConfigurationError, DataProcessingError
    )
    from ..config.constants import (
        ZERO_TOLERANCE, BASIS_POINTS_MULTIPLIER, PERCENTAGE_TOLERANCE
    )
    from ..common.logger import get_logger
    from ..config.settings import MixBridgeConfig
except ImportError:
    # Backwards compatibility during migration
    try:
        from .exceptions import (
            ValidationError, ConfigurationError, DataProcessingError,
            InvalidMetricError, InsufficientDataError
        )
        from .constants import (
            VOLUME_METRICS, RATE_METRICS, COST_METRICS, ALL_METRICS,
            ZERO_TOLERANCE, PERCENTAGE_TOLERANCE, BASIS_POINTS_MULTIPLIER
        )
        from .logger import get_logger
        from .mixbridge_config import MixBridgeConfig, get_config
    except ImportError:
        # Handle direct imports when not run as package
        from exceptions import (
            ValidationError, ConfigurationError, DataProcessingError,
            InvalidMetricError, InsufficientDataError
        )
        from constants import (
        VOLUME_METRICS, RATE_METRICS, COST_METRICS, ALL_METRICS,
        ZERO_TOLERANCE, PERCENTAGE_TOLERANCE, BASIS_POINTS_MULTIPLIER
    )
    from logger import get_logger
    from mixbridge_config import MixBridgeConfig, get_config


logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = 'info'  # 'info', 'warning', 'error'


class MixBridgeValidator:
    """Enhanced validation framework for MixBridge calculations"""
    
    def __init__(self, config: Optional[MixBridgeConfig] = None):
        """
        Initialize validator
        
        Args:
            config: Configuration object, uses global if None
        """
        self.config = config or get_config()
        self.tolerance = self.config.validation_tolerance
        self.validation_results: List[ValidationResult] = []
        logger.info("MixBridgeValidator initialized")
    
    def validate_required_columns(
        self, 
        df: pd.DataFrame, 
        required_columns: List[str],
        dataset_name: str = "dataset"
    ) -> None:
        """
        Validate that required columns exist in DataFrame.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            dataset_name: Name of dataset for error messages
            
        Raises:
            ValidationError: If required columns are missing
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            error_msg = f"Missing required columns in {dataset_name}: {missing_columns}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        logger.debug(f"All required columns present in {dataset_name}")
    
    def validate_numeric_columns(
        self,
        df: pd.DataFrame,
        numeric_columns: List[str],
        dataset_name: str = "dataset"
    ) -> None:
        """
        Validate that specified columns contain numeric data.
        
        Args:
            df: DataFrame to validate
            numeric_columns: List of columns that should be numeric
            dataset_name: Name of dataset for error messages
            
        Raises:
            ValidationError: If non-numeric data found in numeric columns
        """
        non_numeric = []
        for col in numeric_columns:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    # Try to convert to numeric
                    pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    non_numeric.append(col)
        
        if non_numeric:
            error_msg = f"Non-numeric data in {dataset_name} columns: {non_numeric}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        logger.debug(f"All numeric columns validated in {dataset_name}")
    
    def validate_date_column(
        self,
        df: pd.DataFrame,
        date_column: str,
        dataset_name: str = "dataset"
    ) -> None:
        """
        Validate date column format and values.
        
        Args:
            df: DataFrame to validate
            date_column: Name of date column
            dataset_name: Name of dataset for error messages
            
        Raises:
            ValidationError: If date column has invalid format
        """
        if date_column not in df.columns:
            error_msg = f"Date column '{date_column}' not found in {dataset_name}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        try:
            # Try to parse dates
            pd.to_datetime(df[date_column], errors='coerce')
            invalid_dates = df[pd.to_datetime(df[date_column], errors='coerce').isna()]
            if len(invalid_dates) > 0:
                error_msg = f"Invalid dates found in {dataset_name}: {len(invalid_dates)} rows"
                logger.error(error_msg)
                raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Error validating dates in {dataset_name}: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        logger.debug(f"Date column validated in {dataset_name}")
    
    def validate_metric_calculations(
        self,
        df: pd.DataFrame,
        tolerance: float = PERCENTAGE_TOLERANCE
    ) -> None:
        """
        Validate calculated metrics match expected values.
        
        Args:
            df: DataFrame with metrics to validate
            tolerance: Acceptable tolerance for calculations
            
        Raises:
            ValidationError: If calculations don't match expected values
        """
        errors = []
        
        # Validate CTR if present
        if all(col in df.columns for col in ['clicks', 'impressions', 'CTR']):
            mask = df['impressions'] > 0
            expected_ctr = (df.loc[mask, 'clicks'] / df.loc[mask, 'impressions']) * 100
            actual_ctr = df.loc[mask, 'CTR']
            
            diff = np.abs(expected_ctr - actual_ctr)
            invalid = diff > tolerance
            
            if invalid.any():
                errors.append(f"CTR calculation mismatch: {invalid.sum()} rows exceed tolerance")
        
        # Validate CVR if present
        if all(col in df.columns for col in ['conversions', 'clicks', 'CVR']):
            mask = df['clicks'] > 0
            expected_cvr = (df.loc[mask, 'conversions'] / df.loc[mask, 'clicks']) * 100
            actual_cvr = df.loc[mask, 'CVR']
            
            diff = np.abs(expected_cvr - actual_cvr)
            invalid = diff > tolerance
            
            if invalid.any():
                errors.append(f"CVR calculation mismatch: {invalid.sum()} rows exceed tolerance")
        
        if errors:
            error_msg = "Metric calculation errors: " + "; ".join(errors)
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        logger.debug("Metric calculations validated")
    
    def validate_non_negative_values(
        self,
        df: pd.DataFrame,
        columns: List[str],
        dataset_name: str = "dataset"
    ) -> None:
        """
        Validate that specified columns contain non-negative values.
        
        Args:
            df: DataFrame to validate
            columns: List of columns that should be non-negative
            dataset_name: Name of dataset for error messages
            
        Raises:
            ValidationError: If negative values found
        """
        negative_columns = []
        
        for col in columns:
            if col in df.columns:
                if (df[col] < 0).any():
                    negative_count = (df[col] < 0).sum()
                    negative_columns.append(f"{col} ({negative_count} rows)")
        
        if negative_columns:
            error_msg = f"Negative values found in {dataset_name}: {negative_columns}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        logger.debug(f"Non-negative values validated in {dataset_name}")
    
    def validate_percentage_bounds(
        self,
        df: pd.DataFrame,
        percentage_columns: List[str],
        dataset_name: str = "dataset"
    ) -> None:
        """
        Validate that percentage columns are within 0-100 bounds.
        
        Args:
            df: DataFrame to validate
            percentage_columns: List of percentage columns
            dataset_name: Name of dataset for error messages
            
        Raises:
            ValidationError: If percentages are out of bounds
        """
        out_of_bounds = []
        
        for col in percentage_columns:
            if col in df.columns:
                if ((df[col] < 0) | (df[col] > 100)).any():
                    count = ((df[col] < 0) | (df[col] > 100)).sum()
                    out_of_bounds.append(f"{col} ({count} rows)")
        
        if out_of_bounds:
            error_msg = f"Percentage values out of bounds in {dataset_name}: {out_of_bounds}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        logger.debug(f"Percentage bounds validated in {dataset_name}")
    
    def detect_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        threshold: float = 3.0
    ) -> pd.Series:
        """
        Detect outliers using z-score method.
        
        Args:
            df: DataFrame containing the data
            column: Column to check for outliers
            threshold: Z-score threshold for outlier detection
            
        Returns:
            Series of outlier values
        """
        if column not in df.columns:
            raise InvalidMetricError(f"Column '{column}' not found in DataFrame")
        
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        outliers = df[column][z_scores > threshold]
        
        if len(outliers) > 0:
            logger.warning(f"Found {len(outliers)} outliers in {column}")
        
        return outliers
    
    def validate_campaign_consistency(
        self,
        raw_data: pd.DataFrame,
        bridge_data: pd.DataFrame
    ) -> None:
        """
        Validate campaign consistency between raw and bridge data.
        
        Args:
            raw_data: Raw campaign data
            bridge_data: Bridge calculation data
            
        Raises:
            ValidationError: If campaigns are inconsistent
        """
        raw_campaigns = set(raw_data['Campaign Name'].unique())
        bridge_campaigns = set(bridge_data['Campaign Name'].unique())
        
        # Check for campaigns in bridge but not in raw
        missing_in_raw = bridge_campaigns - raw_campaigns
        if missing_in_raw:
            error_msg = f"Campaigns in bridge data not found in raw data: {missing_in_raw}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        # Check for campaigns in raw but not in bridge (warning only)
        missing_in_bridge = raw_campaigns - bridge_campaigns
        if missing_in_bridge:
            logger.warning(f"Campaigns in raw data not found in bridge data: {missing_in_bridge}")
        
        logger.debug("Campaign consistency validated")
    
    def validate_bridge_totals(
        self,
        bridge_data: pd.DataFrame,
        tolerance: float = ZERO_TOLERANCE
    ) -> None:
        """
        Validate that bridge calculation totals are correct.
        
        Args:
            bridge_data: Bridge calculation results
            tolerance: Acceptable tolerance for calculations
            
        Raises:
            ValidationError: If totals don't match
        """
        errors = []
        
        # Check if expected columns exist
        required_cols = ['baseline_total', 'actual_total', 'incremental_total']
        for col in required_cols:
            if col not in bridge_data.columns:
                logger.warning(f"Column '{col}' not found in bridge data, skipping total validation")
                return
        
        # Validate incremental = actual - baseline
        expected_incremental = bridge_data['actual_total'] - bridge_data['baseline_total']
        actual_incremental = bridge_data['incremental_total']
        
        diff = np.abs(expected_incremental - actual_incremental)
        invalid = diff > tolerance
        
        if invalid.any():
            invalid_metrics = bridge_data.loc[invalid, 'metric'].tolist() if 'metric' in bridge_data.columns else []
            errors.append(f"Incremental total mismatch for metrics: {invalid_metrics}")
        
        if errors:
            error_msg = "Bridge total validation errors: " + "; ".join(errors)
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        logger.debug("Bridge totals validated")
    
    def validate_contributions(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> bool:
        """
        Comprehensive validation of contribution calculations.
        
        Args:
            output_df: Campaign data with contributions
            total_row: Totals row dataframe
            
        Returns:
            True if all validations pass, False otherwise
        """
        self.validation_results.clear()
        logger.info("Starting comprehensive contribution validation")
        
        # Run all validation checks
        checks = [
            self._check_mathematical_consistency,
            self._check_contribution_sums,
            self._check_zero_baseline_handling,
            self._check_calculation_precision,
            self._check_data_integrity,
            self._check_business_logic
        ]
        
        all_passed = True
        for check in checks:
            try:
                result = check(output_df, total_row)
                self.validation_results.append(result)
                if not result.passed:
                    all_passed = False
                    logger.warning(f"{check.__name__}: {result.message}")
            except Exception as e:
                error_result = ValidationResult(
                    passed=False,
                    message=f"Validation check failed: {check.__name__}",
                    details={'error': str(e)},
                    severity='error'
                )
                self.validation_results.append(error_result)
                all_passed = False
                logger.error(f"Validation check {check.__name__} failed with error: {str(e)}")
        
        logger.info(f"Validation complete. All passed: {all_passed}")
        return all_passed
    
    def _check_mathematical_consistency(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Verify mathematical consistency of calculations"""
        absolute_metrics = self._get_absolute_metrics()
        inconsistencies = {}
        
        for metric in absolute_metrics:
            # Calculate expected total change in basis points
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            contrib_col = f'{metric} - Contribution'
            
            if jan_col not in total_row.columns or feb_col not in total_row.columns:
                continue
                
            jan_total = total_row.at[0, jan_col]
            feb_total = total_row.at[0, feb_col]
            
            if jan_total > 0:
                expected_change_bps = ((feb_total - jan_total) / jan_total) * BASIS_POINTS_MULTIPLIER
                
                if contrib_col in output_df.columns:
                    actual_contribution_sum = output_df[contrib_col].sum()
                    
                    difference = abs(expected_change_bps - actual_contribution_sum)
                    if difference > self.tolerance * BASIS_POINTS_MULTIPLIER:
                        inconsistencies[metric] = {
                            'expected_bps': round(expected_change_bps, 2),
                            'actual_sum': round(actual_contribution_sum, 2),
                            'difference': round(difference, 2)
                        }
        
        if inconsistencies:
            return ValidationResult(
                passed=False,
                message="Mathematical inconsistencies detected",
                details={'inconsistencies': inconsistencies},
                severity='warning'
            )
        
        return ValidationResult(
            passed=True,
            message="Mathematical consistency verified",
            severity='info'
        )
    
    def _check_contribution_sums(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Check that individual contributions sum appropriately"""
        absolute_metrics = self._get_absolute_metrics()
        sum_issues = {}
        
        for metric in absolute_metrics:
            contrib_col = f'{metric} - Contribution'
            if contrib_col not in output_df.columns:
                continue
                
            campaign_contributions = output_df[contrib_col]
            
            # Check for NaN or infinite values
            if campaign_contributions.isna().any():
                sum_issues[f'{metric}_nan'] = "Contains NaN values"
            
            if np.isinf(campaign_contributions).any():
                sum_issues[f'{metric}_inf'] = "Contains infinite values"
            
            # Check contribution distribution
            total_contribution = campaign_contributions.sum()
            if abs(total_contribution) > 1e6:  # Very large contributions
                sum_issues[f'{metric}_large'] = f"Unusually large total contribution: {total_contribution:.2f}"
        
        if sum_issues:
            return ValidationResult(
                passed=False,
                message="Contribution sum issues detected",
                details={'issues': sum_issues},
                severity='warning'
            )
        
        return ValidationResult(
            passed=True,
            message="Contribution sums validated",
            severity='info'
        )
    
    def _check_zero_baseline_handling(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Check proper handling of zero baseline scenarios"""
        absolute_metrics = self._get_absolute_metrics()
        zero_baseline_stats = {}
        issues = []
        
        for metric in absolute_metrics:
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            contrib_col = f'{metric} - Contribution'
            
            if not all(col in output_df.columns for col in [jan_col, feb_col, contrib_col]):
                continue
            
            # Find zero baseline campaigns
            zero_baseline_mask = (
                (output_df[jan_col] == 0) & 
                (output_df[feb_col] > 0)
            )
            zero_baseline_campaigns = output_df[zero_baseline_mask]
            
            if len(zero_baseline_campaigns) > 0:
                zero_contributions = zero_baseline_campaigns[contrib_col]
                
                zero_baseline_stats[metric] = {
                    'count': len(zero_baseline_campaigns),
                    'total_contribution': round(zero_contributions.sum(), 2),
                    'avg_contribution': round(zero_contributions.mean(), 2)
                }
                
                # Check if zero baseline campaigns have zero contributions
                if (zero_contributions == 0).all():
                    issues.append(f"{metric}: All zero baseline campaigns have zero contributions")
        
        severity = 'warning' if issues else 'info'
        message = "Zero baseline handling issues detected" if issues else "Zero baseline handling validated"
        
        return ValidationResult(
            passed=len(issues) == 0,
            message=message,
            details={'stats': zero_baseline_stats, 'issues': issues},
            severity=severity
        )
    
    def _check_calculation_precision(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Check calculation precision and rounding"""
        precision_issues = []
        
        for metric in self._get_absolute_metrics():
            contrib_col = f'{metric} - Contribution'
            if contrib_col not in output_df.columns:
                continue
                
            contributions = output_df[contrib_col]
            
            # Check for excessive decimal places
            decimal_places = contributions.apply(
                lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0
            )
            max_decimals = decimal_places.max()
            
            if max_decimals > self.config.precision_decimals + 2:
                precision_issues.append(f"{metric}: Excessive decimal places ({max_decimals})")
        
        if precision_issues:
            return ValidationResult(
                passed=False,
                message="Calculation precision issues detected",
                details={'issues': precision_issues},
                severity='warning'
            )
        
        return ValidationResult(
            passed=True,
            message="Calculation precision validated",
            severity='info'
        )
    
    def _check_data_integrity(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Check data integrity and consistency"""
        integrity_issues = []
        
        for metric in self._get_absolute_metrics():
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            contrib_col = f'{metric} - Contribution'
            
            if not all(col in output_df.columns for col in [jan_col, feb_col, contrib_col]):
                continue
            
            # Check for data type consistency
            if not pd.api.types.is_numeric_dtype(output_df[contrib_col]):
                integrity_issues.append(f"{metric}: Non-numeric contribution values")
            
            # Check for unrealistic growth scenarios
            mask = output_df[jan_col] > 0
            if mask.any():
                growth_ratio = output_df.loc[mask, feb_col] / output_df.loc[mask, jan_col]
                unrealistic_growth = growth_ratio > 100  # 10,000% growth
                
                if unrealistic_growth.any():
                    count = unrealistic_growth.sum()
                    integrity_issues.append(f"{metric}: {count} campaigns with unrealistic growth")
        
        if integrity_issues:
            return ValidationResult(
                passed=False,
                message="Data integrity issues detected",
                details={'issues': integrity_issues},
                severity='warning'
            )
        
        return ValidationResult(
            passed=True,
            message="Data integrity validated",
            severity='info'
        )
    
    def _check_business_logic(
        self,
        output_df: pd.DataFrame,
        total_row: pd.DataFrame
    ) -> ValidationResult:
        """Check business logic and common sense validation"""
        business_issues = []
        
        # Check for campaigns that disappeared
        disappeared_campaigns = {}
        for metric in self._get_absolute_metrics():
            jan_col = f'{metric} - January 2025'
            feb_col = f'{metric} - February 2025'
            
            if not all(col in output_df.columns for col in [jan_col, feb_col]):
                continue
                
            disappeared = output_df[
                (output_df[jan_col] > 0) & 
                (output_df[feb_col] == 0)
            ]
            if len(disappeared) > 0:
                disappeared_campaigns[metric] = len(disappeared)
        
        if disappeared_campaigns:
            business_issues.append(f"Campaigns that disappeared: {disappeared_campaigns}")
        
        # Check for total contribution reasonableness
        for metric in self._get_absolute_metrics():
            contrib_col = f'{metric} - Contribution'
            if contrib_col in output_df.columns:
                total_contrib = output_df[contrib_col].sum()
                if abs(total_contrib) > 50000:  # 500% change in basis points
                    business_issues.append(
                        f"{metric}: Extremely large total contribution ({total_contrib:.0f} bps)"
                    )
        
        if business_issues:
            return ValidationResult(
                passed=False,
                message="Business logic issues detected",
                details={'issues': business_issues},
                severity='info'
            )
        
        return ValidationResult(
            passed=True,
            message="Business logic validated",
            severity='info'
        )
    
    def _get_absolute_metrics(self) -> List[str]:
        """Get list of absolute metrics"""
        return [
            'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
            'Same SKU Ad Sales', 'Other SKU Sales', 'Same SKU Ad Orders',
            'Other SKU Ad Orders', 'Total Ad Orders'
        ]
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.
        
        Returns:
            Dictionary with validation results and summary
        """
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results if r.passed)
        failed_checks = total_checks - passed_checks
        
        # Group results by severity
        by_severity = {'info': [], 'warning': [], 'error': []}
        for result in self.validation_results:
            by_severity[result.severity].append(result)
        
        return {
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'success_rate': round(passed_checks / total_checks * 100, 1) if total_checks > 0 else 0
            },
            'by_severity': {
                severity: [{'message': r.message, 'passed': r.passed, 'details': r.details} 
                          for r in results]
                for severity, results in by_severity.items()
            },
            'config_used': {
                'strategy': 'delta_assignment',
                'tolerance': self.config.validation_tolerance,
                'precision': self.config.precision_decimals
            }
        }
    
    def print_validation_report(self) -> None:
        """Print formatted validation report"""
        report = self.get_validation_report()
        
        print("\n" + "="*60)
        print("MIXBRIDGE VALIDATION REPORT")
        print("="*60)
        
        summary = report['summary']
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']}%")
        
        # Print details by severity
        for severity in ['error', 'warning', 'info']:
            results = report['by_severity'][severity]
            if results:
                print(f"\n{severity.upper()} ({len(results)}):")
                for i, result in enumerate(results, 1):
                    status = "✅" if result['passed'] else "❌"
                    print(f"  {i}. {status} {result['message']}")
                    if result['details'] and self.config.debug_mode:
                        print(f"     Details: {result['details']}")
        
        print("\nConfiguration:")
        config = report['config_used']
        print(f"  Strategy: {config['strategy']}")
        print(f"  Tolerance: {config['tolerance']}")
        print(f"  Precision: {config['precision']} decimals")
        print("="*60)


# Maintain backward compatibility
ContributionValidator = MixBridgeValidator