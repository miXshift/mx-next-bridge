#!/usr/bin/env python3
"""
Output Manager CLI - Command line interface for improved output management
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from improved_output_manager import get_output_manager, ImprovedOutputConfig
except ImportError:
    print("❌ Could not import improved output manager")
    sys.exit(1)


def show_status():
    """Show current output directory status"""
    manager = get_output_manager()
    summary = manager.get_status_summary()
    
    print("📊 OUTPUT DIRECTORY STATUS")
    print("=" * 50)
    print(f"Base directory: {summary['base_directory']}")
    print(f"Total files: {summary['total_files']}")
    
    print("\n📁 DIRECTORIES:")
    for name, info in summary['directories'].items():
        status = "✅" if info['exists'] else "❌"
        size_mb = info['total_size'] / (1024 * 1024) if info['total_size'] > 0 else 0
        print(f"  {status} {name:10} ({info['file_count']:3} files, {size_mb:.1f}MB) - {info['path']}")
    
    print("\n📄 LATEST FILES:")
    if summary['latest_files']:
        for analysis_type, info in summary['latest_files'].items():
            print(f"  📄 {analysis_type}:")
            if info['latest_file']:
                print(f"      Latest: {Path(info['latest_file']).name}")
            if info['previous_file']:
                print(f"      Previous: {Path(info['previous_file']).name}")
            if info['metadata']:
                created = info['metadata'].get('created', 'unknown')
                campaigns = info['metadata'].get('total_campaigns', 0)
                print(f"      Created: {created}, Campaigns: {campaigns}")
    else:
        print("  No latest files found")


def show_latest(analysis_type='mixbridge'):
    """Show information about latest file"""
    manager = get_output_manager()
    info = manager.get_file_info(analysis_type)
    
    print(f"📄 LATEST {analysis_type.upper()} ANALYSIS")
    print("=" * 40)
    
    if info['latest_file']:
        print(f"✅ Latest file: {info['latest_file']}")
        
        if info['metadata']:
            meta = info['metadata']
            print(f"   Created: {meta.get('created', 'unknown')}")
            print(f"   Strategy: {meta.get('strategy', 'unknown')}")
            print(f"   Campaigns: {meta.get('total_campaigns', 0)}")
            if meta.get('periods'):
                periods = meta['periods']
                print(f"   Periods: {periods.get('p1', 'unknown')} → {periods.get('p2', 'unknown')}")
        
        if info['previous_file']:
            print(f"📋 Previous file: {info['previous_file']}")
    else:
        print("❌ No latest file found")


def list_recent(analysis_type='mixbridge', limit=10):
    """List recent analysis files"""
    manager = get_output_manager()
    files = manager.list_recent_files(analysis_type, limit)
    
    print(f"📅 RECENT {analysis_type.upper()} FILES (last {limit})")
    print("=" * 60)
    
    if files:
        for i, file_info in enumerate(files, 1):
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"{i:2}. {file_info['filename']}")
            print(f"     Size: {size_mb:.1f}MB, Modified: {file_info['modified']}")
    else:
        print("No files found")


def cleanup(dry_run=True):
    """Clean up old files"""
    manager = get_output_manager()
    stats = manager.cleanup_old_files(dry_run=dry_run)
    
    action = "Would archive" if dry_run else "Archived"
    print(f"🧹 CLEANUP RESULTS")
    print("=" * 30)
    print(f"Files analyzed: {stats['analyzed']}")
    print(f"{action}: {stats['archived']}")
    print(f"Errors: {stats['errors']}")
    
    if dry_run and stats['archived'] > 0:
        print("\n⚠️  This was a dry run. Use --execute to actually archive files.")


def archive_old_files():
    """Archive old files (force archiving)"""
    manager = get_output_manager()
    manager._auto_archive()
    print("✅ Old files archived")


def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print("📊 OUTPUT MANAGER CLI")
        print("=" * 30)
        print("Usage:")
        print("  python output_manager_cli.py status          - Show directory status")
        print("  python output_manager_cli.py latest [type]   - Show latest file info")
        print("  python output_manager_cli.py recent [type]   - List recent files") 
        print("  python output_manager_cli.py cleanup         - Dry run cleanup")
        print("  python output_manager_cli.py cleanup --execute - Execute cleanup")
        print("  python output_manager_cli.py archive         - Force archive old files")
        print("\nAnalysis types: mixbridge, validation, comparison")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        show_status()
    
    elif command == 'latest':
        analysis_type = sys.argv[2] if len(sys.argv) > 2 else 'mixbridge'
        show_latest(analysis_type)
    
    elif command == 'recent':
        analysis_type = sys.argv[2] if len(sys.argv) > 2 else 'mixbridge'
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        list_recent(analysis_type, limit)
    
    elif command == 'cleanup':
        execute = '--execute' in sys.argv
        cleanup(dry_run=not execute)
    
    elif command == 'archive':
        archive_old_files()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()