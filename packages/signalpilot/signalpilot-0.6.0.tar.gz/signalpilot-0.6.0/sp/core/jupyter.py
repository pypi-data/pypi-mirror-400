"""Jupyter Lab launch logic for SignalPilot CLI"""

import os
import subprocess
from pathlib import Path

from sp.ui.console import console, LOGO


def run_jupyter_lab(
    venv_dir: Path,
    workspace_dir: Path,
    extra_args: list = None,
    show_warning: bool = False
):
    """Launch Jupyter Lab with proper environment configuration.

    Args:
        venv_dir: Path to virtual environment with jupyter
        workspace_dir: Working directory for Jupyter Lab
        extra_args: Additional command-line arguments for jupyter lab
        show_warning: Whether to show local .venv warning

    Returns:
        None (blocks until Jupyter is terminated)
    """
    venv_jupyter = venv_dir / "bin" / "jupyter"

    # Print diagnostic information
    console.print("\n" + "="*60, style="white")
    console.print(LOGO, style="cyan")

    # Show warning if local .venv exists but we're using home .venv
    if show_warning:
        console.print("\n⚠️  WARNING: Local .venv detected with jupyter!", style="bold red")
        console.print(f"⚠️  Location: {Path.cwd() / '.venv'}", style="bold red")
        console.print("⚠️  Currently using home .venv, NOT your local project .venv", style="bold red")
        console.print("⚠️  Run 'uvx signalpilot lab --project' to use local .venv\n", style="bold red")

    console.print("\n→ Starting Jupyter Lab", style="bold green")
    console.print(f"  Workspace: {workspace_dir}", style="dim")
    console.print(f"  Environment: {venv_dir}", style="dim")
    if extra_args:
        console.print(f"  Extra args: {' '.join(extra_args)}", style="dim")
    console.print("="*60 + "\n", style="white")

    # Set up environment to point Jupyter to the correct venv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_dir)
    env["PATH"] = f"{venv_dir / 'bin'}:{env.get('PATH', '')}"
    # Remove PYTHONHOME if set, as it can interfere with venv
    env.pop("PYTHONHOME", None)

    # Build command with null token, native kernels only, and any extra args
    cmd = [
        str(venv_jupyter),
        "lab",
        "--IdentityProvider.token=''",
        "--KernelSpecManager.ensure_native_kernel=True",
        "--KernelSpecManager.allowed_kernelspecs=[]",
        "--ContentsManager.hide_globs=['*.venv', '.venv', '__pycache__', '*.egg-info', '.git']",
        # Startup speed optimizations
        "--LabApp.news_url=''",  # Skip news fetch (~100-500ms)
        "--LabApp.collaborative=False",  # Skip collaboration init (~50-200ms)
        # Performance optimizations
        "--ServerApp.contents_manager_class=jupyter_server.services.contents.largefilemanager.AsyncLargeFileManager",  # Better async file handling
    ]
    if extra_args:
        cmd.extend(extra_args)

    subprocess.run(cmd, cwd=workspace_dir, env=env)
