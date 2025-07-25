"""
Example script demonstrating Mix Bridge analysis using the modular toolkit.
This script shows how to use the modules together for a complete analysis workflow.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from config import AnalysisConfig, default_config
from excel_operations import load_workbook_values_only, find_header_row, get_column_headers
from dataframe_operations import read_csv_with_multiheaders, merge_period_data, export_to_csv
from bridge_calculations import BridgeCalculator, create_bridge_summary
from data_comparison import compare_dataframes, generate_comparison_summary
from validation import DataValidator, validate_excel_file_structure
from reporting import ReportGenerator, print_welcome_message, print_completion_message

def analyze_mix_bridge_excel(excel_path: str, 
                           csv_path: str,
                           config: AnalysisConfig) -> Dict[str, Any]:
    """
    Complete Mix Bridge analysis workflow.
    
    Args:
        excel_path: Path to Excel file
        csv_path: Path to CSV output file
        config: Analysis configuration
        
    Returns:
        Analysis results dictionary
    """
    start_time = time.time()
    output_files = []
    
    print_welcome_message()
    
    reporter = ReportGenerator(config)
    validator = DataValidator(config)
    calculator = BridgeCalculator(config)
    
    # Step 1: Validate Excel file structure
    print("\n1. Validating Excel file structure...")
    expected_sheets = ["Campaign Tab", "Keyword Tab", "Product Tab"]
    excel_validation = validate_excel_file_structure(excel_path, expected_sheets)
    
    if not excel_validation.is_valid:
        print("❌ Excel file validation failed")
        excel_validation.print_summary()
        return {"error": "Excel validation failed", "validation": excel_validation.get_summary()}
    
    print("✅ Excel file validation passed")
    
    # Step 2: Load Excel data
    print("\n2. Loading Excel data...")
    try:
        workbook = load_workbook_values_only(excel_path)
        worksheet = workbook["Campaign Tab"]  # Use campaign tab
        
        # Find header row
        header_row = find_header_row(worksheet)
        if not header_row:
            raise ValueError("Could not find header row in Excel file")
        
        print(f"✅ Found headers at row {header_row}")
        
        # Get column headers
        headers = get_column_headers(worksheet, header_row)
        print(f"✅ Found {len(headers)} columns")
        
    except Exception as e:
        print(f"❌ Error loading Excel: {str(e)}")
        return {"error": f"Excel loading failed: {str(e)}"}
    
    # Step 3: Load CSV data (if exists)
    csv_data = None
    if Path(csv_path).exists():
        print("\n3. Loading CSV data for comparison...")
        try:
            csv_data = read_csv_with_multiheaders(csv_path)
            print(f"✅ Loaded CSV with {len(csv_data)} rows")
        except Exception as e:
            print(f"⚠️ Could not load CSV: {str(e)}")
    
    # Step 4: Extract data from Excel to DataFrame
    print("\n4. Converting Excel to DataFrame...")
    try:
        import pandas as pd
        
        # Extract data starting from header row
        data_rows = []
        for row in range(header_row + 1, worksheet.max_row + 1):
            row_data = {}
            for col_name, col_num in headers.items():
                cell_value = worksheet.cell(row=row, column=col_num).value
                row_data[col_name] = cell_value
            data_rows.append(row_data)
        
        excel_df = pd.DataFrame(data_rows)
        
        # Remove empty rows
        excel_df = excel_df.dropna(how='all')
        
        print(f"✅ Created DataFrame with {len(excel_df)} rows")
        
    except Exception as e:
        print(f"❌ Error converting Excel to DataFrame: {str(e)}")
        return {"error": f"Excel conversion failed: {str(e)}"}
    
    # Step 5: Validate data structure
    print("\n5. Validating data structure...")
    
    # Define required columns for Mix Bridge
    required_columns = ["Campaign"]  # Minimum required
    numeric_columns = []
    
    # Find numeric columns
    for col in excel_df.columns:
        if excel_df[col].dtype in ['int64', 'float64'] or col in ['Spend', 'Clicks', 'Impressions']:
            numeric_columns.append(col)
    
    data_validation = validator.validate_complete_dataset(
        excel_df, 
        required_columns, 
        numeric_columns
    )
    
    if data_validation.errors:
        print("❌ Data validation found errors")
        data_validation.print_summary()
    else:
        print("✅ Data validation passed")
    
    # Step 6: Perform Mix Bridge calculations
    print("\n6. Performing Mix Bridge calculations...")
    try:
        # For demo, assume we have P1 and P2 data in same sheet
        # In real scenario, you'd have separate period data
        
        # Create sample P1/P2 mapping (this would be determined by your data structure)
        p1_columns = {}
        p2_columns = {}
        
        # Find metrics that might have P1/P2 data
        for col in excel_df.columns:
            if any(metric in col for metric in ['Spend', 'Clicks', 'Impressions']):
                if 'P1' in col or 'Jan' in col:
                    metric_name = col.replace('P1', '').replace('Jan', '').strip()
                    p1_columns[metric_name] = col
                elif 'P2' in col or 'Feb' in col:
                    metric_name = col.replace('P2', '').replace('Feb', '').strip()
                    p2_columns[metric_name] = col
        
        if p1_columns and p2_columns:
            # Calculate Mix Bridge analytics
            bridge_df = calculator.process_dataframe(
                excel_df, 
                p1_columns, 
                p2_columns
            )
            
            print(f"✅ Calculated Mix Bridge analytics for {len(p1_columns)} metrics")
            
            # Create summary
            metrics = list(p1_columns.keys())
            bridge_summary = create_bridge_summary(bridge_df, metrics)
            
        else:
            print("⚠️ Could not find P1/P2 columns for Mix Bridge calculation")
            bridge_df = excel_df
            bridge_summary = pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error in Mix Bridge calculations: {str(e)}")
        bridge_df = excel_df
        bridge_summary = pd.DataFrame()
    
    # Step 7: Compare with CSV if available
    comparison_result = None
    if csv_data is not None:
        print("\n7. Comparing Excel vs CSV data...")
        try:
            comparison_result = compare_dataframes(
                excel_df, 
                csv_data,
                config=config
            )
            
            if comparison_result.summary:
                match_rate = comparison_result.summary.get('match_rate', 0) * 100
                print(f"✅ Comparison complete - {match_rate:.1f}% match rate")
            
        except Exception as e:
            print(f"❌ Error in comparison: {str(e)}")
    
    # Step 8: Generate outputs
    print("\n8. Generating output files...")
    try:
        output_dir = Path(config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Export processed data to CSV
        bridge_csv_path = output_dir / "mix_bridge_analysis.csv"
        export_to_csv(bridge_df, bridge_csv_path, config)
        output_files.append(str(bridge_csv_path))
        
        # Export summary if available
        if not bridge_summary.empty:
            summary_csv_path = output_dir / "mix_bridge_summary.csv"
            bridge_summary.to_csv(summary_csv_path, index=False)
            output_files.append(str(summary_csv_path))
        
        # Export comparison results if available
        if comparison_result:
            comparison_csv_path = output_dir / "comparison_results.csv"
            from data_comparison import export_comparison_to_csv
            export_comparison_to_csv(comparison_result, comparison_csv_path)
            output_files.append(str(comparison_csv_path))
            
            # Generate comparison summary
            comparison_summary_path = output_dir / "comparison_summary.json"
            generate_comparison_summary(comparison_result, comparison_summary_path)
            output_files.append(str(comparison_summary_path))
        
        print(f"✅ Generated {len(output_files)} output files")
        
    except Exception as e:
        print(f"❌ Error generating outputs: {str(e)}")
    
    # Step 9: Generate reports
    print("\n9. Generating reports...")
    try:
        # Console report
        if comparison_result:
            report_content = reporter.generate_comparison_report(
                comparison_result, 
                format_type="console"
            )
            print(report_content)
        
        # Bridge analysis report
        if not bridge_summary.empty:
            bridge_report = reporter.generate_bridge_analysis_report(
                bridge_df,
                list(p1_columns.keys()) if p1_columns else [],
                format_type="console"
            )
            print(bridge_report)
        
    except Exception as e:
        print(f"❌ Error generating reports: {str(e)}")
    
    # Completion
    duration = time.time() - start_time
    print_completion_message(duration, output_files)
    
    return {
        "success": True,
        "duration": duration,
        "output_files": output_files,
        "excel_rows": len(excel_df),
        "csv_rows": len(csv_data) if csv_data is not None else 0,
        "comparison_summary": comparison_result.get_summary() if comparison_result else None,
        "validation_summary": data_validation.get_summary()
    }

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mix Bridge Analysis Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python example_analysis.py data.xlsx
  python example_analysis.py data.xlsx --csv output.csv
  python example_analysis.py data.xlsx --config custom_config.json
        """
    )
    
    parser.add_argument("excel_path", help="Path to Excel file")
    parser.add_argument("--csv", help="Path to CSV file for comparison")
    parser.add_argument("--config", help="Path to configuration JSON file")
    parser.add_argument("--output-dir", help="Output directory", default="../output")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = AnalysisConfig.from_dict(config_dict)
    else:
        config = default_config
    
    # Set output directory
    config.output_dir = Path(args.output_dir)
    
    # Run analysis
    result = analyze_mix_bridge_excel(
        args.excel_path,
        args.csv or "",
        config
    )
    
    # Exit with appropriate code
    if result.get("success", False):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()