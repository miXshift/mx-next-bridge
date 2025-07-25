# miXshift neXt SERVICES

## Getting Started

## vBridge Analytics

The project includes vBridge, a KPI analysis and mix/rate bridge calculator for campaign data analysis.

### vBridge Commands

```bash
# Install/update Python dependencies in vBridge virtual environment
pnpm vbridge:install

# Clean the vBridge output directory (preserves README.md files)
pnpm vbridge:clean

# Run the vBridge campaign bridge analysis
pnpm vbridge:run

# Complete workflow: clean output directory and run analysis
pnpm vbridge:full

# Run tests for vBridge
pnpm vbridge:test

# Run demo with improved output formatting
pnpm vbridge:demo
```

### Command Details

- **`vbridge:install`** - Sets up or updates Python dependencies required for vBridge analysis
- **`vbridge:clean`** - Empties the output directory while preserving documentation files
- **`vbridge:run`** - Executes the campaign bridge analysis using the modular src structure (src.core.campaign_bridge)
- **`vbridge:full`** - Complete workflow that cleans and runs the analysis (most commonly used)
- **`vbridge:test`** - Runs the vBridge test suite to ensure calculations are correct
- **`vbridge:demo`** - Runs a demonstration with improved output formatting
