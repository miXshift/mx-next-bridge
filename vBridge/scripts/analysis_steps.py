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


class UnifiedOutputCollector:
    """Collects all analysis outputs for unified file generation"""
    
    def __init__(self):
        self.sections = {}
        self.section_order = []
    
    def add_section(self, section_name: str, data: pd.DataFrame, description: str = ""):
        """Add a section to the unified output"""
        self.sections[section_name] = {
            'data': data,
            'description': description
        }
        if section_name not in self.section_order:
            self.section_order.append(section_name)
    
    def save_unified_file(self, output_path: str):
        """Save all sections to a single unified CSV file"""
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
        
        # Save P1 campaign KPIs
        if not p1_kpis.empty:
            description = f"Period 1 ({p1_period}) campaign-level KPIs - all 14 calculated KPIs for each campaign"
            self._save_results(p1_kpis, 'p1_campaign_kpis.csv', description)
            print(f"✓ Saved P1 campaign KPIs")
        
        # Save P2 campaign KPIs
        if not p2_kpis.empty:
            description = f"Period 2 ({p2_period}) campaign-level KPIs - all 14 calculated KPIs for each campaign"
            self._save_results(p2_kpis, 'p2_campaign_kpis.csv', description)
            print(f"✓ Saved P2 campaign KPIs")
        
        # Save P1 totals
        if not p1_totals_kpis.empty:
            description = f"Period 1 ({p1_period}) total/aggregate KPIs - overall performance across all campaigns"
            self._save_results(p1_totals_kpis, 'p1_totals_kpis.csv', description)
            print(f"✓ Saved P1 totals")
        
        # Save P2 totals
        if not p2_totals_kpis.empty:
            description = f"Period 2 ({p2_period}) total/aggregate KPIs - overall performance across all campaigns"
            self._save_results(p2_totals_kpis, 'p2_totals_kpis.csv', description)
            print(f"✓ Saved P2 totals")
        
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
                p1_totals_kpis: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Execute Step 2: Calculate absolute metric contributions
        
        Returns:
            Dictionary of metric contributions
        """
        print("\n=== STEP 2: MIX CONTRIBUTION (ABSOLUTE METRICS) ===")
        
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
        
        for metric in absolute_metrics:
            if metric in p1_kpis.columns and metric in p2_kpis.columns and not p1_totals_kpis.empty:
                try:
                    contribution = self._calculate_absolute_metric_contribution(
                        p1_kpis[metric],
                        p2_kpis[metric],
                        p1_totals_kpis.loc['TOTAL', metric]
                    )
                    
                    # Apply formatting based on KPI configuration
                    display_name = self.config.get_kpi_display_name(metric)
                    if display_name in self.config.kpi_format:
                        formatted_contribution = contribution.apply(
                            lambda x: self.config.format_contribution_value(x, display_name)
                        )
                        contribution_df = pd.DataFrame({
                            'Contribution (Raw)': contribution,
                            'Contribution (Formatted)': formatted_contribution
                        })
                    else:
                        contribution_df = contribution.to_frame()
                    
                    absolute_contributions[metric] = contribution_df
                    
                    # Don't save individual metric files - only save combined at the end
                    print(f"✓ Calculated {metric} contribution")
                    
                except Exception as e:
                    print(f"✗ Error calculating {metric} contribution: {e}")
            else:
                print(f"✗ Skipping {metric} - missing data or empty totals")
        
        # Save combined absolute contributions
        if absolute_contributions:
            combined_data = {}
            for metric, contrib_df in absolute_contributions.items():
                if 'Contribution (Raw)' in contrib_df.columns:
                    combined_data[metric] = contrib_df['Contribution (Raw)']
                else:
                    combined_data[metric] = contrib_df.iloc[:, 0]
            
            combined_df = pd.DataFrame(combined_data)
            description = "Combined absolute metric contributions - all absolute metrics in one table showing campaign-level contributions to period-over-period changes"
            self._save_results(combined_df, 'all_absolute_metric_contributions.csv', description)
            print(f"✓ Saved combined absolute contributions")
        
        return absolute_contributions
    
    def _calculate_absolute_metric_contribution(self, p1_metric_series: pd.Series, 
                                              p2_metric_series: pd.Series, 
                                              p1_metric_total: float) -> pd.Series:
        """
        Calculates the contribution of each campaign to the total change of an absolute metric.
        Output is in Basis Points (BPS).
        """
        if p1_metric_total == 0:
            return pd.Series(0.0, index=p1_metric_series.index, name='Contribution (BPS)')

        net_change_series = p2_metric_series.fillna(0) - p1_metric_series.fillna(0)
        contribution_bps = (net_change_series / p1_metric_total) * 10000
        return contribution_bps.rename('Contribution (BPS)') 


class Step3MixRateContributions(AnalysisStep):
    """Step 3: Calculate mix/rate contributions for all calculated KPIs"""
    
    def get_step_name(self) -> str:
        return "mix_rate_contributions"
    
    def execute(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                p2_totals_kpis: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Execute Step 3: Calculate mix rate contributions
        
        Returns:
            Dictionary of mix rate contributions
        """
        print("\n=== STEP 3: MIX RATE CONTRIBUTION (CALCULATED KPIS) ===")
        
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
                
                # Calculate mix shares for each period
                p1_total_mix = p1_kpis[mix_driver].sum()
                p2_total_mix = p2_kpis[mix_driver].sum()
                p1_mix = p1_kpis[mix_driver] / p1_total_mix if p1_total_mix > 0 else pd.Series(0, index=p1_kpis.index)
                p2_mix = p2_kpis[mix_driver] / p2_total_mix if p2_total_mix > 0 else pd.Series(0, index=p2_kpis.index)
                
                # Calculate the overall KPI value for P2 (weighted average)
                p2_total_kpi = self._calculate_weighted_average_kpi(kpi, p2_kpis)
                
                # Calculate mix rate contribution
                contributions = self._calculate_mix_rate_contribution(
                    p1_kpi_values=p1_kpis[kpi],
                    p2_kpi_values=p2_kpis[kpi],
                    p1_mix_shares=p1_mix,
                    p2_mix_shares=p2_mix,
                    p2_total_kpi_value=p2_total_kpi,
                    is_percentage_metric=is_percentage
                )
                
                # Add MoM change columns with proper formatting
                self._add_mom_change_formatting(contributions, kpi, p1_kpis, p2_kpis, is_percentage)
                
                mix_rate_contributions[kpi] = contributions
                
                # Don't save individual KPI files - will save combined at the end
                print(f"✓ Calculated {kpi} mix/rate contribution")
                
            except Exception as e:
                print(f"✗ Error calculating {kpi} mix/rate contribution: {e}")
        
        # Save combined mix/rate contributions
        if mix_rate_contributions:
            # Create a combined DataFrame with all KPIs
            combined_sections = []
            for kpi, contrib_df in mix_rate_contributions.items():
                # Add KPI identifier column
                kpi_df = contrib_df.copy()
                kpi_df.insert(0, 'KPI', kpi)
                combined_sections.append(kpi_df)
            
            if combined_sections:
                combined_df = pd.concat(combined_sections, ignore_index=False)
                description = "Combined Mix/Rate contributions for all KPIs - shows Mix Impact, Rate Impact, and Total Contribution for each campaign across all calculated KPIs"
                self._save_results(combined_df, 'all_mix_rate_contributions.csv', description)
                print(f"✓ Saved combined mix/rate contributions")
        
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
        """Calculate Mix Impact, Rate Impact, and Total Contribution for a calculated KPI"""
        df = pd.DataFrame({
            'p1_kpi': p1_kpi_values,
            'p2_kpi': p2_kpi_values,
            'p1_mix': p1_mix_shares,
            'p2_mix': p2_mix_shares
        }).fillna(0)

        # Mixed Rate Change formula
        mix_impact = (df['p2_mix'] - df['p1_mix']) * (df['p2_kpi'] - p2_total_kpi_value)
        rate_impact = (df['p2_kpi'] - df['p1_kpi']) * df['p1_mix']
        total_contribution = mix_impact + rate_impact

        # Scale to BPS if it's a percentage metric
        if is_percentage_metric:
            mix_impact *= 10000
            rate_impact *= 10000
            total_contribution *= 10000

        return pd.DataFrame({
            'Mix Impact': mix_impact,
            'Rate Impact': rate_impact,
            'Total Contribution': total_contribution
        })
    
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
    """Step 4: Handle ACoS/ROAS infinity cases and generate final contributions"""
    
    def get_step_name(self) -> str:
        return "acos_roas_final"
    
    def execute(self, p1_kpis: pd.DataFrame, p2_kpis: pd.DataFrame, 
                p1_totals_kpis: pd.DataFrame, p2_totals_kpis: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Execute Step 4: Apply ACoS/ROAS infinity handling
        
        Returns:
            DataFrame with final ACoS/ROAS contributions
        """
        print("\n=== STEP 4: ACOS/ROAS INFINITY HANDLING ===")
        
        # Get all metrics with bridge_type "MR+I" from KPI format
        infinity_handling_kpis = []
        for kpi_name, config in self.config.kpi_format.items():
            if config.get('bridge_type') == 'MR+I':
                internal_name = self.config.get_kpi_internal_name(kpi_name)
                infinity_handling_kpis.append(internal_name)
        
        # Fallback to ACoS if KPI_FORMAT is empty or no MR+I found
        if not infinity_handling_kpis:
            infinity_handling_kpis = ['ACoS']
            print("No MR+I KPIs found in format config, defaulting to ACoS")
        
        print(f"Processing infinity handling for: {infinity_handling_kpis}")
        
        try:
            # Calculate spend mix shares
            p1_total_spend = p1_kpis['Spend'].sum()
            p2_total_spend = p2_kpis['Spend'].sum()
            p1_spend_mix = p1_kpis['Spend'] / p1_total_spend if p1_total_spend > 0 else pd.Series(0, index=p1_kpis.index)
            p2_spend_mix = p2_kpis['Spend'] / p2_total_spend if p2_total_spend > 0 else pd.Series(0, index=p2_kpis.index)
            
            # Apply ACoS/ROAS bridge with infinity handling
            acos_roas_bridge = self._calculate_acos_roas_bridge_contribution(
                p1_kpis['Total Ad Sales'], p1_kpis['Spend'],
                p2_kpis['Total Ad Sales'], p2_kpis['Spend'],
                p1_spend_mix, p2_spend_mix,
                p1_totals_kpis.loc['TOTAL', 'Total Ad Sales'], p1_totals_kpis.loc['TOTAL', 'Spend'],
                p2_totals_kpis.loc['TOTAL', 'Total Ad Sales'], p2_totals_kpis.loc['TOTAL', 'Spend']
            )
            
            # Apply formatting based on KPI configuration
            formatted_bridge = acos_roas_bridge.copy()
            
            # Format ACoS contributions
            if 'ACoS' in infinity_handling_kpis:
                acos_display_name = self.config.get_kpi_display_name('ACoS')
                if acos_display_name in self.config.kpi_format:
                    formatted_bridge['ACoS_Contribution_BPS (Formatted)'] = acos_roas_bridge['ACoS_Contribution_BPS'].apply(
                        lambda x: self.config.format_contribution_value(x, acos_display_name)
                    )
            
            # Format ROAS contributions
            roas_display_name = self.config.get_kpi_display_name('ROAS')
            if roas_display_name in self.config.kpi_format:
                formatted_bridge['ROAS_Contribution (Formatted)'] = acos_roas_bridge['ROAS_Contribution'].apply(
                    lambda x: self.config.format_contribution_value(x, roas_display_name)
                )
            
            # Save the final ACoS/ROAS contributions
            description = "Final ACoS/ROAS contributions with infinity handling applied - handles cases where campaigns have zero sales or spend that would cause infinite ACoS values"
            self._save_results(formatted_bridge, 'acos_roas_final_contributions.csv', description)
            print(f"✓ Applied infinity handling and saved final ACoS/ROAS contributions")
            
            return formatted_bridge
            
        except Exception as e:
            print(f"✗ Error in ACoS/ROAS infinity handling: {e}")
            return None
    
    def _calculate_acos_roas_bridge_contribution(self, p1_sales_series: pd.Series, p1_spend_series: pd.Series,
                                               p2_sales_series: pd.Series, p2_spend_series: pd.Series,
                                               p1_spend_mix_series: pd.Series, p2_spend_mix_series: pd.Series,
                                               p1_total_sales: float, p1_total_spend: float,
                                               p2_total_sales: float, p2_total_spend: float) -> pd.DataFrame:
        """
        Calculates ACoS and ROAS contributions, including infinity error handling for ACoS
        by transforming ROAS contributions.
        """
        # Align all series to ensure consistent indexing
        df = pd.DataFrame({
            'P1_Sales': p1_sales_series,
            'P1_Spend': p1_spend_series,
            'P2_Sales': p2_sales_series,
            'P2_Spend': p2_spend_series,
            'P1_Spend_Mix': p1_spend_mix_series,
            'P2_Spend_Mix': p2_spend_mix_series
        }).fillna(0)

        # Calculate campaign-level metrics
        df['P1_ACoS'] = np.where(df['P1_Sales'] > 0, df['P1_Spend'] / df['P1_Sales'], np.nan)
        df['P2_ACoS'] = np.where(df['P2_Sales'] > 0, df['P2_Spend'] / df['P2_Sales'], np.nan)
        df['P1_ROAS'] = np.where(df['P1_Spend'] > 0, df['P1_Sales'] / df['P1_Spend'], 0)
        df['P2_ROAS'] = np.where(df['P2_Spend'] > 0, df['P2_Sales'] / df['P2_Spend'], 0)

        # Calculate Total KPIs
        P1_Total_ACoS = p1_total_spend / p1_total_sales if p1_total_sales > 0 else np.nan
        P2_Total_ACoS = p2_total_spend / p2_total_sales if p2_total_sales > 0 else np.nan
        P1_Total_ROAS = p1_total_sales / p1_total_spend if p1_total_spend > 0 else 0
        P2_Total_ROAS = p2_total_sales / p2_total_spend if p2_total_spend > 0 else 0
        
        # --- ROAS Bridge ---
        step3 = Step3MixRateContributions(self.config, self.output_dir)
        roas_contributions_df = step3._calculate_mix_rate_contribution(
            df['P1_ROAS'], df['P2_ROAS'],
            df['P1_Spend_Mix'], df['P2_Spend_Mix'],
            P2_Total_ROAS,
            is_percentage_metric=False
        )
        df['ROAS_Contribution'] = roas_contributions_df['Total Contribution']

        # --- ACoS Bridge ---
        P2_Total_ACoS_for_calc = P2_Total_ACoS if not pd.isna(P2_Total_ACoS) else 0
        acos_contributions_std_df = step3._calculate_mix_rate_contribution(
            df['P1_ACoS'].fillna(0),
            df['P2_ACoS'].fillna(0),
            df['P1_Spend_Mix'], df['P2_Spend_Mix'],
            P2_Total_ACoS_for_calc,
            is_percentage_metric=True
        )
        df['ACoS_Contribution_BPS'] = acos_contributions_std_df['Total Contribution']

        # Apply transformation where ACoS might be infinite
        infinity_condition = df['P1_ACoS'].isna() | df['P2_ACoS'].isna()
        
        total_overall_roas_change = P2_Total_ROAS - P1_Total_ROAS
        
        if pd.isna(P1_Total_ACoS) or pd.isna(P2_Total_ACoS):
            total_overall_acos_change_bps = 0
        else:
            total_overall_acos_change_bps = (P2_Total_ACoS - P1_Total_ACoS) * 10000

        if total_overall_roas_change != 0:
            df.loc[infinity_condition, 'ACoS_Contribution_BPS'] = \
                (df.loc[infinity_condition, 'ROAS_Contribution'] / total_overall_roas_change) * total_overall_acos_change_bps
        elif total_overall_roas_change == 0 and total_overall_acos_change_bps != 0:
            print("Warning: Total ROAS change is 0, but ACoS change is not. ACoS transformation for infinity cases may be inaccurate.")
        elif total_overall_roas_change == 0 and total_overall_acos_change_bps == 0:
             df.loc[infinity_condition, 'ACoS_Contribution_BPS'] = 0
             
        return df[['ACoS_Contribution_BPS', 'ROAS_Contribution']] 


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