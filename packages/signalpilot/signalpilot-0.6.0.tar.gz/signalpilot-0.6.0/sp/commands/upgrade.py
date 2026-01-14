"""Upgrade commands for SignalPilot CLI"""

import subprocess
import sys
from pathlib import Path

import typer

from sp.core.config import SIGNALPILOT_CLI, is_running_via_uvx
from sp.core.environment import ensure_home_setup, check_local_venv
from sp.ui.console import console
from sp.upgrade_check import (
    get_cli_version,
    get_pypi_version,
    detect_signalpilot_package,
    compare_versions
)


def upgrade_cli() -> bool:
    """Upgrade signalpilot CLI package.

    Strategy:
    1. Check current vs latest version
    2. If already latest, return True (no-op)
    3. Warn about uvx execution context
    4. Run: uv tool install --force signalpilot

    Returns:
        True if successful or already up-to-date, False on error
    """
    console.print("\n→ Checking CLI version...", style="dim")

    current_version = get_cli_version()
    if not current_version:
        console.print("✗ Could not determine current CLI version", style="red")
        return False

    latest_version = get_pypi_version(SIGNALPILOT_CLI, timeout=5.0)
    if not latest_version:
        console.print("✗ Could not fetch latest version from PyPI", style="red")
        console.print("  Check your internet connection", style="dim")
        return False

    upgrade_type = compare_versions(current_version, latest_version)
    if upgrade_type == "none":
        console.print(f"✓ CLI already up-to-date (v{current_version})", style="green")
        return True

    console.print(f"  Current: {current_version}", style="dim")
    console.print(f"  Latest:  {latest_version}", style="green")

    console.print("\n→ Upgrading CLI...", style="bold cyan")

    try:
        subprocess.run(
            ["uv", "tool", "install", "--force", SIGNALPILOT_CLI],
            check=True,
        )
        console.print(f"✓ CLI upgraded to v{latest_version}", style="bold green")

        # Inform about uvx context (tool install above automatically updates uvx cache)
        if is_running_via_uvx():
            console.print("[dim]→ uvx cache updated (new version will be used next time)[/dim]")

        return True
    except subprocess.CalledProcessError as e:
        console.print(f"✗ CLI upgrade failed with exit code {e.returncode}", style="bold red")
        return False
    except FileNotFoundError:
        console.print("✗ uv not found in PATH", style="bold red")
        console.print("  Install uv first: https://docs.astral.sh/uv/", style="dim")
        return False


def upgrade_library(venv_dir: Path) -> bool:
    """Upgrade signalpilot-ai library in specified venv.

    Strategy:
    1. Detect installed package (ai vs ai-internal)
    2. Check current vs latest version
    3. Run: uv pip install --upgrade {package_name}

    Args:
        venv_dir: Path to virtual environment

    Returns:
        True if successful or already up-to-date, False on error
    """
    console.print("\n→ Checking library version...", style="dim")

    lib_info = detect_signalpilot_package(venv_dir)
    if not lib_info:
        console.print("✗ SignalPilot library not found in environment", style="red")
        return False

    package_name, current_version = lib_info
    console.print(f"  Package: {package_name}", style="dim")

    latest_version = get_pypi_version(package_name, timeout=5.0)
    if not latest_version:
        # For -internal, PyPI will return 404 (expected)
        if "internal" in package_name:
            console.print("  → Upgrading from internal package source...", style="dim")
            # Try to upgrade anyway - may have access to internal PyPI
            latest_version = current_version  # Placeholder
        else:
            console.print("✗ Could not fetch latest version from PyPI", style="red")
            console.print("  Check your internet connection", style="dim")
            return False

    if latest_version != current_version:  # We have comparison
        upgrade_type = compare_versions(current_version, latest_version)
        if upgrade_type == "none":
            console.print(f"✓ Library already up-to-date (v{current_version})", style="green")
            return True

        console.print(f"  Current: {current_version}", style="dim")
        console.print(f"  Latest:  {latest_version}", style="green")

    console.print(f"\n→ Upgrading {package_name}...", style="bold cyan")

    try:
        subprocess.run(
            ["uv", "pip", "install", "--upgrade", package_name],
            cwd=venv_dir.parent,  # Run from SignalPilotHome directory
            check=True,
        )
        console.print(f"✓ Library upgraded successfully", style="bold green")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"✗ Library upgrade failed with exit code {e.returncode}", style="bold red")
        return False
    except FileNotFoundError:
        console.print("✗ uv not found in PATH", style="bold red")
        console.print("  Install uv first: https://docs.astral.sh/uv/", style="dim")
        return False


def upgrade_command(
    project: bool = typer.Option(False, "--project", help="Upgrade project .venv instead of home")
):
    """Upgrade SignalPilot CLI and library.

    Default: Upgrades ~/SignalPilotHome/.venv
    --project: Upgrades current directory's .venv
    """
    console.print("="*60, style="white")
    console.print("📦 SignalPilot Upgrade", style="bold cyan")
    console.print("="*60 + "\n", style="white")

    # Determine venv location
    if project:
        # Use current directory's .venv
        workspace_dir = Path.cwd()
        venv_dir = check_local_venv(workspace_dir)

        if venv_dir is None:
            console.print("✗ No .venv with jupyter found in current directory", style="bold red")
            console.print("\nCreate a virtual environment first:", style="yellow")
            console.print("  uv venv --seed --python 3.12", style="dim")
            console.print("  uv pip install jupyterlab signalpilot-ai", style="dim")
            sys.exit(1)

        console.print(f"→ Upgrading project environment: {workspace_dir}", style="dim")
    else:
        # Use home .venv
        home_dir, venv_dir = ensure_home_setup()
        console.print(f"→ Upgrading home environment: {home_dir}", style="dim")

    # Upgrade both CLI and library
    cli_success = upgrade_cli()
    lib_success = upgrade_library(venv_dir)

    # Print summary
    console.print("\n" + "="*60, style="white")
    if cli_success and lib_success:
        console.print("✓ Upgrade completed successfully!", style="bold green")
    elif cli_success:
        console.print("⚠ CLI upgraded, but library upgrade failed", style="yellow")
        console.print("  Try running 'uvx signalpilot@latest upgrade' again", style="dim")
    elif lib_success:
        console.print("⚠ Library upgraded, but CLI upgrade failed", style="yellow")
        console.print("  Try running 'uvx signalpilot@latest upgrade' again", style="dim")
    else:
        console.print("✗ Upgrade failed", style="bold red")
        console.print("  Check error messages above", style="dim")

    console.print("="*60 + "\n", style="white")
