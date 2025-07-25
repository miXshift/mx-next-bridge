#!/usr/bin/env python3
"""
Comparison Report Generator
Creates formatted reports from comparison results
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def load_comparison_results(results_file: str) -> Optional[Dict[str, Any]]:
    """Load comparison results from JSON file"""
    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return None

def generate_markdown_report(results: Dict[str, Any]) -> str:
    """Generate markdown formatted report"""
    
    report = []
    report.append("# MixBridge Comparison Analysis Report")
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Analysis Timestamp**: {results.get('timestamp', 'Unknown')}")
    report.append("")
    
    # Files compared
    report.append("## Files Compared")
    report.append(f"- **Excel Source**: `{results.get('excel_file', 'Unknown')}`")
    report.append(f"- **CSV Output**: `{results.get('csv_file', 'Unknown')}`")
    report.append("")
    
    # Campaign Coverage
    coverage = results.get('campaign_coverage', {})
    if coverage:
        report.append("## Campaign Coverage Analysis")
        report.append(f"- **Excel campaigns**: {coverage.get('excel_campaigns', 0)}")
        report.append(f"- **CSV campaigns**: {coverage.get('csv_campaigns', 0)}")
        report.append(f"- **Common campaigns**: {coverage.get('common_campaigns', 0)}")
        report.append(f"- **Coverage rate**: {coverage.get('coverage_rate', 0):.1f}%")
        
        if coverage.get('excel_only', 0) > 0:
            report.append(f"- **Excel-only campaigns**: {coverage.get('excel_only', 0)}")
        if coverage.get('csv_only', 0) > 0:
            report.append(f"- **CSV-only campaigns**: {coverage.get('csv_only', 0)}")
        report.append("")
    
    # Total Metrics Accuracy
    totals = results.get('total_metrics', {})
    if totals and 'overall_grade' in totals:
        grade_icons = {
            'PERFECT': '🎯',
            'EXCELLENT': '✅',
            'GOOD': '✅',
            'FAIR': '⚠️',
            'POOR': '❌'
        }
        
        grade = totals.get('overall_grade', 'UNKNOWN')
        icon = grade_icons.get(grade, '❓')
        
        report.append("## Accuracy Assessment")
        report.append(f"- **Overall Grade**: {icon} {grade}")
        report.append(f"- **Accuracy Score**: {totals.get('accuracy_score', 0):.2f}%")
        report.append(f"- **Average Error**: {totals.get('average_error', 0):.4f}%")
        report.append(f"- **Maximum Error**: {totals.get('maximum_error', 0):.4f}%")
        report.append("")
        
        # Individual metrics
        metric_results = totals.get('metric_results', [])
        if metric_results:
            report.append("### Individual Metrics")
            report.append("| Metric | Excel Value | CSV Value | Error % | Grade |")
            report.append("|--------|-------------|-----------|---------|-------|")
            
            for metric in metric_results:
                excel_val = metric.get('excel_value', 0)
                csv_val = metric.get('csv_value', 0)
                error = metric.get('relative_difference', 0)
                grade = metric.get('grade', 'UNKNOWN')
                
                grade_icon = grade_icons.get(grade, '❓')
                
                report.append(f"| {metric.get('metric', 'Unknown')} | ${excel_val:,.2f} | ${csv_val:,.2f} | {error:.4f}% | {grade_icon} {grade} |")
            
            report.append("")
    
    # Sample Campaign Verification
    samples = results.get('sample_campaigns', {})
    if samples and 'pass_rate' in samples:
        report.append("## Sample Campaign Verification")
        report.append(f"- **Campaigns tested**: {samples.get('sample_size', 0)}")
        report.append(f"- **Pass count**: {samples.get('pass_count', 0)}")
        report.append(f"- **Pass rate**: {samples.get('pass_rate', 0):.1f}%")
        report.append("")
    
    # Conclusion
    report.append("## Conclusion")
    
    if totals and 'overall_grade' in totals:
        grade = totals.get('overall_grade', 'UNKNOWN')
        accuracy = totals.get('accuracy_score', 0)
        
        if grade in ['PERFECT', 'EXCELLENT']:
            report.append("✅ **The enhanced MixBridge implementation shows excellent accuracy** compared to the Excel source of truth.")
        elif grade == 'GOOD':
            report.append("✅ **The enhanced MixBridge implementation shows good accuracy** with minor discrepancies.")
        elif grade == 'FAIR':
            report.append("⚠️ **The enhanced MixBridge implementation shows acceptable accuracy** but may need review.")
        else:
            report.append("❌ **The enhanced MixBridge implementation needs investigation** due to significant discrepancies.")
        
        report.append(f"Overall accuracy score: **{accuracy:.2f}%**")
    
    if coverage and coverage.get('coverage_rate', 0) > 90:
        report.append("✅ **Campaign coverage is excellent** with most campaigns matching between files.")
    elif coverage and coverage.get('coverage_rate', 0) > 70:
        report.append("✅ **Campaign coverage is good** with most campaigns accounted for.")
    else:
        report.append("⚠️ **Campaign coverage may need attention** - some campaigns are missing.")
    
    report.append("")
    report.append("---")
    report.append("*Report generated by Enhanced MixBridge Comparison System v2.0*")
    
    return "\n".join(report)

def generate_csv_summary(results: Dict[str, Any]) -> pd.DataFrame:
    """Generate CSV summary table"""
    
    summary_data = []
    
    # Add coverage information
    coverage = results.get('campaign_coverage', {})
    if coverage:
        summary_data.append({
            'Category': 'Campaign Coverage',
            'Metric': 'Coverage Rate',
            'Value': f"{coverage.get('coverage_rate', 0):.1f}%",
            'Status': 'GOOD' if coverage.get('coverage_rate', 0) > 90 else 'REVIEW'
        })
        
        summary_data.append({
            'Category': 'Campaign Coverage',
            'Metric': 'Common Campaigns',
            'Value': coverage.get('common_campaigns', 0),
            'Status': 'INFO'
        })
    
    # Add accuracy information
    totals = results.get('total_metrics', {})
    if totals:
        summary_data.append({
            'Category': 'Accuracy',
            'Metric': 'Overall Grade',
            'Value': totals.get('overall_grade', 'UNKNOWN'),
            'Status': totals.get('overall_grade', 'UNKNOWN')
        })
        
        summary_data.append({
            'Category': 'Accuracy',
            'Metric': 'Accuracy Score',
            'Value': f"{totals.get('accuracy_score', 0):.2f}%",
            'Status': 'GOOD' if totals.get('accuracy_score', 0) > 99 else 'REVIEW'
        })
    
    # Add sample verification
    samples = results.get('sample_campaigns', {})
    if samples:
        summary_data.append({
            'Category': 'Sample Verification',
            'Metric': 'Pass Rate',
            'Value': f"{samples.get('pass_rate', 0):.1f}%",
            'Status': 'GOOD' if samples.get('pass_rate', 0) > 90 else 'REVIEW'
        })
    
    return pd.DataFrame(summary_data)

def save_reports(results: Dict[str, Any], output_dir: str = '../output/reports'):
    """Save formatted reports"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate and save markdown report
    markdown_report = generate_markdown_report(results)
    markdown_file = output_path / f"comparison_report_{timestamp}.md"
    
    with open(markdown_file, 'w') as f:
        f.write(markdown_report)
    
    print(f"📄 Markdown report saved: {markdown_file}")
    
    # Generate and save CSV summary
    csv_summary = generate_csv_summary(results)
    csv_file = output_path / f"comparison_summary_{timestamp}.csv"
    csv_summary.to_csv(csv_file, index=False)
    
    print(f"📊 CSV summary saved: {csv_file}")
    
    return str(markdown_file), str(csv_file)

def main():
    """Main report generation function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_comparison_report.py <results_file.json>")
        return
    
    results_file = sys.argv[1]
    results = load_comparison_results(results_file)
    
    if results is None:
        return
    
    print("📊 Generating comparison reports...")
    markdown_file, csv_file = save_reports(results)
    
    print("✅ Reports generated successfully!")

if __name__ == "__main__":
    main()