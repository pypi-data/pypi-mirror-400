#!/usr/bin/env python3
"""Test script for upgrade system - can run without network"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add sp to path
sys.path.insert(0, str(Path(__file__).parent))

from sp.core.config import SP_CONFIG_DIR, SP_CACHE_FILE, load_config, is_upgrade_check_enabled
from sp.upgrade_check import (
    parse_version,
    compare_versions,
    load_cache,
    save_cache,
    is_cache_valid,
)


def test_version_parsing():
    """Test semantic version parsing"""
    print("\n📋 Testing version parsing...")

    tests = [
        ("0.11.2", (0, 11, 2)),
        ("1.0.0", (1, 0, 0)),
        ("0.11.2rc1", (0, 11, 2)),
        ("2.3.4beta", (2, 3, 4)),
    ]

    for version_str, expected in tests:
        result = parse_version(version_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {version_str} -> {result} (expected {expected})")

    print("  ✓ Version parsing tests passed")


def test_version_comparison():
    """Test version comparison logic"""
    print("\n📋 Testing version comparison...")

    tests = [
        ("0.11.2", "0.11.3", "minor"),
        ("0.11.2", "0.12.0", "major"),
        ("0.11.2", "1.0.0", "breaking"),
        ("0.11.2", "0.11.2", "none"),
        ("1.0.0", "1.0.1", "minor"),
        ("1.0.0", "1.1.0", "major"),
        ("1.0.0", "2.0.0", "breaking"),
    ]

    for current, latest, expected in tests:
        result = compare_versions(current, latest)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {current} -> {latest} = {result} (expected {expected})")

    print("  ✓ Version comparison tests passed")


def test_cache_system():
    """Test cache read/write/validation"""
    print("\n📋 Testing cache system...")

    # Create test cache
    test_cache = {
        "signalpilot": {
            "latest_version": "0.5.4",
            "last_check_time": datetime.now(timezone.utc).isoformat()
        },
        "signalpilot-ai": {
            "current_version": "0.11.2",
            "latest_version": "0.11.3",
            "last_check_time": datetime.now(timezone.utc).isoformat()
        }
    }

    # Save cache
    save_cache(test_cache)
    print(f"  ✓ Cache saved to {SP_CACHE_FILE}")

    # Load cache
    loaded = load_cache()
    print(f"  ✓ Cache loaded successfully")

    # Validate cache entries
    valid_cli = is_cache_valid(loaded, "signalpilot")
    valid_lib = is_cache_valid(loaded, "signalpilot-ai")
    print(f"  ✓ CLI cache valid: {valid_cli}")
    print(f"  ✓ Library cache valid: {valid_lib}")

    # Test expired cache
    old_cache = {
        "signalpilot": {
            "latest_version": "0.5.3",
            "last_check_time": (datetime.now(timezone.utc) - timedelta(hours=13)).isoformat()
        }
    }
    save_cache(old_cache)
    loaded = load_cache()
    expired = is_cache_valid(loaded, "signalpilot")
    print(f"  ✓ Expired cache detected correctly: {not expired}")

    print("  ✓ Cache system tests passed")


def test_config_system():
    """Test config file loading"""
    print("\n📋 Testing config system...")

    # Test default config (no file)
    config = load_config()
    enabled = is_upgrade_check_enabled()
    print(f"  ✓ Default config loaded: upgrade check enabled = {enabled}")

    # Create test config
    test_config = """[upgrade]
check_enabled = false
"""

    SP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file = SP_CONFIG_DIR / "config.toml"
    config_file.write_text(test_config)
    print(f"  ✓ Test config written to {config_file}")

    # Load and verify
    config = load_config()
    enabled = is_upgrade_check_enabled()
    print(f"  ✓ Custom config loaded: upgrade check enabled = {enabled}")

    # Cleanup
    config_file.unlink()
    print("  ✓ Config system tests passed")


def create_mock_cache(upgrade_type: str = "minor"):
    """Create a mock cache file for testing notifications"""
    print(f"\n📋 Creating mock cache for {upgrade_type.upper()} upgrade...")

    # Detect which signalpilot package is installed
    from sp.upgrade_check import detect_signalpilot_package
    from sp.core.environment import get_home_paths

    _, venv_dir = get_home_paths()
    lib_info = detect_signalpilot_package(venv_dir)

    if lib_info:
        package_name, installed_version = lib_info
        print(f"  → Detected installed package: {package_name} v{installed_version}")
        current = installed_version
    else:
        # Default to signalpilot-ai if nothing installed
        package_name = "signalpilot-ai"
        current = "0.11.2"
        print(f"  → No package detected, using default: {package_name}")

    if upgrade_type == "minor":
        # Increment minor version
        parts = current.split('.')
        latest = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
    elif upgrade_type == "major":
        # Increment major version
        parts = current.split('.')
        latest = f"{parts[0]}.{int(parts[1]) + 1}.0"
    elif upgrade_type == "breaking":
        # Increment breaking version
        parts = current.split('.')
        latest = f"{int(parts[0]) + 1}.0.0"
    else:
        latest = current

    mock_cache = {
        "signalpilot": {
            "latest_version": "0.5.4",
            "last_check_time": datetime.now(timezone.utc).isoformat()
        },
        package_name: {
            "current_version": current,
            "latest_version": latest,
            "last_check_time": datetime.now(timezone.utc).isoformat()
        }
    }

    save_cache(mock_cache)
    print(f"  ✓ Mock cache created: {current} -> {latest}")
    print(f"  ✓ Package: {package_name}")
    print(f"  ✓ Run 'uvx signalpilot lab' to see {upgrade_type.upper()} upgrade notification")
    print(f"  ✓ Cache location: {SP_CACHE_FILE}")


def main():
    print("="*60)
    print("🧪 SignalPilot Upgrade System Tests")
    print("="*60)

    try:
        test_version_parsing()
        test_version_comparison()
        test_cache_system()
        test_config_system()

        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)

        # Offer to create mock cache for manual testing
        print("\n📝 Manual Testing Options:")
        print("  1. Test MINOR upgrade notification:")
        print("     python test_upgrade_system.py mock-minor")
        print("  2. Test MAJOR upgrade notification:")
        print("     python test_upgrade_system.py mock-major")
        print("  3. Test BREAKING upgrade notification:")
        print("     python test_upgrade_system.py mock-breaking")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "mock-minor":
            create_mock_cache("minor")
        elif cmd == "mock-major":
            create_mock_cache("major")
        elif cmd == "mock-breaking":
            create_mock_cache("breaking")
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    else:
        main()
