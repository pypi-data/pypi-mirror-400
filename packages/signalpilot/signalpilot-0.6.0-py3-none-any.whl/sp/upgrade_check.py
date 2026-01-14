"""Version checking, caching, and upgrade notifications for SignalPilot CLI"""

import json
import re
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm

from sp.core.config import SP_CACHE_FILE, SIGNALPILOT_CLI, SIGNALPILOT_AI, SIGNALPILOT_AI_INTERNAL, get_cache_dir
from sp.ui.console import console


# ============================================================================
# Version Management
# ============================================================================

def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse semantic version string to tuple (BREAKING, MAJOR, MINOR).

    Args:
        version_str: Version string like "0.11.2" or "0.11.2rc1"

    Returns:
        Tuple of (breaking, major, minor) as integers

    Examples:
        "0.11.2" -> (0, 11, 2)
        "1.0.0" -> (1, 0, 0)
        "0.11.2rc1" -> (0, 11, 2)
    """
    # Strip suffixes like rc1, beta, alpha, etc.
    clean_version = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if not clean_version:
        # Fallback for malformed versions
        return (0, 0, 0)

    breaking, major, minor = clean_version.groups()
    return (int(breaking), int(major), int(minor))


def compare_versions(current: str, latest: str) -> str:
    """Compare versions and return upgrade type.

    Args:
        current: Current installed version
        latest: Latest available version

    Returns:
        One of: "breaking", "major", "minor", "none"
    """
    c_breaking, c_major, c_minor = parse_version(current)
    l_breaking, l_major, l_minor = parse_version(latest)

    if l_breaking > c_breaking:
        return "breaking"
    elif l_major > c_major:
        return "major"
    elif l_minor > c_minor:
        return "minor"
    else:
        return "none"


# ============================================================================
# PyPI Integration
# ============================================================================

def get_pypi_version(package_name: str, timeout: float = 3.0) -> str | None:
    """Fetch latest version from PyPI JSON API.

    Args:
        package_name: Package name on PyPI
        timeout: Network timeout in seconds

    Returns:
        Latest version string, or None if not found/error

    Note:
        Returns None for 404 (expected for signalpilot-ai-internal)
    """
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read())
            return data['info']['version']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Package not found (expected for signalpilot-ai-internal)
            return None
        return None
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError):
        return None


# ============================================================================
# Cache Management
# ============================================================================

def load_cache() -> dict:
    """Load upgrade cache from SignalPilotHome/.signalpilot/upgrade-cache.json.

    Returns:
        Cache dict, or empty dict if missing/expired/corrupted
    """
    if not SP_CACHE_FILE.exists():
        return {}

    try:
        with open(SP_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        return cache
    except (json.JSONDecodeError, IOError):
        # Corrupted cache, delete it
        try:
            SP_CACHE_FILE.unlink()
        except Exception:
            pass
        return {}


def save_cache(cache_data: dict):
    """Save cache to SignalPilotHome/.signalpilot/upgrade-cache.json.

    Args:
        cache_data: Dict to save as JSON

    Note:
        Failures are silent (no exceptions raised)
    """
    try:
        # Ensure directory exists
        get_cache_dir()

        with open(SP_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        # Silent failure - don't block on cache write errors
        pass


def is_cache_valid(cache_data: dict, package_key: str) -> bool:
    """Check if cache entry is valid (< 12 hours old).

    Args:
        cache_data: Cache dict
        package_key: Package name key (e.g., "signalpilot", "signalpilot-ai")

    Returns:
        True if cache entry exists and is fresh
    """
    if package_key not in cache_data:
        return False

    last_check = cache_data[package_key].get('last_check_time')
    if not last_check:
        return False

    try:
        last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
        age = datetime.now(timezone.utc) - last_check_time
        return age < timedelta(hours=12)
    except (ValueError, AttributeError):
        return False


# ============================================================================
# Version Detection
# ============================================================================

def get_installed_version(venv_dir: Path, package_name: str) -> str | None:
    """Get installed version of package using importlib.metadata.

    Much faster than pip show since it doesn't spawn a subprocess.

    Args:
        venv_dir: Path to virtual environment
        package_name: Package name to check

    Returns:
        Version string, or None if not installed
    """
    import sys
    from importlib.metadata import version, PackageNotFoundError

    # Find site-packages directory
    lib_dir = venv_dir / "lib"
    site_packages_dirs = list(lib_dir.glob("python*/site-packages"))

    if not site_packages_dirs:
        return None

    site_packages = str(site_packages_dirs[0])

    # Temporarily add venv's site-packages to path
    original_path = sys.path.copy()
    sys.path.insert(0, site_packages)

    try:
        return version(package_name)
    except PackageNotFoundError:
        return None
    finally:
        # Restore original path
        sys.path = original_path


def detect_signalpilot_package(venv_dir: Path) -> tuple[str, str] | None:
    """Detect which signalpilot package is installed (ai vs ai-internal).

    Checks for public package first (more common), then internal.

    Args:
        venv_dir: Path to virtual environment

    Returns:
        Tuple of (package_name, version), or None if not found
    """
    # Check for public package first (more common)
    version = get_installed_version(venv_dir, SIGNALPILOT_AI)
    if version:
        return (SIGNALPILOT_AI, version)

    # Check for internal package (less common)
    version = get_installed_version(venv_dir, SIGNALPILOT_AI_INTERNAL)
    if version:
        return (SIGNALPILOT_AI_INTERNAL, version)

    return None


def get_cli_version() -> str | None:
    """Get current CLI version from package metadata.

    Returns:
        Version string, or None if not found
    """
    try:
        from importlib.metadata import version
        return version(SIGNALPILOT_CLI)
    except Exception:
        return None


# ============================================================================
# Background Check
# ============================================================================

def check_versions_background(venv_dir: Path, result_container: list):
    """Background thread function to check both CLI and library versions.

    Checks PyPI for:
    1. signalpilot CLI
    2. signalpilot-ai or signalpilot-ai-internal (from venv)

    Updates cache after checking PyPI.

    Args:
        venv_dir: Path to virtual environment
        result_container: List to append result dict to

    Result format:
        {
            'cli': {'current': '0.5.3', 'latest': '0.5.4', 'upgrade_type': 'minor'},
            'library': {'current': '0.11.2', 'latest': '0.11.3', 'upgrade_type': 'minor', 'package': 'signalpilot-ai'}
        }
    """
    result = {}

    # Load cache
    cache = load_cache()
    now = datetime.now(timezone.utc).isoformat()

    # Check CLI version
    cli_current = get_cli_version()
    if cli_current:
        cli_latest = get_pypi_version(SIGNALPILOT_CLI)
        if cli_latest:
            upgrade_type = compare_versions(cli_current, cli_latest)
            result['cli'] = {
                'current': cli_current,
                'latest': cli_latest,
                'upgrade_type': upgrade_type
            }

            # Update cache
            cache[SIGNALPILOT_CLI] = {
                'latest_version': cli_latest,
                'last_check_time': now
            }

    # Check library version
    lib_info = detect_signalpilot_package(venv_dir)
    if lib_info:
        lib_package, lib_current = lib_info
        lib_latest = get_pypi_version(lib_package)

        # If PyPI check fails (expected for -internal), use cache
        if not lib_latest and is_cache_valid(cache, lib_package):
            lib_latest = cache[lib_package].get('latest_version')

        if lib_latest:
            upgrade_type = compare_versions(lib_current, lib_latest)
            result['library'] = {
                'current': lib_current,
                'latest': lib_latest,
                'upgrade_type': upgrade_type,
                'package': lib_package
            }

            # Update cache
            cache[lib_package] = {
                'current_version': lib_current,
                'latest_version': lib_latest,
                'last_check_time': now
            }

    # Save updated cache
    save_cache(cache)

    # Append result to container
    result_container.append(result)


def start_version_check(venv_dir: Path) -> tuple[threading.Thread, list]:
    """Start background version check (daemon thread).

    Args:
        venv_dir: Path to virtual environment

    Returns:
        Tuple of (thread, result_container)
    """
    result_container = []
    thread = threading.Thread(
        target=check_versions_background,
        args=(venv_dir, result_container),
        daemon=True
    )
    thread.start()
    return thread, result_container


# ============================================================================
# Notification UI
# ============================================================================

def show_non_blocking_notification(current: str, latest: str, package_name: str, duration: int = 10):
    """Show non-blocking notification for MINOR upgrades.

    Displays a brief notification without blocking Jupyter startup.

    Args:
        current: Current version
        latest: Latest version
        package_name: Package name
        duration: Ignored (kept for API compatibility)
    """
    panel = Panel(
        f"[yellow]Update Available:[/yellow] {latest} (installed: {current})\n"
        f"[dim]Package: {package_name}[/dim]\n"
        f"[dim]Run 'sp upgrade' to update[/dim]",
        title="📦 SignalPilot Update",
        border_style="yellow"
    )

    # Just print the panel without blocking
    console.print(panel)
    console.print("[dim]Starting Jupyter Lab...[/dim]\n")


def show_blocking_prompt(current: str, latest: str, package_name: str, timeout: int = 5) -> bool:
    """Show blocking prompt with timeout for MAJOR/BREAKING upgrades.

    Args:
        current: Current version
        latest: Latest version
        package_name: Package name
        timeout: Seconds to wait for user input

    Returns:
        True if user wants to upgrade, False otherwise
    """
    import signal

    console.print(Panel(
        f"[bold yellow]Important Update:[/bold yellow] {latest} (installed: {current})\n"
        f"[dim]Package: {package_name}[/dim]\n"
        f"[yellow]This is a {'BREAKING' if parse_version(latest)[0] > parse_version(current)[0] else 'MAJOR'} update[/yellow]",
        title="📦 SignalPilot Update",
        border_style="yellow"
    ))

    # Set timeout alarm (Unix only)
    def timeout_handler(signum, frame):
        raise TimeoutError()

    old_handler = None
    try:
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        result = Confirm.ask("[yellow]Upgrade now?[/yellow]", default=False)

        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Cancel alarm
        return result

    except (TimeoutError, KeyboardInterrupt):
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        console.print("[dim]Skipping upgrade (timed out)[/dim]")
        return False
    finally:
        if old_handler is not None and hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, old_handler)


def check_cache_for_upgrades(venv_dir: Path) -> dict | None:
    """Check cache for available upgrades (no network call, no subprocess).

    Reads current and latest versions from cache - does NOT call pip show.
    Cache is populated/updated by background check after Jupyter starts.

    Args:
        venv_dir: Path to virtual environment

    Returns:
        Dict with upgrade info, or None if no upgrades available
        Format: {'type': 'minor'|'major'|'breaking', 'current': '...', 'latest': '...', 'package': '...'}
    """
    cache = load_cache()

    # Try to find cached package info (no subprocess calls)
    # Check both possible packages in priority order (public first, more common)
    for lib_package in [SIGNALPILOT_AI, SIGNALPILOT_AI_INTERNAL]:
        if lib_package not in cache:
            continue

        if not is_cache_valid(cache, lib_package):
            continue

        # Get current and latest from cache
        lib_current = cache[lib_package].get('current_version')
        lib_latest = cache[lib_package].get('latest_version')

        if not lib_current or not lib_latest:
            continue

        # Compare versions
        upgrade_type = compare_versions(lib_current, lib_latest)
        if upgrade_type == "none":
            continue

        return {
            'type': upgrade_type,
            'current': lib_current,
            'latest': lib_latest,
            'package': lib_package
        }

    return None
