"""
Configuration Management for vBridge KPI Analysis

This module handles configuration loading, formatting, and column mappings
for the KPI analysis system.
"""

import json
from typing import Dict, Any
import pandas as pd


class ConfigManager:
    """Manages configuration and formatting for KPI analysis"""
    
    def __init__(self):
        self.kpi_format = self._load_kpi_format()
        self._setup_column_mappings()
        self._setup_kpi_mappings()
    
    def _load_kpi_format(self) -> Dict[str, Any]:
        """Load KPI format configuration from kpi_format.py"""
        try:
            with open('kpi_format.py', 'r') as f:
                content = f.read()
                start = content.find('{')
                end = content.rfind('}') + 1
                json_content = content[start:end]
                return json.loads(json_content)
        except Exception as e:
            print(f"Warning: Could not load kpi_format.py: {e}")
            return {}
    
    def _setup_column_mappings(self):
        """Setup default column name mappings"""
        self.CAMPAIGN_ID_COL = 'CampaignID'
        self.CAMPAIGN_NAME_COL = 'CampaignName'
        self.DATE_COL = 'DateKey'
        self.COST_COL = 'Cost'
        self.CLICKS_COL = 'Clicks'
        self.IMPRESSIONS_COL = 'Impressions'
        
        # Attribution columns - will be dynamically selected
        self.SALES_COL_ATTR = 'Sales'
        self.ORDERS_COL_ATTR = 'AttributedConversions7day'
        self.SALES_SAME_SKU_COL_ATTR = 'AttributedSalesSameSKU7day'
        self.ORDERS_SAME_SKU_COL_ATTR = 'AttributedConversionsSameSKU7day'
    
    def _setup_kpi_mappings(self):
        """Setup KPI name mappings"""
        self.KPI_NAME_MAPPING = {
            'CTR': 'Clickthrough Rate',
            'CPC': 'Cost Per Click'
        }
    
    def get_kpi_display_name(self, internal_name: str) -> str:
        """Get the display name for a KPI from the format configuration"""
        return self.KPI_NAME_MAPPING.get(internal_name, internal_name)
    
    def get_kpi_internal_name(self, display_name: str) -> str:
        """Get the internal name for a KPI from the display name"""
        reverse_mapping = {v: k for k, v in self.KPI_NAME_MAPPING.items()}
        return reverse_mapping.get(display_name, display_name)
    
    def format_value(self, value: float, format_spec: Dict[str, Any]) -> str:
        """Format a value according to the format specification"""
        if pd.isna(value):
            return ''
        
        format_type = format_spec.get('type', 'decimal')
        
        if format_type == 'currency':
            decimals = format_spec.get('decimals', 2)
            if value >= 0:
                return f"${value:,.{decimals}f}"
            else:
                return f"-${abs(value):,.{decimals}f}"
        elif format_type == 'percentage':
            # Percentage as decimal format with 12 decimal places (e.g., 0.131000000000)
            return f"{value:.12f}"
        elif format_type == 'bps':
            decimals = format_spec.get('decimals', 0)
            # Don't append BPS to the value, it will be in the column header
            return f"{value:+.{decimals}f}"
        elif format_type == 'integer':
            return f"{int(round(value)):,}"
        elif format_type == 'decimal':
            decimals = format_spec.get('decimals', 2)
            return f"{value:.{decimals}f}"
        else:
            return str(value)
    
    def format_change_value(self, value: float, kpi_name: str, change_type: str = 'net_change') -> str:
        """Format a change value according to KPI specifications"""
        if kpi_name not in self.kpi_format:
            return str(value)
        
        kpi_config = self.kpi_format[kpi_name]
        
        if change_type == 'net_change' and 'change_type' in kpi_config:
            if kpi_config['change_type'] == 'pts_change':
                change_type = 'pts_change'
        
        format_spec = kpi_config['formats'].get(
            change_type, 
            kpi_config['formats'].get('net_change', {'type': 'decimal', 'decimals': 2})
        )
        return self.format_value(value, format_spec)
    
    def format_contribution_value(self, value: float, kpi_name: str) -> str:
        """Format a contribution value according to KPI specifications"""
        if kpi_name not in self.kpi_format:
            return f"{value:+.2f}"
        
        format_spec = self.kpi_format[kpi_name]['formats'].get(
            'contribution', 
            {'type': 'decimal', 'decimals': 2}
        )
        return self.format_value(value, format_spec)
    
    def get_bridge_type(self, kpi_name: str) -> str:
        """Get the bridge type for a KPI"""
        display_name = self.get_kpi_display_name(kpi_name)
        return self.kpi_format.get(display_name, {}).get('bridge_type', 'M') 