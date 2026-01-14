#!/usr/bin/env python3
"""Create mock cache files for testing notifications"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Cache location
CACHE_DIR = Path.home() / "SignalPilotHome" / ".signalpilot"
CACHE_FILE = CACHE_DIR / "upgrade-cache.json"


def create_cache(scenario: str):
    """Create a mock cache file for different test scenarios.

    Args:
        scenario: One of "minor", "major", "breaking", "none", "cli-only", "lib-only"
    """
    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Detect installed package versions
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from sp.upgrade_check import detect_signalpilot_package, get_cli_version
        from sp.core.environment import get_home_paths

        # Detect library version
        _, venv_dir = get_home_paths()
        lib_info = detect_signalpilot_package(venv_dir)

        if lib_info:
            package_name, current_lib = lib_info
            print(f"  📦 Detected library: {package_name} v{current_lib}")
        else:
            package_name = "signalpilot-ai"
            current_lib = "0.11.2"
            print(f"  ⚠️  No library detected, using default: {package_name} v{current_lib}")

        # Detect CLI version
        detected_cli = get_cli_version()
        if detected_cli:
            current_cli = detected_cli
            print(f"  📦 Detected CLI: signalpilot v{current_cli}")
        else:
            current_cli = "0.5.3"
            print(f"  ⚠️  CLI not detected, using default: v{current_cli}")

    except Exception as e:
        package_name = "signalpilot-ai-internal"
        current_lib = "0.11.7"
        current_cli = "0.5.3"
        print(f"  ⚠️  Detection failed, using defaults")
        print(f"     Library: {package_name} v{current_lib}")
        print(f"     CLI: signalpilot v{current_cli}")

    # Calculate target versions based on scenario
    if scenario == "minor":
        # Increment MINOR version
        parts = current_lib.split('.')
        latest_lib = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        latest_cli = "0.5.4"
        desc = f"MINOR upgrade ({current_lib} → {latest_lib})"

    elif scenario == "major":
        # Increment MAJOR version
        parts = current_lib.split('.')
        latest_lib = f"{parts[0]}.{int(parts[1]) + 1}.0"
        latest_cli = "0.6.0"
        desc = f"MAJOR upgrade ({current_lib} → {latest_lib})"

    elif scenario == "breaking":
        # Increment BREAKING version
        parts = current_lib.split('.')
        latest_lib = f"{int(parts[0]) + 1}.0.0"
        latest_cli = "1.0.0"
        desc = f"BREAKING upgrade ({current_lib} → {latest_lib})"

    elif scenario == "none":
        # No upgrade available
        latest_lib = current_lib
        latest_cli = current_cli
        desc = "No upgrade available (up-to-date)"

    elif scenario == "cli-only":
        # Only CLI has upgrade
        latest_lib = current_lib
        latest_cli = "0.6.0"
        desc = f"CLI upgrade only ({current_cli} → {latest_cli})"

    elif scenario == "lib-only":
        # Only library has upgrade
        parts = current_lib.split('.')
        latest_lib = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        latest_cli = current_cli
        desc = f"Library upgrade only ({current_lib} → {latest_lib})"

    else:
        print(f"✗ Unknown scenario: {scenario}")
        print("\nAvailable scenarios:")
        print("  minor      - MINOR library upgrade (0.11.7 → 0.11.8)")
        print("  major      - MAJOR library upgrade (0.11.7 → 0.12.0)")
        print("  breaking   - BREAKING library upgrade (0.11.7 → 1.0.0)")
        print("  none       - No upgrades available")
        print("  cli-only   - Only CLI upgrade available")
        print("  lib-only   - Only library upgrade available")
        sys.exit(1)

    # Create cache
    cache = {
        "signalpilot": {
            "latest_version": latest_cli,
            "last_check_time": datetime.now(timezone.utc).isoformat()
        },
        package_name: {
            "current_version": current_lib,
            "latest_version": latest_lib,
            "last_check_time": datetime.now(timezone.utc).isoformat()
        }
    }

    # Write cache file
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

    # Print success message
    print(f"\n✅ Created mock cache: {desc}")
    print(f"\n📊 Cache contents:")
    print(f"  CLI:     {current_cli} → {latest_cli}")
    print(f"  Library: {current_lib} → {latest_lib} ({package_name})")
    print(f"\n📂 Cache location: {CACHE_FILE}")
    print(f"\n📝 To test notification, run:")
    print(f"  uvx signalpilot@latest lab")
    print(f"  # or: python -m sp.main lab")


def show_cache():
    """Display current cache contents"""
    if not CACHE_FILE.exists():
        print("✗ No cache file found")
        print(f"  Expected location: {CACHE_FILE}")
        return

    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)

    print("📦 Current Cache:")
    print(json.dumps(cache, indent=2))


def delete_cache():
    """Delete the cache file"""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f"✓ Deleted cache: {CACHE_FILE}")
    else:
        print("✗ No cache file to delete")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python create_test_cache.py <scenario>")
        print("  python create_test_cache.py show")
        print("  python create_test_cache.py delete")
        print("\nScenarios:")
        print("  minor      - MINOR upgrade notification (non-blocking)")
        print("  major      - MAJOR upgrade notification (blocking prompt)")
        print("  breaking   - BREAKING upgrade notification (blocking prompt)")
        print("  none       - No upgrades (no notification)")
        print("  cli-only   - CLI upgrade only")
        print("  lib-only   - Library upgrade only")
        print("\nExamples:")
        print("  python create_test_cache.py minor")
        print("  python create_test_cache.py show")
        print("  python create_test_cache.py delete")
        sys.exit(0)

    command = sys.argv[1]

    if command == "show":
        show_cache()
    elif command == "delete":
        delete_cache()
    else:
        create_cache(command)


if __name__ == "__main__":
    main()
