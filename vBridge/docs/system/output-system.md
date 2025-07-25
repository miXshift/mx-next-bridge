# Output System

## Overview

MixBridge output management system provides easy access to latest results, automatic archiving, and comprehensive file organization.

## Key Features

- **Latest File Access**: Latest analysis at `output/current/LATEST_mixbridge.csv`
- **Previous Version Backup**: Automatic backup of previous analysis
- **Automatic Archiving**: Old files moved to timestamped storage
- **Rich Metadata**: Analysis details in JSON metadata files
- **CLI Tools**: Command-line management utilities

## Directory Structure

```
output/
├── current/           # Latest and previous files (easy access)
│   ├── LATEST_mixbridge.csv           # ← Always the newest file
│   ├── LATEST_mixbridge_info.json     # ← Metadata about latest
│   └── PREVIOUS_mixbridge.csv         # ← Previous version backup
│
├── analyses/          # All timestamped files (historical record)
│   ├── mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv
│   ├── mixbridge_jan2025-feb2025_delta_assignment_20250721_203224.csv
│   └── ...
│
├── archive/           # Automatically archived old files
│   ├── archived_20250721_203224_mixbridge_[...].csv.gz
│   ├── archived_20250721_203243_mixbridge_[...].csv.gz
│   └── ...
│
└── reports/           # Analysis reports and comparisons
    ├── comparison_results_*.json
    └── ...
```

## Quick Access Guide

### Getting the Latest File

The latest analysis is **always** available at:
```
output/current/LATEST_mixbridge.csv
```

No more searching through timestamped files!

### Getting the Previous File

The previous analysis is backed up at:
```
output/current/PREVIOUS_mixbridge.csv
```

### Getting File Information

Metadata about the latest file:
```
output/current/LATEST_mixbridge_info.json
```

## Usage Examples

### Basic Usage

```python
from src.campaign_bridge_modular import CampaignBridge

# Run analysis - output automatically managed
bridge = CampaignBridge('data/campaign_data.csv')
bridge.calculate_bridge()
latest_path, timestamped_path, previous_path = bridge.save_to_csv()

print(f"Latest file: {latest_path}")
# Output: Latest file: output/current/LATEST_mixbridge.csv
```

### Using the Output Manager Directly

```python
from src.improved_output_manager import get_output_manager
import pandas as pd

manager = get_output_manager()

# Save analysis with automatic management
latest_path, timestamped_path, previous_path = manager.save_analysis(
    data=analysis_df,
    analysis_type='mixbridge',
    periods={'p1': 'jan2025', 'p2': 'feb2025'},
    strategy='delta_assignment',
    metadata={'data_source': 'campaign_data.csv'}
)
```

### Getting Latest File Programmatically

```python
from src.improved_output_manager import get_output_manager

manager = get_output_manager()

# Get latest file path
latest_file = manager.get_latest_file('mixbridge')
print(f"Latest analysis: {latest_file}")

# Get file information
info = manager.get_file_info('mixbridge')
print(f"Created: {info['metadata']['created']}")
print(f"Campaigns: {info['metadata']['total_campaigns']}")
```

## CLI Management Tools

The system includes a comprehensive command-line interface for managing output files.

### Basic Commands

```bash
# Show overall status
python3 output_manager_cli.py status

# Show latest file information
python3 output_manager_cli.py latest

# List recent files
python3 output_manager_cli.py recent

# Clean up old files (dry run)
python3 output_manager_cli.py cleanup

# Actually execute cleanup
python3 output_manager_cli.py cleanup --execute

# Force archive old files
python3 output_manager_cli.py archive
```

### Example Output

```bash
$ python3 output_manager_cli.py status
📊 OUTPUT DIRECTORY STATUS
==================================================
Base directory: output
Total files: 20

📁 DIRECTORIES:
  ✅ current    (  3 files, 0.2MB) - output/current
  ✅ archive    ( 11 files, 0.2MB) - output/archive
  ✅ analyses   (  4 files, 0.3MB) - output/analyses
  ✅ reports    (  2 files, 0.0MB) - output/reports

📄 LATEST FILES:
  📄 mixbridge:
      Latest: LATEST_mixbridge.csv
      Previous: PREVIOUS_mixbridge.csv
      Created: 2025-07-21T20:32:43.151625, Campaigns: 156
```

## Automatic Archiving

### How It Works

The system automatically archives old files based on configurable criteria:

1. **Age-based**: Files older than 7 days (configurable)
2. **Count-based**: Keep only the 3 most recent files (configurable)
3. **Compression**: Archived files are compressed with gzip
4. **Timestamped**: Archive names include timestamp to prevent conflicts

### Configuration

```python
from src.improved_output_manager import ImprovedOutputConfig

config = ImprovedOutputConfig(
    auto_archive=True,                    # Enable automatic archiving
    archive_after_generations=3,          # Keep only 3 recent files
    archive_age_days=7,                   # Archive files older than 7 days
    compress_archived=True,               # Compress archived files
    max_files_before_cleanup=50           # Emergency cleanup threshold
)
```

### Manual Archiving

```python
from src.improved_output_manager import get_output_manager

manager = get_output_manager()
manager._auto_archive()  # Force archiving now
```

## File Naming Conventions

### Latest Files
- `LATEST_{analysis_type}.csv` - Always the newest analysis
- `LATEST_{analysis_type}_info.json` - Metadata about the latest file
- `PREVIOUS_{analysis_type}.csv` - Backup of the previous version

### Timestamped Files
- `{analysis_type}_{periods}_{strategy}_{timestamp}.csv`
- Example: `mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv`

### Archived Files
- `archived_{timestamp}_{original_filename}.csv.gz`
- Example: `archived_20250721_203224_mixbridge_jan2025-feb2025_delta_20250718_145844.csv.gz`

## Metadata Structure

The metadata file (`LATEST_mixbridge_info.json`) contains:

```json
{
  "analysis_type": "mixbridge",
  "created": "2025-07-21T20:32:43.151625",
  "strategy": "delta_assignment",
  "periods": {
    "p1": "jan2025",
    "p2": "feb2025"
  },
  "total_campaigns": 156,
  "file_size": 123456,
  "timestamped_file": "mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv",
  "previous_file": "PREVIOUS_mixbridge.csv"
}
```

## Migration from Legacy System

### Automatic Detection

The system automatically detects and works with both old and new output formats:

```python
# This works with both old and new systems
bridge = CampaignBridge('data.csv')
result = bridge.save_to_csv()

# New system returns: (latest_path, timestamped_path, previous_path)
# Old system returns: (csv_path, meta_path)
```

### Finding Existing Files

If you have existing output files, the system can help organize them:

```bash
# Check what's currently in your output directory
python3 output_manager_cli.py status

# Clean up old files
python3 output_manager_cli.py cleanup --execute
```

## Best Practices

### For Users

1. **Always use the latest file**: `output/current/LATEST_mixbridge.csv`
2. **Check metadata**: Use the info file to understand analysis parameters
3. **Keep previous version**: Don't delete `PREVIOUS_mixbridge.csv` manually
4. **Use CLI tools**: Leverage the management CLI for status and cleanup

### For Developers

1. **Use the output manager**: Don't implement custom file naming
2. **Include metadata**: Provide rich metadata for tracking
3. **Handle return values**: Check for 2-tuple vs 3-tuple returns for compatibility
4. **Configure appropriately**: Set archiving parameters based on usage patterns

## Configuration Reference

### ImprovedOutputConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_directory` | `'output'` | Base output directory |
| `auto_archive` | `True` | Enable automatic archiving |
| `archive_after_generations` | `3` | Keep this many recent files |
| `archive_age_days` | `7` | Archive files older than this |
| `compress_archived` | `True` | Compress archived files |
| `latest_file_pattern` | `'LATEST_{analysis_type}.csv'` | Pattern for latest files |
| `previous_file_pattern` | `'PREVIOUS_{analysis_type}.csv'` | Pattern for previous files |
| `keep_previous_latest` | `True` | Keep backup of previous version |
| `max_files_before_cleanup` | `50` | Emergency cleanup threshold |

### Directory Configuration

| Directory | Purpose | Configurable |
|-----------|---------|--------------|
| `current` | Latest and previous files | Yes |
| `archive` | Archived old files | Yes |
| `analyses` | All timestamped files | Yes |
| `reports` | Analysis reports | Yes |

## Troubleshooting

### Common Issues

**Q: Where is my latest analysis file?**
A: Always at `output/current/LATEST_mixbridge.csv`

**Q: My old files disappeared!**
A: Check `output/archive/` - they were automatically archived and compressed.

**Q: How do I disable archiving?**
A: Set `auto_archive=False` in the configuration or use explicit filenames.

**Q: Can I change the file naming?**
A: Yes, modify the `latest_file_pattern` and `previous_file_pattern` in configuration.

**Q: How do I restore an archived file?**
A: Decompress the `.gz` file and copy it back to the desired location.

### Error Recovery

```python
# If you need to recover from issues
from src.improved_output_manager import get_output_manager

manager = get_output_manager()

# Check status
status = manager.get_status_summary()
print(status)

# Force cleanup if needed
stats = manager.cleanup_old_files(dry_run=False)
print(f"Cleaned up {stats['archived']} files")
```

## Performance Considerations

- **Compression**: Archived files use gzip compression (typically 60-80% size reduction)
- **I/O Optimization**: Batch operations minimize disk access
- **Memory Efficient**: Large files are streamed during compression
- **Background Processing**: Archiving doesn't block analysis operations

## Security Considerations

- **File Permissions**: Maintains original file permissions
- **Path Safety**: Prevents path traversal attacks
- **Data Integrity**: Checksums could be added for critical applications
- **Access Control**: Respects system file access controls

## Future Enhancements

Planned improvements include:

- **Cloud Storage Integration**: Support for S3, Azure Blob, GCS
- **Database Tracking**: Optional database for advanced file tracking
- **Retention Policies**: More sophisticated retention rules
- **Notification System**: Alerts for archiving and cleanup operations
- **Web Interface**: Browser-based file management
- **Backup Verification**: Automated integrity checking

For questions or feature requests, please refer to the main project documentation or open an issue.