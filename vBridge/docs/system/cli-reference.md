# CLI Reference

## Overview

Command-line tools for managing the MixBridge output system.

## Usage

```bash
python3 output_manager_cli.py <command> [options]
```

## Commands

### `status`

Shows overall output directory status including file counts, sizes, and latest files.

```bash
python3 output_manager_cli.py status
```

**Output:**
```
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

### `latest [analysis_type]`

Shows detailed information about the latest file for a specific analysis type.

```bash
# Show latest mixbridge analysis (default)
python3 output_manager_cli.py latest

# Show latest validation analysis
python3 output_manager_cli.py latest validation

# Show latest comparison analysis
python3 output_manager_cli.py latest comparison
```

**Parameters:**
- `analysis_type` (optional): Type of analysis (mixbridge, validation, comparison). Default: mixbridge

**Output:**
```
📄 LATEST MIXBRIDGE ANALYSIS
========================================
✅ Latest file: output/current/LATEST_mixbridge.csv
   Created: 2025-07-21T20:32:43.151625
   Strategy: delta_assignment
   Campaigns: 156
   Periods: jan2025 → feb2025
📋 Previous file: output/current/PREVIOUS_mixbridge.csv
```

### `recent [analysis_type] [limit]`

Lists recent analysis files with timestamps and sizes.

```bash
# Show last 10 mixbridge files (default)
python3 output_manager_cli.py recent

# Show last 5 mixbridge files
python3 output_manager_cli.py recent mixbridge 5

# Show last 15 validation files
python3 output_manager_cli.py recent validation 15
```

**Parameters:**
- `analysis_type` (optional): Type of analysis. Default: mixbridge
- `limit` (optional): Number of files to show. Default: 10

**Output:**
```
📅 RECENT MIXBRIDGE FILES (last 10)
============================================================
 1. mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv
     Size: 0.1MB, Modified: 2025-07-21T20:32:43.151625
 2. mixbridge_jan2025-feb2025_delta_assignment_20250721_203224.csv
     Size: 0.1MB, Modified: 2025-07-21T20:32:24.123456
 3. mixbridge_jan2025-feb2025_delta_20250721_190317.csv
     Size: 0.1MB, Modified: 2025-07-21T19:03:17.643075
```

### `cleanup [--execute]`

Cleans up old files by archiving them. By default, runs in dry-run mode.

```bash
# Dry run - show what would be archived
python3 output_manager_cli.py cleanup

# Actually execute the cleanup
python3 output_manager_cli.py cleanup --execute
```

**Options:**
- `--execute`: Actually perform the cleanup (without this, it's a dry run)

**Output (Dry Run):**
```
🧹 CLEANUP RESULTS
==============================
Files analyzed: 25
Would archive: 18
Errors: 0

⚠️  This was a dry run. Use --execute to actually archive files.
```

**Output (Executed):**
```
🧹 CLEANUP RESULTS
==============================
Files analyzed: 25
Archived: 18
Errors: 0
```

### `archive`

Force immediate archiving of old files based on the configured rules.

```bash
python3 output_manager_cli.py archive
```

**Output:**
```
✅ Old files archived
```

## Analysis Types

The CLI supports different analysis types:

| Type | Description | Latest File |
|------|-------------|-------------|
| `mixbridge` | Campaign bridge analysis | `LATEST_mixbridge.csv` |
| `validation` | Validation reports | `LATEST_validation.csv` |
| `comparison` | Comparison analysis | `LATEST_comparison.csv` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (unknown command, file not found, etc.) |

## Examples

### Daily Workflow

```bash
# Check overall status
python3 output_manager_cli.py status

# View latest analysis details
python3 output_manager_cli.py latest

# List recent files to see history
python3 output_manager_cli.py recent mixbridge 5

# Clean up old files weekly
python3 output_manager_cli.py cleanup --execute
```

### Debugging Workflow

```bash
# Check if files are being created
python3 output_manager_cli.py status

# See recent file activity
python3 output_manager_cli.py recent

# Check specific analysis type
python3 output_manager_cli.py latest validation

# Force archive if directories are full
python3 output_manager_cli.py archive
```

### Monitoring Workflow

```bash
# Create a simple monitoring script
#!/bin/bash
echo "=== Daily Output Status ==="
python3 output_manager_cli.py status

echo ""
echo "=== Latest Analysis ==="
python3 output_manager_cli.py latest

echo ""
echo "=== Recent Activity ==="
python3 output_manager_cli.py recent mixbridge 3
```

## Integration with Scripts

### Bash Integration

```bash
#!/bin/bash

# Get latest file path
LATEST_FILE=$(python3 output_manager_cli.py latest | grep "Latest file:" | cut -d' ' -f3)
echo "Processing: $LATEST_FILE"

# Check if cleanup is needed
CLEANUP_OUTPUT=$(python3 output_manager_cli.py cleanup)
WOULD_ARCHIVE=$(echo "$CLEANUP_OUTPUT" | grep "Would archive:" | cut -d' ' -f3)

if [ "$WOULD_ARCHIVE" -gt 10 ]; then
    echo "Archiving $WOULD_ARCHIVE files..."
    python3 output_manager_cli.py cleanup --execute
fi
```

### Python Integration

```python
import subprocess
import json

def get_latest_file_info():
    """Get information about the latest file using CLI"""
    result = subprocess.run([
        'python3', 'output_manager_cli.py', 'latest'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        # Parse the output to extract file path
        for line in result.stdout.split('\n'):
            if 'Latest file:' in line:
                return line.split('Latest file:')[1].strip()
    return None

def check_cleanup_needed():
    """Check if cleanup is needed"""
    result = subprocess.run([
        'python3', 'output_manager_cli.py', 'cleanup'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if 'Would archive:' in line:
                count = int(line.split('Would archive:')[1].strip())
                return count > 5  # Cleanup if more than 5 files
    return False

# Usage
latest_file = get_latest_file_info()
if latest_file:
    print(f"Latest analysis: {latest_file}")

if check_cleanup_needed():
    print("Running cleanup...")
    subprocess.run(['python3', 'output_manager_cli.py', 'cleanup', '--execute'])
```

## Error Handling

### Common Errors

**Command not found:**
```bash
$ python3 output_manager_cli.py invalid_command
❌ Unknown command: invalid_command
```

**Import errors:**
```bash
$ python3 output_manager_cli.py status
❌ Could not import improved output manager
```

**No files found:**
```bash
$ python3 output_manager_cli.py latest validation
📄 LATEST VALIDATION ANALYSIS
========================================
❌ No latest file found
```

### Troubleshooting

1. **Import errors**: Ensure you're running from the project root directory
2. **Permission errors**: Check file permissions in the output directory
3. **Missing directories**: The CLI will create missing directories automatically
4. **Corrupted metadata**: Delete the `.json` files and they'll be regenerated

## Performance Notes

- **Status command**: Fast operation, scans directory structure only
- **Recent command**: Performance depends on number of files in analyses directory
- **Cleanup command**: Can be slow with many files, but provides progress feedback
- **Archive command**: Compression is CPU-intensive but runs in background

## Configuration

The CLI uses the same configuration as the output manager:

```python
# To customize CLI behavior, modify the config
from src.improved_output_manager import ImprovedOutputConfig

config = ImprovedOutputConfig(
    archive_after_generations=5,  # Keep more files before archiving
    archive_age_days=14,          # Archive after 2 weeks instead of 1
    compress_archived=False       # Disable compression for faster archiving
)
```

## Scripting Tips

### Automated Cleanup

```bash
# Add to crontab for weekly cleanup
0 0 * * 0 cd /path/to/mixbridge && python3 output_manager_cli.py cleanup --execute
```

### Status Monitoring

```bash
# Check disk usage and cleanup if needed
TOTAL_SIZE=$(python3 output_manager_cli.py status | grep "Total files:" | cut -d' ' -f3)
if [ "$TOTAL_SIZE" -gt 100 ]; then
    python3 output_manager_cli.py cleanup --execute
fi
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Check Output Status
  run: |
    python3 output_manager_cli.py status
    python3 output_manager_cli.py cleanup --execute
```