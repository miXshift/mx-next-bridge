"""
Mix Bridge Analysis Modules

A modular toolkit for analyzing Mix Bridge Excel files and comparing outputs.
Focused on the 5 analytic points for each KPI:
1. Mix (P1 Mix percentage)
2. Mix Rate (Growth rate between periods)
3. Contribution (Mix * Growth * Scale)
4. TBD - Additional analytic point
5. TBD - Additional analytic point
"""

from .excel_operations import *
from .data_comparison import *
from .formula_analysis import *
from .dataframe_operations import *
from .bridge_calculations import *
from .config import *
from .reporting import *
from .validation import *

__version__ = "0.1.0"