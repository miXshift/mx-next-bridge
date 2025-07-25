#!/usr/bin/env python3
"""
Demo script showing the improved output structure
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def main():
    print("🎯 IMPROVED OUTPUT STRUCTURE DEMONSTRATION")
    print("=" * 60)
    
    print("\n📁 NEW DIRECTORY STRUCTURE:")
    print("  output/")
    print("  ├── current/           ← Easy to find latest files")
    print("  │   ├── LATEST_mixbridge.csv           ← Always the newest file")
    print("  │   ├── LATEST_mixbridge_info.json     ← Metadata about latest")
    print("  │   └── PREVIOUS_mixbridge.csv         ← Previous version backup")
    print("  │")
    print("  ├── analyses/          ← All timestamped files")
    print("  │   ├── mixbridge_jan2025-feb2025_delta_assignment_20250721_203243.csv")
    print("  │   └── mixbridge_jan2025-feb2025_delta_assignment_20250721_203224.csv")
    print("  │")
    print("  ├── archive/           ← Automatically archived old files")
    print("  │   ├── archived_20250721_203224_mixbridge_[...].csv.gz")
    print("  │   └── archived_20250721_203243_mixbridge_[...].csv.gz")
    print("  │")
    print("  └── reports/           ← Analysis reports")
    
    print("\n✨ KEY IMPROVEMENTS:")
    print("  📄 Latest file is always: output/current/LATEST_mixbridge.csv")
    print("  📋 Previous file backup: output/current/PREVIOUS_mixbridge.csv")
    print("  📊 Metadata with details: output/current/LATEST_mixbridge_info.json")
    print("  🗂️  Automatic archiving of old files (compressed)")
    print("  📅 Timestamped history preserved in analyses/")
    print("  🎛️  CLI management tool: python3 output_manager_cli.py status")
    
    print("\n🔧 USAGE EXAMPLES:")
    print("  # Check status")
    print("  python3 output_manager_cli.py status")
    print("")
    print("  # Show latest file info")
    print("  python3 output_manager_cli.py latest")
    print("")
    print("  # List recent files")
    print("  python3 output_manager_cli.py recent")
    print("")
    print("  # Clean up old files")
    print("  python3 output_manager_cli.py cleanup")
    
    print("\n🎯 BENEFITS:")
    print("  ✅ Latest file is always easy to find")
    print("  ✅ Automatic archiving keeps directories clean") 
    print("  ✅ Previous version backup prevents data loss")
    print("  ✅ Compressed archives save disk space")
    print("  ✅ Rich metadata tracking")
    print("  ✅ CLI management tools")
    print("  ✅ Backward compatibility maintained")

if __name__ == "__main__":
    main()