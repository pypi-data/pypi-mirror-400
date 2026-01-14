# SignalPilot Auto-Upgrade Feature Specification

## Overview

Implement a non-blocking version check for the `sp lab` command that:
- Checks PyPI for the latest version of `signalpilot-ai` (or `signalpilot-ai-internal` in dev mode)
- Shows an interactive upgrade prompt before Jupyter Lab logs start streaming
- Allows users to upgrade immediately with a simple `y/n` response
- Never blocks or delays Jupyter Lab startup

## Architecture

### Design Principle: Zero-Delay Startup
Jupyter Lab starts **immediately** in the background while version check runs concurrently. The check completes within 3 seconds (or times out), then shows an interactive prompt before log streaming begins.

### Solution: Interactive TUI Panel

```
┌─ Flow ─────────────────────────────────────────┐
│ 1. Start Jupyter Lab (background, non-blocking) │
│ 2. Check version (3s max, parallel)            │
│ 3. If update available:                        │
│    - Show panel with y/n prompt (10s timeout)  │
│    - If 'y': Run pip upgrade, then stream logs │
│    - If 'n'/timeout: Skip, stream logs         │
│ 4. Stream Jupyter logs normally                │
└─────────────────────────────────────────────────┘
```

## Implementation

### 1. New Module: `sp/version.py`

Encapsulates all version checking logic using the threading pattern from `sp/demos.py`.

#### Key Functions

```python
def get_cache_path(package_name: str) -> Path:
    """Returns ~/.cache/signalpilot/version_check_{package_name}.json"""

def load_cache(package_name: str) -> dict | None:
    """Load cache if < 24 hours old, None if expired/missing/corrupted

    Validates:
    - File exists and readable
    - JSON is well-formed
    - Required fields present
    - Timestamp < 24 hours old
    """

def save_cache(package_name: str, installed: str, latest: str, is_dev: bool):
    """Save version check results with timestamp

    Creates ~/.cache/signalpilot/ directory if needed
    Handles write failures gracefully
    """

def get_installed_version(venv_dir: Path) -> tuple[bool | None, str | None, str | None]:
    """Detect installed package (dev vs prod) and version

    Uses `pip show` pattern from main.py:272-287

    Returns:
        (is_dev, package_name, version)
        - (True, "signalpilot-ai-internal", "0.10.5") for dev
        - (False, "signalpilot-ai", "0.11.0") for prod
        - (None, None, None) if neither found
    """

def get_pypi_version(package_name: str, timeout: float = 2.0) -> str | None:
    """Fetch latest version from PyPI JSON API

    URL: https://pypi.org/pypi/{package_name}/json
    Returns: data['info']['version']

    Handles:
    - Network timeouts (2s default)
    - HTTP 404 (package not on PyPI)
    - Connection errors
    - JSON parse errors
    """

def check_version_background(venv_dir: Path, result_container: list):
    """Background thread function (daemon)

    Follows demos.py:14-18 pattern exactly

    Flow:
    1. Get installed version and package name
    2. Load cache (if valid and < 24h old)
    3. If cache miss/expired: fetch from PyPI
    4. Compare installed vs latest (string comparison)
    5. Save result to cache
    6. Append result dict to result_container

    Result dict structure:
    {
        'installed': '0.10.5',
        'latest': '0.11.0',
        'package': 'signalpilot-ai',
        'is_dev': False,
        'upgrade_available': True  # latest > installed
    }
    """

def start_version_check(venv_dir: Path) -> tuple[threading.Thread, list]:
    """Start background version check

    Follows demos.py:21-33 pattern exactly

    Returns:
        (daemon_thread, result_container)

    Thread is daemon=True so it auto-terminates when main process exits
    """
```

#### Cache Format

Location: `~/.cache/signalpilot/version_check_{package_name}.json`

```json
{
  "package": "signalpilot-ai",
  "installed_version": "0.10.5",
  "latest_version": "0.11.0",
  "last_checked": "2026-01-06T15:30:00",
  "is_dev": false
}
```

#### Error Handling

| Error | Behavior |
|-------|----------|
| Network timeout | Use cache if available, else skip silently |
| PyPI 404 (e.g., signalpilot-ai-internal) | Use cache if available, else skip |
| Corrupted cache JSON | Delete cache file, skip check |
| No package installed | Return (None, None, None), caller skips |
| Cache directory creation fails | Skip check, no error shown |

### 2. Modifications to `sp/main.py`

#### A. Add Imports (top of file, after line 9)

```python
from rich.panel import Panel
from rich.prompt import Confirm
from sp.version import start_version_check
```

#### B. Start Version Check (after line 401, before welcome message)

Insert before the welcome message display:

```python
# Start version check in background (non-blocking)
version_thread = None
version_result = []

try:
    version_thread, version_result = start_version_check(venv_dir)
except Exception:
    # If version check fails to start, continue without it
    pass
```

#### C. Replace Jupyter Launch Logic (REPLACE lines 412-420)

Replace the existing `subprocess.run()` block with:

```python
try:
    # Start Jupyter immediately in background
    jupyter_process = subprocess.Popen(
        [str(venv_jupyter), "lab"] + list(ctx.args),
        cwd=workspace_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )

    # Check for version update (wait max 3 seconds)
    should_upgrade = False
    if version_thread:
        version_thread.join(timeout=3.0)
        if version_result and version_result[0].get('upgrade_available'):
            result = version_result[0]

            # Show upgrade panel with prompt
            console.print()
            console.print(Panel(
                f"[bold yellow]Update Available:[/bold yellow] {result['latest']} (installed: {result['installed']})\n"
                f"[dim]Package: {result['package']}[/dim]",
                title="📦 SignalPilot Update",
                border_style="yellow",
                padding=(0, 1)
            ))
            console.print()

            # Prompt with timeout using signal
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError()

            # Set 10-second timeout for user response
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)

            try:
                should_upgrade = Confirm.ask(
                    "[yellow]Upgrade now?[/yellow]",
                    default=False
                )
                signal.alarm(0)  # Cancel alarm
            except (TimeoutError, KeyboardInterrupt):
                signal.alarm(0)
                console.print("[dim]Skipping upgrade (no response)[/dim]")
                should_upgrade = False

            console.print()

    # Run upgrade if user confirmed
    if should_upgrade:
        console.print("→ Upgrading SignalPilot...", style="cyan")
        pip_path = venv_dir / "bin" / "pip"
        try:
            upgrade_result = subprocess.run(
                [str(pip_path), "install", "--upgrade", result['package']],
                capture_output=True,
                text=True,
                timeout=60
            )
            if upgrade_result.returncode == 0:
                console.print("✓ Upgrade complete!", style="green")
            else:
                console.print(f"✗ Upgrade failed: {upgrade_result.stderr}", style="red")
        except subprocess.TimeoutExpired:
            console.print("✗ Upgrade timed out", style="red")
        except Exception as e:
            console.print(f"✗ Upgrade error: {e}", style="red")
        console.print()

    # Stream Jupyter logs
    console.print("[dim]Streaming Jupyter Lab logs...[/dim]\n")
    for line in jupyter_process.stdout:
        print(line, end='')  # Print logs directly to stdout

    jupyter_process.wait()

except KeyboardInterrupt:
    # Gracefully shutdown Jupyter (and upgrade process if running)
    jupyter_process.terminate()
    try:
        jupyter_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        jupyter_process.kill()
    console.print("\n\n→ Jupyter Lab stopped", style="dim")
```

## User Experience

### Terminal Output Flow (Happy Path)

```
============================================================
   ┌───┐
   │ ↗ │  ╔═╗┬┌─┐┌┐┌┌─┐┬  ╔═╗┬┬  ┌─┐┌┬┐
   │▓▓▓│  ╚═╗││ ┬│││├─┤│  ╠═╝││  │ │ │
   │▓░░│  ╚═╝┴└─┘┘└┘┴ ┴┴─┘╩  ┴┴─┘└─┘ ┴
   └───┘  Your Trusted CoPilot for Data Analysis

→ Starting Jupyter Lab
  Workspace: /Users/user/SignalPilotHome
  Environment: /Users/user/SignalPilotHome/.venv
============================================================

╭──────────────── 📦 SignalPilot Update ────────────────╮
│ Update Available: 0.11.0 (installed: 0.10.5)         │
│ Package: signalpilot-ai                               │
╰───────────────────────────────────────────────────────╯

Upgrade now? [y/n] (n): y█

→ Upgrading SignalPilot...
✓ Upgrade complete!

Streaming Jupyter Lab logs...

[I 2026-01-06 15:30:00.123 ServerApp] Jupyter Server 2.x.x is running at:
[I 2026-01-06 15:30:00.124 ServerApp] http://localhost:8888/lab
...
```

### Alternate Flows

**User declines upgrade (or 10s timeout):**
```
Upgrade now? [y/n] (n): n
Skipping upgrade (no response)

Streaming Jupyter Lab logs...
...
```

**Up to date (no prompt shown):**
```
============================================================
...
============================================================

Streaming Jupyter Lab logs...

[I 2026-01-06 15:30:00.123 ServerApp] Jupyter Server...
```

## Edge Cases & Behavior Matrix

| Scenario | Behavior |
|----------|----------|
| **Up to date** | No message, logs stream immediately |
| **Cache hit (< 24h)** | Use cached data, no PyPI call (~0ms overhead) |
| **Cache expired (> 24h)** | Fetch from PyPI, update cache |
| **Network timeout (> 2s)** | Use cache if available, else skip silently |
| **PyPI 404** | Skip silently (expected for signalpilot-ai-internal) |
| **Corrupted cache** | Delete cache file, skip this run |
| **No package installed** | Skip check entirely |
| **Offline mode** | Timeout after 2s, continue with no error |
| **`--here` mode** | Check ~/SignalPilotHome/.venv |
| **`--project` mode** | Check local ./.venv |
| **User presses Ctrl+C during prompt** | Cancel upgrade, stream logs |
| **User presses Ctrl+C during upgrade** | Kill pip, kill Jupyter, exit gracefully |

## Performance Impact

| Scenario | Overhead |
|----------|----------|
| **Cache hit** | ~0ms (instant result from disk) |
| **Cache miss, fast network** | 500-1000ms (PyPI request time) |
| **Network timeout** | 2000ms max (then continues) |
| **Jupyter startup** | **0ms** (starts immediately regardless) |

## Testing Checklist

- [ ] **Happy path**: Older version → Prompt appears → User says 'y' → Upgrade succeeds → Logs stream
- [ ] **User declines**: Prompt appears → User says 'n' → Skip upgrade → Logs stream
- [ ] **Timeout**: Prompt appears → No input for 10s → Auto-skip → Logs stream
- [ ] **Up to date**: No prompt → Logs stream immediately
- [ ] **Cache hit**: Second run within 24h → Uses cache (no network call)
- [ ] **Cache expiry**: Manually set timestamp to 25h ago → Fresh PyPI request
- [ ] **Offline mode**: Disconnect network → 2s timeout → Logs stream
- [ ] **Dev mode**: `signalpilot-ai-internal` installed → Attempts check (may 404)
- [ ] **`--here` flag**: Different directory → Checks default venv
- [ ] **`--project` flag**: Local .venv → Checks local environment
- [ ] **Ctrl+C during prompt**: Cancels, continues to Jupyter
- [ ] **Ctrl+C during upgrade**: Kills pip and Jupyter, exits cleanly

## Dependencies

**Zero new dependencies** - Uses only Python stdlib:

- `threading` - Already used in `sp/demos.py`
- `json` - stdlib
- `urllib.request` - Already imported in `sp/main.py`
- `datetime` - stdlib
- `signal` - stdlib (for timeout)
- `pathlib.Path` - Already used throughout
- `subprocess` - Already used throughout

**External dependencies already present:**
- `rich` - Already a dependency, used for Panel and Confirm

## Files Modified

### New Files
- `sp/version.py` (~200 lines)

### Modified Files
- `sp/main.py` (~50 lines changed)
  - Line 12: Add imports
  - Line 401: Start version check thread
  - Lines 412-420: Replace with Popen + interactive prompt logic

### Reference Implementation Files
- `sp/demos.py` (lines 14-33) - Threading pattern to copy
- `sp/main.py` (lines 272-287) - `pip show` pattern to reuse

## Success Criteria

1. ✅ **Zero Jupyter delay**: Lab starts immediately, no waiting
2. ✅ **Interactive upgrade**: Users can upgrade with 1 keystroke
3. ✅ **Non-intrusive**: Times out gracefully, never blocks indefinitely
4. ✅ **Offline-friendly**: Works perfectly without internet (uses cache or skips)
5. ✅ **Dev mode support**: Handles both `signalpilot-ai` and `-internal` packages
6. ✅ **Cache efficient**: Only checks PyPI once per day max
7. ✅ **Error resilient**: Never crashes, always launches Jupyter
