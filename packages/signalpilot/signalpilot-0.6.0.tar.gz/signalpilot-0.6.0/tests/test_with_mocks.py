#!/usr/bin/env python3
"""Test upgrade system with mocked PyPI responses (no network required)"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sp.test_mocks import mock_pypi_responses, mock_network_failure, set_mock_version
from sp.upgrade_check import get_pypi_version, compare_versions
from sp.ui.console import console


def test_pypi_mocking():
    """Test that PyPI mocking works correctly"""
    print("\n📋 Testing PyPI mocking...")

    # Test with default mock responses
    with mock_pypi_responses():
        cli_version = get_pypi_version("signalpilot")
        lib_version = get_pypi_version("signalpilot-ai-internal")

        print(f"  ✓ signalpilot: {cli_version}")
        print(f"  ✓ signalpilot-ai-internal: {lib_version}")

        assert cli_version is not None, "CLI version should not be None"
        assert lib_version is not None, "Library version should not be None"

    # Test with custom versions
    with mock_pypi_responses({"signalpilot": "0.9.9", "signalpilot-ai-internal": "0.99.0"}):
        cli_version = get_pypi_version("signalpilot")
        lib_version = get_pypi_version("signalpilot-ai-internal")

        print(f"  ✓ Custom signalpilot: {cli_version}")
        print(f"  ✓ Custom signalpilot-ai-internal: {lib_version}")

        assert cli_version == "0.9.9", "Custom CLI version mismatch"
        assert lib_version == "0.99.0", "Custom library version mismatch"

    # Test network failure
    with mock_network_failure():
        version = get_pypi_version("signalpilot")
        print(f"  ✓ Network failure: {version} (should be None)")
        assert version is None, "Should return None on network failure"

    print("  ✓ PyPI mocking tests passed")


def test_upgrade_scenarios():
    """Test different upgrade scenarios with mocks"""
    print("\n📋 Testing upgrade scenarios...")

    # Scenario 1: MINOR upgrade available
    print("\n  → Scenario 1: MINOR upgrade (0.11.7 -> 0.11.8)")
    with mock_pypi_responses({"signalpilot-ai-internal": "0.11.8"}):
        latest = get_pypi_version("signalpilot-ai-internal")
        upgrade_type = compare_versions("0.11.7", latest)
        print(f"    Current: 0.11.7, Latest: {latest}, Type: {upgrade_type}")
        assert upgrade_type == "minor", "Should detect MINOR upgrade"
        print(f"    ✓ Correctly detected {upgrade_type.upper()} upgrade")

    # Scenario 2: MAJOR upgrade available
    print("\n  → Scenario 2: MAJOR upgrade (0.11.7 -> 0.12.0)")
    with mock_pypi_responses({"signalpilot-ai-internal": "0.12.0"}):
        latest = get_pypi_version("signalpilot-ai-internal")
        upgrade_type = compare_versions("0.11.7", latest)
        print(f"    Current: 0.11.7, Latest: {latest}, Type: {upgrade_type}")
        assert upgrade_type == "major", "Should detect MAJOR upgrade"
        print(f"    ✓ Correctly detected {upgrade_type.upper()} upgrade")

    # Scenario 3: BREAKING upgrade available
    print("\n  → Scenario 3: BREAKING upgrade (0.11.7 -> 1.0.0)")
    with mock_pypi_responses({"signalpilot-ai-internal": "1.0.0"}):
        latest = get_pypi_version("signalpilot-ai-internal")
        upgrade_type = compare_versions("0.11.7", latest)
        print(f"    Current: 0.11.7, Latest: {latest}, Type: {upgrade_type}")
        assert upgrade_type == "breaking", "Should detect BREAKING upgrade"
        print(f"    ✓ Correctly detected {upgrade_type.upper()} upgrade")

    # Scenario 4: No upgrade needed
    print("\n  → Scenario 4: No upgrade (0.11.7 -> 0.11.7)")
    with mock_pypi_responses({"signalpilot-ai-internal": "0.11.7"}):
        latest = get_pypi_version("signalpilot-ai-internal")
        upgrade_type = compare_versions("0.11.7", latest)
        print(f"    Current: 0.11.7, Latest: {latest}, Type: {upgrade_type}")
        assert upgrade_type == "none", "Should detect no upgrade needed"
        print(f"    ✓ Correctly detected: up-to-date")

    # Scenario 5: Network failure
    print("\n  → Scenario 5: Network failure")
    with mock_network_failure():
        latest = get_pypi_version("signalpilot-ai-internal")
        print(f"    Latest: {latest} (should be None)")
        assert latest is None, "Should return None on network failure"
        print(f"    ✓ Gracefully handled network failure")

    print("\n  ✓ All upgrade scenarios passed")


def test_full_upgrade_flow():
    """Test complete upgrade flow with mocks"""
    print("\n📋 Testing full upgrade flow...")

    # Simulate a MINOR upgrade scenario
    current_cli = "0.5.3"
    current_lib = "0.11.7"

    with mock_pypi_responses({
        "signalpilot": "0.5.4",
        "signalpilot-ai-internal": "0.11.8"
    }):
        # Check CLI
        cli_latest = get_pypi_version("signalpilot")
        cli_upgrade = compare_versions(current_cli, cli_latest)

        print(f"\n  CLI: {current_cli} -> {cli_latest}")
        print(f"  Upgrade type: {cli_upgrade.upper()}")

        # Check Library
        lib_latest = get_pypi_version("signalpilot-ai-internal")
        lib_upgrade = compare_versions(current_lib, lib_latest)

        print(f"\n  Library: {current_lib} -> {lib_latest}")
        print(f"  Upgrade type: {lib_upgrade.upper()}")

        # Verify both are MINOR
        assert cli_upgrade == "minor", "CLI should be MINOR upgrade"
        assert lib_upgrade == "minor", "Library should be MINOR upgrade"

    print("\n  ✓ Full upgrade flow test passed")


def demo_upgrade_command():
    """Demo the upgrade command with mocked responses"""
    console.print("\n" + "="*60, style="white")
    console.print("📦 Mock Upgrade Command Demo", style="bold cyan")
    console.print("="*60, style="white")

    current_cli = "0.5.3"
    current_lib = "0.11.7"

    with mock_pypi_responses({
        "signalpilot": "0.5.4",
        "signalpilot-ai-internal": "0.11.8"
    }):
        # CLI check
        console.print("\n→ Checking CLI version...", style="dim")
        cli_latest = get_pypi_version("signalpilot")
        console.print(f"  Current: {current_cli}", style="dim")
        console.print(f"  Latest:  {cli_latest}", style="green")

        cli_upgrade = compare_versions(current_cli, cli_latest)
        if cli_upgrade != "none":
            console.print(f"  → {cli_upgrade.upper()} upgrade available", style="yellow")
            console.print("  → Would run: uv tool install --force signalpilot", style="dim")
        else:
            console.print("  ✓ Already up-to-date", style="green")

        # Library check
        console.print("\n→ Checking library version...", style="dim")
        lib_latest = get_pypi_version("signalpilot-ai-internal")
        console.print(f"  Package: signalpilot-ai-internal", style="dim")
        console.print(f"  Current: {current_lib}", style="dim")
        console.print(f"  Latest:  {lib_latest}", style="green")

        lib_upgrade = compare_versions(current_lib, lib_latest)
        if lib_upgrade != "none":
            console.print(f"  → {lib_upgrade.upper()} upgrade available", style="yellow")
            console.print("  → Would run: uv pip install --upgrade signalpilot-ai-internal", style="dim")
        else:
            console.print("  ✓ Already up-to-date", style="green")

    console.print("\n" + "="*60, style="white")
    console.print("✅ Mock upgrade complete!", style="bold green")
    console.print("\n[dim]Note: This was a simulation with mocked PyPI responses.[/dim]")
    console.print("[dim]No actual network calls were made.[/dim]")
    console.print("="*60 + "\n", style="white")


def main():
    print("="*60)
    print("🧪 Upgrade System Tests (Mocked - No Network)")
    print("="*60)

    try:
        test_pypi_mocking()
        test_upgrade_scenarios()
        test_full_upgrade_flow()

        print("\n" + "="*60)
        print("✅ All mocked tests passed!")
        print("="*60)

        # Show demo
        demo_upgrade_command()

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
