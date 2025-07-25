# Output System Quick Reference

## 🎯 Essential Locations

| What | Where |
|------|-------|
| **Latest Analysis** | `output/current/LATEST_mixbridge.csv` |
| **Previous Version** | `output/current/PREVIOUS_mixbridge.csv` |
| **Analysis Info** | `output/current/LATEST_mixbridge_info.json` |
| **All History** | `output/analyses/` |
| **Archived Files** | `output/archive/` |

## 🔧 Quick Commands

```bash
# Check system status
python3 output_manager_cli.py status

# View latest file details
python3 output_manager_cli.py latest

# List recent files
python3 output_manager_cli.py recent

# Clean up old files
python3 output_manager_cli.py cleanup --execute
```

## 📝 Basic Usage

```python
from src.campaign_bridge_modular import CampaignBridge

# Run analysis
bridge = CampaignBridge('data.csv')
bridge.calculate_bridge()
latest, timestamped, previous = bridge.save_to_csv()

# Access latest file
print(f"Results: {latest}")
```

## 🗂️ Directory Structure

```
output/
├── current/       # Latest & previous files
├── analyses/      # All timestamped files
├── archive/       # Auto-archived files
└── reports/       # Analysis reports
```

## ⚙️ Key Features

- ✅ Latest file always in same location
- ✅ Previous version backup
- ✅ Automatic archiving & compression
- ✅ Rich metadata tracking
- ✅ CLI management tools
- ✅ Backward compatible

---
📖 **Full Documentation**: [output-system.md](output-system.md)