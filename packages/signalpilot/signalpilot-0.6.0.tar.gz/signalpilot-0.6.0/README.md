# SignalPilot Installer CLI

This installer CLI is a bootstrap installer that sets up the [SignalPilot-AI](https://pypi.org/project/signalpilot-ai/) Jupyter extension in one command.


**The CLI is NOT the product.** It's a convenience installer. The **SignalPilot Jupyter extension** (agentic harness) is the actual product.

## What You're Installing

SignalPilot is a **Jupyter-native AI agentic harness** that investigates data by connecting to your organizational context:

**Four core capabilities:**

- 🔌 **Multi-Source Context** — Auto-connects to db warehouse, dbt lineage, query history, Slack threads, Jira tickets, and past investigations via MCP
- 🔄 **Long-Running Agent Loop** — Plans, executes, iterates until task complete with analyst-in-the-loop approval (not single-shot completions)
- 🧠 **Multi-Session Memory** — Remembers past hypotheses, validated assumptions, known data quirks across investigations
- 📚 **Skills & Rules** — Custom analysis patterns (skills) + team coding standards (rules) + business logic

**Security:** Zero data retention • Read-only access • Local-first execution • SOC 2 in progress

## Quick Install

**Prerequisites:** macOS, Linux, or Windows (WSL) • Internet connection

**Don't have [uv](https://docs.astral.sh/uv/getting-started/installation/)?** Install it first (takes 10 seconds):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install SignalPilot:**
```bash
uvx signalpilot@latest
```

**What happens:**
- Creates `~/SignalPilotHome` workspace with starter notebooks
- Installs isolated Python 3.12 + Jupyter Lab + SignalPilot extension
- Installs data packages (pandas, numpy, matplotlib, seaborn, plotly)
- Optimizes Jupyter cache for fast startup
- Launches Jupyter Lab at `http://localhost:8888`

**Time:** ~2 minutes

**Why uv?**
- **10-100x faster** than pip/conda for package installation
- **SignalPilot runs on it** — native integration with kernel
- Modern Python package management with better dependency resolution

## Launch Jupyter Lab Anytime

Once installed, start Jupyter Lab with:

```bash
uvx signalpilot@latest lab
```

**What this does:**
- Opens Jupyter Lab in your **current directory**
- Uses **home environment** from `~/SignalPilotHome/.venv`
- SignalPilot extension pre-loaded
- Opens browser at `http://localhost:8888`

**⚠️ Smart Detection:** If a local `.venv` with jupyter is detected in your current directory, you'll see a red warning. Use `--project` flag to use it instead.

## Keeping SignalPilot Updated

SignalPilot automatically checks for updates when you launch Jupyter Lab. When an update is available, you'll see a notification:

**For minor updates:**
```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Update Available: 0.11.8 (installed: 0.11.7)        │
│ Run 'sp upgrade' to update                          │
╰──────────────────────────────────────────────────────╯
```

**For major updates:**
```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Important Update: 0.12.0 (installed: 0.11.7)        │
│ This is a MAJOR update                              │
╰──────────────────────────────────────────────────────╯
Upgrade now? [y/n] (n):
```

### Manual Upgrade

Upgrade both the CLI and library anytime:

```bash
uvx signalpilot@latest upgrade
```

Upgrade your project's local environment:

```bash
cd /path/to/project
uvx signalpilot@latest upgrade --project
```

**Note:** Update checks happen in the background and never slow down Jupyter startup. You can disable them in `~/SignalPilotHome/.signalpilot/config.toml` if desired.

📖 **Full upgrade guide:** [docs/UPGRADE-USER-GUIDE.md](docs/UPGRADE-USER-GUIDE.md)

## What Gets Installed

**Python Packages:**
- `signalpilot-ai` — AI agent integration (the actual product)
- `jupyterlab` — Modern Jupyter interface
- `pandas`, `numpy` — Data manipulation
- `matplotlib`, `seaborn`, `plotly` — Visualization
- `python-dotenv`, `tomli` — Configuration utilities

**Directory Structure:**
```
~/SignalPilotHome/
├── user-skills/       # Custom analysis patterns
├── user-rules/        # Team coding standards
├── team-workspace/    # Shared notebooks (git-tracked)
├── demo-project/      # Example notebooks
├── pyproject.toml     # Python project config
├── start-here.ipynb   # Quick start guide
└── .venv/             # Python environment
```

## Working in Different Modes

SignalPilot offers three ways to launch Jupyter Lab:

### Default Mode (Current Folder + Home Environment)

```bash
cd ~/projects/my-analysis
uvx signalpilot@latest lab
```

**What this does:**
- Opens Jupyter Lab in your **current directory**
- Uses **home environment** from `~/SignalPilotHome/.venv`
- Perfect for quick exploration without setting up new environment

**⚠️ Warning:** If you have a local `.venv` with jupyter, you'll see a red warning prompting you to use `--project` flag.

### Project Mode (Current Folder + Local Environment)

```bash
cd ~/projects/custom-analytics
uvx signalpilot@latest lab --project
```

**What this does:**
- Opens Jupyter Lab in your **current directory**
- Uses **local `.venv`** in that directory (fails if missing)
- Great for project-specific work with custom dependencies

**Requirements:**
- A `.venv` must exist in current directory
- Must have `jupyterlab` and `signalpilot-ai` installed

**Create project environment:**
```bash
mkdir ~/projects/custom-analytics && cd ~/projects/custom-analytics
uv venv --seed --python 3.12
source .venv/bin/activate
uv pip install jupyterlab signalpilot-ai pandas numpy matplotlib plotly
uvx signalpilot@latest lab --project
```

### Home Mode (SignalPilotHome Workspace + Home Environment)

```bash
uvx signalpilot@latest lab --home
# Or use the shortcut:
uvx signalpilot@latest home
```

**What this does:**
- Opens Jupyter Lab in `~/SignalPilotHome` directory
- Uses **home environment** from `~/SignalPilotHome/.venv`
- Default workspace with all your skills, rules, and team notebooks

## Pass Jupyter Lab Arguments

You can pass any Jupyter Lab flags after the command:

```bash
# Custom port
uvx signalpilot@latest lab --port=8889

# Disable browser auto-open
uvx signalpilot@latest lab --no-browser

# Combine with mode flags
uvx signalpilot@latest lab --project --port=8889
uvx signalpilot@latest home --no-browser

# Bind to all interfaces (remote access)
uvx signalpilot@latest lab --ip=0.0.0.0 --port=9999
```

All standard `jupyter lab` arguments work.

## Alternative Installation Methods

### Option 1: Run with uvx (Recommended)
```bash
uvx signalpilot@latest
```
No permanent installation needed. Perfect for most users. Always gets the latest version.

### Option 2: Install with uv tool
```bash
uv tool install signalpilot
sp init
```
Installs `sp` command globally. Use `sp lab`, `sp home` to launch later.

**Note:** Global installations don't auto-update. Reinstall periodically:
```bash
uv tool install --force signalpilot
```

### Option 3: Install with pip
```bash
pip install signalpilot
sp init
```
Works but slower than uv (10-100x). May have dependency conflicts.

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## Links

- [Homepage](https://signalpilot.ai)
- [Full Documentation](https://docs.signalpilot.ai)
- [Installation Guide](https://docs.signalpilot.ai/getting-started/installation)
- [5-Minute Quickstart](https://docs.signalpilot.ai/getting-started/quickstart)
- [GitHub](https://github.com/SignalPilot-Labs/signalpilot-cli)

## License

MIT License - See LICENSE file for details
