#!/usr/bin/env python3
"""
Unique Output Manager for vBridge
Enhanced output management with unique filenames in current directory
"""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd

try:
    from ..common.logger import get_logger
except ImportError:
    # Backwards compatibility during migration
    try:
        from .logger import get_logger
    except ImportError:
        from logger import get_logger

logger = get_logger(__name__)


@dataclass
class UniqueOutputConfig:
    """Configuration for unique filename output management"""
    
    # Directory structure
    base_directory: str = 'output'
    subdirectories: Dict[str, str] = None
    
    # Unique filename generation
    use_session_id: bool = True
    use_timestamp: bool = True
    use_sequence: bool = True
    timestamp_format: str = '%Y%m%d_%H%M%S'
    
    # Latest file tracking
    maintain_latest_symlinks: bool = True
    latest_prefix: str = 'LATEST'
    previous_prefix: str = 'PREVIOUS'
    
    # File organization
    max_current_files: int = 10  # Max files to keep in current before auto-cleanup
    archive_threshold: int = 20  # Archive when current directory has this many files
    
    def __post_init__(self):
        if self.subdirectories is None:
            self.subdirectories = {
                'current': 'current',
                'archive': 'archive', 
                'analyses': 'analyses',
                'reports': 'reports'
            }


class UniqueOutputManager:
    """Output manager that generates unique filenames while maintaining latest file tracking"""
    
    def __init__(self, config: Optional[UniqueOutputConfig] = None):
        self.config = config or UniqueOutputConfig()
        self.session_id = self._generate_session_id()
        self.sequence_counter = 0
        self._setup_directories()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        if self.config.use_session_id:
            # Use first 8 characters of UUID for brevity
            return str(uuid.uuid4())[:8]
        return ""
    
    def _setup_directories(self):
        """Create necessary directories"""
        base_path = Path(self.config.base_directory)
        
        for subdir in self.config.subdirectories.values():
            (base_path / subdir).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Output directories initialized with session ID: {self.session_id}")
    
    def _generate_unique_filename(self, 
                                 analysis_type: str,
                                 periods: Optional[Dict[str, str]] = None,
                                 strategy: str = 'delta_assignment',
                                 extension: str = '.csv') -> str:
        """Generate unique filename with multiple uniqueness factors"""
        
        components = [analysis_type]
        
        # Add periods if provided
        if periods:
            period_str = f"{periods.get('p1', 'unknown')}-{periods.get('p2', 'unknown')}"
            components.append(period_str)
        
        # Add strategy
        if strategy:
            components.append(strategy)
            
        # Add timestamp
        if self.config.use_timestamp:
            timestamp = datetime.now().strftime(self.config.timestamp_format)
            components.append(timestamp)
            
        # Add session ID
        if self.config.use_session_id and self.session_id:
            components.append(self.session_id)
            
        # Add sequence number
        if self.config.use_sequence:
            self.sequence_counter += 1
            components.append(f"seq{self.sequence_counter:03d}")
        
        return '_'.join(components) + extension
    
    def _update_latest_tracking(self, 
                               unique_filename: str,
                               analysis_type: str,
                               current_dir: Path):
        """Update latest file tracking using symlinks or copies"""
        
        latest_filename = f"{self.config.latest_prefix}_{analysis_type}.csv"
        previous_filename = f"{self.config.previous_prefix}_{analysis_type}.csv"
        
        latest_path = current_dir / latest_filename
        previous_path = current_dir / previous_filename
        unique_path = current_dir / unique_filename
        
        # Move current latest to previous
        if latest_path.exists():
            if previous_path.exists():
                previous_path.unlink()
            
            if self.config.maintain_latest_symlinks and latest_path.is_symlink():
                # If it's a symlink, just remove it
                latest_path.unlink()
            else:
                # If it's a regular file, move it to previous
                shutil.move(str(latest_path), str(previous_path))
        
        # Create new latest reference
        if self.config.maintain_latest_symlinks:
            try:
                # Create symlink to unique file
                latest_path.symlink_to(unique_filename)
                logger.debug(f"Created symlink: {latest_filename} -> {unique_filename}")
            except OSError:
                # Fall back to copying if symlinks aren't supported
                shutil.copy2(str(unique_path), str(latest_path))
                logger.debug(f"Created copy: {latest_filename} (symlink failed)")
        else:
            # Create copy of unique file as latest
            shutil.copy2(str(unique_path), str(latest_path))
            logger.debug(f"Created copy: {latest_filename}")
    
    def save_analysis(self,
                     data: pd.DataFrame,
                     analysis_type: str = 'mixbridge',
                     periods: Optional[Dict[str, str]] = None,
                     strategy: str = 'delta_assignment',
                     metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
        """
        Save analysis with unique filename
        
        Returns:
            Tuple of (unique_path, latest_path, previous_path)
        """
        logger.info(f"Saving {analysis_type} analysis with unique filename ({len(data)} rows)")
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(
            analysis_type=analysis_type,
            periods=periods,
            strategy=strategy
        )
        
        # Set up paths
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        analyses_dir = base_path / self.config.subdirectories['analyses']
        
        unique_path = current_dir / unique_filename
        latest_filename = f"{self.config.latest_prefix}_{analysis_type}.csv"
        latest_path = current_dir / latest_filename
        previous_filename = f"{self.config.previous_prefix}_{analysis_type}.csv"
        previous_path = current_dir / previous_filename
        
        # Save unique file
        data.to_csv(unique_path, index=False)
        
        # Also save timestamped copy in analyses directory
        analyses_copy_path = analyses_dir / unique_filename
        data.to_csv(analyses_copy_path, index=False)
        
        # Update latest file tracking
        self._update_latest_tracking(unique_filename, analysis_type, current_dir)
        
        # Create metadata
        metadata_info = {
            'analysis_type': analysis_type,
            'created': datetime.now().isoformat(),
            'strategy': strategy,
            'periods': periods or {},
            'session_id': self.session_id,
            'sequence_number': self.sequence_counter,
            'unique_filename': unique_filename,
            'total_campaigns': len(data) - 1 if len(data) > 0 and 'Total' in str(data.iloc[-1, 0]) else len(data),
            'file_size': unique_path.stat().st_size,
            'latest_file': latest_filename,
            'previous_file': previous_filename if previous_path.exists() else None
        }
        
        if metadata:
            metadata_info.update(metadata)
        
        # Save metadata for unique file
        metadata_filename = unique_filename.replace('.csv', '_info.json')
        metadata_path = current_dir / metadata_filename
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_info, f, indent=2, default=str)
        
        # Also save latest metadata
        latest_metadata_filename = f"{self.config.latest_prefix}_{analysis_type}_info.json"
        latest_metadata_path = current_dir / latest_metadata_filename
        
        with open(latest_metadata_path, 'w') as f:
            json.dump(metadata_info, f, indent=2, default=str)
        
        logger.info(f"Analysis saved: unique={unique_path.name}, latest={latest_filename}")
        
        # Trigger cleanup if needed
        self._cleanup_if_needed()
        
        return str(unique_path), str(latest_path), str(previous_path) if previous_path.exists() else None
    
    def _cleanup_if_needed(self):
        """Clean up current directory if it has too many files"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        # Count actual analysis files (not symlinks or metadata)
        analysis_files = [f for f in current_dir.glob('*.csv') 
                         if not f.name.startswith(self.config.latest_prefix) 
                         and not f.name.startswith(self.config.previous_prefix)
                         and not f.is_symlink()]
        
        if len(analysis_files) > self.config.archive_threshold:
            # Sort by modification time, keep newest files
            analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            files_to_archive = analysis_files[self.config.max_current_files:]
            
            archive_dir = base_path / self.config.subdirectories['archive']
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archived_count = 0
            for file_path in files_to_archive:
                try:
                    # Move to archive with timestamp prefix
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    archived_name = f"archived_{timestamp}_{file_path.name}"
                    archive_path = archive_dir / archived_name
                    
                    shutil.move(str(file_path), str(archive_path))
                    
                    # Move associated metadata if exists
                    metadata_name = file_path.name.replace('.csv', '_info.json')
                    metadata_path = current_dir / metadata_name
                    if metadata_path.exists():
                        archived_metadata_name = f"archived_{timestamp}_{metadata_name}"
                        archived_metadata_path = archive_dir / archived_metadata_name
                        shutil.move(str(metadata_path), str(archived_metadata_path))
                    
                    archived_count += 1
                    
                except Exception as e:
                    logger.error(f"Error archiving {file_path}: {e}")
            
            if archived_count > 0:
                logger.info(f"Auto-archived {archived_count} files from current directory")
    
    def get_latest_file(self, analysis_type: str = 'mixbridge') -> Optional[str]:
        """Get path to latest analysis file"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        latest_filename = f"{self.config.latest_prefix}_{analysis_type}.csv"
        latest_path = current_dir / latest_filename
        
        if latest_path.exists():
            return str(latest_path)
        
        return None
    
    def get_current_files(self, analysis_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of current unique files with metadata"""
        base_path = Path(self.config.base_directory)
        current_dir = base_path / self.config.subdirectories['current']
        
        # Get all analysis files (excluding LATEST/PREVIOUS files)
        pattern = '*.csv'
        all_files = list(current_dir.glob(pattern))
        
        analysis_files = [f for f in all_files 
                         if not f.name.startswith(self.config.latest_prefix)
                         and not f.name.startswith(self.config.previous_prefix)]
        
        # Filter by analysis type if specified
        if analysis_type:
            analysis_files = [f for f in analysis_files if f.name.startswith(analysis_type)]
        
        # Sort by modification time (newest first)
        analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        file_list = []
        for file_path in analysis_files:
            # Load metadata if available
            metadata_name = file_path.name.replace('.csv', '_info.json')
            metadata_path = current_dir / metadata_name
            
            file_info = {
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'metadata': {}
            }
            
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r') as f:
                        file_info['metadata'] = json.load(f)
                except (json.JSONDecodeError, IOError):
                    logger.warning(f"Could not read metadata for {file_path.name}")
            
            file_list.append(file_info)
        
        return file_list
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status of output management"""
        base_path = Path(self.config.base_directory)
        
        summary = {
            'session_id': self.session_id,
            'sequence_counter': self.sequence_counter,
            'base_directory': str(base_path),
            'directories': {},
            'current_files': {},
            'total_unique_files': 0
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
                
                if name == 'current':
                    unique_files = [f for f in files 
                                  if f.name.endswith('.csv')
                                  and not f.name.startswith(self.config.latest_prefix)
                                  and not f.name.startswith(self.config.previous_prefix)]
                    summary['total_unique_files'] = len(unique_files)
            else:
                summary['directories'][name] = {
                    'path': str(dir_path),
                    'exists': False,
                    'file_count': 0,
                    'total_size': 0
                }
        
        # Get current files by analysis type
        current_files = self.get_current_files()
        analysis_types = set()
        for file_info in current_files:
            # Extract analysis type from filename
            filename_parts = file_info['filename'].split('_')
            if filename_parts:
                analysis_types.add(filename_parts[0])
        
        for analysis_type in analysis_types:
            type_files = self.get_current_files(analysis_type)
            summary['current_files'][analysis_type] = {
                'count': len(type_files),
                'latest': self.get_latest_file(analysis_type),
                'newest_unique': type_files[0]['filename'] if type_files else None
            }
        
        return summary


# Global instance with unique manager
_global_unique_manager: Optional[UniqueOutputManager] = None


def get_unique_output_manager() -> UniqueOutputManager:
    """Get or create global unique output manager"""
    global _global_unique_manager
    if _global_unique_manager is None:
        _global_unique_manager = UniqueOutputManager()
    return _global_unique_manager


def set_unique_output_manager(manager: UniqueOutputManager):
    """Set global unique output manager"""
    global _global_unique_manager
    _global_unique_manager = manager