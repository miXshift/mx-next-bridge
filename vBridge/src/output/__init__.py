"""
Output Management Module

Handles output formatting, file management, and archiving:
- formatter: Basic CSV formatting and structure
- enhanced_formatter: Advanced formatting with metadata
- manager: File management and archiving operations
"""

# Re-export main classes for easy access
try:
    from .formatter import OutputFormatter
    from .enhanced_formatter import EnhancedOutputFormatter, OutputNamingConfig
    from .manager import ImprovedOutputManager
except ImportError:
    # Will be available after Phase 2
    pass

__all__ = [
    'OutputFormatter',
    'EnhancedOutputFormatter',
    'OutputNamingConfig', 
    'ImprovedOutputManager'
]