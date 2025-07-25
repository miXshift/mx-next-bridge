#!/usr/bin/env python3
"""
Configuration Management for MixBridge Calculations
Centralized configuration with validation and defaults
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
import warnings


@dataclass
class MixBridgeConfig:
    """Configuration dataclass for MixBridge calculations using delta assignment strategy"""
    
    # Calculation precision
    precision_decimals: int = 12
    validation_tolerance: float = 1e-6
    
    # Auditing and logging
    enable_audit_trail: bool = True
    mathematical_validation: bool = True
    debug_mode: bool = False
    
    # Output formatting
    output_precision: int = 2
    percentage_as_decimal: bool = True
    
    # Performance settings
    enable_parallel_processing: bool = False
    chunk_size: int = 1000
    
    # Output naming configuration
    output_naming: Optional['OutputNamingConfig'] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Initialize output naming config if not provided
        if self.output_naming is None:
            from enhanced_output_formatter import OutputNamingConfig
            self.output_naming = OutputNamingConfig()
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate numeric values
        if self.precision_decimals < 0 or self.precision_decimals > 15:
            raise ValueError("precision_decimals must be between 0 and 15")
        
        if self.validation_tolerance < 0:
            raise ValueError("validation_tolerance must be non-negative")
        
        if self.output_precision < 0:
            raise ValueError("output_precision must be non-negative")
        
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
    
    @classmethod
    def create_config(cls, **overrides) -> 'MixBridgeConfig':
        """
        Create configuration with optional overrides
        
        Args:
            **overrides: Configuration parameters to override
            
        Returns:
            MixBridgeConfig instance
        """
        return cls(**overrides)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'MixBridgeConfig':
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            MixBridgeConfig instance
        """
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        except FileNotFoundError:
            warnings.warn(f"Config file not found: {config_path}. Using defaults.")
            return cls()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def to_file(self, config_path: str):
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save configuration file
        """
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def update(self, **kwargs):
        """
        Update configuration parameters
        
        Args:
            **kwargs: Parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")
        
        # Re-validate after updates
        self._validate_config()
    
    def apply_naming_profile(self, profile_name: str):
        """
        Apply a predefined naming profile
        
        Args:
            profile_name: Profile name ('production', 'development', 'legacy', etc.)
        """
        from enhanced_output_formatter import create_naming_profiles
        
        profiles = create_naming_profiles()
        if profile_name not in profiles:
            available = ', '.join(profiles.keys())
            raise ValueError(f"Unknown naming profile: {profile_name}. Available: {available}")
        
        self.output_naming = profiles[profile_name]
    
    def get_strategy_info(self) -> Dict[str, str]:
        """Get information about the delta assignment strategy"""
        return {
            'strategy': 'delta_assignment',
            'description': (
                "Delta assignment strategy calculates standard contributions for campaigns with "
                "baseline values, then proportionally assigns the remaining delta to zero baseline "
                "campaigns based on their Period 2 mix. This ensures mathematical consistency."
            )
        }


class ConfigManager:
    """Manager class for handling configuration lifecycle"""
    
    DEFAULT_CONFIG_PATH = 'config/mixbridge_config.json'
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config = None
    
    @property
    def config(self) -> MixBridgeConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> MixBridgeConfig:
        """Load configuration from file or create default"""
        try:
            return MixBridgeConfig.from_file(self.config_path)
        except Exception:
            # Return default configuration if loading fails
            return MixBridgeConfig()
    
    def save_config(self, config: Optional[MixBridgeConfig] = None):
        """
        Save configuration to file
        
        Args:
            config: Configuration to save, uses current if None
        """
        config_to_save = config or self.config
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        config_to_save.to_file(self.config_path)
    
    def update_config(self, **kwargs):
        """
        Update current configuration
        
        Args:
            **kwargs: Parameters to update
        """
        self.config.update(**kwargs)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = MixBridgeConfig()
    
    def get_profile_configs(self) -> Dict[str, MixBridgeConfig]:
        """Get predefined configuration profiles using delta assignment strategy"""
        return {
            'production': MixBridgeConfig(
                precision_decimals=12,
                mathematical_validation=True,
                debug_mode=False,
                enable_audit_trail=True
            ),
            'development': MixBridgeConfig(
                precision_decimals=10,
                mathematical_validation=True,
                debug_mode=True,
                enable_audit_trail=True
            ),
            'performance': MixBridgeConfig(
                precision_decimals=8,
                mathematical_validation=False,
                debug_mode=False,
                enable_parallel_processing=True
            ),
            'accuracy': MixBridgeConfig(
                precision_decimals=15,
                mathematical_validation=True,
                debug_mode=True,
                validation_tolerance=1e-10
            )
        }
    
    def apply_profile(self, profile_name: str):
        """
        Apply a predefined configuration profile
        
        Args:
            profile_name: Name of profile to apply
        """
        profiles = self.get_profile_configs()
        if profile_name not in profiles:
            raise ValueError(f"Unknown profile: {profile_name}. Available: {list(profiles.keys())}")
        
        self._config = profiles[profile_name]


# Global configuration instance
_config_manager = ConfigManager()

def get_config() -> MixBridgeConfig:
    """Get global configuration instance"""
    return _config_manager.config

def set_config_path(path: str):
    """Set global configuration file path"""
    global _config_manager
    _config_manager = ConfigManager(path)

def apply_config_profile(profile_name: str):
    """Apply a configuration profile globally"""
    _config_manager.apply_profile(profile_name)