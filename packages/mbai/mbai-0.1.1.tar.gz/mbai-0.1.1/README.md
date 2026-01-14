# Atlas Agent

**AI-powered server monitoring that automatically fixes issues.**

Stop getting woken up at 3am. Atlas monitors your servers 24/7 and automatically fixes common problems while you sleep.

## Quick Start

```bash
pip install mbai
sudo mbai setup
sudo mbai start
```

That's it. No API key required. 30-day free trial.

## What Atlas Monitors

- **Disk usage** - Auto-cleans logs, temp files, apt cache when disk is full
- **Memory** - Identifies memory hogs, restarts problematic services
- **CPU** - Detects runaway processes
- **Nginx errors** - Auto-restarts upstream services on 502 errors
- **Service crashes** - Automatically restarts failed services
- **SSL certificates** - Runs certbot renewal before expiry

## Commands

```bash
sudo mbaisetup      # Download binary, generate config
sudo mbaistart      # Start monitoring daemon
sudo mbaistop       # Stop daemon
sudo mbaistatus     # Check status and trial info
sudo mbailogs       # View recent logs
sudo mbaiclaim      # Open dashboard to claim this server
sudo mbaiuninstall  # Remove Atlas
```

## How It Works

1. **Install** - Downloads a small binary for your platform
2. **Discover** - Auto-detects running services (nginx, postgres, redis, docker)
3. **Monitor** - Watches logs and metrics every 30 seconds
4. **Fix** - When issues are detected, Atlas diagnoses and fixes them automatically
5. **Notify** - You get notified of what was fixed (not woken up to fix it yourself)

## Requirements

- Linux or macOS
- Root/sudo access (required for monitoring and fixing)
- Python 3.8+

## Trial

- **30 days free** - No credit card required
- After trial, claim your server at the dashboard to continue
- $29/month per server after trial

## Links

- Website: https://managedbyai.dev
- Dashboard: https://managedbyai.dev/dashboard
- Documentation: https://managedbyai.dev/install.html

## License

MIT
