#!/usr/bin/env python3
"""
Improved Output Manager for vBridge
Enhanced file organization with clearer latest file identification and automatic archiving
"""

import json
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
import pandas as pd
import warnings
import os

try:
    from ..common.logger import get_logger
    from .unique_manager import UniqueOutputManager, get_unique_output_manager
except ImportError:
    # Backwards compatibility during migration
    try:
        from .logger import get_logger
        from .unique_manager import UniqueOutputManager, get_unique_output_manager
    except ImportError:
        from logger import get_logger
        # Fallback if unique manager not available
        UniqueOutputManager = None
        get_unique_output_manager = None

logger = get_logger(__name__)


@dataclass
class ImprovedOutputConfig:
    """Enhanced configuration for output file management"""
    
    # Directory structure
    base_directory: str = 'output'
    subdirectories: Dict[str, str] = field(default_factory=lambda: {
        'current': 'current',      # Current/latest files only
        'archive': 'archive',      # Archived older files  
        'analyses': 'analyses',    # All analysis files (legacy compatibility)
        'reports': 'reports'       # Report files
    })
    
    # Latest file management
    latest_file_pattern: str = 'LATEST_{analysis_type}.csv'
    latest_metadata_pattern: str = 'LATEST_{analysis_type}_info.json'
    keep_previous_latest: bool = True
    previous_file_pattern: str = 'PREVIOUS_{analysis_type}.csv'
    
    # Archiving
    auto_archive: bool = True
    archive_after_generations: int = 3  # Archive after 3 new files
    archive_age_days: int = 7           # Also archive files older than 7 days
    compress_archived: bool = True
    
    # Naming
    include_timestamp: bool = True
    timestamp_format: str = '%Y%m%d_%H%M%S'
    include_strategy: bool = True
    
    # Safety
    max_files_before_cleanup: int = 50


class ImprovedOutputManager:
    """Enhanced output manager with clearer file identification and archiving"""
    
    def __init__(self, config: Optional[ImprovedOutputConfig] = None, use_unique_names: bool = True):
        self.config = config or ImprovedOutputConfig()
        self.use_unique_names = use_unique_names
        self.unique_manager = None
        
        if self.use_unique_names and get_unique_output_manager is not None:
            self.unique_manager = get_unique_output_manager()
        
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary directories"""
        base_path = Path(self.config.base_directory)
        
        for subdir in self.config.subdirectories.values():
            (base_path / subdir).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Output directories initialized: {list(self.config.subdirectories.values())}")
    
    def save_analysis(self,
                     data: pd.DataFrame,
                     analysis_type: str = 'mixbridge',
                     periods: Optional[Dict[str, str]] = None,
                     strategy: str = 'delta_assignment',
                     metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
        """
        Save analysis with improved file management
        
        Returns:
            Tuple of (latest_path, timestamped_path, previous_path)
        """
        logger.info(f"Saving {analysis_type} analysis with {len(data)} rows")
        
        # Use unique manager if available and enabled
        if self.use_unique_names and self.unique_manager is not None:
            return self.unique_manager.save_analysis(
                data=data,
                analysis_type=analysis_type,
                periods=periods,
                strategy=strategy,
                metadata=metadata
            )
        
        # Fallback to original implementation
        # Archive existing latest file first
        self._archive_current_latest(analysis_type)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        components = [analysis_type]
        
        if periods:
            period_str = f"{periods.get('p1', 'unknown')}-{periods.get('p2', 'unknown')}"
            components.append(period_str)
            
        if self.config.include_strategy and strategy:
            components.append(strategy)
            
        if self.config.include_timestamp:
            components.append(timestamp)
            
        timestamped_filename = '_'.join(components) + '.csv'
        
        # Save paths
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        analyses_dir = base_path / self.config.subdirectories['analyses']
        
        # Latest file (easy to find)
        latest_filename = self.config.latest_file_pattern.format(analysis_type=analysis_type)
        latest_path = current_dir / latest_filename
        
        # Timestamped file (for history)
        timestamped_path = analyses_dir / timestamped_filename
        
        # Previous file (backup of last latest)
        previous_filename = self.config.previous_file_pattern.format(analysis_type=analysis_type)
        previous_path = current_dir / previous_filename
        
        # Save files
        data.to_csv(latest_path, index=False)
        data.to_csv(timestamped_path, index=False)
        
        # Create metadata
        metadata_info = {
            'analysis_type': analysis_type,
            'created': datetime.now().isoformat(),
            'strategy': strategy,
            'periods': periods or {},
            'total_campaigns': len(data) - 1 if 'Total' in str(data.iloc[0, 0]) else len(data),
            'file_size': latest_path.stat().st_size,
            'timestamped_file': timestamped_filename,
            'previous_file': previous_filename if previous_path.exists() else None
        }
        
        if metadata:
            metadata_info.update(metadata)
            
        # Save metadata
        metadata_filename = self.config.latest_metadata_pattern.format(analysis_type=analysis_type)
        metadata_path = current_dir / metadata_filename
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_info, f, indent=2, default=str)
        
        # Trigger archiving if needed
        if self.config.auto_archive:
            self._auto_archive()
            
        logger.info(f"Analysis saved: latest={latest_path}, timestamped={timestamped_path}")
        
        return str(latest_path), str(timestamped_path), str(previous_path) if previous_path.exists() else None
    
    def _archive_current_latest(self, analysis_type: str):
        """Move current latest file to previous before creating new latest"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        latest_filename = self.config.latest_file_pattern.format(analysis_type=analysis_type)
        latest_path = current_dir / latest_filename
        
        previous_filename = self.config.previous_file_pattern.format(analysis_type=analysis_type)
        previous_path = current_dir / previous_filename
        
        if latest_path.exists():
            # Move current latest to previous
            if previous_path.exists():
                previous_path.unlink()  # Remove old previous
            
            shutil.move(str(latest_path), str(previous_path))
            logger.debug(f"Moved latest to previous: {previous_filename}")
    
    def _auto_archive(self):
        """Automatically archive old files based on configuration"""
        base_path = Path(self.config.base_directory)
        analyses_dir = base_path / self.config.subdirectories['analyses']
        archive_dir = base_path / self.config.subdirectories['archive']
        
        if not analyses_dir.exists():
            return
            
        # Get all analysis files sorted by modification time
        analysis_files = list(analyses_dir.glob('*.csv'))
        analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        archived_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.config.archive_age_days)
        
        # Archive by age
        for file_path in analysis_files:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                self._archive_file(file_path, archive_dir)
                archived_count += 1
        
        # Archive by count (keep only recent files)
        if len(analysis_files) > self.config.archive_after_generations:
            files_to_archive = analysis_files[self.config.archive_after_generations:]
            for file_path in files_to_archive:
                if file_path.exists():  # Check if not already archived
                    self._archive_file(file_path, archive_dir)
                    archived_count += 1
        
        if archived_count > 0:
            logger.info(f"Auto-archived {archived_count} old analysis files")
    
    def _archive_file(self, file_path: Path, archive_dir: Path):
        """Archive a single file with optional compression"""
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped archive filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f"archived_{timestamp}_{file_path.name}"
        archive_path = archive_dir / archive_name
        
        # Move file to archive
        shutil.move(str(file_path), str(archive_path))
        
        # Move associated metadata file if exists
        meta_path = file_path.with_suffix('.meta.json')
        if meta_path.exists():
            meta_archive_path = archive_dir / f"archived_{timestamp}_{meta_path.name}"
            shutil.move(str(meta_path), str(meta_archive_path))
        
        # Compress if enabled
        if self.config.compress_archived:
            self._compress_file(archive_path)
            
        logger.debug(f"Archived: {file_path.name} -> {archive_name}")
    
    def _compress_file(self, file_path: Path):
        """Compress file using gzip"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        file_path.unlink()  # Remove original
        logger.debug(f"Compressed: {file_path.name}")
    
    def get_latest_file(self, analysis_type: str = 'mixbridge') -> Optional[str]:
        """Get path to latest analysis file"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        latest_filename = self.config.latest_file_pattern.format(analysis_type=analysis_type)
        latest_path = current_dir / latest_filename
        
        if latest_path.exists():
            return str(latest_path)
        
        return None
    
    def get_previous_file(self, analysis_type: str = 'mixbridge') -> Optional[str]:
        """Get path to previous analysis file"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        previous_filename = self.config.previous_file_pattern.format(analysis_type=analysis_type)
        previous_path = current_dir / previous_filename
        
        if previous_path.exists():
            return str(previous_path)
        
        return None
    
    def get_file_info(self, analysis_type: str = 'mixbridge') -> Dict[str, Any]:
        """Get information about current and previous files"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        # Load metadata
        metadata_filename = self.config.latest_metadata_pattern.format(analysis_type=analysis_type)
        metadata_path = current_dir / metadata_filename
        
        info = {
            'latest_file': self.get_latest_file(analysis_type),
            'previous_file': self.get_previous_file(analysis_type),
            'has_metadata': metadata_path.exists(),
            'metadata': {}
        }
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    info['metadata'] = json.load(f)
            except (json.JSONDecodeError, IOError):
                logger.warning(f"Could not read metadata file: {metadata_path}")
        
        return info
    
    def list_recent_files(self, analysis_type: str = 'mixbridge', limit: int = 10) -> List[Dict[str, Any]]:
        """List recent analysis files"""
        base_path = Path(self.config.base_directory)
        analyses_dir = base_path / self.config.subdirectories['analyses']
        
        if not analyses_dir.exists():
            return []
        
        # Find files matching analysis type
        pattern = f"{analysis_type}_*.csv"
        files = list(analyses_dir.glob(pattern))
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        file_list = []
        for file_path in files[:limit]:
            file_info = {
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            file_list.append(file_info)
        
        return file_list
    
    def cleanup_old_files(self, dry_run: bool = False) -> Dict[str, int]:
        """Clean up old files beyond configured limits"""
        stats = {'analyzed': 0, 'archived': 0, 'errors': 0}
        
        base_path = Path(self.config.base_directory)
        analyses_dir = base_path / self.config.subdirectories['analyses']
        
        if not analyses_dir.exists():
            return stats
        
        files = list(analyses_dir.glob('*.csv'))
        stats['analyzed'] = len(files)
        
        if len(files) > self.config.max_files_before_cleanup:
            # Sort by modification time, keep newest files
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            files_to_archive = files[self.config.max_files_before_cleanup:]
            
            for file_path in files_to_archive:
                try:
                    if not dry_run:
                        archive_dir = base_path / self.config.subdirectories['archive']
                        self._archive_file(file_path, archive_dir)
                    stats['archived'] += 1
                except Exception as e:
                    logger.error(f"Error archiving {file_path}: {e}")
                    stats['errors'] += 1
        
        return stats
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of output directory status"""
        base_path = Path(self.config.base_directory)
        
        summary = {
            'base_directory': str(base_path),
            'directories': {},
            'latest_files': {},
            'total_files': 0
        }
        
        # Check each subdirectory
        for name, subdir in self.config.subdirectories.items():
            dir_path = base_path / subdir
            if dir_path.exists():
                files = list(dir_path.glob('*'))
                summary['directories'][name] = {
                    'path': str(dir_path),
                    'exists': True,
                    'file_count': len(files),
                    'total_size': sum(f.stat().st_size for f in files if f.is_file())
                }
                summary['total_files'] += len(files)
            else:
                summary['directories'][name] = {
                    'path': str(dir_path),
                    'exists': False,
                    'file_count': 0,
                    'total_size': 0
                }
        
        # Check for latest files
        for analysis_type in ['mixbridge', 'validation', 'comparison']:
            info = self.get_file_info(analysis_type)
            if info['latest_file']:
                summary['latest_files'][analysis_type] = info
        
        return summary


# Global instance
_global_output_manager: Optional[ImprovedOutputManager] = None


def get_output_manager() -> ImprovedOutputManager:
    """Get or create global output manager"""
    global _global_output_manager
    if _global_output_manager is None:
        _global_output_manager = ImprovedOutputManager()
    return _global_output_manager


def set_output_manager(manager: ImprovedOutputManager):
    """Set global output manager"""
    global _global_output_manager
    _global_output_manager = manager