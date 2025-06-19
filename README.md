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

# Run the vBridge analysis script
pnpm vbridge:run

# Complete workflow: clean output directory and run analysis
pnpm vbridge:full
```

### Command Details

- **`vbridge:install`** - Sets up or updates Python dependencies required for vBridge analysis
- **`vbridge:clean`** - Empties the output directory while preserving documentation files
- **`vbridge:run`** - Executes the 4-step KPI analysis using the virtual environment's Python
- **`vbridge:full`** - Complete workflow that cleans and runs the analysis (most commonly used)
