# SignalPilot Upgrade System Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Performance Optimizations](#performance-optimizations)
- [Upgrade Notification Flow](#upgrade-notification-flow)
- [Semantic Versioning](#semantic-versioning)
- [Cache System](#cache-system)
- [Configuration](#configuration)
- [Manual Upgrade Commands](#manual-upgrade-commands)
- [Testing](#testing)
- [Implementation Details](#implementation-details)

---

## Overview

The SignalPilot upgrade system provides automatic version checking and manual upgrade capabilities with **zero impact** on Jupyter Lab startup time.

### Key Features

- ✅ **Non-blocking startup**: ~6ms overhead (99.6% faster than original 1.6s)
- ✅ **Cache-based checks**: No subprocess calls on startup
- ✅ **Semantic versioning**: MINOR/MAJOR/BREAKING upgrade notifications
- ✅ **Background updates**: PyPI checks run after Jupyter starts
- ✅ **Configurable**: Users can disable checks via config.toml
- ✅ **Manual upgrades**: `sp upgrade` and `sp upgrade --project` commands

---

## Architecture

### Code Organization

```
sp/
├── commands/
│   ├── init.py          # sp init command
│   ├── lab.py           # sp lab/home commands with upgrade integration
│   └── upgrade.py       # sp upgrade commands (manual)
├── core/
│   ├── config.py        # Configuration, paths, cache directories
│   ├── environment.py   # Virtual environment management
│   └── jupyter.py       # Jupyter Lab launch logic
├── ui/
│   └── console.py       # Rich console instance and branding
└── upgrade_check.py     # Version checking, caching, notifications (core logic)
```

### Main Components

**1. `sp/upgrade_check.py`** (412 lines)
   - Version comparison and semantic versioning logic
   - PyPI version fetching
   - Cache management (read/write/validation)
   - Package detection using `importlib.metadata`
   - Background version checking
   - Notification UI (panels and prompts)

**2. `sp/commands/lab.py`** (148 lines)
   - Integrates upgrade check into `sp lab` startup
   - Shows notifications before Jupyter starts
   - Launches background cache update

**3. `sp/commands/upgrade.py`** (191 lines)
   - Manual `sp upgrade` command
   - Upgrades both CLI and library
   - `sp upgrade --project` for local .venv

**4. `sp/core/config.py`** (103 lines)
   - Cache directory: `~/SignalPilotHome/.signalpilot/`
   - Config file: `~/SignalPilotHome/.signalpilot/config.toml`
   - Config loading with auto-creation

---

## Performance Optimizations

### Startup Performance: Before vs After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Total startup overhead** | 1,627ms | **5.74ms** | **99.6% faster (283x)** |
| Subprocess calls | 765ms | **0ms** | Eliminated |
| Package detection (pip show) | 468ms | **0ms** | Eliminated |
| Jupyter version check (pip show) | 286ms | **0ms** | Eliminated |
| Cache operations | 1.4ms | 1.4ms | Same |
| Config loading | 4.7ms | 4.7ms | Same |

### Key Optimizations Applied

#### 1. **Replaced `pip show` with `importlib.metadata`**
```python
# Before: subprocess call (395ms per call)
subprocess.run(["pip", "show", "signalpilot-ai-internal"], ...)

# After: Direct metadata access (instant)
from importlib.metadata import version
version("signalpilot-ai-internal")  # No subprocess!
```

**Impact**: Eliminated 3 subprocess calls (~750ms total)

#### 2. **Cache-Only Startup Checks**
```python
# Startup: Read cache only (no pip show, no network)
def check_cache_for_upgrades(venv_dir: Path) -> dict | None:
    cache = load_cache()  # Read JSON from disk (~1ms)

    # Read versions from cache (no subprocess!)
    lib_current = cache[package].get('current_version')
    lib_latest = cache[package].get('latest_version')

    return compare_versions(lib_current, lib_latest)
```

**Impact**: ~1ms to check for upgrades (was 284ms)

#### 3. **Background Cache Updates**
```python
# After Jupyter starts, update cache in background thread
if is_upgrade_check_enabled():
    start_version_check(venv_dir)  # Daemon thread

# Run Jupyter (blocks until terminated)
run_jupyter_lab(...)
```

**Impact**: Zero delay to Jupyter startup

#### 4. **Removed Jupyter Diagnostic Checks**
```python
# Before: 2 subprocess calls before startup
subprocess.run(["python", "--version"], ...)  # 11ms
subprocess.run(["pip", "show", "jupyterlab"], ...)  # 286ms

# After: Removed from diagnostics (not essential)
console.print(f"  Workspace: {workspace_dir}")
console.print(f"  Environment: {venv_dir}")
```

**Impact**: Saved 297ms

#### 5. **Jupyter Lab Configuration Optimizations**
```python
cmd = [
    "jupyter", "lab",
    # Startup speed optimizations
    "--LabApp.news_url=''",  # Skip news fetch (~100-500ms)
    "--LabApp.collaborative=False",  # Skip collaboration init (~50-200ms)
    # Performance optimizations
    "--ServerApp.contents_manager_class=AsyncLargeFileManager",  # Better async I/O
]
```

**Impact**: 150-700ms faster Jupyter startup

#### 6. **Package Detection Priority**
```python
# Check public package first (more common)
version = get_installed_version(venv_dir, SIGNALPILOT_AI)
if version:
    return (SIGNALPILOT_AI, version)

# Fallback to internal package (less common)
version = get_installed_version(venv_dir, SIGNALPILOT_AI_INTERNAL)
if version:
    return (SIGNALPILOT_AI_INTERNAL, version)
```

**Impact**: Faster detection for most users

---

## Upgrade Notification Flow

### Startup Sequence

```
┌─ sp lab ────────────────────────────────────────────────────┐
│                                                              │
│ 1. Load config (~5ms)                                        │
│    ├─ Read ~/SignalPilotHome/.signalpilot/config.toml       │
│    └─ Check if upgrade checks enabled                       │
│                                                              │
│ 2. Check cache for upgrades (~1ms)                           │
│    ├─ Read ~/SignalPilotHome/.signalpilot/upgrade-cache.json│
│    ├─ Get current_version and latest_version from cache     │
│    └─ Compare versions (semantic versioning)                │
│                                                              │
│ 3. Show notification (if upgrade available)                 │
│    ├─ MINOR: Non-blocking panel (instant, no delay)         │
│    ├─ MAJOR: Blocking prompt with 5s timeout                │
│    └─ BREAKING: Blocking prompt with 5s timeout             │
│                                                              │
│ 4. Launch Jupyter Lab (0ms delay)                           │
│    └─ Start with optimized flags                            │
│                                                              │
│ 5. Background: Update cache (after Jupyter starts)          │
│    ├─ Detect installed package (importlib.metadata)         │
│    ├─ Fetch latest from PyPI                                │
│    ├─ Update cache for next session                         │
│    └─ Daemon thread (terminates when Jupyter stops)         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Critical Design Choice**: Cache is updated *after* Jupyter starts, so the current session uses the previous session's cache data.

---

## Semantic Versioning

### Version Format: BREAKING.MAJOR.MINOR

```
1.0.0
│ │ │
│ │ └─ MINOR: Bug fixes, small features (0.11.2 → 0.11.3)
│ └─── MAJOR: New features, some breaking changes (0.11.x → 0.12.0)
└───── BREAKING: Major breaking changes (0.x.x → 1.0.0)
```

### Notification Types

#### MINOR Upgrade (Non-Blocking)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Update Available: 0.11.8 (installed: 0.11.7)        │
│ Package: signalpilot-ai-internal                    │
│ Run 'sp upgrade' to update                          │
╰──────────────────────────────────────────────────────╯
Starting Jupyter Lab...
```

**Behavior**:
- Displays immediately (no delay)
- Jupyter starts right away
- User can upgrade later with `sp upgrade`

#### MAJOR/BREAKING Upgrade (Blocking Prompt)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Important Update: 0.12.0 (installed: 0.11.7)        │
│ Package: signalpilot-ai-internal                    │
│ This is a MAJOR update                              │
╰──────────────────────────────────────────────────────╯

Upgrade now? [y/n] (n): _
```

**Behavior**:
- Blocks for user input with 5-second timeout
- If 'y': Runs upgrade immediately, then starts Jupyter
- If 'n' or timeout: Continues to Jupyter

**Implementation**:
```python
def compare_versions(current: str, latest: str) -> str:
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
```

---

## Cache System

### Cache Location

```
~/SignalPilotHome/.signalpilot/upgrade-cache.json
```

### Cache Format

```json
{
  "signalpilot": {
    "latest_version": "0.5.4",
    "last_check_time": "2026-01-08T10:30:00+00:00"
  },
  "signalpilot-ai-internal": {
    "current_version": "0.11.7",
    "latest_version": "0.11.8",
    "last_check_time": "2026-01-08T10:30:00+00:00"
  }
}
```

### Cache Lifecycle

1. **Startup**: Read cache (fast JSON read)
2. **Validation**: Check if `last_check_time` < 12 hours old
3. **Background Update**: After Jupyter starts
   - Detect installed packages (importlib.metadata)
   - Fetch latest from PyPI
   - Update cache with new data
4. **Next Session**: Uses updated cache from previous session

### Cache Behavior

| Scenario | Behavior |
|----------|----------|
| **No cache file** | No notification, background creates cache |
| **Cache < 12 hours old** | Use cache data (no PyPI call) |
| **Cache > 12 hours old** | Treat as expired, background updates |
| **Corrupted cache** | Delete file, continue without notification |
| **Cache write fails** | Silent failure, no error shown |

---

## Configuration

### Config File

Location: `~/SignalPilotHome/.signalpilot/config.toml`

**Auto-creation**: Created automatically with defaults on first run

### Default Configuration

```toml
[upgrade]
check_enabled = true
```

### Disabling Upgrade Checks

```toml
[upgrade]
check_enabled = false
```

**Effect**: Skips all upgrade checks (both startup and background)

### Implementation

```python
def is_upgrade_check_enabled() -> bool:
    config = load_config()
    return config.get('upgrade', {}).get('check_enabled', True)
```

---

## Manual Upgrade Commands

### `sp upgrade` - Upgrade CLI and Library

Upgrades packages in `~/SignalPilotHome/.venv`:

```bash
sp upgrade
```

**What it does**:
1. Detects installed package (signalpilot-ai or signalpilot-ai-internal)
2. Checks PyPI for latest version
3. Runs `uv tool install --force signalpilot` (CLI upgrade)
4. Runs `uv pip install --upgrade {package}` (library upgrade)
5. Shows summary of changes

**Example output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦 SignalPilot Upgrade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Upgrading: ~/SignalPilotHome/.venv

CLI Upgrade
  Package: signalpilot
  Current: 0.5.3
  Latest:  0.5.4
  → Running: uv tool install --force signalpilot

✓ CLI upgraded to v0.5.4
→ uvx cache updated (new version will be used next time)

Library Upgrade
  Package: signalpilot-ai-internal
  Current: 0.11.7
  Latest:  0.11.8
  → Running: uv pip install --upgrade signalpilot-ai-internal

✓ Library upgraded to v0.11.8

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Upgrade Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `sp upgrade --project` - Upgrade Project's .venv

Upgrades packages in current directory's `.venv`:

```bash
cd /path/to/project
sp upgrade --project
```

**Use case**: When working in a project-specific environment

---

## Testing

### Quick Testing with Mock Cache

Use `create_test_cache.py` to create mock upgrade scenarios:

```bash
# Create different upgrade scenarios
python create_test_cache.py minor      # MINOR upgrade (non-blocking)
python create_test_cache.py major      # MAJOR upgrade (blocking prompt)
python create_test_cache.py breaking   # BREAKING upgrade (blocking prompt)
python create_test_cache.py none       # No upgrade available

# View current cache
python create_test_cache.py show

# Delete cache
python create_test_cache.py delete
```

**Auto-detection**: The script automatically detects your installed versions and uses them as the base:

```bash
$ python create_test_cache.py minor
  📦 Detected library: signalpilot-ai-internal v0.11.7
  📦 Detected CLI: signalpilot v0.5.3

✅ Created mock cache: MINOR upgrade (0.11.7 → 0.11.8)

📊 Cache contents:
  CLI:     0.5.3 → 0.5.4
  Library: 0.11.7 → 0.11.8 (signalpilot-ai-internal)

📂 Cache location: ~/SignalPilotHome/.signalpilot/upgrade-cache.json

📝 To test notification, run:
  uvx signalpilot@latest lab
  # or: python -m sp.main lab
```

### Testing Workflow

1. **Create mock cache**:
   ```bash
   python create_test_cache.py minor
   ```

2. **Test notification**:
   ```bash
   python -m sp.main lab
   ```

3. **Verify behavior**:
   - MINOR: Shows yellow panel, starts Jupyter immediately
   - MAJOR/BREAKING: Shows yellow panel + y/n prompt, waits 5s

4. **Clean up**:
   ```bash
   python create_test_cache.py delete
   ```

### Performance Profiling

Run startup profiler to measure performance:

```bash
python profile_lab_startup.py
```

**Expected output**:
```
======================================================================
PROFILING: sp lab startup
======================================================================

1. HOME SETUP
  ensure_home_setup()                                    0.06ms

2. CONFIG LOADING
  is_upgrade_check_enabled()                             4.20ms

3. CACHE OPERATIONS
  load_cache()                                           0.48ms

4. UPGRADE CHECK (cache-only, no subprocess)
  check_cache_for_upgrades(venv_dir)                     0.94ms

5. REMOVED OPERATIONS (no longer called on startup)
  ❌ detect_signalpilot_package() - moved to background
  ❌ pip show signalpilot-ai-internal - moved to background
  ❌ pip show signalpilot-ai - moved to background
  ❌ python --version - removed from diagnostics
  ❌ pip show jupyterlab - removed from diagnostics

======================================================================
SUMMARY
======================================================================

Total startup overhead: 5.74ms

🚀 EXCELLENT: Startup is blazing fast (<10ms)

📊 Optimizations applied:
  ✅ Removed pip show calls from startup (moved to background)
  ✅ Removed python --version from diagnostics
  ✅ Removed pip show jupyterlab from diagnostics
  ✅ Cache-only upgrade check (no subprocess)

💡 Background thread updates cache after Jupyter starts

======================================================================
```

---

## Implementation Details

### Version Detection with importlib.metadata

**Old Approach** (slow):
```python
# Spawned subprocess for each check (~400ms per call)
result = subprocess.run(
    ["pip", "show", "signalpilot-ai-internal"],
    capture_output=True, text=True
)
# Parse stdout to extract version
```

**New Approach** (fast):
```python
from importlib.metadata import version, PackageNotFoundError

# Find site-packages in venv
lib_dir = venv_dir / "lib"
site_packages = list(lib_dir.glob("python*/site-packages"))[0]

# Temporarily add to sys.path
sys.path.insert(0, str(site_packages))

try:
    return version(package_name)  # Instant! No subprocess
except PackageNotFoundError:
    return None
finally:
    sys.path = original_path  # Restore
```

**Performance**: <1ms vs ~400ms (400x faster)

### Background Version Check

**Pattern** (from `sp/demos.py`):
```python
def check_versions_background(venv_dir: Path, result_container: list):
    """Daemon thread function"""
    # 1. Detect installed package (importlib.metadata)
    lib_info = detect_signalpilot_package(venv_dir)

    # 2. Fetch latest from PyPI
    lib_latest = get_pypi_version(lib_package)

    # 3. Update cache
    cache[lib_package] = {
        'current_version': lib_current,
        'latest_version': lib_latest,
        'last_check_time': datetime.now(timezone.utc).isoformat()
    }
    save_cache(cache)

    # 4. Append result to container
    result_container.append(result)

def start_version_check(venv_dir: Path):
    result_container = []
    thread = threading.Thread(
        target=check_versions_background,
        args=(venv_dir, result_container),
        daemon=True  # Auto-terminates when Jupyter stops
    )
    thread.start()
    return thread, result_container
```

**Key Design**:
- Daemon thread (terminates with main process)
- No blocking on main thread
- Updates cache for next session

### uvx Cache Auto-Update

When upgrading CLI via `sp upgrade`:

```python
# This command automatically updates uvx cache
subprocess.run(["uv", "tool", "install", "--force", "signalpilot"])

# No need for manual 'uvx --refresh'!
if is_running_via_uvx():
    console.print("[dim]→ uvx cache updated (new version will be used next time)[/dim]")
```

**Detection**:
```python
def is_running_via_uvx() -> bool:
    return "uvx" in sys.prefix or ".local/share/uv" in sys.prefix
```

---

## Error Handling

All errors are handled gracefully - the upgrade system never crashes or blocks Jupyter:

| Error | Behavior |
|-------|----------|
| **Network timeout** | Use cache if valid, else skip silently |
| **PyPI 404** | Expected for signalpilot-ai-internal, skip silently |
| **Corrupted cache JSON** | Delete cache file, continue without notification |
| **No package installed** | Skip check entirely |
| **Cache write failure** | Silent failure (cache not critical) |
| **importlib.metadata fails** | Returns None, skips detection |
| **Config file missing** | Auto-created with defaults |
| **Config file corrupted** | Use defaults silently |

**Philosophy**: Upgrade system is a convenience feature - it should never interfere with Jupyter Lab startup.

---

## Files Reference

### Core Implementation Files

- [`sp/upgrade_check.py`](sp/upgrade_check.py) - Core upgrade logic (412 lines)
- [`sp/commands/lab.py`](sp/commands/lab.py) - Lab command integration (148 lines)
- [`sp/commands/upgrade.py`](sp/commands/upgrade.py) - Manual upgrade commands (191 lines)
- [`sp/core/config.py`](sp/core/config.py) - Configuration management (103 lines)
- [`sp/core/jupyter.py`](sp/core/jupyter.py) - Jupyter launch with optimizations (102 lines)

### Testing Files

- [`create_test_cache.py`](create_test_cache.py) - Mock cache creator (195 lines)
- [`profile_lab_startup.py`](profile_lab_startup.py) - Startup profiler (183 lines)
- [`TESTING.md`](TESTING.md) - Testing guide

### Documentation

- [`UPGRADE-SYSTEM.md`](UPGRADE-SYSTEM.md) - This file (comprehensive docs)
- [`TESTING.md`](TESTING.md) - Testing procedures
- [`UPGRADE-SPEC.md`](UPGRADE-SPEC.md) - Original specification (outdated)

---

## Summary

The SignalPilot upgrade system provides:

✅ **Lightning-fast startup** (~6ms overhead, 99.6% improvement)
✅ **Smart notifications** (MINOR/MAJOR/BREAKING with appropriate UX)
✅ **Zero blocking** (cache-based checks, background updates)
✅ **Full control** (manual commands + config to disable)
✅ **Robust error handling** (never crashes, always launches Jupyter)
✅ **Easy testing** (mock cache creator with auto-detection)

**Key Innovation**: Separate cache population (background) from cache reading (startup), ensuring Jupyter starts instantly while keeping version data fresh.
