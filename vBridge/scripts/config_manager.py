"""
Simplified Configuration Management for Streamlined vBridge

This module handles basic configuration and column mappings.
Complex formatting logic has been moved to ExcelStyleOutputGenerator.
"""

from typing import Dict, Any


class ConfigManager:
    """Simplified configuration manager for streamlined vBridge"""
    
    def __init__(self):
        self._setup_column_mappings()
    
    def _setup_column_mappings(self):
        """Setup column name mappings for data processing"""
        # Core data columns
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


# Note: Legacy formatting methods removed - ExcelStyleOutputGenerator handles all formatting
# Legacy kpi_format.py loading removed - not needed for streamlined approach
# Complex KPI mappings removed - streamlined processor handles KPI names directly