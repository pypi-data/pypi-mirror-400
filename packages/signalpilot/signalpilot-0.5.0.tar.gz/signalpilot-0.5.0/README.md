# SignalPilot CLI

Your Trusted CoPilot for Data Analysis - A simple CLI tool to bootstrap Jupyter-powered data science workspaces with AI agent support.

## Features

- 🚀 **One-command setup** - Get from zero to Jupyter Lab in under 3 minutes
- ⚡  **Python 3.12** - Uses the latest Python with uv for fast package management
- 📊 **Pre-configured workspace** - Includes pandas, numpy, matplotlib, seaborn, plotly
- 🤖 **AI-ready** - Built-in SignalPilot AI agent support
- ⚡ **Fast** - Optimized Jupyter cache for quick startups
- ✨ **Beautiful CLI** - Clean, colorful terminal output

## Quick Start

```bash
# No uv installed: curl -LsSf https://astral.sh/uv/install.sh | sh
uvx signalpilot      # Initialize workspace and starts Jupyter Lab
```
**OR Any time later**
```bash
# Easy way to start
uvx signalpilot lab  # Start Jupyter Lab in ~/SignalPilotHome

# OR manually activate and start
cd ~/SignalPilotHome && source .venv/bin/activate
jupyter lab
```

**What happens:**
- Creates `~/SignalPilotHome` workspace with starter notebooks
- Sets up Python 3.12 + Jupyter Lab + data packages (pandas, numpy, matplotlib, plotly)
- Optimizes for fast startup
- Launches Jupyter Lab in your default browser

**Why uv?**
- **10-100x faster** than pip/conda for package installation
- **SignalPilot Kernel runs on it** - native integration
- Modern Python package management

**Other ways to install uv:**
```bash
# Linux/macOS (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS
brew install uv
```

## What Gets Installed

**Python Packages:**
- `signalpilot-ai` - AI agent integration
- `jupyterlab` - Modern Jupyter interface
- `pandas`, `numpy` - Data manipulation
- `matplotlib`, `seaborn`, `plotly` - Visualization
- `python-dotenv`, `tomli` - Configuration utilities

**Directory Structure:**
```
~/SignalPilotHome/
├── user-skills/       # Custom agent skills
├── user-rules/        # Custom agent rules
├── team-workspace/    # Shared team notebooks
├── demo-project/      # Example notebooks
├── pyproject.toml     # Python project config
├── start-here.ipynb   # Quick start guide
└── .venv/             # Python environment
```

## Advanced Lab Options

### Working in Different Directories

```bash
# Default: Open ~/SignalPilotHome w/ default .venv
uvx signalpilot lab

# Open in current folder using default .venv in ~/SignalPilotHome
uvx signalpilot lab --here

# Open in current folder using local .venv
# MUST have a .venv in the current directory w/ jupyterlab and signalpilot-ai installed
uvx signalpilot lab --project
```

**`--here` flag:**
- Opens Jupyter Lab in your current directory
- Uses the default environment from `~/SignalPilotHome/.venv`
- Perfect for quick exploration in any folder

**`--project` flag:**
- Opens Jupyter Lab in your current directory
- Uses a local `.venv` in that directory
- Great for project-specific work with custom dependencies
- Requires a `.venv` to exist (create with `uv venv --seed --python 3.12`)

### Passing Extra Arguments to Jupyter Lab

You can pass any Jupyter Lab arguments after the command:

```bash
# Custom port
uvx signalpilot lab --port=8888

# Disable browser auto-open
uvx signalpilot lab --no-browser

# Combine with directory flags
uvx signalpilot lab --here --port=8888

# Any jupyter lab flag works
uvx signalpilot lab --ip=0.0.0.0 --port=9999
```

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Permanent Installation Options (Not Recommended)

### Option 1: Consider Running with uvx (Recommended - no installation needed)
```bash
uvx signalpilot
```

### Option 2: Install with uv
```bash
uv tool install signalpilot
sp init
```

### Option 3: Install with pip
```bash
pip install signalpilot
sp init
```

## License

MIT License - See LICENSE file for details

## Links

- [Homepage](https://signalpilot.ai)
- [Documentation](https://docs.signalpilot.ai)
- [GitHub](https://github.com/SignalPilot-Labs/signalpilot-cli)