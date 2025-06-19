"""
vBridge.py - Modular KPI Analysis and Mix/Rate Bridge Calculator

This module now serves as a compatibility layer that imports from the new modular structure.
The original large file has been broken down into smaller, focused modules:

- config_manager.py: Configuration and formatting management
- data_processor.py: Data loading and preprocessing
- analysis_steps.py: All analysis step implementations
- vbridge_main.py: Main orchestrator class

For new code, import directly from the specific modules or use:
    from vbridge_main import VBridge
"""

# Import everything from the new modular structure for backward compatibility
from config_manager import ConfigManager
from data_processor import DataProcessor
from analysis_steps import (
    AnalysisStep,
    Step1KPICalculation,
    Step2AbsoluteContributions,
    Step3MixRateContributions,
    Step4AcosRoasInfinityHandling,
    SummaryReportGenerator
)
from vbridge_main import VBridge

# For backward compatibility, expose the main execution
if __name__ == '__main__':
    # Initialize VBridge
    vbridge = VBridge(output_dir='output')
    
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