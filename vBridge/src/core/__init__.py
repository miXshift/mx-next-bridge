"""
Core Calculation Engine

Contains the main bridge calculation logic and algorithms:
- bridge_calculator: Main bridge calculation engine  
- enhanced_calculator: Zero baseline handling with delta assignment
- mixrate_calculator: Rate metric calculations with infinity error handling
- campaign_bridge: Campaign-level bridge analysis
"""

# Re-export main classes for easy access
from .bridge_calculator import BridgeCalculator
from .enhanced_calculator import EnhancedMixBridgeCalculator
from .mixrate_calculator import MixRateBridgeCalculator
from .campaign_bridge import CampaignBridge
from .campaign_bridge_modular import CampaignBridge as CampaignBridgeModular

__all__ = [
    'BridgeCalculator',
    'EnhancedMixBridgeCalculator', 
    'MixRateBridgeCalculator',
    'CampaignBridge',
    'CampaignBridgeModular'
]