# Unique Filename System Documentation

## Overview

The vBridge project now uses a unique filename generation system for the `output/current/` directory to prevent file overwriting and provide better tracking of analysis runs.

## Key Improvements

### ✅ Before (Problems)
- Static files: `LATEST_mixbridge.csv`, `PREVIOUS_mixbridge.csv`
- Files would overwrite each other
- No way to distinguish between multiple runs
- Lost analysis history in current directory

### ✅ After (Solutions)
- **Unique filenames** with multiple uniqueness factors
- **Latest file tracking** via symlinks/copies
- **Session-based organization** for multiple runs
- **Automatic cleanup** and archiving
- **Rich metadata** for each file

## Filename Structure

### Unique Filename Format
```
{analysis_type}_{periods}_{strategy}_{timestamp}_{session_id}_{sequence}.csv
```

**Example**:
```
mixbridge_January2025-February2025_delta_assignment_20250725_164834_095cc7a0_seq001.csv
```

### Components
- **analysis_type**: `mixbridge`, `validation`, etc.
- **periods**: `January2025-February2025` (extracted from data)
- **strategy**: `delta_assignment`, `campaign_bridge`, etc.
- **timestamp**: `YYYYMMDD_HHMMSS` format
- **session_id**: 8-character UUID for this session
- **sequence**: `seq001`, `seq002`, etc. for ordering

### Latest File Tracking
- `LATEST_mixbridge.csv` - Always points to newest file
- `PREVIOUS_mixbridge.csv` - Previous version for comparison
- `LATEST_mixbridge_info.json` - Metadata for latest file

## Directory Structure

```
output/
├── current/           # Unique files + latest tracking
│   ├── mixbridge_..._seq001.csv
│   ├── mixbridge_..._seq002.csv
│   ├── LATEST_mixbridge.csv      # Points to newest
│   ├── PREVIOUS_mixbridge.csv    # Previous version
│   └── *.json                    # Metadata files
├── analyses/          # Timestamped copies for history
├── archive/           # Auto-archived old files
└── reports/           # Report files
```

## Usage

### Automatic Usage
The system activates automatically when using:
- `CampaignBridge.save_to_csv()`
- `ImprovedOutputManager.save_analysis()`
- Any vBridge analysis output

### Manual Usage
```python
from src.output.unique_manager import get_unique_output_manager

manager = get_unique_output_manager()

# Save analysis with unique filename
unique_path, latest_path, previous_path = manager.save_analysis(
    data=dataframe,
    analysis_type='mixbridge',
    periods={'p1': 'January 2025', 'p2': 'February 2025'},
    strategy='campaign_bridge',
    metadata={'custom_info': 'value'}
)

# Get latest file
latest_file = manager.get_latest_file('mixbridge')

# List current files
current_files = manager.get_current_files('mixbridge')

# Get status
status = manager.get_status_summary()
```

## Benefits

### 🚀 Performance
- **No file collisions** - Each run gets unique filename
- **Parallel execution safe** - Multiple processes won't conflict
- **Session isolation** - Different sessions have different IDs

### 📊 Tracking
- **Full history** in current directory (up to cleanup threshold)
- **Rich metadata** for each file with timing and parameters
- **Easy latest file access** via `LATEST_*` files
- **Previous version comparison** via `PREVIOUS_*` files

### 🧹 Organization
- **Automatic cleanup** when too many files accumulate
- **Smart archiving** based on age and count
- **Metadata preservation** during archiving
- **Configurable thresholds** for cleanup behavior

## Configuration

### Default Settings
```python
@dataclass
class UniqueOutputConfig:
    # Unique filename generation
    use_session_id: bool = True      # Include session ID
    use_timestamp: bool = True       # Include timestamp
    use_sequence: bool = True        # Include sequence number
    timestamp_format: str = '%Y%m%d_%H%M%S'
    
    # Latest file tracking
    maintain_latest_symlinks: bool = True
    latest_prefix: str = 'LATEST'
    previous_prefix: str = 'PREVIOUS'
    
    # File organization
    max_current_files: int = 10      # Max unique files in current/
    archive_threshold: int = 20      # Archive when current/ has 20+ files
```

### Customization
```python
from src.output.unique_manager import UniqueOutputManager, UniqueOutputConfig

# Custom configuration
config = UniqueOutputConfig(
    max_current_files=5,           # Keep fewer files
    use_session_id=False,          # Shorter filenames
    archive_threshold=10           # Archive sooner
)

manager = UniqueOutputManager(config)
```

## Migration

### Backward Compatibility
- **Old system still works** as fallback
- **Existing scripts unchanged** - automatically use unique system
- **Latest files maintained** - `LATEST_mixbridge.csv` still available
- **No breaking changes** to public APIs

### Migration Path
1. **Immediate**: New analyses use unique filenames automatically
2. **Legacy files**: Existing `LATEST_mixbridge.csv` files continue to work
3. **Gradual**: Old files get archived naturally over time

## Testing

### Validation Scripts
- `scripts/verification/test_unique_output_system.py` - Complete system test
- Tests uniqueness, file creation, metadata, integration
- Validates backward compatibility and error handling

### Test Results
- ✅ **100% unique filenames** across multiple runs
- ✅ **File existence** in both current/ and analyses/
- ✅ **Latest tracking** works correctly
- ✅ **Metadata system** functional
- ✅ **Campaign bridge integration** seamless

## Technical Implementation

### Core Classes
- `UniqueOutputManager` - Main filename generation and management
- `UniqueOutputConfig` - Configuration and settings
- Integration with existing `ImprovedOutputManager`

### Uniqueness Factors
1. **Timestamp** - Down to seconds (YYYYMMDD_HHMMSS)
2. **Session ID** - 8-character UUID per session
3. **Sequence Number** - Incremental counter within session
4. **Process isolation** - Each process gets unique session

### Error Handling
- **Graceful fallback** to timestamp-only naming if unique system fails
- **Import error handling** for backward compatibility
- **File operation error recovery** with logging
- **Metadata corruption resilience**

## Maintenance

### Automatic Cleanup
- Files auto-archive when current/ directory exceeds threshold
- Old files moved to archive/ with timestamp prefix
- Optional compression for archived files
- Metadata preserved during archiving

### Manual Cleanup
```python
# Check status
status = manager.get_status_summary()
print(f"Total unique files: {status['total_unique_files']}")

# Manual cleanup (dry run)
stats = manager.cleanup_old_files(dry_run=True)
print(f"Would archive {stats['archived']} files")

# Execute cleanup
stats = manager.cleanup_old_files(dry_run=False)
```

### Monitoring
- Log file operations at INFO level
- Track sequence counters and session IDs
- Monitor directory sizes and cleanup actions
- Metadata includes timing and performance info

---

## Example Output

### Before Improvement
```
output/current/
├── LATEST_mixbridge.csv    # Gets overwritten
└── PREVIOUS_mixbridge.csv  # Previous version
```

### After Improvement
```
output/current/
├── mixbridge_jan2025-feb2025_delta_20250725_164834_095cc7a0_seq001.csv
├── mixbridge_jan2025-feb2025_delta_20250725_164834_095cc7a0_seq002.csv
├── mixbridge_jan2025-feb2025_delta_20250725_164834_095cc7a0_seq003.csv
├── LATEST_mixbridge.csv    # Points to seq003
├── PREVIOUS_mixbridge.csv  # Points to seq002
└── *_info.json            # Metadata for each file
```

The unique filename system provides robust file management while maintaining the simplicity of accessing the latest results via familiar `LATEST_*` files.