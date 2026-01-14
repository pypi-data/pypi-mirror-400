#!/usr/bin/env python3
"""Interactive demo of the upgrade notification flow"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sp.upgrade_check import (
    check_cache_for_upgrades,
    show_non_blocking_notification,
    show_blocking_prompt,
)
from sp.core.config import SP_HOME, SP_VENV


def demo_notifications():
    """Demo all notification types"""
    print("\n" + "="*60)
    print("🎬 SignalPilot Upgrade Notification Demo")
    print("="*60)

    # Check what's in cache
    venv_dir = SP_VENV
    if not venv_dir.exists():
        print("\n⚠️  SignalPilotHome not initialized")
        print("Run 'uvx signalpilot init' first")
        return

    upgrade_info = check_cache_for_upgrades(venv_dir)

    if not upgrade_info:
        print("\n✓ No upgrades available in cache")
        print("\nTo test notifications, create a mock cache:")
        print("  python test_upgrade_system.py mock-minor")
        print("  python test_upgrade_system.py mock-major")
        print("  python test_upgrade_system.py mock-breaking")
        return

    upgrade_type = upgrade_info['type']
    current = upgrade_info['current']
    latest = upgrade_info['latest']
    package = upgrade_info['package']

    print(f"\n📦 Upgrade detected in cache:")
    print(f"  Package: {package}")
    print(f"  Current: {current}")
    print(f"  Latest:  {latest}")
    print(f"  Type:    {upgrade_type.upper()}")

    if upgrade_type == "minor":
        print("\n🔔 Showing MINOR upgrade notification (10s, non-blocking)...")
        print("    (This will auto-dismiss after 10 seconds)")
        show_non_blocking_notification(current, latest, package, duration=10)
        print("\n✓ Notification dismissed")

    elif upgrade_type in ["major", "breaking"]:
        print(f"\n🔔 Showing {upgrade_type.upper()} upgrade notification (5s, blocking)...")
        print("    (You have 5 seconds to respond, or it auto-declines)")
        should_upgrade = show_blocking_prompt(current, latest, package, timeout=5)

        if should_upgrade:
            print("\n✓ User chose to upgrade")
            print("  (In real flow, upgrade_library() would run here)")
        else:
            print("\n✓ User declined or timed out")

    print("\n" + "="*60)
    print("✅ Demo complete!")
    print("="*60)


if __name__ == "__main__":
    try:
        demo_notifications()
    except KeyboardInterrupt:
        print("\n\n✗ Demo cancelled")
        sys.exit(1)
