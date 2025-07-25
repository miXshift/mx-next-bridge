# Output System Usage Examples

## Overview

This document provides practical examples of using the MixBridge v2 output system in real-world scenarios. From basic usage to advanced workflows, these examples demonstrate how to effectively leverage the improved file management capabilities.

## Basic Examples

### Example 1: Running a Standard Analysis

```python
from src.campaign_bridge_modular import CampaignBridge

# Run a standard bridge analysis
bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
result = bridge.calculate_bridge()

# Save with improved output system
latest_path, timestamped_path, previous_path = bridge.save_to_csv()

print(f"✅ Analysis complete!")
print(f"📄 Latest file: {latest_path}")
print(f"📅 Timestamped copy: {timestamped_path}")
if previous_path:
    print(f"📋 Previous backup: {previous_path}")
```

**Output:**
```
✅ Analysis complete!
📄 Latest file: output/current/LATEST_mixbridge.csv
📅 Timestamped copy: output/analyses/mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv
📋 Previous backup: output/current/PREVIOUS_mixbridge.csv
```

### Example 2: Accessing the Latest File

```python
import pandas as pd
from src.improved_output_manager import get_output_manager

# Always get the latest analysis
manager = get_output_manager()
latest_file = manager.get_latest_file('mixbridge')

if latest_file:
    df = pd.read_csv(latest_file)
    print(f"📊 Loaded {len(df)} rows from latest analysis")
    
    # Get metadata about the file
    info = manager.get_file_info('mixbridge')
    metadata = info['metadata']
    print(f"📅 Created: {metadata['created']}")
    print(f"🎯 Strategy: {metadata['strategy']}")
    print(f"📈 Campaigns: {metadata['total_campaigns']}")
else:
    print("❌ No latest file found")
```

## Advanced Examples

### Example 3: Automated Daily Workflow

```python
#!/usr/bin/env python3
"""
Daily automated analysis workflow with intelligent file management
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from src.campaign_bridge_modular import CampaignBridge
from src.improved_output_manager import get_output_manager

def daily_analysis_workflow(data_path: str):
    """Run daily analysis with automatic comparison to previous day"""
    
    print(f"🚀 Starting daily analysis: {datetime.now()}")
    
    # Get the output manager
    manager = get_output_manager()
    
    # Check if we have a previous analysis
    previous_file = manager.get_previous_file('mixbridge')
    has_previous = previous_file is not None
    
    print(f"📋 Previous analysis: {'Found' if has_previous else 'Not found'}")
    
    # Run new analysis
    bridge = CampaignBridge(data_path)
    result = bridge.calculate_bridge()
    latest_path, timestamped_path, previous_path = bridge.save_to_csv()
    
    print(f"✅ New analysis saved: {Path(latest_path).name}")
    
    # Compare with previous if available
    if has_previous and previous_path:
        print("📊 Comparing with previous analysis...")
        compare_analyses(latest_path, previous_path)
    
    # Check if cleanup is needed
    stats = manager.cleanup_old_files(dry_run=True)
    if stats['archived'] > 10:
        print(f"🧹 Archiving {stats['archived']} old files...")
        manager.cleanup_old_files(dry_run=False)
    
    return latest_path

def compare_analyses(current_path: str, previous_path: str):
    """Compare current analysis with previous"""
    current_df = pd.read_csv(current_path)
    previous_df = pd.read_csv(previous_path)
    
    # Find the totals rows
    current_total = current_df[current_df['Campaign'].str.contains('Total', na=False)]
    previous_total = previous_df[previous_df['Campaign'].str.contains('Total', na=False)]
    
    if not current_total.empty and not previous_total.empty:
        current_spend = current_total['Spend - February 2025'].iloc[0]
        previous_spend = previous_total['Spend - February 2025'].iloc[0]
        
        change = current_spend - previous_spend
        change_pct = (change / previous_spend * 100) if previous_spend != 0 else 0
        
        print(f"💰 Spend change: ${change:,.2f} ({change_pct:+.1f}%)")
        
        if abs(change_pct) > 5:
            print("⚠️  Significant change detected - review recommended")

if __name__ == "__main__":
    latest_file = daily_analysis_workflow('data/Hydrapak YTD - campaign.csv')
    print(f"🎯 Latest analysis available at: {latest_file}")
```

### Example 4: Batch Processing Multiple Periods

```python
#!/usr/bin/env python3
"""
Process multiple time periods and organize results
"""

import pandas as pd
from src.improved_output_manager import get_output_manager, ImprovedOutputConfig
from src.campaign_bridge_modular import CampaignBridge

def batch_period_analysis(data_files: dict):
    """Process multiple periods with organized output"""
    
    # Configure for batch processing
    config = ImprovedOutputConfig(
        archive_after_generations=5,  # Keep more files during batch
        auto_archive=False            # Disable auto-archive during batch
    )
    
    manager = get_output_manager()
    results = {}
    
    for period_name, file_path in data_files.items():
        print(f"🔄 Processing {period_name}...")
        
        try:
            # Create custom analysis type for this period
            analysis_type = f"mixbridge_{period_name}"
            
            # Run analysis
            bridge = CampaignBridge(file_path)
            bridge_data = bridge.calculate_bridge()
            
            # Save with custom metadata
            latest_path, timestamped_path, previous_path = manager.save_analysis(
                data=bridge_data,
                analysis_type=analysis_type,
                periods={'period': period_name},
                strategy='delta_assignment',
                metadata={
                    'batch_id': 'quarterly_review',
                    'source_file': file_path,
                    'processed_at': pd.Timestamp.now().isoformat()
                }
            )
            
            results[period_name] = {
                'latest': latest_path,
                'timestamped': timestamped_path,
                'status': 'success'
            }
            
            print(f"✅ {period_name} completed")
            
        except Exception as e:
            print(f"❌ {period_name} failed: {str(e)}")
            results[period_name] = {'status': 'failed', 'error': str(e)}
    
    # Re-enable auto-archive and clean up
    config.auto_archive = True
    manager._auto_archive()
    
    return results

# Example usage
data_files = {
    'q1_2025': 'data/q1_campaign_data.csv',
    'q2_2025': 'data/q2_campaign_data.csv',
    'q3_2025': 'data/q3_campaign_data.csv',
    'q4_2025': 'data/q4_campaign_data.csv'
}

results = batch_period_analysis(data_files)

print("\n📊 Batch Processing Summary:")
for period, result in results.items():
    status_icon = "✅" if result['status'] == 'success' else "❌"
    print(f"  {status_icon} {period}: {result['status']}")
    if result['status'] == 'success':
        print(f"      📄 {result['latest']}")
```

### Example 5: Integration with External Systems

```python
#!/usr/bin/env python3
"""
Integration example for external reporting systems
"""

import json
import requests
from pathlib import Path
from src.improved_output_manager import get_output_manager

def send_to_dashboard(analysis_type: str = 'mixbridge'):
    """Send latest analysis results to external dashboard"""
    
    manager = get_output_manager()
    
    # Get latest file and metadata
    latest_file = manager.get_latest_file(analysis_type)
    file_info = manager.get_file_info(analysis_type)
    
    if not latest_file:
        print(f"❌ No latest {analysis_type} file found")
        return False
    
    # Read the analysis data
    import pandas as pd
    df = pd.read_csv(latest_file)
    
    # Extract key metrics from totals row
    totals_row = df[df['Campaign'].str.contains('Total', na=False)]
    if totals_row.empty:
        print("❌ No totals row found in analysis")
        return False
    
    # Prepare payload
    metrics = {
        'timestamp': file_info['metadata']['created'],
        'analysis_type': analysis_type,
        'strategy': file_info['metadata']['strategy'],
        'total_campaigns': file_info['metadata']['total_campaigns'],
        'spend_jan': float(totals_row['Spend - January 2025'].iloc[0]),
        'spend_feb': float(totals_row['Spend - February 2025'].iloc[0]),
        'spend_change': float(totals_row['Spend - Net Change'].iloc[0]),
        'spend_change_pct': float(totals_row['Spend - % Change'].iloc[0]),
        'sales_jan': float(totals_row['Total Ad Sales - January 2025'].iloc[0]),
        'sales_feb': float(totals_row['Total Ad Sales - February 2025'].iloc[0]),
        'file_path': latest_file,
        'file_size': file_info['metadata']['file_size']
    }
    
    # Send to dashboard (example endpoint)
    try:
        response = requests.post(
            'https://dashboard.example.com/api/mixbridge-metrics',
            json=metrics,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Metrics sent to dashboard successfully")
            return True
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Failed to send to dashboard: {str(e)}")
        return False

def export_for_excel(analysis_type: str = 'mixbridge', output_path: str = None):
    """Export latest analysis in Excel-compatible format"""
    
    manager = get_output_manager()
    latest_file = manager.get_latest_file(analysis_type)
    
    if not latest_file:
        print(f"❌ No latest {analysis_type} file found")
        return None
    
    # Read and process data
    import pandas as pd
    df = pd.read_csv(latest_file)
    
    # Create Excel-friendly format
    if output_path is None:
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"exports/mixbridge_export_{timestamp}.xlsx"
    
    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Export with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main data
        df.to_excel(writer, sheet_name='Bridge Analysis', index=False)
        
        # Summary sheet
        totals_row = df[df['Campaign'].str.contains('Total', na=False)]
        if not totals_row.empty:
            summary_data = {
                'Metric': ['Total Campaigns', 'Spend January', 'Spend February', 
                          'Spend Change', 'Spend Change %'],
                'Value': [
                    len(df) - 1,  # Exclude totals row
                    totals_row['Spend - January 2025'].iloc[0],
                    totals_row['Spend - February 2025'].iloc[0],
                    totals_row['Spend - Net Change'].iloc[0],
                    totals_row['Spend - % Change'].iloc[0]
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Metadata sheet
        file_info = manager.get_file_info(analysis_type)
        metadata_df = pd.DataFrame([
            ['Created', file_info['metadata']['created']],
            ['Strategy', file_info['metadata']['strategy']],
            ['Source File', file_info['metadata'].get('data_source', 'Unknown')],
            ['File Path', latest_file]
        ], columns=['Property', 'Value'])
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
    
    print(f"✅ Excel export saved: {output_path}")
    return output_path

# Example usage
if __name__ == "__main__":
    # Send latest metrics to dashboard
    send_to_dashboard()
    
    # Export for Excel
    excel_file = export_for_excel()
    print(f"📊 Excel export available at: {excel_file}")
```

## Monitoring and Maintenance Examples

### Example 6: Health Check Script

```python
#!/usr/bin/env python3
"""
Health check script for output system monitoring
"""

import subprocess
from pathlib import Path
from src.improved_output_manager import get_output_manager

def health_check():
    """Comprehensive health check of output system"""
    
    print("🔍 MixBridge Output System Health Check")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # Check 1: Directory structure
    manager = get_output_manager()
    status = manager.get_status_summary()
    
    print("📁 Directory Status:")
    for name, info in status['directories'].items():
        if info['exists']:
            print(f"  ✅ {name}: {info['file_count']} files ({info['total_size']/1024/1024:.1f}MB)")
        else:
            print(f"  ❌ {name}: Missing")
            issues.append(f"Missing directory: {name}")
    
    # Check 2: Latest files
    print("\n📄 Latest Files:")
    if status['latest_files']:
        for analysis_type, info in status['latest_files'].items():
            if info['latest_file']:
                print(f"  ✅ {analysis_type}: {Path(info['latest_file']).name}")
                
                # Check file age
                from datetime import datetime, timedelta
                created = datetime.fromisoformat(info['metadata']['created'].replace('Z', '+00:00').replace('+00:00', ''))
                age = datetime.now() - created.replace(tzinfo=None)
                
                if age > timedelta(days=7):
                    warnings.append(f"{analysis_type} latest file is {age.days} days old")
            else:
                warnings.append(f"No latest file for {analysis_type}")
    else:
        warnings.append("No latest files found")
    
    # Check 3: Disk usage
    print("\n💾 Disk Usage:")
    total_size = status.get('total_files', 0)
    if total_size > 1000:  # More than 1000 files
        warnings.append(f"High file count: {total_size} files")
    
    # Check 4: Archive health
    archive_dir = Path('output/archive')
    if archive_dir.exists():
        archive_files = list(archive_dir.glob('*'))
        compressed_files = list(archive_dir.glob('*.gz'))
        compression_ratio = len(compressed_files) / len(archive_files) if archive_files else 0
        
        print(f"  📦 Archive: {len(archive_files)} files ({compression_ratio:.1%} compressed)")
        
        if compression_ratio < 0.8:
            warnings.append("Low compression ratio in archive")
    
    # Check 5: CLI functionality
    print("\n🎛️ CLI Functionality:")
    try:
        result = subprocess.run(['python3', 'output_manager_cli.py', 'status'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✅ CLI tools working")
        else:
            print("  ❌ CLI tools failing")
            issues.append("CLI tools not working")
    except Exception as e:
        print(f"  ❌ CLI test failed: {str(e)}")
        issues.append(f"CLI error: {str(e)}")
    
    # Summary
    print("\n📊 Health Check Summary:")
    print(f"  Issues: {len(issues)}")
    print(f"  Warnings: {len(warnings)}")
    
    if issues:
        print("\n❌ ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
    
    if warnings:
        print("\n⚠️ WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not issues and not warnings:
        print("\n✅ All systems healthy!")
    
    return len(issues) == 0

if __name__ == "__main__":
    healthy = health_check()
    exit(0 if healthy else 1)
```

### Example 7: Automated Cleanup Script

```bash
#!/bin/bash
# automated_cleanup.sh - Weekly cleanup script

echo "🧹 MixBridge Output Cleanup - $(date)"
echo "=" * 50

cd /path/to/mixbridge

# Check current status
echo "📊 Current Status:"
python3 output_manager_cli.py status

# Perform cleanup
echo ""
echo "🗂️ Performing cleanup..."
python3 output_manager_cli.py cleanup --execute

# Check archive status
echo ""
echo "📦 Archive Status:"
ARCHIVE_SIZE=$(du -sh output/archive 2>/dev/null | cut -f1 || echo "0")
echo "Archive size: $ARCHIVE_SIZE"

# Cleanup very old archives (older than 90 days)
echo ""
echo "🗑️ Removing archives older than 90 days..."
find output/archive -name "archived_*" -type f -mtime +90 -delete

# Final status
echo ""
echo "✅ Cleanup complete - $(date)"
python3 output_manager_cli.py status
```

## Best Practices Examples

### Example 8: Production Deployment Pattern

```python
#!/usr/bin/env python3
"""
Production-ready deployment pattern with error handling and monitoring
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from src.campaign_bridge_modular import CampaignBridge
from src.improved_output_manager import get_output_manager, ImprovedOutputConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mixbridge_production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def production_analysis_pipeline(data_path: str, config_overrides: dict = None):
    """Production-ready analysis pipeline with full error handling"""
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting production analysis pipeline")
    
    try:
        # Configure output manager for production
        config = ImprovedOutputConfig(
            auto_archive=True,
            archive_after_generations=10,  # Keep more files in production
            archive_age_days=30,           # Archive after 30 days
            compress_archived=True,
            max_files_before_cleanup=100
        )
        
        if config_overrides:
            for key, value in config_overrides.items():
                setattr(config, key, value)
        
        # Initialize output manager
        from src.improved_output_manager import set_output_manager, ImprovedOutputManager
        manager = ImprovedOutputManager(config)
        set_output_manager(manager)
        
        # Validate input data
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        logger.info(f"Processing data file: {data_path}")
        
        # Run analysis with error handling
        bridge = CampaignBridge(data_path)
        
        # Pre-flight checks
        jan_data, feb_data = bridge.load_data()
        logger.info(f"Loaded data: {len(jan_data)} Jan records, {len(feb_data)} Feb records")
        
        if len(jan_data) == 0 or len(feb_data) == 0:
            raise ValueError("Insufficient data for analysis")
        
        # Execute analysis
        result = bridge.calculate_bridge(validate=True)
        logger.info(f"Analysis completed: {len(result)} rows generated")
        
        # Save with production metadata
        metadata = {
            'environment': 'production',
            'data_source': str(Path(data_path).absolute()),
            'input_records_jan': len(jan_data),
            'input_records_feb': len(feb_data),
            'processing_time': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        latest_path, timestamped_path, previous_path = bridge.save_to_csv()
        
        # Log success
        logger.info(f"Analysis saved successfully:")
        logger.info(f"  Latest: {latest_path}")
        logger.info(f"  Timestamped: {timestamped_path}")
        if previous_path:
            logger.info(f"  Previous: {previous_path}")
        
        # Verify output
        import pandas as pd
        verification_df = pd.read_csv(latest_path)
        
        if len(verification_df) != len(result):
            raise ValueError("Output verification failed: row count mismatch")
        
        logger.info("Output verification passed")
        
        # Return success information
        return {
            'status': 'success',
            'latest_file': latest_path,
            'timestamped_file': timestamped_path,
            'previous_file': previous_path,
            'campaigns_processed': len(result) - 1,  # Exclude totals row
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Production analysis failed: {str(e)}", exc_info=True)
        
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Production configuration
    config_overrides = {
        'archive_age_days': 30,
        'max_files_before_cleanup': 100
    }
    
    # Run production analysis
    result = production_analysis_pipeline(
        'data/Hydrapak YTD - campaign.csv',
        config_overrides
    )
    
    if result['status'] == 'success':
        print(f"✅ Production analysis successful")
        print(f"📄 Latest file: {result['latest_file']}")
        sys.exit(0)
    else:
        print(f"❌ Production analysis failed: {result['error']}")
        sys.exit(1)
```

These examples demonstrate the flexibility and power of the improved output system, from simple daily workflows to complex production deployments. The system's design ensures that whether you're running a quick analysis or managing a complex batch process, your files are organized, accessible, and properly maintained.