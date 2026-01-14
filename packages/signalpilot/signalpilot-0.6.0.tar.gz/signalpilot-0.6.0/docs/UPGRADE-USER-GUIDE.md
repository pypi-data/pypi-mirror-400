# SignalPilot Upgrade Guide

## What is the Upgrade System?

SignalPilot automatically checks for updates and lets you upgrade with a single command. The system is designed to be **fast** and **non-intrusive** - your Jupyter Lab starts instantly, and you're only notified when important updates are available.

---

## Automatic Update Notifications

When you run `sp lab`, SignalPilot checks if a newer version is available:

### Minor Updates (Small improvements)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Update Available: 0.11.8 (installed: 0.11.7)        │
│ Package: signalpilot-ai                             │
│ Run 'sp upgrade' to update                          │
╰──────────────────────────────────────────────────────╯
Starting Jupyter Lab...
```

**What happens**: Notification appears briefly, Jupyter starts immediately. You can upgrade later when convenient.

### Major Updates (New features, important changes)

```
╭─────────────── 📦 SignalPilot Update ───────────────╮
│ Important Update: 0.12.0 (installed: 0.11.7)        │
│ Package: signalpilot-ai                             │
│ This is a MAJOR update                              │
╰──────────────────────────────────────────────────────╯

Upgrade now? [y/n] (n): _
```

**What happens**:
- You're prompted to upgrade now
- Press `y` to upgrade immediately
- Press `n` or wait 5 seconds to skip
- Jupyter starts either way

---

## Manual Upgrade Commands

### Upgrade Everything

```bash
sp upgrade
```

**What it does**:
- Upgrades the SignalPilot CLI tool
- Upgrades the SignalPilot library in your home environment

**Example**:
```bash
$ sp upgrade

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦 SignalPilot Upgrade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Upgrading: ~/SignalPilotHome/.venv

CLI Upgrade
  Current: 0.5.3
  Latest:  0.5.4

✓ CLI upgraded to v0.5.4

Library Upgrade
  Current: 0.11.7
  Latest:  0.11.8

✓ Library upgraded to v0.11.8

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Upgrade Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Upgrade Project Environment

```bash
cd /path/to/your/project
sp upgrade --project
```

**What it does**:
- Upgrades SignalPilot in your project's `.venv`
- Also upgrades the CLI tool

**When to use**: If you're working in a project with its own virtual environment.

---

## Configuration

### Disabling Update Checks

If you don't want automatic update notifications, you can disable them:

1. **Edit config file**:
   ```bash
   nano ~/SignalPilotHome/.signalpilot/config.toml
   ```

2. **Set check_enabled to false**:
   ```toml
   [upgrade]
   check_enabled = false
   ```

3. **Save and exit**

You can still manually upgrade with `sp upgrade` anytime.

### Re-enabling Update Checks

Change the config back to:
```toml
[upgrade]
check_enabled = true
```

---

## Understanding Version Numbers

SignalPilot uses semantic versioning: `BREAKING.MAJOR.MINOR`

```
0.11.7
│ │  │
│ │  └─ Minor: Bug fixes, small improvements (0.11.7 → 0.11.8)
│ └──── Major: New features, some changes (0.11.x → 0.12.0)
└────── Breaking: Big changes, breaking (0.x.x → 1.0.0)
```

### Notification Behavior

- **Minor updates**: Shown briefly, doesn't interrupt
- **Major/Breaking updates**: Prompts for confirmation (important changes)

---

## Frequently Asked Questions

### How often does it check for updates?

Once every 12 hours. Results are cached, so it doesn't slow down your workflow.

### Does it slow down Jupyter Lab startup?

No! Startup is instant (~6ms overhead). The check happens in the background after Jupyter starts.

### What if I'm offline?

The system uses cached data. If no cache exists, it silently skips the check. Jupyter always starts.

### Can I upgrade without the prompt?

Yes! Just run:
```bash
sp upgrade
```

### What if the upgrade fails?

The system is designed to never break your setup. If an upgrade fails:
- You'll see an error message
- Your current version remains working
- Jupyter Lab starts normally

### How do I know what version I have?

The upgrade system shows your current version in the notification panel, or run:
```bash
sp upgrade
```
It will display current and latest versions without upgrading.

---

## Troubleshooting

### Notification not appearing

1. Check if checks are enabled:
   ```bash
   cat ~/SignalPilotHome/.signalpilot/config.toml
   ```
   Should show `check_enabled = true`

2. Delete cache to force a fresh check:
   ```bash
   rm ~/SignalPilotHome/.signalpilot/upgrade-cache.json
   ```

3. Run `sp lab` again

### Upgrade command not found

Make sure you're running the latest CLI:
```bash
uvx signalpilot@latest upgrade
```

### Want to see cache contents

```bash
cat ~/SignalPilotHome/.signalpilot/upgrade-cache.json | python -m json.tool
```

---

## Summary

- ✅ **Automatic checks**: Happens in background, doesn't slow you down
- ✅ **Smart notifications**: Minor updates don't interrupt, major updates ask first
- ✅ **Simple commands**: Just `sp upgrade` to update everything
- ✅ **Configurable**: Turn checks off if you want
- ✅ **Safe**: Never breaks your setup, Jupyter always starts
