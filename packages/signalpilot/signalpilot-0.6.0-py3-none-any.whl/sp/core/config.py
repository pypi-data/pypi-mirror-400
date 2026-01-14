"""Configuration and paths for SignalPilot CLI"""

import sys
from pathlib import Path

# Core paths
SP_HOME = Path.home() / "SignalPilotHome"
SP_VENV = SP_HOME / ".venv"
SP_CONFIG_DIR = SP_HOME / ".signalpilot"
SP_CACHE_FILE = SP_CONFIG_DIR / "upgrade-cache.json"
SP_CONFIG_FILE = SP_CONFIG_DIR / "config.toml"

# Workspace paths
SP_USER_SKILLS = SP_HOME / "user-skills"
SP_USER_RULES = SP_HOME / "user-rules"
SP_TEAM_WORKSPACE = SP_HOME / "team-workspace"
SP_DEMO_PROJECT = SP_HOME / "demo-project"

# Package names
SIGNALPILOT_CLI = "signalpilot"
SIGNALPILOT_AI = "signalpilot-ai"
SIGNALPILOT_AI_INTERNAL = "signalpilot-ai-internal"

# Core packages for workspace (used during init)
CORE_PACKAGES = [
    "jupyterlab>=4.0",
    "ipykernel",
    "pandas",
    "numpy",
    "matplotlib>=3.7",
    "seaborn>=0.13",
    "plotly>=5.0",
    "python-dotenv>=1.0",
    "tomli>=2.0",
]


def get_cache_dir() -> Path:
    """Get SignalPilot config/cache directory.

    Creates ~/.SignalPilotHome/.signalpilot/ if it doesn't exist.

    Returns:
        Path to config directory
    """
    SP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return SP_CONFIG_DIR


def is_initialized() -> bool:
    """Check if SignalPilotHome is initialized with venv."""
    return SP_HOME.exists() and SP_VENV.exists()


def is_running_via_uvx() -> bool:
    """Detect if running in uvx ephemeral environment context."""
    return "uvx" in sys.prefix or ".local/share/uv" in sys.prefix


def load_config() -> dict:
    """Load user configuration from config.toml.

    Automatically creates default config file if it doesn't exist.

    Returns:
        Dict with config values, or defaults if file doesn't exist.
        Default: {'upgrade': {'check_enabled': True}}
    """
    default_config = {
        'upgrade': {
            'check_enabled': True
        }
    }

    # Ensure config directory exists
    SP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Create default config file if it doesn't exist
    if not SP_CONFIG_FILE.exists():
        try:
            with open(SP_CONFIG_FILE, 'w') as f:
                f.write("[upgrade]\n")
                f.write("check_enabled = true\n")
        except Exception:
            # If we can't write config, just return defaults
            pass
        return default_config

    # Load existing config file
    try:
        import tomli
        with open(SP_CONFIG_FILE, 'rb') as f:
            config = tomli.load(f)
        return config
    except Exception:
        # If any error loading config, return defaults
        return default_config


def is_upgrade_check_enabled() -> bool:
    """Check if auto-upgrade checking is enabled in config."""
    config = load_config()
    return config.get('upgrade', {}).get('check_enabled', True)
