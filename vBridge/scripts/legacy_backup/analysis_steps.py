"""
Analysis Steps for vBridge KPI Analysis

This module contains the base AnalysisStep class and all 4 step implementations:
1. Step1KPICalculation
2. Step2AbsoluteContributions  
3. Step3MixRateContributions
4. Step4AcosRoasInfinityHandling
5. SummaryReportGenerator
"""

import pandas as pd
import numpy as np
import os
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, Any, List
from config_manager import ConfigManager
from data_processor import DataProcessor
from bridge_calculations_improved import (
    BridgeCalculationUtils,
    ImprovedMixBridgeCalculator,
    ImprovedMixRateCalculator,
    ImprovedInfinityHandler,
    BridgeValidation
)


class UnifiedOutputCollector:
    """Collects all analysis outputs for unified file generation"""
    
    def __init__(self, output_format: str = 'sections'):
        """
        Initialize the collector
        
        Args:
            output_format: 'sections' for traditional sectioned output, 'excel' for Excel-style format
        """
        self.sections = {}
        self.section_order = []
        self.output_format = output_format
        
        # Store analysis results for Excel format
        self.analysis_results = {
            'p1_kpis': None,
            'p2_kpis': None,
            'p1_totals': None,
            'p2_totals': None,
            'absolute_contributions': {},
            'mix_rate_contributions': {},
            'acos_roas_contributions': None,
            'p1_period_name': 'January 2025',
            'p2_period_name': 'February 2025'
        }
    
    def add_section(self, section_name: str, data: pd.DataFrame, description: str = ""):
        """Add a section to the unified output"""
        self.sections[section_name] = {
            'data': data,
            'description': description
        }
        if section_name not in self.section_order:
            self.section_order.append(section_name)
    
    def store_analysis_result(self, result_type: str, data: Any, **kwargs):
        """Store analysis results for Excel format generation"""
        if result_type in self.analysis_results:
            self.analysis_results[result_type] = data
        
        # Handle additional parameters
        for key, value in kwargs.items():
            if key in self.analysis_results:
                self.analysis_results[key] = value
    
    def store_contribution(self, contribution_type: str, metric_name: str, data: Any):
        """Store contribution data for specific metrics"""
        if contribution_type == 'absolute':
            self.analysis_results['absolute_contributions'][metric_name] = data
        elif contribution_type == 'mix_rate':
            self.analysis_results['mix_rate_contributions'][metric_name] = data
    
    def save_unified_file(self, output_path: str):
        """Save all sections to a single unified CSV file"""
        if self.output_format == 'excel':
            self._save_excel_format(output_path)
        else:
            self._save_sections_format(output_path)
    
    def _save_sections_format(self, output_path: str):
        """Save in traditional sectioned format"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            for i, section_name in enumerate(self.section_order):
                section = self.sections[section_name]
                
                # Add section header
                f.write(f"\n{'='*80}\n")
                f.write(f"SECTION: {section_name.upper()}\n")
                if section['description']:
                    f.write(f"DESCRIPTION: {section['description']}\n")
                f.write(f"{'='*80}\n\n")
                
                # Add the data
                section['data'].to_csv(f, index=True)
                f.write("\n")
    
    def _save_excel_format(self, output_path: str):
        """Save in Excel-style format"""
        from excel_style_output import ExcelStyleOutputGenerator
        
        generator = ExcelStyleOutputGenerator()
        
        # Generate Excel-style DataFrame
        excel_df = generator.generate_excel_style_output(
            p1_kpis=self.analysis_results['p1_kpis'],
            p2_kpis=self.analysis_results['p2_kpis'],
            p1_totals=self.analysis_results['p1_totals'],
            p2_totals=self.analysis_results['p2_totals'],
            absolute_contributions=self.analysis_results['absolute_contributions'],
            mix_rate_contributions=self.analysis_results['mix_rate_contributions'],
            acos_roas_contributions=self.analysis_results['acos_roas_contributions'],
            p1_period_name=self.analysis_results['p1_period_name'],
            p2_period_name=self.analysis_results['p2_period_name']
        )
        
        # Save with Excel-style headers
        generator.save_excel_style_output(
            excel_df, 
            output_path,
            title="Hydrapak - US",
            subtitle=f"{self.analysis_results['p1_period_name']} vs {self.analysis_results['p2_period_name']}"
        )


class AnalysisStep(ABC):
    """Base class for all analysis steps"""
    
    def __init__(self, config: ConfigManager, output_dir: str, unified_collector: UnifiedOutputCollector = None):
        self.config = config
        self.output_dir = output_dir
        self.unified_collector = unified_collector
        
        # Create step-specific subdirectory only if not using unified output
        if unified_collector is None:
            self.step_output_dir = os.path.join(output_dir, self.get_step_name())
            os.makedirs(self.step_output_dir, exist_ok=True)
        else:
            self.step_output_dir = None
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the analysis step"""
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Return the name of the step for directory organization"""
        return "kpi_calculation"
    
    def _save_results(self, data: pd.DataFrame, filename: str, description: str = ""):
        """Save results either to unified collector or individual files"""
        if self.unified_collector is not None:
            # Add to unified collector with step prefix
            section_name = f"{self.get_step_name()}_{filename.replace('.csv', '')}"
            self.unified_collector.add_section(section_name, data, description)
            print(f"✓ Added {filename} to unified output")
        else:
            # Save to individual file (original behavior)
            filepath = os.path.join(self.step_output_dir, filename)
            data.to_csv(filepath, index=True)
            print(f"✓ Saved {filename} to {self.step_output_dir}/")


class Step1KPICalculation(AnalysisStep):
    """Step 1: Calculate all KPIs for both periods"""
    
    def get_step_name(self) -> str:
        return "kpi_calculation"
    
    def execute(self, full_df: pd.DataFrame, p1_start_date: pd.Timestamp, p1_end_date: pd.Timestamp,
                p2_start_date: pd.Timestamp, p2_end_date: pd.Timestamp) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Execute Step 1: Calculate all KPIs for both periods
        
        Returns:
            Tuple of (p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis)
        """
        print("\n=== STEP 1: KPI CALCULATION ===")
        
        data_processor = DataProcessor(self.config)
        
        # Aggregate data for P1 and P2
        p1_aggregated_data = data_processor.aggregate_data_for_period(full_df, p1_start_date, p1_end_date)
        p2_aggregated_data = data_processor.aggregate_data_for_period(full_df, p2_start_date, p2_end_date)
        
        if p1_aggregated_data.empty and p2_aggregated_data.empty:
            print("No data for both P1 and P2. Exiting.")
            return None, None, None, None
        
        # Calculate KPIs for P1 and P2
        p1_kpis = self._calculate_kpis(p1_aggregated_data)
        p2_kpis = self._calculate_kpis(p2_aggregated_data)
        
        # Calculate totals for P1 and P2
        p1_totals_kpis = self._calculate_kpis(p1_aggregated_data.sum().to_frame().T.set_index(pd.Index(['TOTAL'])))
        p2_totals_kpis = self._calculate_kpis(p2_aggregated_data.sum().to_frame().T.set_index(pd.Index(['TOTAL'])))
        
        print(f"✓ Calculated KPIs for {len(p1_kpis)} campaigns in P1 and {len(p2_kpis)} campaigns in P2")
        print(f"✓ Generated totals for both periods")
        
        # Save KPI calculations to files
        self._save_kpi_files(p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis, p1_start_date, p1_end_date, p2_start_date, p2_end_date)
        
        return p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis
    
    def _save_kpi_files(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                       p1_totals_kpis: pd.DataFrame, p2_totals_kpis: pd.DataFrame,
                       p1_start_date: pd.Timestamp, p1_end_date: pd.Timestamp,
                       p2_start_date: pd.Timestamp, p2_end_date: pd.Timestamp):
        """Save all KPI calculations to files"""
        
        # Format dates for file descriptions
        p1_period = f"{p1_start_date.strftime('%Y-%m-%d')} to {p1_end_date.strftime('%Y-%m-%d')}"
        p2_period = f"{p2_start_date.strftime('%Y-%m-%d')} to {p2_end_date.strftime('%Y-%m-%d')}"
        # New: Get month/year for multi-level header
        p1_period_name = p1_start_date.strftime('%B %Y')
        p2_period_name = p2_start_date.strftime('%B %Y')
        
        # Skip saving individual P1/P2 campaign and totals KPI files
        # Data is still calculated and passed to subsequent steps
        # Uncomment the sections below if you need these individual files
        
        # # Save P1 campaign KPIs
        # if not p1_kpis.empty:
        #     description = f"Period 1 ({p1_period}) campaign-level KPIs - all 14 calculated KPIs for each campaign"
        #     self._save_results(p1_kpis, 'p1_campaign_kpis.csv', description)
        #     print(f"✓ Saved P1 campaign KPIs")
        # 
        # # Save P2 campaign KPIs
        # if not p2_kpis.empty:
        #     description = f"Period 2 ({p2_period}) campaign-level KPIs - all 14 calculated KPIs for each campaign"
        #     self._save_results(p2_kpis, 'p2_campaign_kpis.csv', description)
        #     print(f"✓ Saved P2 campaign KPIs")
        # 
        # # Save P1 totals
        # if not p1_totals_kpis.empty:
        #     description = f"Period 1 ({p1_period}) total/aggregate KPIs - overall performance across all campaigns"
        #     self._save_results(p1_totals_kpis, 'p1_totals_kpis.csv', description)
        #     print(f"✓ Saved P1 totals")
        # 
        # # Save P2 totals
        # if not p2_totals_kpis.empty:
        #     description = f"Period 2 ({p2_period}) total/aggregate KPIs - overall performance across all campaigns"
        #     self._save_results(p2_totals_kpis, 'p2_totals_kpis.csv', description)
        #     print(f"✓ Saved P2 totals")
        
        print(f"✓ Skipped individual KPI files (data still available for subsequent steps)")
        
        # Create a combined comparison file
        if not p1_kpis.empty and not p2_kpis.empty:
            # Pass new period names for multi-level header
            comparison_df = self._create_period_comparison(
                p1_kpis, p2_kpis, p1_totals_kpis, p2_totals_kpis, p1_period_name, p2_period_name
            )
            description = f"Period comparison - {p1_period_name} vs {p2_period_name} with MoM changes for all campaigns and totals"
            self._save_results(comparison_df, 'period_comparison.csv', description)
            print(f"✓ Saved period comparison")
    
    def _create_period_comparison(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame,
                                 p1_totals_kpis: pd.DataFrame, p2_totals_kpis: pd.DataFrame,
                                 p1_period_name: str, p2_period_name: str) -> pd.DataFrame:
        """
        Create a comprehensive period comparison file with multi-level columns:
        Top level: Metric
        Second level: [P1, P2, Net Change, % Change, Contribution]
        For metrics using basis points, appends "(BPS)" to the Contribution column header
        """
        # Align campaign indices
        all_campaigns = p1_kpis.index.union(p2_kpis.index)
        p1_aligned = p1_kpis.reindex(all_campaigns, fill_value=0)
        p2_aligned = p2_kpis.reindex(all_campaigns, fill_value=0)
        
        # Get metric order
        required_kpi_cols = [
            'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
            'Impressions', 'Clicks', 'Clickthrough Rate', 'Cost Per Click', 'Same SKU Ad Sales',
            'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders'
        ]
        
        # Prepare multi-level columns
        columns = []
        data = {}
        for metric in required_kpi_cols:
            display_name = self.config.get_kpi_display_name(metric)
            kpi_format = self.config.kpi_format.get(display_name, {})
            
            # Check if this metric uses basis points for contribution
            uses_bps = (
                'formats' in kpi_format 
                and 'contribution' in kpi_format['formats']
                and kpi_format['formats']['contribution'].get('type') == 'bps'
            )
            
            # Top-level: metric, second-level: [P1, P2, Net Change, % Change, Contribution]
            contribution_label = 'Contribution (BPS)' if uses_bps else 'Contribution'
            col_tuples = [
                (metric, p1_period_name),
                (metric, p2_period_name),
                (metric, 'Net Change'),
                (metric, '% Change'),
                (metric, contribution_label)
            ]
            columns.extend(col_tuples)
            
            # Get values for each campaign
            p1_vals = p1_aligned[metric] if metric in p1_aligned.columns else pd.Series(0, index=all_campaigns)
            p2_vals = p2_aligned[metric] if metric in p2_aligned.columns else pd.Series(0, index=all_campaigns)
            net_change = p2_vals - p1_vals
            # Avoid division by zero for % change
            pct_change = np.where(p1_vals != 0, (p2_vals - p1_vals) / p1_vals, 0)
            
            # For contribution, use the correct calculation based on bridge_type
            # For now, use net_change as the base, but format it using the contribution format
            contribution = net_change.copy()
            
            # Format contribution using config
            if 'formats' in kpi_format and 'contribution' in kpi_format['formats']:
                contribution = contribution.apply(lambda x: self.config.format_value(x, kpi_format['formats']['contribution']))
            else:
                contribution = contribution.apply(lambda x: f"{x:+.2f}")
            
            # Format period values, net change, and % change
            if 'formats' in kpi_format:
                p1_vals_fmt = p1_vals.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                p2_vals_fmt = p2_vals.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                net_change_fmt = net_change.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('net_change', {'type': 'decimal', 'decimals': 2})))
                pct_change_fmt = pct_change * 100
                pct_change_fmt = pd.Series(pct_change_fmt, index=all_campaigns).apply(lambda x: self.config.format_value(x/100, kpi_format['formats'].get('percent_change', {'type': 'percentage'})))
            else:
                p1_vals_fmt = p1_vals
                p2_vals_fmt = p2_vals
                net_change_fmt = net_change
                pct_change_fmt = pct_change
            
            # Store in data dict
            data[(metric, p1_period_name)] = p1_vals_fmt
            data[(metric, p2_period_name)] = p2_vals_fmt
            data[(metric, 'Net Change')] = net_change_fmt
            data[(metric, '% Change')] = pct_change_fmt
            data[(metric, contribution_label)] = contribution
        
        # Build MultiIndex DataFrame
        columns = pd.MultiIndex.from_tuples(columns)
        comparison_df = pd.DataFrame(data, index=all_campaigns)
        comparison_df = comparison_df.reindex(columns=columns)
        
        # Add totals row if both totals exist
        if not p1_totals_kpis.empty and not p2_totals_kpis.empty:
            totals_row = {}
            for metric in required_kpi_cols:
                # P1, P2
                p1_total = p1_totals_kpis.loc['TOTAL', metric] if metric in p1_totals_kpis.columns else 0
                p2_total = p2_totals_kpis.loc['TOTAL', metric] if metric in p2_totals_kpis.columns else 0
                net_change = p2_total - p1_total
                pct_change = (net_change / p1_total) if p1_total != 0 else 0
                
                display_name = self.config.get_kpi_display_name(metric)
                kpi_format = self.config.kpi_format.get(display_name, {})
                
                # Check if this metric uses basis points for contribution
                uses_bps = (
                    'formats' in kpi_format 
                    and 'contribution' in kpi_format['formats']
                    and kpi_format['formats']['contribution'].get('type') == 'bps'
                )
                contribution_label = 'Contribution (BPS)' if uses_bps else 'Contribution'
                
                # Format
                if 'formats' in kpi_format:
                    p1_total_fmt = self.config.format_value(p1_total, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                    p2_total_fmt = self.config.format_value(p2_total, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                    net_change_fmt = self.config.format_value(net_change, kpi_format['formats'].get('net_change', {'type': 'decimal', 'decimals': 2}))
                    pct_change_fmt = self.config.format_value(pct_change, kpi_format['formats'].get('percent_change', {'type': 'percentage'}))
                    contribution_fmt = self.config.format_value(net_change, kpi_format['formats'].get('contribution', {'type': 'decimal', 'decimals': 2}))
                else:
                    p1_total_fmt = p1_total
                    p2_total_fmt = p2_total
                    net_change_fmt = net_change
                    pct_change_fmt = pct_change
                    contribution_fmt = net_change
                
                totals_row[(metric, p1_period_name)] = p1_total_fmt
                totals_row[(metric, p2_period_name)] = p2_total_fmt
                totals_row[(metric, 'Net Change')] = net_change_fmt
                totals_row[(metric, '% Change')] = pct_change_fmt
                totals_row[(metric, contribution_label)] = contribution_fmt
            
            # Add totals row
            totals_series = pd.Series(totals_row, name='TOTAL')
            comparison_df = pd.concat([comparison_df, totals_series.to_frame().T])
        
        return comparison_df
    
    def _calculate_kpis(self, aggregated_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates all specified KPIs from an aggregated DataFrame.
        KPIs: Spend, Total Ad Sales, ACoS, ROAS, Conversion Rate, Impressions, Clicks,
              Clickthrough Rate, Cost Per Click, Same SKU Ad Sales, Other SKU Sales, 
              Same SKU Ad Orders, Other SKU Ad Orders, Total Ad Orders.
        """
        kpis = aggregated_df.copy()

        # Rename columns for clarity
        kpis.rename(columns={
            self.config.COST_COL: 'Spend',
            self.config.SALES_COL_ATTR: 'Total Ad Sales',
            self.config.IMPRESSIONS_COL: 'Impressions',
            self.config.CLICKS_COL: 'Clicks',
            self.config.ORDERS_COL_ATTR: 'Total Ad Orders',
            self.config.SALES_SAME_SKU_COL_ATTR: 'Same SKU Ad Sales',
            self.config.ORDERS_SAME_SKU_COL_ATTR: 'Same SKU Ad Orders'
        }, inplace=True)

        # Calculate derived KPIs
        kpis['ACoS'] = np.where(kpis['Total Ad Sales'] > 0, kpis['Spend'] / kpis['Total Ad Sales'], 0)
        kpis['ROAS'] = np.where(kpis['Spend'] > 0, kpis['Total Ad Sales'] / kpis['Spend'], 0)

        kpis['Conversion Rate'] = np.where(kpis['Clicks'] > 0, kpis['Total Ad Orders'] / kpis['Clicks'], 0)
        kpis['Clickthrough Rate'] = np.where(kpis['Impressions'] > 0, kpis['Clicks'] / kpis['Impressions'], 0)
        kpis['Cost Per Click'] = np.where(kpis['Clicks'] > 0, kpis['Spend'] / kpis['Clicks'], 0)

        kpis['Other SKU Sales'] = kpis['Total Ad Sales'] - kpis['Same SKU Ad Sales']
        kpis['Other SKU Ad Orders'] = kpis['Total Ad Orders'] - kpis['Same SKU Ad Orders']
        
        # Ensure all required columns are present
        required_kpi_cols = [
            'Spend', 'Total Ad Sales', 'ACoS', 'ROAS', 'Conversion Rate',
            'Impressions', 'Clicks', 'Clickthrough Rate', 'Cost Per Click', 'Same SKU Ad Sales',
            'Other SKU Sales', 'Same SKU Ad Orders', 'Other SKU Ad Orders', 'Total Ad Orders'
        ]
        
        for col in required_kpi_cols:
            if col not in kpis.columns:
                kpis[col] = 0.0
                
        return kpis[required_kpi_cols] 


class Step2AbsoluteContributions(AnalysisStep):
    """Step 2: Calculate absolute metric contributions for all 9 absolute metrics"""
    
    def get_step_name(self) -> str:
        return "absolute_contributions"
    
    def execute(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                p1_totals_kpis: pd.DataFrame, p2_totals_kpis: pd.DataFrame,
                p1_start_date: pd.Timestamp, p1_end_date: pd.Timestamp,
                p2_start_date: pd.Timestamp, p2_end_date: pd.Timestamp) -> Dict[str, pd.DataFrame]:
        """
        Execute Step 2: Calculate absolute metric contributions
        
        Returns:
            Dictionary of metric contributions
        """
        print("\n=== STEP 2: MIX CONTRIBUTION (ABSOLUTE METRICS) ===")
        
        # Get period names for column headers
        p1_period_name = p1_start_date.strftime('%B %Y')
        p2_period_name = p2_start_date.strftime('%B %Y')
        
        # Get all metrics with bridge_type "M" from KPI format
        absolute_metrics = []
        for kpi_name, config in self.config.kpi_format.items():
            if config.get('bridge_type') == 'M':
                internal_name = self.config.get_kpi_internal_name(kpi_name)
                absolute_metrics.append(internal_name)
        
        # Fallback to original list if KPI_FORMAT is empty
        if not absolute_metrics:
            absolute_metrics = [
                'Spend', 'Total Ad Sales', 'Impressions', 'Clicks', 
                'Total Ad Orders', 'Same SKU Ad Sales', 'Other SKU Sales',
                'Same SKU Ad Orders', 'Other SKU Ad Orders'
            ]
        
        absolute_contributions = {}
        
        # Create combined DataFrame with multi-level columns
        all_campaigns = p1_kpis.index.union(p2_kpis.index)
        columns = []
        data = {}
        
        for metric in absolute_metrics:
            if metric in p1_kpis.columns and metric in p2_kpis.columns and not p1_totals_kpis.empty:
                try:
                    # Align data
                    p1_aligned = p1_kpis[metric].reindex(all_campaigns, fill_value=0)
                    p2_aligned = p2_kpis[metric].reindex(all_campaigns, fill_value=0)
                    
                    # Calculate contribution
                    contribution = self._calculate_absolute_metric_contribution(
                        p1_aligned,
                        p2_aligned,
                        p1_totals_kpis.loc['TOTAL', metric]
                    )
                    
                    # Get display name and format configuration
                    display_name = self.config.get_kpi_display_name(metric)
                    kpi_format = self.config.kpi_format.get(display_name, {})
                    
                    # Add columns for this metric (new format: Period names, Net Change, % Change (pts), Contribution (BPS))
                    columns.extend([
                        (metric, p1_period_name),
                        (metric, p2_period_name), 
                        (metric, 'Net Change'),
                        (metric, '% Change (pts)'),
                        (metric, 'Contribution (BPS)')
                    ])
                    
                    # Calculate net change and % change
                    net_change = p2_aligned - p1_aligned
                    pct_change = ((p2_aligned - p1_aligned) / p1_aligned * 100).fillna(0)  # % change in percentage points
                    pct_change = pct_change.replace([float('inf'), float('-inf')], 0)
                    
                    # Format values
                    if 'formats' in kpi_format:
                        p1_fmt = p1_aligned.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                        p2_fmt = p2_aligned.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                        net_change_fmt = net_change.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('net_change', {'type': 'decimal', 'decimals': 2})))
                        pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                        contribution_fmt = contribution.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('contribution', {'type': 'bps'})))
                    else:
                        p1_fmt = p1_aligned
                        p2_fmt = p2_aligned
                        net_change_fmt = net_change
                        pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                        contribution_fmt = contribution.apply(lambda x: f"{x:+.0f}")
                    
                    # Store data
                    data[(metric, p1_period_name)] = p1_fmt
                    data[(metric, p2_period_name)] = p2_fmt
                    data[(metric, 'Net Change')] = net_change_fmt
                    data[(metric, '% Change (pts)')] = pct_change_fmt
                    data[(metric, 'Contribution (BPS)')] = contribution_fmt
                    
                    absolute_contributions[metric] = contribution
                    print(f"✓ Calculated {metric} contribution")
                    
                except Exception as e:
                    print(f"✗ Error calculating {metric} contribution: {e}")
            else:
                print(f"✗ Skipping {metric} - missing data or empty totals")
        
        # Create multi-index DataFrame
        if data:
            columns = pd.MultiIndex.from_tuples(columns)
            combined_df = pd.DataFrame(data, index=all_campaigns)
            combined_df = combined_df.reindex(columns=columns)
            
            # Add totals row
            totals_row = {}
            for metric in absolute_metrics:
                if metric in p1_totals_kpis.columns and metric in p2_totals_kpis.columns:
                    p1_total = p1_totals_kpis.loc['TOTAL', metric]
                    p2_total = p2_totals_kpis.loc['TOTAL', metric]
                    net_change = p2_total - p1_total
                    contribution = (net_change / p1_total * 10000) if p1_total != 0 else 0
                    
                    display_name = self.config.get_kpi_display_name(metric)
                    kpi_format = self.config.kpi_format.get(display_name, {})
                    
                    if 'formats' in kpi_format:
                        p1_total_fmt = self.config.format_value(p1_total, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                        p2_total_fmt = self.config.format_value(p2_total, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                        net_change_fmt = self.config.format_value(net_change, kpi_format['formats'].get('net_change', {'type': 'decimal', 'decimals': 2}))
                        contribution_fmt = self.config.format_value(contribution, kpi_format['formats'].get('contribution', {'type': 'bps'}))
                    else:
                        p1_total_fmt = p1_total
                        p2_total_fmt = p2_total
                        net_change_fmt = net_change
                        contribution_fmt = f"{contribution:+.0f}"
                    
                    # Calculate % change for totals
                    pct_change_total = ((p2_total - p1_total) / p1_total * 100) if p1_total != 0 else 0
                    pct_change_total_fmt = f"{pct_change_total:+.1f}"
                    
                    totals_row[(metric, p1_period_name)] = p1_total_fmt
                    totals_row[(metric, p2_period_name)] = p2_total_fmt
                    totals_row[(metric, 'Net Change')] = net_change_fmt
                    totals_row[(metric, '% Change (pts)')] = pct_change_total_fmt
                    totals_row[(metric, 'Contribution (BPS)')] = contribution_fmt
            
            # Add totals row
            totals_series = pd.Series(totals_row, name='TOTAL')
            combined_df = pd.concat([combined_df, totals_series.to_frame().T])
            
            description = f"Absolute metric contributions - {p1_period_name} vs {p2_period_name} - showing campaign-level contributions to period-over-period changes"
            self._save_results(combined_df, 'all_absolute_metric_contributions.csv', description)
            print(f"✓ Saved absolute contributions in period comparison format")
        
        return absolute_contributions
    
    def _calculate_absolute_metric_contribution(self, p1_metric_series: pd.Series, 
                                              p2_metric_series: pd.Series, 
                                              p1_metric_total: float) -> pd.Series:
        """Updated to use improved mix bridge calculation"""
        from bridge_calculations_improved import ImprovedMixBridgeCalculator, BridgeValidation
        
        calculator = ImprovedMixBridgeCalculator()
        validator = BridgeValidation()
        
        result = calculator.calculate_mix_bridge(
            p1_values=p1_metric_series,
            p2_values=p2_metric_series,
            p1_total=p1_metric_total,
            p2_total=p2_metric_series.sum(),
            metric_name="absolute_metric"
        )
        
        # Validate the contributions
        expected_change = (p2_metric_series.sum() - p1_metric_total) / p1_metric_total * 10000 if p1_metric_total != 0 else 0
        is_valid = validator.validate_contribution_sum(
            contributions=result['Total Contribution (BPS)'],
            expected_total_change=expected_change,
            metric_name="absolute_metric"
        )
        
        if not is_valid:
            print(f"⚠️  Validation warning for absolute metric contributions")
        
        return result['Total Contribution (BPS)'] 


class Step3MixRateContributions(AnalysisStep):
    """Step 3: Calculate mix/rate contributions for all calculated KPIs"""
    
    def get_step_name(self) -> str:
        return "mix_rate_contributions"
    
    def execute(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                p2_totals_kpis: pd.DataFrame, p1_totals_kpis: pd.DataFrame,
                p1_start_date: pd.Timestamp, p1_end_date: pd.Timestamp,
                p2_start_date: pd.Timestamp, p2_end_date: pd.Timestamp) -> Dict[str, pd.DataFrame]:
        """
        Execute Step 3: Calculate mix rate contributions
        
        Returns:
            Dictionary of mix rate contributions
        """
        print("\n=== STEP 3: MIX RATE CONTRIBUTION (CALCULATED KPIS) ===")
        
        # Get period names for column headers
        p1_period_name = p1_start_date.strftime('%B %Y')
        p2_period_name = p2_start_date.strftime('%B %Y')
        
        # Get all metrics with bridge_type "MR" from KPI format
        mix_rate_kpis = []
        for kpi_name, config in self.config.kpi_format.items():
            if config.get('bridge_type') in ['MR', 'MR+I']:
                internal_name = self.config.get_kpi_internal_name(kpi_name)
                mix_rate_kpis.append(internal_name)
        
        # Fallback to original list if KPI_FORMAT is empty
        expected_kpis = ['Clickthrough Rate', 'Conversion Rate', 'Cost Per Click', 'ROAS', 'ACoS']
        if not mix_rate_kpis:
            mix_rate_kpis = expected_kpis
        else:
            # Ensure all expected KPIs are included
            for kpi in expected_kpis:
                if kpi not in mix_rate_kpis:
                    mix_rate_kpis.append(kpi)
        
        print(f"Processing mix rate KPIs: {mix_rate_kpis}")
        
        # Define KPI-specific mix drivers and whether they're percentage metrics
        kpi_config = {
            'Clickthrough Rate': {'mix_driver': 'Impressions', 'is_percentage': True},
            'Conversion Rate': {'mix_driver': 'Clicks', 'is_percentage': True},
            'Cost Per Click': {'mix_driver': 'Clicks', 'is_percentage': False},
            'ROAS': {'mix_driver': 'Spend', 'is_percentage': False},
            'ACoS': {'mix_driver': 'Spend', 'is_percentage': True}
        }
        
        mix_rate_contributions = {}
        
        # Create combined DataFrame with multi-level columns
        all_campaigns = p1_kpis.index.union(p2_kpis.index)
        columns = []
        data = {}
        
        for kpi in mix_rate_kpis:
            if kpi not in kpi_config:
                print(f"✗ Skipping {kpi} - no configuration found")
                continue
                
            if kpi not in p1_kpis.columns or kpi not in p2_kpis.columns:
                print(f"✗ Skipping {kpi} - not found in KPI data")
                continue
                
            try:
                config = kpi_config[kpi]
                mix_driver = config['mix_driver']
                is_percentage = config['is_percentage']
                
                # Align data
                p1_aligned = p1_kpis.reindex(all_campaigns, fill_value=0)
                p2_aligned = p2_kpis.reindex(all_campaigns, fill_value=0)
                
                # Calculate mix shares for each period
                p1_total_mix = p1_aligned[mix_driver].sum()
                p2_total_mix = p2_aligned[mix_driver].sum()
                p1_mix = p1_aligned[mix_driver] / p1_total_mix if p1_total_mix > 0 else pd.Series(0, index=all_campaigns)
                p2_mix = p2_aligned[mix_driver] / p2_total_mix if p2_total_mix > 0 else pd.Series(0, index=all_campaigns)
                
                # Calculate the overall KPI value for P2 (weighted average)
                p2_total_kpi = self._calculate_weighted_average_kpi(kpi, p2_aligned)
                
                # Calculate mix rate contribution
                contributions = self._calculate_mix_rate_contribution(
                    p1_kpi_values=p1_aligned[kpi],
                    p2_kpi_values=p2_aligned[kpi],
                    p1_mix_shares=p1_mix,
                    p2_mix_shares=p2_mix,
                    p2_total_kpi_value=p2_total_kpi,
                    is_percentage_metric=is_percentage
                )
                
                # Get display name and format configuration
                display_name = self.config.get_kpi_display_name(kpi)
                kpi_format = self.config.kpi_format.get(display_name, {})
                
                # Determine contribution label
                uses_bps = is_percentage or (
                    'formats' in kpi_format 
                    and 'contribution' in kpi_format['formats']
                    and kpi_format['formats']['contribution'].get('type') == 'bps'
                )
                contribution_label = 'Contribution (BPS)' if uses_bps else 'Contribution'
                
                # Add columns for this KPI (new format: Period names, Net Change, % Change (pts), Contribution (BPS))
                columns.extend([
                    (kpi, p1_period_name),
                    (kpi, p2_period_name),
                    (kpi, 'Net Change'),
                    (kpi, '% Change (pts)'),
                    (kpi, 'Contribution (BPS)')
                ])
                
                # Calculate net change and % change
                net_change = p2_aligned[kpi] - p1_aligned[kpi]
                pct_change = ((p2_aligned[kpi] - p1_aligned[kpi]) / p1_aligned[kpi] * 100).fillna(0)
                pct_change = pct_change.replace([float('inf'), float('-inf')], 0)
                
                # Format values
                if 'formats' in kpi_format:
                    p1_fmt = p1_aligned[kpi].apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                    p2_fmt = p2_aligned[kpi].apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('period_values', {'type': 'decimal', 'decimals': 2})))
                    net_change_fmt = net_change.apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('net_change', {'type': 'decimal', 'decimals': 2})))
                    pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                    contribution_fmt = contributions['Total Contribution'].apply(lambda x: self.config.format_value(x, kpi_format['formats'].get('contribution', {'type': 'bps'})))
                else:
                    p1_fmt = p1_aligned[kpi]
                    p2_fmt = p2_aligned[kpi]
                    net_change_fmt = net_change
                    pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                    if uses_bps:
                        contribution_fmt = contributions['Total Contribution'].apply(lambda x: f"{x:+.0f}")
                    else:
                        contribution_fmt = contributions['Total Contribution'].apply(lambda x: f"{x:+.2f}")
                
                # Store data
                data[(kpi, p1_period_name)] = p1_fmt
                data[(kpi, p2_period_name)] = p2_fmt
                data[(kpi, 'Net Change')] = net_change_fmt
                data[(kpi, '% Change (pts)')] = pct_change_fmt
                data[(kpi, 'Contribution (BPS)')] = contribution_fmt
                
                mix_rate_contributions[kpi] = contributions
                print(f"✓ Calculated {kpi} mix/rate contribution")
                
            except Exception as e:
                print(f"✗ Error calculating {kpi} mix/rate contribution: {e}")
        
        # Create multi-index DataFrame
        if data:
            columns = pd.MultiIndex.from_tuples(columns)
            combined_df = pd.DataFrame(data, index=all_campaigns)
            combined_df = combined_df.reindex(columns=columns)
            
            # Add totals row
            totals_row = {}
            for kpi in mix_rate_kpis:
                if kpi in p1_totals_kpis.columns and kpi in p2_totals_kpis.columns and kpi in mix_rate_contributions:
                    p1_total = p1_totals_kpis.loc['TOTAL', kpi]
                    p2_total = p2_totals_kpis.loc['TOTAL', kpi]
                    net_change = p2_total - p1_total
                    
                    # Sum contributions
                    total_mix_impact = mix_rate_contributions[kpi]['Mix Impact'].sum()
                    total_rate_impact = mix_rate_contributions[kpi]['Rate Impact'].sum()
                    total_contribution = mix_rate_contributions[kpi]['Total Contribution'].sum()
                    
                    display_name = self.config.get_kpi_display_name(kpi)
                    kpi_format_config = self.config.kpi_format.get(display_name, {})
                    
                    # Check if this metric uses basis points
                    is_percentage = kpi_config.get(kpi, {}).get('is_percentage', False)
                    uses_bps = is_percentage or (
                        'formats' in kpi_format_config 
                        and 'contribution' in kpi_format_config['formats']
                        and kpi_format_config['formats']['contribution'].get('type') == 'bps'
                    )
                    contribution_label = 'Contribution (BPS)' if uses_bps else 'Contribution'
                    
                    if 'formats' in kpi_format_config:
                        p1_total_fmt = self.config.format_value(p1_total, kpi_format_config['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                        p2_total_fmt = self.config.format_value(p2_total, kpi_format_config['formats'].get('period_values', {'type': 'decimal', 'decimals': 2}))
                        net_change_fmt = self.config.format_value(net_change, kpi_format_config['formats'].get('net_change', {'type': 'decimal', 'decimals': 2}))
                        mix_impact_fmt = self.config.format_value(total_mix_impact, kpi_format_config['formats'].get('contribution', {'type': 'bps'}))
                        rate_impact_fmt = self.config.format_value(total_rate_impact, kpi_format_config['formats'].get('contribution', {'type': 'bps'}))
                        contribution_fmt = self.config.format_value(total_contribution, kpi_format_config['formats'].get('contribution', {'type': 'bps'}))
                    else:
                        p1_total_fmt = p1_total
                        p2_total_fmt = p2_total
                        net_change_fmt = net_change
                        if uses_bps:
                            mix_impact_fmt = f"{total_mix_impact:+.0f}"
                            rate_impact_fmt = f"{total_rate_impact:+.0f}"
                            contribution_fmt = f"{total_contribution:+.0f}"
                        else:
                            mix_impact_fmt = f"{total_mix_impact:+.2f}"
                            rate_impact_fmt = f"{total_rate_impact:+.2f}"
                            contribution_fmt = f"{total_contribution:+.2f}"
                    
                    totals_row[(kpi, p1_period_name)] = p1_total_fmt
                    totals_row[(kpi, p2_period_name)] = p2_total_fmt
                    totals_row[(kpi, 'Net Change')] = net_change_fmt
                    totals_row[(kpi, 'Mix Impact')] = mix_impact_fmt
                    totals_row[(kpi, 'Rate Impact')] = rate_impact_fmt
                    totals_row[(kpi, contribution_label)] = contribution_fmt
            
            # Add totals row
            totals_series = pd.Series(totals_row, name='TOTAL')
            combined_df = pd.concat([combined_df, totals_series.to_frame().T])
            
            description = f"Mix/Rate contributions - {p1_period_name} vs {p2_period_name} - showing Mix Impact, Rate Impact, and Total Contribution for calculated KPIs"
            self._save_results(combined_df, 'all_mix_rate_contributions.csv', description)
            print(f"✓ Saved mix/rate contributions in period comparison format")
        
        return mix_rate_contributions
    
    def _calculate_weighted_average_kpi(self, kpi: str, p2_kpis: pd.DataFrame) -> float:
        """Calculate the weighted average KPI value for P2"""
        if kpi == 'Clickthrough Rate':
            return p2_kpis['Clicks'].sum() / p2_kpis['Impressions'].sum() if p2_kpis['Impressions'].sum() > 0 else 0
        elif kpi == 'Conversion Rate':
            return p2_kpis['Total Ad Orders'].sum() / p2_kpis['Clicks'].sum() if p2_kpis['Clicks'].sum() > 0 else 0
        elif kpi == 'Cost Per Click':
            return p2_kpis['Spend'].sum() / p2_kpis['Clicks'].sum() if p2_kpis['Clicks'].sum() > 0 else 0
        elif kpi == 'ROAS':
            return p2_kpis['Total Ad Sales'].sum() / p2_kpis['Spend'].sum() if p2_kpis['Spend'].sum() > 0 else 0
        elif kpi == 'ACoS':
            return p2_kpis['Spend'].sum() / p2_kpis['Total Ad Sales'].sum() if p2_kpis['Total Ad Sales'].sum() > 0 else 0
        else:
            return 0
    
    def _calculate_mix_rate_contribution(self, p1_kpi_values: pd.Series, p2_kpi_values: pd.Series,
                                       p1_mix_shares: pd.Series, p2_mix_shares: pd.Series,
                                       p2_total_kpi_value: float, is_percentage_metric: bool = False) -> pd.DataFrame:
        """Updated to use improved mix/rate calculation"""
        from bridge_calculations_improved import ImprovedMixRateCalculator, BridgeValidation
        
        calculator = ImprovedMixRateCalculator()
        validator = BridgeValidation()
        
        # Reconstruct mix driver data from shares (approximation)
        p1_total_driver = 1.0  # Normalized
        p2_total_driver = 1.0
        p1_mix_driver = p1_mix_shares * p1_total_driver
        p2_mix_driver = p2_mix_shares * p2_total_driver
        
        result = calculator.calculate_mix_rate_contribution(
            p1_kpi_values=p1_kpi_values,
            p2_kpi_values=p2_kpi_values,
            p1_mix_driver=p1_mix_driver,
            p2_mix_driver=p2_mix_driver,
            kpi_name="calculated_kpi",
            is_percentage_metric=is_percentage_metric
        )
        
        # Validate mix + rate = total
        is_valid = validator.validate_mix_rate_decomposition(
            mix_impact=result['Mix Impact'],
            rate_impact=result['Rate Impact'],
            total_contribution=result['Total Contribution'],
            metric_name="calculated_kpi"
        )
        
        if not is_valid:
            print(f"⚠️  Validation warning for mix/rate decomposition")
        
        return result[['Mix Impact', 'Rate Impact', 'Total Contribution']]
    
    def _add_mom_change_formatting(self, contributions: pd.DataFrame, kpi: str, 
                                 p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, is_percentage: bool):
        """Add MoM change columns with proper formatting"""
        display_name = self.config.get_kpi_display_name(kpi)
        mom_change = p2_kpis[kpi] - p1_kpis[kpi]
        
        if display_name in self.config.kpi_format:
            # Use format configuration for MoM change
            kpi_format_config = self.config.kpi_format[display_name]
            change_type = kpi_format_config.get('change_type', 'net_change')
            
            if change_type == 'pts_change':
                contributions['MoM Change'] = mom_change.apply(
                    lambda x: self.config.format_change_value(x, display_name, 'pts_change')
                )
            else:
                contributions['MoM Change'] = mom_change.apply(
                    lambda x: self.config.format_change_value(x, display_name, 'net_change')
                )
            
            # Format contribution columns
            for col in ['Mix Impact', 'Rate Impact', 'Total Contribution']:
                contributions[f'{col} (Formatted)'] = contributions[col].apply(
                    lambda x: self.config.format_contribution_value(x, display_name)
                )
        else:
            # Fallback formatting
            if is_percentage:
                contributions['MoM Change (BPS)'] = (mom_change * 10000).apply(lambda x: f"{x:+.0f} BPS")
            elif kpi == 'ROAS':
                def format_dollar_hundreds(x):
                    if pd.isna(x):
                        return ''
                    return f"${int(round(x, -2)):,}" if x >= 0 else f"-${int(round(abs(x), -2)):,}"
                contributions['MoM Change ($)'] = mom_change.apply(format_dollar_hundreds)
            else:
                contributions['MoM Change'] = mom_change.apply(lambda x: f"{x:+.2f}") 


class Step4AcosRoasInfinityHandling(AnalysisStep):
    """Step 4: Handle infinity values in ACoS and ROAS contributions"""
    
    def get_step_name(self) -> str:
        return "acos_roas_final"
    
    def execute(self, mix_rate_contributions: Dict[str, pd.DataFrame],
                absolute_contributions: Dict[str, pd.DataFrame],
                p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame,  # Add these parameters
                p1_start_date: pd.Timestamp, p1_end_date: pd.Timestamp,
                p2_start_date: pd.Timestamp, p2_end_date: pd.Timestamp) -> Dict[str, pd.DataFrame]:
        """
        Execute Step 4: Handle infinity values in ACoS and ROAS contributions
        
        Returns:
            Dictionary of final ACoS/ROAS contributions
        """
        print("\n=== STEP 4: ACOS/ROAS INFINITY HANDLING ===")
        
        # Define infinity handling KPIs based on what's available in mix_rate_contributions
        infinity_kpis = [kpi for kpi in ['ACoS', 'ROAS'] 
                        if kpi in mix_rate_contributions]
        
        print(f"Processing infinity handling for: {infinity_kpis}")
        
        # Get period names for column headers
        p1_period_name = f"{p1_start_date.strftime('%B %Y')}"
        p2_period_name = f"{p2_start_date.strftime('%B %Y')}"
        
        # Prepare results dictionary
        final_contributions = {}
        
        # Updated infinity handling with context awareness
        from bridge_calculations_improved import ImprovedInfinityHandler
        
        handler = ImprovedInfinityHandler()
        
        # Process each KPI that needs infinity handling
        for kpi in infinity_kpis:
            if kpi in mix_rate_contributions:
                # Get the DataFrame for this KPI
                kpi_df = mix_rate_contributions[kpi]
                
                # Get the Total Contribution column
                if 'Total Contribution' in kpi_df.columns:
                    contributions = kpi_df['Total Contribution']
                    
                    # Get spend and sales data
                    p1_spend = p1_kpis['Spend']
                    p2_spend = p2_kpis['Spend']
                    p1_sales = p1_kpis['Total Ad Sales']
                    p2_sales = p2_kpis['Total Ad Sales']
                    
                    result = handler.handle_acos_roas_infinity(
                        contributions=contributions,
                        p1_spend=p1_spend,
                        p2_spend=p2_spend,
                        p1_sales=p1_sales,
                        p2_sales=p2_sales,
                        metric_type=kpi
                    )
                    
                    final_contributions[kpi] = result['Handled Contribution']
        
        # Create output with multi-column format matching other steps
        if final_contributions:
            # Start with campaign names
            all_campaigns = list(mix_rate_contributions[infinity_kpis[0]].index)
            
            # Create multi-index DataFrame
            columns = []
            data = {}
            
            for kpi in infinity_kpis:
                if kpi in final_contributions:
                    # Get original P1 and P2 values from mix_rate_contributions
                    original_data = mix_rate_contributions[kpi]
                    p1_values = p1_kpis[kpi].reindex(all_campaigns, fill_value=0)
                    p2_values = p2_kpis[kpi].reindex(all_campaigns, fill_value=0)
                    net_change = p2_values - p1_values
                    
                    # Calculate % change
                    pct_change = ((p2_values - p1_values) / p1_values * 100).fillna(0)
                    pct_change = pct_change.replace([float('inf'), float('-inf')], 0)
                    
                    # Add columns for this KPI
                    columns.extend([
                        (kpi, p1_period_name),
                        (kpi, p2_period_name),
                        (kpi, 'Net Change'),
                        (kpi, '% Change (pts)'),
                        (kpi, 'Contribution (BPS)')
                    ])
                    
                    # Format values
                    if kpi == 'ACoS':
                        p1_fmt = p1_values.apply(lambda x: f"{x:.2%}")
                        p2_fmt = p2_values.apply(lambda x: f"{x:.2%}")
                        net_change_fmt = net_change.apply(lambda x: f"{x:+.2%}")
                        pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                        contribution_fmt = final_contributions[kpi].apply(lambda x: f"{x:+.0f}")
                    else:  # ROAS
                        p1_fmt = p1_values.apply(lambda x: f"{x:.2f}")
                        p2_fmt = p2_values.apply(lambda x: f"{x:.2f}")
                        net_change_fmt = net_change.apply(lambda x: f"{x:+.2f}")
                        pct_change_fmt = pct_change.apply(lambda x: f"{x:+.1f}")
                        contribution_fmt = final_contributions[kpi].apply(lambda x: f"{x:+.2f}")
                    
                    # Store data
                    data[(kpi, p1_period_name)] = p1_fmt
                    data[(kpi, p2_period_name)] = p2_fmt
                    data[(kpi, 'Net Change')] = net_change_fmt
                    data[(kpi, '% Change (pts)')] = pct_change_fmt
                    data[(kpi, 'Contribution (BPS)')] = contribution_fmt
            
            # Create the DataFrame
            if data:
                columns = pd.MultiIndex.from_tuples(columns)
                result_df = pd.DataFrame(data, index=all_campaigns)
                result_df = result_df.reindex(columns=columns)
                
                # Save results
                description = f"ACoS/ROAS Final Contributions - {p1_period_name} vs {p2_period_name} - with infinity handling applied"
                self._save_results(result_df, 'acos_roas_final_contributions.csv', description)
                print(f"✓ Applied infinity handling and saved final ACoS/ROAS contributions")
            
            return final_contributions
        else:
            print("✗ No ACoS or ROAS contributions found to process")
            return {}


class SummaryReportGenerator(AnalysisStep):
    """Generate summary reports and formatted outputs"""
    
    def get_step_name(self) -> str:
        return "summary_reports"
    
    def execute(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                p1_totals_kpis: pd.DataFrame, p2_totals_kpis: pd.DataFrame):
        """Generate summary reports"""
        print("\n=== GENERATING SUMMARY REPORT ===")
        
        # Create a comprehensive summary with all data
        summary_sections = {}
        
        # Create MoM change report
        if not p1_kpis.empty and not p2_kpis.empty:
            mom_df = p2_kpis.copy()
            for col in p1_kpis.columns:
                if col in p2_kpis.columns:
                    mom_change = p2_kpis[col] - p1_kpis[col]
                    display_name = self.config.get_kpi_display_name(col)
                    
                    if display_name in self.config.kpi_format:
                        # Use format configuration
                        kpi_config = self.config.kpi_format[display_name]
                        change_type = kpi_config.get('change_type', 'net_change')
                        
                        if change_type == 'pts_change':
                            mom_df[col + ' MoM'] = mom_change.apply(
                                lambda x: self.config.format_change_value(x, display_name, 'pts_change')
                            )
                        else:
                            mom_df[col + ' MoM'] = mom_change.apply(
                                lambda x: self.config.format_change_value(x, display_name, 'net_change')
                            )
                    else:
                        # Fallback formatting
                        if col in ['Spend', 'Total Ad Sales', 'Same SKU Ad Sales', 'Other SKU Sales', 'ROAS']:
                            def format_dollar_hundreds(x):
                                if pd.isna(x):
                                    return ''
                                return f"${int(round(x, -2)):,}" if x >= 0 else f"-${int(round(abs(x), -2)):,}"
                            mom_df[col + ' MoM'] = mom_change.apply(format_dollar_hundreds)
                        elif col in ['ACoS', 'Conversion Rate', 'Clickthrough Rate', 'Cost Per Click']:
                            mom_df[col + ' MoM'] = (mom_change * 10000).apply(lambda x: f"{x:+.0f} BPS")
                        else:
                            mom_df[col + ' MoM'] = mom_change.apply(lambda x: f"{x:+}")
            
            summary_sections['MoM_Changes'] = mom_df
            print(f"✓ Prepared MoM KPI changes")
        
        # Add individual period KPIs with formatting
        if not p1_kpis.empty:
            p1_formatted = self._format_period_kpis(p1_kpis)
            summary_sections['P1_Campaign_KPIs'] = p1_formatted
            print(f"✓ Prepared P1 KPIs")
        
        if not p2_kpis.empty:
            p2_formatted = self._format_period_kpis(p2_kpis)
            summary_sections['P2_Campaign_KPIs'] = p2_formatted
            print(f"✓ Prepared P2 KPIs")
        
        # Add totals
        if not p1_totals_kpis.empty:
            summary_sections['P1_Totals'] = p1_totals_kpis
            print(f"✓ Prepared P1 totals")
        
        if not p2_totals_kpis.empty:
            summary_sections['P2_Totals'] = p2_totals_kpis
            print(f"✓ Prepared P2 totals")
        
        # Create one combined summary file
        if summary_sections:
            # If using unified collector, add each section separately
            if self.unified_collector is not None:
                for section_name, data in summary_sections.items():
                    section_description = {
                        'MoM_Changes': "Month-over-Month (MoM) KPI changes - shows P2 values alongside formatted MoM changes for each campaign",
                        'P1_Campaign_KPIs': "Period 1 (P1) campaign-level KPIs with proper formatting applied",
                        'P2_Campaign_KPIs': "Period 2 (P2) campaign-level KPIs with proper formatting applied", 
                        'P1_Totals': "Period 1 (P1) total/aggregate KPIs across all campaigns",
                        'P2_Totals': "Period 2 (P2) total/aggregate KPIs across all campaigns"
                    }
                    self._save_results(data, f'{section_name.lower()}.csv', section_description.get(section_name, ""))
            else:
                # For individual files mode, create one combined summary
                combined_sections = []
                for section_name, data in summary_sections.items():
                    section_df = data.copy()
                    section_df.insert(0, 'Section', section_name)
                    combined_sections.append(section_df)
                
                if combined_sections:
                    combined_summary = pd.concat(combined_sections, ignore_index=False)
                    description = "Complete summary report containing MoM changes, P1/P2 campaign KPIs, and totals"
                    self._save_results(combined_summary, 'complete_summary_report.csv', description)
                    print(f"✓ Saved complete summary report")
    
    def _format_period_kpis(self, kpis: pd.DataFrame) -> pd.DataFrame:
        """Format period KPIs with proper formatting"""
        formatted = kpis.copy()
        for col in kpis.columns:
            display_name = self.config.get_kpi_display_name(col)
            if display_name in self.config.kpi_format:
                format_spec = self.config.kpi_format[display_name]['formats'].get(
                    'period_values', {'type': 'decimal', 'decimals': 2}
                )
                formatted[col + ' (Formatted)'] = kpis[col].apply(
                    lambda x: self.config.format_value(x, format_spec)
                )
        return formatted 