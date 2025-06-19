"""
vBridge KPI Analysis Package

A modular system for performing 4-step KPI analysis and mix/rate bridge calculations.
"""

from .config_manager import ConfigManager
from .data_processor import DataProcessor
from .analysis_steps import (
    AnalysisStep,
    Step1KPICalculation,
    Step2AbsoluteContributions,
    Step3MixRateContributions,
    Step4AcosRoasInfinityHandling,
    SummaryReportGenerator
)
from .vbridge_main import VBridge

__version__ = "2.0.0"
__all__ = [
    "ConfigManager",
    "DataProcessor", 
    "AnalysisStep",
    "Step1KPICalculation",
    "Step2AbsoluteContributions",
    "Step3MixRateContributions", 
    "Step4AcosRoasInfinityHandling",
    "SummaryReportGenerator",
    "VBridge"
] 