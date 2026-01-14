"""Lab and home commands for SignalPilot CLI"""

import sys
from pathlib import Path

import typer

from sp.core.config import is_upgrade_check_enabled
from sp.core.environment import ensure_home_setup, check_local_venv
from sp.core.jupyter import run_jupyter_lab
from sp.ui.console import console
from sp.upgrade_check import (
    check_cache_for_upgrades,
    show_non_blocking_notification,
    show_blocking_prompt,
    start_version_check
)
from sp.commands.upgrade import upgrade_library


def launch_jupyter_with_upgrade_check(
    venv_dir: Path,
    workspace_dir: Path,
    extra_args: list = None,
    show_warning: bool = False
):
    """Launch Jupyter with auto-upgrade check and proper interrupt handling.

    Flow:
    1. Load cache (fast, no web call)
    2. If cache shows upgrade available:
       - MINOR: Show non-blocking notification (no delay)
       - MAJOR/BREAKING: Show blocking prompt (5s timeout)
    3. If user accepts upgrade: Run upgrade_library()
    4. Print diagnostic info (workspace, venv, versions)
    5. Launch Jupyter
    6. Start background PyPI check to update cache for next session
    7. Handle KeyboardInterrupt gracefully

    Args:
        venv_dir: Path to virtual environment
        workspace_dir: Working directory for Jupyter
        extra_args: Additional arguments for jupyter lab
        show_warning: Whether to show local .venv warning
    """
    # Check if upgrade checking is enabled
    if is_upgrade_check_enabled():
        # Check cache for available upgrades (no network call)
        upgrade_info = check_cache_for_upgrades(venv_dir)

        if upgrade_info:
            upgrade_type = upgrade_info['type']
            current = upgrade_info['current']
            latest = upgrade_info['latest']
            package = upgrade_info['package']

            # Show notification based on upgrade type
            if upgrade_type == "minor":
                # Non-blocking notification (displays immediately, no delay)
                show_non_blocking_notification(current, latest, package)

            elif upgrade_type in ["major", "breaking"]:
                # Blocking prompt (5s timeout)
                should_upgrade = show_blocking_prompt(current, latest, package, timeout=5)

                if should_upgrade:
                    # Run upgrade now
                    console.print("\n→ Starting upgrade process...\n", style="cyan")
                    upgrade_library(venv_dir)
                    console.print()  # Blank line

    # Launch Jupyter Lab
    try:
        # Start background version check to update cache for next session
        if is_upgrade_check_enabled():
            start_version_check(venv_dir)

        # Run Jupyter (blocks until terminated)
        run_jupyter_lab(venv_dir, workspace_dir, extra_args=extra_args, show_warning=show_warning)

    except KeyboardInterrupt:
        console.print("\n\n→ Jupyter Lab stopped", style="dim")


def lab_command(
    ctx: typer.Context,
    home: bool = typer.Option(False, "--home", help="Use SignalPilotHome workspace + venv"),
    project: bool = typer.Option(False, "--project", help="Use current folder + local .venv (fail if missing)"),
):
    """Start Jupyter Lab (default: current folder + home .venv)"""

    # Validate mutually exclusive flags
    if home and project:
        console.print("✗ Cannot use --home and --project together", style="bold red")
        sys.exit(1)

    # Ensure home setup exists
    home_dir, home_venv_dir = ensure_home_setup()

    # Determine workspace and venv based on flags
    if home:
        # Explicit home: Use SignalPilotHome for both workspace and venv
        workspace_dir = home_dir
        venv_dir = home_venv_dir
        show_warning = False

    elif project:
        # Explicit project: Use current folder and local .venv (fail fast)
        workspace_dir = Path.cwd()
        local_venv = check_local_venv(workspace_dir)

        if local_venv is None:
            console.print("✗ No .venv with jupyter found in current directory", style="bold red")
            console.print("\nCreate a virtual environment first:", style="yellow")
            console.print("  uv venv --seed --python 3.12", style="dim")
            console.print("  uv pip install jupyterlab signalpilot-ai", style="dim")
            sys.exit(1)

        venv_dir = local_venv
        show_warning = False

    else:
        # Default: Use current folder + home .venv
        workspace_dir = Path.cwd()
        venv_dir = home_venv_dir

        # Warn if local .venv exists with jupyter (but not if we're in SignalPilotHome)
        local_venv = check_local_venv(workspace_dir)
        show_warning = local_venv is not None and workspace_dir != home_dir

    # Launch Jupyter Lab with auto-upgrade check
    launch_jupyter_with_upgrade_check(
        venv_dir,
        workspace_dir,
        extra_args=list(ctx.args) if ctx.args else None,
        show_warning=show_warning
    )


def home_command(ctx: typer.Context):
    """Start Jupyter Lab in SignalPilotHome (shortcut for 'lab --home')"""
    home_dir, home_venv_dir = ensure_home_setup()
    launch_jupyter_with_upgrade_check(
        home_venv_dir,
        home_dir,
        extra_args=list(ctx.args) if ctx.args else None
    )
