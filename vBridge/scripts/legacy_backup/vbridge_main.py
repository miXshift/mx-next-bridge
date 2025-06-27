"""
Main VBridge Orchestrator

This module contains the main VBridge class that coordinates the execution
of all 4 steps in the KPI analysis process.
"""

import pandas as pd
import os
from typing import Dict, Any
from config_manager import ConfigManager
from data_processor import DataProcessor
from analysis_steps import (
    Step1KPICalculation,
    Step2AbsoluteContributions,
    Step3MixRateContributions,
    Step4AcosRoasInfinityHandling,
    SummaryReportGenerator,
    UnifiedOutputCollector
)


class VBridge:
    """
    Main orchestrator class for the 4-step KPI analysis process.
    
    This class coordinates the execution of all 4 steps:
    1. KPI Calculation
    2. Mix Contribution (Absolute Metrics)
    3. Mix Rate Contribution (Calculated KPIs)
    4. ACoS/ROAS Infinity Handling
    """
    
    def __init__(self, output_dir: str = 'output', output_format: str = 'separate'):
        """
        Initialize VBridge with configuration and output directory
        
        Args:
            output_dir: Directory to save all output files
            output_format: Output format - 'separate', 'unified', or 'excel'
                          'separate': Individual CSV files in subdirectories (default)
                          'unified': Single file with sections
                          'excel': Single file matching Excel source of truth format
        """
        self.config = ConfigManager()
        self.data_processor = DataProcessor(self.config)
        self.output_dir = output_dir
        self.output_format = output_format
        
        # Validate output format
        valid_formats = ['separate', 'unified', 'excel']
        if output_format not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize unified collector if needed
        if output_format in ['unified', 'excel']:
            collector_format = 'excel' if output_format == 'excel' else 'sections'
            self.unified_collector = UnifiedOutputCollector(output_format=collector_format)
        else:
            self.unified_collector = None
        
        # Initialize all analysis steps
        self.step1 = Step1KPICalculation(self.config, output_dir, self.unified_collector)
        self.step2 = Step2AbsoluteContributions(self.config, output_dir, self.unified_collector)
        self.step3 = Step3MixRateContributions(self.config, output_dir, self.unified_collector)
        self.step4 = Step4AcosRoasInfinityHandling(self.config, output_dir, self.unified_collector)
        self.summary_generator = SummaryReportGenerator(self.config, output_dir, self.unified_collector)
    
    def run_complete_analysis(self, csv_file_path: str, p1_start_date: str, p1_end_date: str,
                            p2_start_date: str, p2_end_date: str) -> Dict[str, Any]:
        """
        Run the complete 4-step analysis process as outlined in the README
        
        Args:
            csv_file_path: Path to the CSV data file
            p1_start_date: Start date for Period 1 (YYYY-MM-DD format)
            p1_end_date: End date for Period 1 (YYYY-MM-DD format)
            p2_start_date: Start date for Period 2 (YYYY-MM-DD format)
            p2_end_date: End date for Period 2 (YYYY-MM-DD format)
            
        Returns:
            Dictionary containing all analysis results
        """
        print("=" * 60)
        print("STARTING COMPLETE 4-STEP KPI ANALYSIS")
        if self.output_format == 'excel':
            print("MODE: Excel-Style Output (Single File)")
        elif self.output_format == 'unified':
            print("MODE: Unified Output (Single File)")
        else:
            print("MODE: Individual Files")
        print("=" * 60)
        
        # Convert date strings to pandas timestamps
        p1_start = pd.to_datetime(p1_start_date)
        p1_end = pd.to_datetime(p1_end_date)
        p2_start = pd.to_datetime(p2_start_date)
        p2_end = pd.to_datetime(p2_end_date)
        
        # Load and preprocess data
        print("\n=== LOADING AND PREPROCESSING DATA ===")
        full_df = self.data_processor.load_and_preprocess_data(csv_file_path)
        if full_df is None:
            print("✗ Failed to load data. Exiting.")
            return {}
        print(f"✓ Loaded {len(full_df)} rows of data")
        
        # Step 1: Calculate all KPIs
        p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis = self.step1.execute(
            full_df, p1_start, p1_end, p2_start, p2_end
        )
        if p1_kpis is None:
            return {}
        
        # Store results for Excel format if needed
        if self.output_format == 'excel' and self.unified_collector:
            p1_period_name = p1_start.strftime('%B %Y')
            p2_period_name = p2_start.strftime('%B %Y')
            self.unified_collector.store_analysis_result('p1_kpis', p1_kpis)
            self.unified_collector.store_analysis_result('p2_kpis', p2_kpis)
            self.unified_collector.store_analysis_result('p1_totals', p1_totals_kpis)
            self.unified_collector.store_analysis_result('p2_totals', p2_totals_kpis)
            self.unified_collector.store_analysis_result('p1_period_name', p1_period_name)
            self.unified_collector.store_analysis_result('p2_period_name', p2_period_name)
        
        # Step 2: Calculate all absolute metric contributions
        absolute_contributions = self.step2.execute(
            p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis,
            p1_start, p1_end, p2_start, p2_end
        )
        
        # Store absolute contributions for Excel format
        if self.output_format == 'excel' and self.unified_collector and absolute_contributions:
            for metric_name, contributions in absolute_contributions.items():
                self.unified_collector.store_contribution('absolute', metric_name, contributions)
        
        # Step 3: Calculate all mix rate contributions
        mix_rate_contributions = self.step3.execute(
            p1_kpis, p2_kpis, p2_totals_kpis, p1_totals_kpis,
            p1_start, p1_end, p2_start, p2_end
        )
        
        # Store mix rate contributions for Excel format
        if self.output_format == 'excel' and self.unified_collector and mix_rate_contributions:
            for metric_name, contributions in mix_rate_contributions.items():
                self.unified_collector.store_contribution('mix_rate', metric_name, contributions)
        
        # Step 4: Apply ACoS/ROAS infinity handling
        final_acos_roas = self.step4.execute(
            mix_rate_contributions, absolute_contributions,
            p1_kpis, p2_kpis,  # Add these missing parameters
            p1_start, p1_end, p2_start, p2_end
        )
        
        # Store ACoS/ROAS contributions for Excel format
        if self.output_format == 'excel' and self.unified_collector and final_acos_roas is not None:
            self.unified_collector.store_analysis_result('acos_roas_contributions', final_acos_roas)
        
        # Generate summary report
        self.summary_generator.execute(
            p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis
        )
        
        # Save unified output if enabled
        if self.output_format in ['unified', 'excel'] and self.unified_collector:
            if self.output_format == 'excel':
                unified_file_path = os.path.join(self.output_dir, 'vbridge_excel_style_analysis.csv')
            else:
                unified_file_path = os.path.join(self.output_dir, 'vbridge_unified_analysis.csv')
            
            self.unified_collector.save_unified_file(unified_file_path)
            print(f"\n✓ Saved {self.output_format} analysis to: {unified_file_path}")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        
        if self.output_format == 'excel':
            print(f"Excel-style output saved to: {self.output_dir}/vbridge_excel_style_analysis.csv")
            print("\nThis single file matches the Excel source of truth format with:")
            print("- Multi-metric layout with all KPIs side-by-side")
            print("- Totals row followed by individual campaigns")
            print("- Period values, net changes, % changes, and contributions")
            print("- Proper formatting (currency, percentages, BPS)")
        elif self.output_format == 'unified':
            print(f"Unified output saved to: {self.output_dir}/vbridge_unified_analysis.csv")
            print("\nThis single file contains all analysis results organized by sections:")
            print("- Step 1: KPI calculations and period comparisons")
            print("- Step 2: Combined absolute metric contributions")
            print("- Step 3: Combined mix/rate contributions")
            print("- Step 4: ACoS/ROAS final contributions")
            print("- Summary: All campaign KPIs, totals, and MoM changes")
        else:
            print(f"All outputs saved to: {self.output_dir}/")
            print("\nGenerated files (1 file per step):")
            print("📁 kpi_calculation/")
            print("   📄 period_comparison.csv")
            print("   ⏭️  Individual P1/P2 KPI files skipped (data still processed)")
            print("📁 absolute_contributions/")
            print("   📄 all_absolute_metric_contributions.csv")
            print("📁 mix_rate_contributions/")
            print("   📄 all_mix_rate_contributions.csv")
            print("📁 acos_roas_final/")
            print("   📄 acos_roas_final_contributions.csv")
            print("📁 summary_reports/")
            print("   📄 complete_summary_report.csv")
        
        return {
            'p1_kpis': p1_kpis,
            'p2_kpis': p2_kpis,
            'p1_totals_kpis': p1_totals_kpis,
            'p2_totals_kpis': p2_totals_kpis,
            'absolute_contributions': absolute_contributions,
            'mix_rate_contributions': mix_rate_contributions,
            'final_acos_roas': final_acos_roas
        }


# Example usage and main execution
if __name__ == '__main__':
    # Initialize VBridge with unified output disabled to generate individual files
    vbridge = VBridge(output_dir='output', unified_output=False)
    
    # Define file path and date ranges for P1 and P2
    csv_file_path = 'Hydrapak YTD - campaign.csv'

    # Define P1 and P2 date ranges (full months for MoM comparison)
    p1_start_date = '2025-01-01'
    p1_end_date = '2025-01-31'
    p2_start_date = '2025-02-01'
    p2_end_date = '2025-02-28'

    # Run the complete 4-step analysis
    results = vbridge.run_complete_analysis(
        csv_file_path, p1_start_date, p1_end_date, p2_start_date, p2_end_date
    ) 