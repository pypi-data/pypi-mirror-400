"""Virtual environment management for SignalPilot CLI"""

import sys
from pathlib import Path

from sp.core.config import SP_HOME, SP_VENV
from sp.ui.console import console


def get_home_paths() -> tuple[Path, Path]:
    """Get SignalPilotHome directory and venv paths.

    Returns:
        Tuple of (home_dir, home_venv_dir)
    """
    return SP_HOME, SP_VENV


def check_venv_has_jupyter(venv_dir: Path) -> bool:
    """Check if venv has jupyter installed.

    Args:
        venv_dir: Path to virtual environment

    Returns:
        True if jupyter binary exists in venv/bin/
    """
    return (venv_dir / "bin" / "jupyter").exists()


def check_local_venv(directory: Path = None) -> Path | None:
    """Check if directory has a .venv with jupyter installed.

    Args:
        directory: Directory to check (defaults to current working directory)

    Returns:
        Path to .venv if it exists with jupyter, None otherwise
    """
    if directory is None:
        directory = Path.cwd()

    venv_dir = directory / ".venv"
    if not venv_dir.exists():
        return None

    if not check_venv_has_jupyter(venv_dir):
        return None

    return venv_dir


def ensure_home_setup() -> tuple[Path, Path]:
    """Ensure SignalPilotHome exists with jupyter.

    Returns:
        Tuple of (home_dir, venv_dir)

    Exits:
        If SignalPilotHome or jupyter not found
    """
    home_dir, home_venv_dir = get_home_paths()

    if not home_dir.exists():
        console.print("✗ SignalPilotHome not found", style="bold red")
        console.print("\nRun 'uvx signalpilot init' first to set up your workspace", style="yellow")
        sys.exit(1)

    if not check_venv_has_jupyter(home_venv_dir):
        console.print("✗ Jupyter not found in SignalPilotHome/.venv", style="bold red")
        console.print("\nRun 'uvx signalpilot init' to set up your environment", style="yellow")
        sys.exit(1)

    return home_dir, home_venv_dir


def check_uv() -> bool:
    """Check if uv package manager is installed.

    Returns:
        True if uv is available in PATH
    """
    import subprocess

    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
