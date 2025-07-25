"""
Enhanced Output Formatter for vBridge
Implements semantic file naming and advanced file management
"""

import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
import pandas as pd
import warnings
import os


@dataclass
class OutputNamingConfig:
    """Configuration for output file naming and management"""
    
    # Directory structure
    base_directory: str = 'output'
    use_subdirectories: bool = True
    subdirectories: Dict[str, str] = field(default_factory=lambda: {
        'analyses': 'analyses',
        'reports': 'reports', 
        'archive': 'archive',
        'latest': 'latest'
    })
    
    # Naming components
    include_strategy: bool = True
    include_timestamp: bool = True
    timestamp_format: str = '%Y%m%d_%H%M%S'
    period_separator: str = '-'
    component_separator: str = '_'
    
    # File management
    create_latest_links: bool = True
    archive_older_files: bool = True
    max_files_per_directory: int = 100
    archive_age_days: int = 30
    
    # Metadata
    generate_metadata: bool = True
    compress_archived: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutputNamingConfig':
        """Create from dictionary"""
        return cls(**data)


class EnhancedOutputFormatter:
    """Advanced output formatter with semantic naming and file management"""
    
    def __init__(self, config: Optional[OutputNamingConfig] = None):
        self.config = config or OutputNamingConfig()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary output directories"""
        base_path = Path(self.config.base_directory)
        
        if self.config.use_subdirectories:
            for subdir in self.config.subdirectories.values():
                (base_path / subdir).mkdir(parents=True, exist_ok=True)
        else:
            base_path.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, 
                         analysis_type: str,
                         periods: Dict[str, str],
                         strategy: Optional[str] = None,
                         extension: str = 'csv',
                         include_timestamp: Optional[bool] = None) -> str:
        """
        Generate semantic filename based on analysis context
        
        Args:
            analysis_type: Type of analysis (mixbridge, validation, comparison)
            periods: Dictionary with period information
            strategy: Strategy used (delta_assignment)
            extension: File extension
            include_timestamp: Override config timestamp setting
            
        Returns:
            Generated filename
        """
        components = [analysis_type]
        
        # Add period string
        if periods:
            period_parts = []
            if 'p1' in periods and 'p2' in periods:
                period_str = f"{periods['p1']}{self.config.period_separator}{periods['p2']}"
                period_parts.append(period_str)
            elif 'period_range' in periods:
                period_parts.append(periods['period_range'])
            
            if period_parts:
                components.extend(period_parts)
        
        # Add strategy if enabled and provided
        if strategy and self.config.include_strategy:
            # Shorten strategy name
            strategy_map = {
                'delta_assignment': 'delta'
            }
            components.append(strategy_map.get(strategy, strategy))
        
        # Add timestamp if enabled
        use_timestamp = include_timestamp if include_timestamp is not None else self.config.include_timestamp
        if use_timestamp:
            timestamp = datetime.now().strftime(self.config.timestamp_format)
            components.append(timestamp)
        
        filename = self.config.component_separator.join(components) + f'.{extension}'
        return filename
    
    def get_output_path(self, 
                       filename: str, 
                       subdirectory: Optional[str] = None) -> Path:
        """
        Get full output path for a filename
        
        Args:
            filename: Generated filename
            subdirectory: Subdirectory key (analyses, reports, etc.)
            
        Returns:
            Full path to output file
        """
        base_path = Path(self.config.base_directory)
        
        if self.config.use_subdirectories and subdirectory:
            subdir_name = self.config.subdirectories.get(subdirectory, subdirectory)
            return base_path / subdir_name / filename
        else:
            return base_path / filename
    
    def save_analysis(self,
                     data: pd.DataFrame,
                     analysis_type: str,
                     periods: Dict[str, str],
                     strategy: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     subdirectory: str = 'analyses') -> Tuple[str, Optional[str]]:
        """
        Save analysis with enhanced naming and metadata
        
        Args:
            data: DataFrame to save
            analysis_type: Type of analysis
            periods: Period information
            strategy: Strategy used
            metadata: Additional metadata
            subdirectory: Target subdirectory
            
        Returns:
            Tuple of (csv_path, metadata_path)
        """
        # Generate filename
        filename = self.generate_filename(
            analysis_type=analysis_type,
            periods=periods,
            strategy=strategy
        )
        
        # Get output path
        output_path = self.get_output_path(filename, subdirectory)
        
        # Save CSV file
        data.to_csv(output_path, index=False)
        csv_path = str(output_path)
        
        # Generate and save metadata
        metadata_path = None
        if self.config.generate_metadata:
            metadata_path = self._save_metadata(
                output_path, analysis_type, periods, strategy, metadata
            )
        
        # Create latest link
        if self.config.create_latest_links:
            self._create_latest_link(output_path, analysis_type)
        
        # Archive old files if enabled
        if self.config.archive_older_files:
            self._archive_old_files()
        
        return csv_path, metadata_path
    
    def _save_metadata(self,
                      csv_path: Path,
                      analysis_type: str,
                      periods: Dict[str, str],
                      strategy: Optional[str],
                      additional_metadata: Optional[Dict[str, Any]]) -> str:
        """Save metadata file"""
        metadata = {
            'analysis_type': analysis_type,
            'created': datetime.now().isoformat(),
            'csv_file': csv_path.name,
            'periods': periods,
            'strategy': strategy,
            'configuration': self.config.to_dict()
        }
        
        # Add additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Save metadata file
        meta_path = csv_path.with_suffix('.meta.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return str(meta_path)
    
    def _create_latest_link(self, file_path: Path, analysis_type: str):
        """Create symbolic link to latest file"""
        if not self.config.use_subdirectories:
            return
        
        latest_dir = Path(self.config.base_directory) / self.config.subdirectories['latest']
        latest_dir.mkdir(exist_ok=True)
        
        latest_name = f"{analysis_type}_latest{file_path.suffix}"
        latest_path = latest_dir / latest_name
        
        # Remove existing link
        if latest_path.exists() or latest_path.is_symlink():
            latest_path.unlink()
        
        # Create new link (relative path for portability)
        try:
            relative_path = os.path.relpath(file_path, latest_path.parent)
            latest_path.symlink_to(relative_path)
        except (OSError, NotImplementedError):
            # Fallback: copy file if symlinks not supported
            import shutil
            shutil.copy2(file_path, latest_path)
    
    def _archive_old_files(self):
        """Archive files older than configured threshold"""
        if not self.config.archive_older_files:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.config.archive_age_days)
        base_path = Path(self.config.base_directory)
        archive_dir = base_path / self.config.subdirectories['archive']
        
        # Find files to archive in analyses directory
        analyses_dir = base_path / self.config.subdirectories['analyses']
        if not analyses_dir.exists():
            return
        
        archived_count = 0
        for file_path in analyses_dir.glob('*.csv'):
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                self._archive_file(file_path, archive_dir)
                archived_count += 1
        
        if archived_count > 0:
            print(f"Archived {archived_count} old analysis files")
    
    def _archive_file(self, file_path: Path, archive_dir: Path):
        """Archive a single file"""
        archive_dir.mkdir(exist_ok=True)
        
        # Move main file
        archive_path = archive_dir / file_path.name
        file_path.rename(archive_path)
        
        # Move metadata file if exists
        meta_path = file_path.with_suffix('.meta.json')
        if meta_path.exists():
            meta_archive_path = archive_dir / meta_path.name
            meta_path.rename(meta_archive_path)
        
        # Compress if enabled
        if self.config.compress_archived:
            self._compress_file(archive_path)
            if (archive_dir / meta_path.name).exists():
                self._compress_file(archive_dir / meta_path.name)
    
    def _compress_file(self, file_path: Path):
        """Compress a file using gzip"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Remove original file
        file_path.unlink()
    
    def list_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent analysis files with metadata"""
        analyses_dir = Path(self.config.base_directory) / self.config.subdirectories['analyses']
        
        if not analyses_dir.exists():
            return []
        
        files = []
        for csv_file in analyses_dir.glob('*.csv'):
            file_info = {
                'filename': csv_file.name,
                'path': str(csv_file),
                'created': datetime.fromtimestamp(csv_file.stat().st_mtime),
                'size': csv_file.stat().st_size
            }
            
            # Load metadata if available
            meta_file = csv_file.with_suffix('.meta.json')
            if meta_file.exists():
                try:
                    with open(meta_file) as f:
                        metadata = json.load(f)
                    file_info.update({
                        'analysis_type': metadata.get('analysis_type'),
                        'strategy': metadata.get('strategy'),
                        'periods': metadata.get('periods')
                    })
                except (json.JSONDecodeError, KeyError):
                    pass
            
            files.append(file_info)
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        return files[:limit]
    
    def get_latest_analysis(self, analysis_type: str = 'mixbridge') -> Optional[str]:
        """Get path to latest analysis file"""
        latest_dir = Path(self.config.base_directory) / self.config.subdirectories['latest']
        latest_file = latest_dir / f"{analysis_type}_latest.csv"
        
        if latest_file.exists():
            return str(latest_file)
        
        # Fallback: find most recent file manually
        analyses_dir = Path(self.config.base_directory) / self.config.subdirectories['analyses']
        if not analyses_dir.exists():
            return None
        
        csv_files = list(analyses_dir.glob(f"{analysis_type}_*.csv"))
        if not csv_files:
            return None
        
        # Sort by modification time
        csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(csv_files[0])


def create_naming_profiles() -> Dict[str, OutputNamingConfig]:
    """Create pre-defined naming configuration profiles"""
    
    profiles = {
        'production': OutputNamingConfig(
            use_subdirectories=True,
            include_strategy=True,
            include_timestamp=True,
            create_latest_links=True,
            archive_older_files=True,
            generate_metadata=True,
            compress_archived=True,
            archive_age_days=30
        ),
        
        'development': OutputNamingConfig(
            use_subdirectories=True,
            include_strategy=True,
            include_timestamp=True,
            create_latest_links=True,
            archive_older_files=False,
            generate_metadata=True,
            compress_archived=False
        ),
        
        'legacy': OutputNamingConfig(
            use_subdirectories=False,
            include_strategy=False,
            include_timestamp=True,
            timestamp_format='%H%M',  # Original HHMM format
            create_latest_links=False,
            archive_older_files=False,
            generate_metadata=False
        ),
        
        'minimal': OutputNamingConfig(
            use_subdirectories=False,
            include_strategy=True,
            include_timestamp=False,
            create_latest_links=False,
            archive_older_files=False,
            generate_metadata=False
        ),
        
        'comprehensive': OutputNamingConfig(
            use_subdirectories=True,
            include_strategy=True,
            include_timestamp=True,
            create_latest_links=True,
            archive_older_files=True,
            generate_metadata=True,
            compress_archived=True,
            archive_age_days=14,  # More aggressive archiving
            max_files_per_directory=50
        )
    }
    
    return profiles


# Global formatter instance
_global_formatter: Optional[EnhancedOutputFormatter] = None


def get_global_formatter() -> EnhancedOutputFormatter:
    """Get or create global formatter instance"""
    global _global_formatter
    if _global_formatter is None:
        _global_formatter = EnhancedOutputFormatter()
    return _global_formatter


def set_global_formatter(formatter: EnhancedOutputFormatter):
    """Set global formatter instance"""
    global _global_formatter
    _global_formatter = formatter


def apply_naming_profile(profile_name: str):
    """Apply a naming profile globally"""
    profiles = create_naming_profiles()
    if profile_name not in profiles:
        available = ', '.join(profiles.keys())
        raise ValueError(f"Unknown profile: {profile_name}. Available: {available}")
    
    config = profiles[profile_name]
    formatter = EnhancedOutputFormatter(config)
    set_global_formatter(formatter)
    
    return formatter