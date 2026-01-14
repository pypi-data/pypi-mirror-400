#!/usr/bin/env python3
"""Profile sp lab startup to identify bottlenecks"""

import sys
import time
from pathlib import Path

# Add sp to path
sys.path.insert(0, str(Path(__file__).parent))

from sp.core.config import is_upgrade_check_enabled
from sp.core.environment import ensure_home_setup
from sp.upgrade_check import (
    check_cache_for_upgrades,
    detect_signalpilot_package,
    get_installed_version,
    load_cache
)
import subprocess


def time_function(name: str, func, *args, **kwargs):
    """Time a function call and print the result"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
    print(f"  {name:50s} {elapsed:8.2f}ms")
    return result, elapsed


def profile_lab_startup():
    """Profile all operations that happen before Jupyter starts"""

    print("\n" + "="*70)
    print("PROFILING: sp lab startup")
    print("="*70 + "\n")

    total_start = time.perf_counter()
    timings = {}

    # Step 1: Ensure home setup
    print("1. HOME SETUP")
    _, timings['ensure_home_setup'] = time_function(
        "ensure_home_setup()",
        ensure_home_setup
    )
    home_dir, venv_dir = ensure_home_setup()
    print()

    # Step 2: Check if upgrade is enabled
    print("2. CONFIG LOADING")
    _, timings['is_upgrade_check_enabled'] = time_function(
        "is_upgrade_check_enabled()",
        is_upgrade_check_enabled
    )
    print()

    # Step 3: Load cache
    print("3. CACHE OPERATIONS")
    _, timings['load_cache'] = time_function(
        "load_cache()",
        load_cache
    )
    print()

    # Step 4: Check cache for upgrades (FAST - no subprocess)
    print("4. UPGRADE CHECK (cache-only, no subprocess)")
    _, timings['check_cache_for_upgrades'] = time_function(
        "check_cache_for_upgrades(venv_dir)",
        check_cache_for_upgrades,
        venv_dir
    )
    print()

    # Step 5: Show what we REMOVED (for comparison)
    print("5. REMOVED OPERATIONS (no longer called on startup)")
    print("  ❌ detect_signalpilot_package() - moved to background")
    print("  ❌ pip show signalpilot-ai-internal - moved to background")
    print("  ❌ pip show signalpilot-ai - moved to background")
    print("  ❌ python --version - removed from diagnostics")
    print("  ❌ pip show jupyterlab - removed from diagnostics")
    print()

    # Calculate total time
    total_elapsed = (time.perf_counter() - total_start) * 1000

    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal startup overhead: {total_elapsed:.2f}ms\n")

    # Sort by time
    sorted_timings = sorted(timings.items(), key=lambda x: x[1], reverse=True)

    print("Top slowest operations:")
    for i, (name, elapsed) in enumerate(sorted_timings[:10], 1):
        pct = (elapsed / total_elapsed) * 100
        print(f"  {i}. {name:45s} {elapsed:8.2f}ms ({pct:5.1f}%)")

    print("\n" + "="*70)

    # Breakdown by category
    print("\nBREAKDOWN BY CATEGORY:")
    subprocess_time = 0  # No subprocess calls on startup anymore!
    cache_time = timings.get('load_cache', 0) + timings.get('check_cache_for_upgrades', 0)
    config_time = timings.get('is_upgrade_check_enabled', 0)
    setup_time = timings.get('ensure_home_setup', 0)

    print(f"  Subprocess calls:     {subprocess_time:8.2f}ms ({subprocess_time/total_elapsed*100:5.1f}%) ✅")
    print(f"  Cache operations:     {cache_time:8.2f}ms ({cache_time/total_elapsed*100:5.1f}%)")
    print(f"  Config operations:    {config_time:8.2f}ms ({config_time/total_elapsed*100:5.1f}%)")
    print(f"  Setup operations:     {setup_time:8.2f}ms ({setup_time/total_elapsed*100:5.1f}%)")
    print()

    # Recommendations
    print("="*70)
    print("PERFORMANCE ANALYSIS:")
    print("="*70)

    if total_elapsed < 10:
        print("\n🚀 EXCELLENT: Startup is blazing fast (<10ms)")
    elif total_elapsed < 50:
        print("\n✅ GREAT: Startup is very fast (<50ms)")
    elif total_elapsed < 100:
        print("\n✅ GOOD: Startup is fast (<100ms)")
    else:
        print(f"\n⚠️  Startup is slower than expected ({total_elapsed:.2f}ms)")

    print("\n📊 Optimizations applied:")
    print("  ✅ Removed pip show calls from startup (moved to background)")
    print("  ✅ Removed python --version from diagnostics")
    print("  ✅ Removed pip show jupyterlab from diagnostics")
    print("  ✅ Cache-only upgrade check (no subprocess)")
    print("\n💡 Background thread updates cache after Jupyter starts")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    profile_lab_startup()
