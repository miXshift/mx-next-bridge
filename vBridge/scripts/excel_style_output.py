"""
Excel-Style Output Generator for vBridge

This module generates a single comprehensive output file that matches
the Excel source of truth structure exactly.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import os


class ExcelStyleOutputGenerator:
    """
    Generates output in Excel-style format matching the source of truth structure.
    
    Creates a single comprehensive table with all metrics side-by-side,
    multi-header structure, and proper formatting.
    """
    
    def __init__(self):
        """Initialize the Excel-style output generator"""
        # Define the metrics and their column structure with symbols in headers
        self.metrics_config = {
            'Spend ($)': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution (BPS)'],
                'format': 'numeric',
                'contribution_unit': 'BPS'
            },
            'Total Ad Sales ($)': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution (BPS)'],
                'format': 'numeric', 
                'contribution_unit': 'BPS'
            },
            'ACoS (%)': {
                'columns': ['January 2025', 'February 2025', 'Pts Change', '% Change (pts)', 'Contribution (BPS)'],
                'format': 'percentage_decimal',
                'contribution_unit': 'BPS'
            },
            'ROAS': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change (pts)', 'Contribution (BPS)'],
                'format': 'numeric',
                'contribution_unit': 'BPS'
            },
            'Conversion Rate (%)': {
                'columns': ['January 2025', 'February 2025', 'Pts Change', '% Change (pts)', 'Contribution (BPS)'],
                'format': 'percentage_decimal',
                'contribution_unit': 'BPS'
            },
            'Impressions': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution (BPS)'],
                'format': 'numeric',
                'contribution_unit': 'BPS'
            },
            'Clicks': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution (BPS)'],
                'format': 'numeric',
                'contribution_unit': 'BPS'
            },
            'CTR (%)': {
                'columns': ['January 2025', 'February 2025', 'Pts Change', '% Change (pts)', 'Contribution (BPS)'],
                'format': 'percentage_decimal',
                'contribution_unit': 'BPS'
            },
            'CPC ($)': {
                'columns': ['January 2025', 'February 2025', 'Net Change', '% Change', 'Contribution (BPS)'],
                'format': 'numeric',
                'contribution_unit': 'BPS'
            }
        }
    
    def generate_excel_style_output(self, 
                                   p1_kpis: pd.DataFrame,
                                   p2_kpis: pd.DataFrame, 
                                   p1_totals: Dict[str, float],
                                   p2_totals: Dict[str, float],
                                   absolute_contributions: Dict[str, pd.Series],
                                   mix_rate_contributions: Dict[str, pd.DataFrame],
                                   acos_roas_contributions: pd.DataFrame,
                                   p1_period_name: str = "January 2025",
                                   p2_period_name: str = "February 2025") -> pd.DataFrame:
        """
        Generate Excel-style comprehensive output table
        
        Args:
            p1_kpis: Period 1 KPIs DataFrame
            p2_kpis: Period 2 KPIs DataFrame  
            p1_totals: Period 1 totals dictionary
            p2_totals: Period 2 totals dictionary
            absolute_contributions: Absolute metric contributions
            mix_rate_contributions: Mix/rate contributions
            acos_roas_contributions: Final ACoS/ROAS contributions
            p1_period_name: Name for period 1 (e.g., "January 2025")
            p2_period_name: Name for period 2 (e.g., "February 2025")
            
        Returns:
            DataFrame with Excel-style multi-column layout
        """
        
        # Update column names with actual period names
        for metric in self.metrics_config:
            self.metrics_config[metric]['columns'] = [
                col.replace('January 2025', p1_period_name).replace('February 2025', p2_period_name) 
                for col in self.metrics_config[metric]['columns']
            ]
        
        # Get all campaign names (union of both periods)
        campaigns = list(set(p1_kpis.index.tolist() + p2_kpis.index.tolist()))
        campaigns.sort()
        
        # Create the comprehensive data structure
        excel_data = []
        
        # First add the totals row
        totals_row = self._create_totals_row(p1_totals, p2_totals, absolute_contributions, mix_rate_contributions)
        excel_data.append(totals_row)
        
        # Then add individual campaign rows
        for campaign in campaigns:
            campaign_row = self._create_campaign_row(
                campaign, p1_kpis, p2_kpis, absolute_contributions, 
                mix_rate_contributions, acos_roas_contributions
            )
            excel_data.append(campaign_row)
        
        # Create the DataFrame with multi-index columns
        multi_columns = self._create_multi_index_columns()
        
        df = pd.DataFrame(excel_data, columns=multi_columns)
        
        # Set campaign names as index
        index_names = ['Total'] + campaigns
        df.index = index_names
        
        return df
    
    def _create_multi_index_columns(self) -> pd.MultiIndex:
        """Create multi-index columns matching Excel structure"""
        level_0 = []  # KPI names
        level_1 = []  # Column headers
        
        # Add Campaign column
        level_0.append('KPIs')
        level_1.append('Campaign')
        
        # Add columns for each metric
        for metric_name, config in self.metrics_config.items():
            for col_name in config['columns']:
                level_0.append(metric_name)
                level_1.append(col_name)
        
        return pd.MultiIndex.from_tuples(list(zip(level_0, level_1)))
    
    def _create_totals_row(self, 
                          p1_totals: Dict[str, float],
                          p2_totals: Dict[str, float],
                          absolute_contributions: Dict[str, pd.Series],
                          mix_rate_contributions: Dict[str, pd.DataFrame]) -> List[Any]:
        """Create the totals row (first row in Excel)"""
        row_data = ['Total']  # Campaign name
        
        for metric_name, config in self.metrics_config.items():
            # Get metric data from totals
            p1_value = p1_totals.get(metric_name, 0)
            p2_value = p2_totals.get(metric_name, 0)
            
            # Ensure we have scalar values, not Series
            if hasattr(p1_value, 'iloc'):
                p1_value = float(p1_value.iloc[0]) if len(p1_value) > 0 else 0
            if hasattr(p2_value, 'iloc'):
                p2_value = float(p2_value.iloc[0]) if len(p2_value) > 0 else 0
            
            p1_value = float(p1_value) if p1_value is not None else 0
            p2_value = float(p2_value) if p2_value is not None else 0
            
            # Calculate changes
            net_change = p2_value - p1_value
            pct_change = (net_change / p1_value * 100) if p1_value != 0 else 0
            
            # Get contribution
            contribution = 0
            if metric_name in absolute_contributions:
                contribution = absolute_contributions[metric_name].sum()
            elif metric_name in mix_rate_contributions and 'Total Contribution (BPS)' in mix_rate_contributions[metric_name].columns:
                contribution = mix_rate_contributions[metric_name]['Total Contribution (BPS)'].sum()
            
            # Format values according to metric type
            formatted_values = self._format_metric_values(
                metric_name, p1_value, p2_value, net_change, pct_change, contribution
            )
            
            row_data.extend(formatted_values)
        
        return row_data
    
    def _create_campaign_row(self,
                           campaign: str,
                           p1_kpis: pd.DataFrame,
                           p2_kpis: pd.DataFrame,
                           absolute_contributions: Dict[str, pd.Series],
                           mix_rate_contributions: Dict[str, pd.DataFrame],
                           acos_roas_contributions: pd.DataFrame) -> List[Any]:
        """Create a row for an individual campaign"""
        row_data = [campaign]  # Campaign name
        
        for metric_name, config in self.metrics_config.items():
            # Get metric values from KPI DataFrames
            p1_value = p1_kpis.loc[campaign, metric_name] if campaign in p1_kpis.index and metric_name in p1_kpis.columns else 0
            p2_value = p2_kpis.loc[campaign, metric_name] if campaign in p2_kpis.index and metric_name in p2_kpis.columns else 0
            
            # Ensure we have scalar values
            p1_value = float(p1_value) if p1_value is not None else 0
            p2_value = float(p2_value) if p2_value is not None else 0
            
            # Calculate changes
            net_change = p2_value - p1_value
            pct_change = (net_change / p1_value * 100) if p1_value != 0 else 0
            
            # Get contribution for this campaign
            contribution = 0
            if metric_name in absolute_contributions and campaign in absolute_contributions[metric_name].index:
                contribution = absolute_contributions[metric_name].loc[campaign]
            elif metric_name in mix_rate_contributions:
                mr_df = mix_rate_contributions[metric_name]
                if campaign in mr_df.index and 'Total Contribution (BPS)' in mr_df.columns:
                    contribution = mr_df.loc[campaign, 'Total Contribution (BPS)']
            elif metric_name in ['ACoS', 'ROAS'] and campaign in acos_roas_contributions.index:
                # Get contribution from ACoS/ROAS final contributions
                if metric_name == 'ACoS' and f'{metric_name}_Contribution_BPS' in acos_roas_contributions.columns:
                    contribution = acos_roas_contributions.loc[campaign, f'{metric_name}_Contribution_BPS']
                elif metric_name == 'ROAS' and f'{metric_name}_Contribution' in acos_roas_contributions.columns:
                    contribution = acos_roas_contributions.loc[campaign, f'{metric_name}_Contribution']
            
            # Format values according to metric type
            formatted_values = self._format_metric_values(
                metric_name, p1_value, p2_value, net_change, pct_change, contribution
            )
            
            row_data.extend(formatted_values)
        
        return row_data
    
    def _format_metric_values(self,
                             metric_name: str,
                             p1_value: float,
                             p2_value: float, 
                             net_change: float,
                             pct_change: float,
                             contribution: float) -> List[float]:
        """Format metric values as pure numbers for summable CSV"""
        config = self.metrics_config[metric_name]
        format_type = config['format']
        
        formatted_values = []
        
        # All values are returned as pure numbers for CSV summing
        if format_type == 'percentage_decimal':
            # Convert percentages to decimal representation (e.g., 0.2153 instead of 21.53%)
            formatted_values.extend([
                round(p1_value, 6),  # Period 1 value as decimal
                round(p2_value, 6),  # Period 2 value as decimal
                round(net_change, 6),  # Net change as decimal
                round(pct_change / 100, 4),  # Percentage change as decimal (7.4% -> 0.074)
                round(contribution, 2) if abs(contribution) >= 0.01 else 0.0  # Contribution as float BPS
            ])
        elif format_type == 'numeric':
            # Standard numeric format with appropriate precision
            if metric_name in ['Impressions', 'Clicks']:
                # Integer values for impression/click metrics
                formatted_values.extend([
                    int(round(p1_value)),
                    int(round(p2_value)), 
                    int(round(net_change)),
                    round(pct_change / 100, 4),  # Percentage change as decimal
                    round(contribution, 2) if abs(contribution) >= 0.01 else 0.0  # Contribution as float BPS
                ])
            else:
                # Currency and other decimal values
                formatted_values.extend([
                    round(p1_value, 2),
                    round(p2_value, 2),
                    round(net_change, 2),
                    round(pct_change / 100, 4),  # Percentage change as decimal
                    round(contribution, 2) if abs(contribution) >= 0.01 else 0.0  # Contribution as float BPS
                ])
        
        return formatted_values
    
    def save_excel_style_output(self,
                               excel_df: pd.DataFrame,
                               output_path: str,
                               title: str = "Hydrapak - US",
                               subtitle: str = "January 2025 vs February 2025"):
        """
        Save the Excel-style output to a CSV file with proper headers
        
        Args:
            excel_df: The formatted DataFrame 
            output_path: Path to save the output file
            title: Report title
            subtitle: Report subtitle
        """
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Write title and subtitle
            f.write(f'{title}\n')
            f.write(f'{subtitle}\n')
            f.write('ATTRIBUTE: Campaign\n')
            f.write('CAMPAIGN TYPE: sponsoredProducts\n')
            f.write('\n')
            
            # Write notes about bridge calculations
            f.write('Mix Bridge - Explaining % Change\n')
            f.write('MixRate Bridge - Explaining Net Change\n')
            f.write('MixRate Bridge w/Infinity Errors - Explaining Net Change\n')
            f.write('ROAS and CPC are reported in $0.00, all others in %\n')
            f.write('CTR is reported in bps to 1 decimal point, the rest to whole numbers\n')
            f.write('\n')
            
            # Write the main data table
            excel_df.to_csv(f, index=True)
        
        print(f"✓ Saved Excel-style output to {output_path}")