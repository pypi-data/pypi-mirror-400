#!/usr/bin/env python3
"""Test upgrade command flow without actually upgrading"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sp.upgrade_check import (
    get_cli_version,
    get_pypi_version,
    detect_signalpilot_package,
    compare_versions
)
from sp.core.config import SP_VENV, is_running_via_uvx
from sp.ui.console import console


def test_upgrade_flow():
    """Simulate the upgrade command flow"""
    console.print("="*60, style="white")
    console.print("📦 SignalPilot Upgrade Test", style="bold cyan")
    console.print("="*60 + "\n", style="white")

    # Test CLI upgrade check
    console.print("→ Checking CLI version...", style="dim")
    cli_current = get_cli_version()

    if not cli_current:
        console.print("✗ Could not determine CLI version", style="red")
    else:
        console.print(f"  Current: {cli_current}", style="dim")

        cli_latest = get_pypi_version("signalpilot", timeout=5.0)
        if cli_latest:
            console.print(f"  Latest:  {cli_latest}", style="green")
            upgrade_type = compare_versions(cli_current, cli_latest)

            if upgrade_type == "none":
                console.print("✓ CLI already up-to-date", style="green")
            else:
                console.print(f"  → {upgrade_type.upper()} upgrade available", style="yellow")
                console.print(f"  Run 'uvx signalpilot upgrade' to upgrade", style="dim")
        else:
            console.print("✗ Could not fetch from PyPI (network issue?)", style="red")

    # Test library upgrade check
    console.print("\n→ Checking library version...", style="dim")
    lib_info = detect_signalpilot_package(SP_VENV)

    if not lib_info:
        console.print("✗ Library not found in venv", style="red")
    else:
        package_name, lib_current = lib_info
        console.print(f"  Package: {package_name}", style="dim")
        console.print(f"  Current: {lib_current}", style="dim")

        lib_latest = get_pypi_version(package_name, timeout=5.0)
        if lib_latest:
            console.print(f"  Latest:  {lib_latest}", style="green")
            upgrade_type = compare_versions(lib_current, lib_latest)

            if upgrade_type == "none":
                console.print("✓ Library already up-to-date", style="green")
            else:
                console.print(f"  → {upgrade_type.upper()} upgrade available", style="yellow")
                console.print(f"  Run 'uvx signalpilot upgrade' to upgrade", style="dim")
        elif "internal" in package_name:
            console.print("  → Internal package (PyPI check skipped)", style="yellow")
        else:
            console.print("✗ Could not fetch from PyPI (network issue?)", style="red")

    # Check uvx context
    if is_running_via_uvx():
        console.print("\n[yellow]Note:[/yellow] Running via uvx")
        console.print("  uvx cache will be auto-updated after upgrade", style="dim")

    console.print("\n" + "="*60, style="white")
    console.print("✅ Upgrade check complete!", style="bold green")
    console.print("\nTo actually upgrade, run:")
    console.print("  uvx signalpilot@latest upgrade", style="cyan")
    console.print("="*60 + "\n", style="white")


if __name__ == "__main__":
    try:
        test_upgrade_flow()
    except KeyboardInterrupt:
        print("\n\n✗ Test cancelled")
        sys.exit(1)
