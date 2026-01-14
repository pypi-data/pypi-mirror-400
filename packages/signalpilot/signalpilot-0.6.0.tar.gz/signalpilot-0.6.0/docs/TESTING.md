# Testing the Upgrade System

## Quick Start - Test All Notifications

### Create Mock Cache Files

The easiest way to test notifications is to create mock cache files:

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

### Test the Notifications

After creating a cache, test it with:

```bash
uvx signalpilot@latest lab
# or: python -m sp.main lab
```

**What to expect:**

| Scenario | Notification | Blocking? | Duration |
|----------|--------------|-----------|----------|
| `minor` | Yellow panel | No | Instant (no delay) |
| `major` | Yellow panel + y/n prompt | Yes | 5s timeout |
| `breaking` | Yellow panel + y/n prompt | Yes | 5s timeout |
| `none` | No notification | No | N/A |

---

## Testing Manual Upgrade

```bash
# Test upgrade command (checks real PyPI)
uvx signalpilot@latest upgrade

# Test project upgrade
cd /path/to/project
uvx signalpilot@latest upgrade --project
```

---

## Testing Config

### Disable upgrade checks:

```bash
mkdir -p ~/SignalPilotHome/.signalpilot
cat > ~/SignalPilotHome/.signalpilot/config.toml << 'EOF'
[upgrade]
check_enabled = false
EOF

# Verify it's disabled
uvx signalpilot@latest lab  # No notification should appear
```

### Re-enable:

```bash
cat > ~/SignalPilotHome/.signalpilot/config.toml << 'EOF'
[upgrade]
check_enabled = true
EOF
```

---

## Advanced Testing

For automated tests and more detailed testing, see files in `tests/` directory:

- `tests/test_upgrade_system.py` - Automated unit tests
- `tests/test_upgrade_command.py` - Test upgrade command flow
- `tests/demo_upgrade_flow.py` - Interactive notification demo

Run automated tests:
```bash
python tests/test_upgrade_system.py
```

---

## Verify Cache Contents

```bash
# View cache as JSON
python create_test_cache.py show

# Or manually:
cat ~/SignalPilotHome/.signalpilot/upgrade-cache.json | python -m json.tool
```

---

## Common Test Scenarios

### Test cache expiration (12 hours):

```bash
# Create cache
python create_test_cache.py minor

# Manually edit timestamp to be 13 hours old
# (In the JSON file, change last_check_time)

# Run lab - cache should be treated as expired
uvx signalpilot@latest lab
```

### Test background cache update:

```bash
# Delete cache
python create_test_cache.py delete

# Run lab - background thread creates new cache
uvx signalpilot@latest lab

# After Jupyter starts (wait 5 seconds), check cache was created
python create_test_cache.py show
```

### Test network failure:

```bash
# Disconnect network
# Run upgrade
uvx signalpilot@latest upgrade
# Expected: Graceful error message about network
```

---

## Expected Behavior

### MINOR Upgrade (0.11.7 → 0.11.8)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Update Available: 0.11.8 (installed: 0.11.7)        │
│ Package: signalpilot-ai-internal                    │
│ Run 'sp upgrade' to update                          │
╰──────────────────────────────────────────────────────╯
Starting Jupyter Lab...
```

**Behavior:** Displays instantly, Jupyter starts immediately (non-blocking)

### MAJOR/BREAKING Upgrade (0.11.7 → 0.12.0 or 1.0.0)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Important Update: 0.12.0 (installed: 0.11.7)        │
│ Package: signalpilot-ai-internal                    │
│ This is a MAJOR update                              │
╰──────────────────────────────────────────────────────╯

Upgrade now? [y/n] (n): _
```

**Behavior:** Blocks for 5 seconds waiting for y/n, then continues

---

## Troubleshooting

**Cache not showing correct versions:**
```bash
python create_test_cache.py show
# Check if versions match your installed package
```

**Notification not appearing:**
- Check cache exists: `python create_test_cache.py show`
- Check config enabled: `cat ~/SignalPilotHome/.signalpilot/config.toml`
- Create fresh cache: `python create_test_cache.py minor`

**SignalPilotHome not initialized:**
```bash
uvx signalpilot@latest init
```

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Cache read | <10ms | Reading JSON from disk |
| MINOR notification | <100ms | Just displays panel |
| MAJOR/BREAKING prompt | 0-5s | Waits for user input |
| Jupyter startup | 0ms delay | Never blocked by upgrade system |

**Critical:** Jupyter startup is NEVER delayed by the upgrade system!
