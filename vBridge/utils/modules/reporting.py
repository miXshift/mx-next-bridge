"""
Reporting module for Mix Bridge analysis.
Provides formatted output utilities for console and file generation.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from .config import AnalysisConfig

class ReportFormatter:
    """
    Formatter for various types of Mix Bridge reports.
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize formatter with configuration."""
        self.config = config or AnalysisConfig()
        
    def print_section_header(self, title: str, width: int = 80, char: str = "=") -> None:
        """
        Print a formatted section header.
        
        Args:
            title: Section title
            width: Width of header
            char: Character to use for header
        """
        print(f"\n{char * width}")
        print(f"{title.center(width)}")
        print(f"{char * width}")
        
    def print_subsection_header(self, title: str, width: int = 80, char: str = "-") -> None:
        """
        Print a formatted subsection header.
        
        Args:
            title: Subsection title
            width: Width of header
            char: Character to use for header
        """
        print(f"\n{char * width}")
        print(f" {title}")
        print(f"{char * width}")
        
    def format_comparison_table(self, data: List[Dict[str, Any]], 
                               headers: Optional[List[str]] = None,
                               max_width: int = 120) -> str:
        """
        Format comparison data as a table.
        
        Args:
            data: List of dictionaries with comparison data
            headers: List of column headers
            max_width: Maximum width for table
            
        Returns:
            Formatted table string
        """
        if not data:
            return "No data to display"
            
        # Use provided headers or infer from data
        if headers is None:
            headers = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(header)
            for row in data:
                if header in row:
                    col_widths[header] = max(col_widths[header], len(str(row[header])))
        
        # Adjust widths if total exceeds max_width
        total_width = sum(col_widths.values()) + len(headers) * 3 + 1
        if total_width > max_width:
            # Proportionally reduce column widths
            factor = (max_width - len(headers) * 3 - 1) / sum(col_widths.values())
            for header in headers:
                col_widths[header] = max(8, int(col_widths[header] * factor))
        
        # Build table
        lines = []
        
        # Header row
        header_row = "|"
        separator_row = "|"
        for header in headers:
            header_row += f" {header:<{col_widths[header]}} |"
            separator_row += f" {'-' * col_widths[header]} |"
        
        lines.append(header_row)
        lines.append(separator_row)
        
        # Data rows
        for row in data:
            data_row = "|"
            for header in headers:
                value = str(row.get(header, ""))
                if len(value) > col_widths[header]:
                    value = value[:col_widths[header] - 3] + "..."
                data_row += f" {value:<{col_widths[header]}} |"
            lines.append(data_row)
        
        return "\n".join(lines)
        
    def format_summary_stats(self, stats: Dict[str, Any]) -> str:
        """
        Format summary statistics.
        
        Args:
            stats: Dictionary of statistics
            
        Returns:
            Formatted statistics string
        """
        lines = []
        
        for key, value in stats.items():
            # Format key
            formatted_key = key.replace('_', ' ').title()
            
            # Format value
            if isinstance(value, float):
                if abs(value) < 0.001:
                    formatted_value = f"{value:.6f}"
                elif abs(value) < 1:
                    formatted_value = f"{value:.4f}"
                else:
                    formatted_value = f"{value:.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            lines.append(f"{formatted_key:<30}: {formatted_value}")
        
        return "\n".join(lines)
        
    def print_progress_status(self, current: int, total: int, message: str = "") -> None:
        """
        Print progress status.
        
        Args:
            current: Current progress
            total: Total items
            message: Optional message
        """
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\r[{bar}] {percentage:.1f}% ({current}/{total}) {message}", end="", flush=True)
        
        if current == total:
            print()  # New line when complete

class ReportGenerator:
    """
    Generator for various types of Mix Bridge reports.
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize generator with configuration."""
        self.config = config or AnalysisConfig()
        self.formatter = ReportFormatter(config)
        
    def generate_timestamped_filename(self, base_path: Union[str, Path], 
                                    suffix: str = "") -> str:
        """
        Generate timestamped filename.
        
        Args:
            base_path: Base path for file
            suffix: Optional suffix to add
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path(base_path)
        
        if suffix:
            filename = f"{path.stem}_{suffix}_{timestamp}{path.suffix}"
        else:
            filename = f"{path.stem}_{timestamp}{path.suffix}"
            
        return str(path.parent / filename)
        
    def save_analysis_to_json(self, data: Dict[str, Any], 
                             filename: Union[str, Path],
                             include_metadata: bool = True) -> None:
        """
        Save analysis results to JSON file.
        
        Args:
            data: Analysis data
            filename: Output filename
            include_metadata: Whether to include metadata
        """
        output_data = data.copy()
        
        if include_metadata:
            output_data["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "version": "0.1.0",
                "config": self.config.to_dict()
            }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
            
    def save_analysis_to_csv(self, data: Union[pd.DataFrame, List[Dict[str, Any]]], 
                            filename: Union[str, Path],
                            include_metadata: bool = True) -> None:
        """
        Save analysis results to CSV file.
        
        Args:
            data: Analysis data (DataFrame or list of dicts)
            filename: Output filename
            include_metadata: Whether to include metadata
        """
        # Convert to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
            
        # Add metadata row if requested
        if include_metadata:
            metadata_row = {col: '' for col in df.columns}
            metadata_row[df.columns[0]] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            metadata_df = pd.DataFrame([metadata_row])
            df = pd.concat([metadata_df, df], ignore_index=True)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
    def generate_comparison_report(self, comparison_result,
                                 output_path: Optional[Union[str, Path]] = None,
                                 format_type: str = "console") -> Optional[str]:
        """
        Generate comparison report.
        
        Args:
            comparison_result: ComparisonResult object
            output_path: Optional output path
            format_type: Output format ("console", "csv", "json")
            
        Returns:
            Report content if console format, None otherwise
        """
        if format_type == "console":
            return self._generate_console_comparison_report(comparison_result)
        elif format_type == "csv":
            if output_path:
                from .data_comparison import export_comparison_to_csv
                export_comparison_to_csv(comparison_result, output_path)
        elif format_type == "json":
            if output_path:
                from .data_comparison import generate_comparison_summary
                generate_comparison_summary(comparison_result, output_path)
        
        return None
        
    def _generate_console_comparison_report(self, comparison_result) -> str:
        """Generate console-formatted comparison report."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("MIX BRIDGE COMPARISON REPORT".center(80))
        lines.append("=" * 80)
        
        # Summary
        comparison_result.generate_summary()
        summary = comparison_result.summary
        
        lines.append("\nSUMMARY")
        lines.append("-" * 80)
        lines.append(self.formatter.format_summary_stats(summary))
        
        # Mismatches
        if comparison_result.mismatches:
            lines.append("\nMISMATCHES")
            lines.append("-" * 80)
            
            # Show top 20 mismatches
            top_mismatches = sorted(
                comparison_result.mismatches,
                key=lambda x: abs(x.get('relative_difference', 0)),
                reverse=True
            )[:20]
            
            mismatch_data = []
            for mismatch in top_mismatches:
                mismatch_data.append({
                    "Item": mismatch['item'],
                    "Expected": f"{mismatch['expected']:.4f}" if isinstance(mismatch['expected'], float) else str(mismatch['expected']),
                    "Actual": f"{mismatch['actual']:.4f}" if isinstance(mismatch['actual'], float) else str(mismatch['actual']),
                    "Diff": f"{mismatch['difference']:.4f}" if isinstance(mismatch['difference'], float) else str(mismatch['difference']),
                    "Rel Diff %": f"{mismatch['relative_difference']:.2f}" if isinstance(mismatch['relative_difference'], float) else str(mismatch['relative_difference'])
                })
            
            lines.append(self.formatter.format_comparison_table(mismatch_data))
        
        # Missing items
        if comparison_result.missing_in_expected or comparison_result.missing_in_actual:
            lines.append("\nMISSING ITEMS")
            lines.append("-" * 80)
            
            if comparison_result.missing_in_expected:
                lines.append(f"Missing in Expected ({len(comparison_result.missing_in_expected)}):")
                for item in comparison_result.missing_in_expected[:10]:
                    lines.append(f"  - {item}")
                if len(comparison_result.missing_in_expected) > 10:
                    lines.append(f"  ... and {len(comparison_result.missing_in_expected) - 10} more")
            
            if comparison_result.missing_in_actual:
                lines.append(f"\nMissing in Actual ({len(comparison_result.missing_in_actual)}):")
                for item in comparison_result.missing_in_actual[:10]:
                    lines.append(f"  - {item}")
                if len(comparison_result.missing_in_actual) > 10:
                    lines.append(f"  ... and {len(comparison_result.missing_in_actual) - 10} more")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)
        
    def generate_bridge_analysis_report(self, bridge_df: pd.DataFrame,
                                      metrics: List[str],
                                      output_path: Optional[Union[str, Path]] = None,
                                      format_type: str = "console") -> Optional[str]:
        """
        Generate Mix Bridge analysis report.
        
        Args:
            bridge_df: DataFrame with bridge calculations
            metrics: List of metrics analyzed
            output_path: Optional output path
            format_type: Output format ("console", "csv", "json")
            
        Returns:
            Report content if console format, None otherwise
        """
        if format_type == "console":
            return self._generate_console_bridge_report(bridge_df, metrics)
        elif format_type == "csv":
            if output_path:
                self.save_analysis_to_csv(bridge_df, output_path)
        elif format_type == "json":
            if output_path:
                # Convert DataFrame to dict for JSON serialization
                data = {
                    "bridge_analysis": bridge_df.to_dict(orient="records"),
                    "metrics": metrics,
                    "summary": self._calculate_bridge_summary(bridge_df, metrics)
                }
                self.save_analysis_to_json(data, output_path)
        
        return None
        
    def _generate_console_bridge_report(self, bridge_df: pd.DataFrame, 
                                       metrics: List[str]) -> str:
        """Generate console-formatted bridge analysis report."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("MIX BRIDGE ANALYSIS REPORT".center(80))
        lines.append("=" * 80)
        
        # Summary for each metric
        for metric in metrics:
            lines.append(f"\n{metric.upper()} ANALYSIS")
            lines.append("-" * 80)
            
            # Check if metric columns exist
            contribution_col = f"{metric}_contribution"
            impact_col = f"{metric}_impact"
            
            if contribution_col in bridge_df.columns and impact_col in bridge_df.columns:
                # Top contributors
                top_contributors = bridge_df.nlargest(5, contribution_col)
                
                lines.append("Top 5 Contributors:")
                contrib_data = []
                for _, row in top_contributors.iterrows():
                    contrib_data.append({
                        "Campaign": row.get('Campaign', 'N/A'),
                        "Contribution": f"{row[contribution_col]:.2f}",
                        "Impact %": f"{row[impact_col] * 100:.2f}%"
                    })
                
                lines.append(self.formatter.format_comparison_table(contrib_data))
                
                # Summary stats
                summary_stats = {
                    "Total Contribution": bridge_df[contribution_col].sum(),
                    "Average Contribution": bridge_df[contribution_col].mean(),
                    "Max Contribution": bridge_df[contribution_col].max(),
                    "Min Contribution": bridge_df[contribution_col].min()
                }
                
                lines.append("\nSummary Statistics:")
                lines.append(self.formatter.format_summary_stats(summary_stats))
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)
        
    def _calculate_bridge_summary(self, bridge_df: pd.DataFrame, 
                                 metrics: List[str]) -> Dict[str, Any]:
        """Calculate summary statistics for bridge analysis."""
        summary = {}
        
        for metric in metrics:
            contribution_col = f"{metric}_contribution"
            impact_col = f"{metric}_impact"
            
            if contribution_col in bridge_df.columns:
                summary[metric] = {
                    "total_contribution": bridge_df[contribution_col].sum(),
                    "avg_contribution": bridge_df[contribution_col].mean(),
                    "max_contribution": bridge_df[contribution_col].max(),
                    "min_contribution": bridge_df[contribution_col].min(),
                    "campaigns_analyzed": len(bridge_df)
                }
        
        return summary

def print_welcome_message() -> None:
    """Print welcome message for Mix Bridge analysis."""
    print("=" * 80)
    print("MIX BRIDGE ANALYSIS TOOLKIT v0.1.0".center(80))
    print("=" * 80)
    print("A modular toolkit for analyzing Mix Bridge Excel files")
    print("and comparing outputs with configurable precision.")
    print("=" * 80)

def print_completion_message(duration: float, output_files: List[str]) -> None:
    """
    Print completion message.
    
    Args:
        duration: Analysis duration in seconds
        output_files: List of output file paths
    """
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE".center(80))
    print("=" * 80)
    print(f"Duration: {duration:.2f} seconds")
    
    if output_files:
        print("\nOutput Files Generated:")
        for file_path in output_files:
            print(f"  - {file_path}")
    
    print("=" * 80)