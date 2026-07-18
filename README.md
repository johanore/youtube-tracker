# YouTube Tracker Automation System

**Simple but effective AI-automated system** for tracking YouTube uploads and analytics with zero manual intervention.

## 🎯 What It Does

Two powerful scripts work together on **an automatic schedule**:

1. **Upload Logger** (`yt_upload_logger.py`)
   - Auto-detects new videos on your channel
   - Adds them to the spreadsheet with Title, Upload Date, Video ID
   - You fill in the Style Variant Tag (creative decision only)
   - Runs daily at **9 AM**

2. **Analytics Pull** (`yt_analytics_pull.py`)
   - Pulls real YouTube Analytics data (views, retention %, subs gained)
   - Updates only videos 14+ days old (when data is reliable)
   - Runs every **Monday at 10 AM**

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up OAuth (one-time, ~10 min)
Follow [YOUTUBE_SETUP-1.md](YOUTUBE_SETUP-1.md) to:
- Create a Google Cloud project
- Enable YouTube APIs
- Download `client_secret.json`

### 3. Place your spreadsheet
```
data/
  └── AiOre_Prompt_Variant_Tracker.xlsx
```

### 4. Start the automation
```bash
python automation.py
```

The system runs **forever**, checking the schedule every minute. Just leave it running.

## 📋 How to Use

### Run on a schedule (default, recommended)
```bash
python automation.py
```

### Run tasks once (for testing)
```bash
python automation.py --once
```

### Check system status
```bash
python automation.py --status
```

Output:
```
=== YouTube Tracker Status ===
Health: HEALTHY
Last updated: 2026-07-18T14:32:45.123456

Recent tasks:
  ✓ upload_logger: success
     Found 2 new videos
  ✓ analytics_pull: success
     Updated 3 videos
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# When to run tasks
ScheduleConfig.UPLOAD_LOGGER_TIME = time(hour=9, minute=0)      # 9 AM daily
ScheduleConfig.ANALYTICS_PULL_TIME = time(hour=10, minute=0)    # 10 AM Mondays
ScheduleConfig.ANALYTICS_PULL_DAYS = [0]                        # 0=Monday

# Minimum video age before pulling analytics
AnalyticsConfig.MIN_DAYS_OLD = 14

# Logging
LoggingConfig.LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LoggingConfig.LOG_RETENTION_DAYS = 30

# Feature flags
FEATURES["AUTO_SCHEDULE"] = True    # Enable/disable scheduling
FEATURES["HEALTH_CHECKS"] = True    # Monitor system health
FEATURES["AUTO_RETRY"] = True       # Retry failed tasks
```

## 📊 System Architecture

```
automation.py          Main entry point
├── scheduler.py       Task orchestration (no cron needed)
├── logger.py          Centralized logging
├── status_dashboard.py Real-time monitoring
└── config.py          All settings in one place
    ├── yt_upload_logger.py
    └── yt_analytics_pull.py
```

## 📁 Files & Directories

```
.
├── config.py                    # Central configuration
├── automation.py                # Main orchestrator
├── scheduler.py                 # Task scheduling engine
├── logger.py                    # Logging system
├── status_dashboard.py          # Health monitoring
├── yt_upload_logger.py          # Auto-detect uploads
├── yt_analytics_pull.py         # Pull analytics
├── requirements.txt             # Python dependencies
├── client_secret.json           # OAuth credentials (create via setup)
├── token.json                   # Auth token (auto-created)
├── logs/                        # System logs
│   ├── tracker.log              # Main log file (rotating)
│   ├── tasks.jsonl              # Task events (JSON)
│   └── status.json              # Current system status
└── data/
    └── AiOre_Prompt_Variant_Tracker.xlsx  # Your spreadsheet
```

## 📝 Logs

All activity is logged automatically:

```bash
# View main log (human-readable)
cat logs/tracker.log

# View task events (JSON, machine-readable)
cat logs/tasks.jsonl | jq

# View current status
cat logs/status.json | jq
```

## 🛡️ Error Handling

The system is **resilient by design**:

- ✅ Auto-retries failed API calls (up to 3 times)
- ✅ Graceful error logging (no crashes)
- ✅ Health status degradation (self-healing)
- ✅ Old logs cleaned up automatically
- ✅ Status dashboard tracks all events

If something fails:
1. Check `logs/tracker.log`
2. Run `python automation.py --status`
3. Review `logs/status.json`

## ⚙️ What's Different from Manual Scripts

| Feature | Before | Now |
|---------|--------|-----|
| Manual trigger | Every run | Automatic daily/weekly |
| Error handling | Script exits | Auto-retry + logging |
| Monitoring | Terminal output | JSON status file + logs |
| Scheduling | Cron/Task Scheduler | Pure Python, cross-platform |
| Configuration | Hard-coded | Single `config.py` file |
| Logging | Minimal | Comprehensive with rotation |

## 🚀 Running Forever (Recommended)

For a personal project like this, keep it running in the background:

### On Mac (LaunchAgent)
Create `~/Library/LaunchAgents/com.youtube.tracker.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.tracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/automation.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.youtube.tracker.plist
launchctl start com.youtube.tracker
```

### On Linux (systemd)
Create `/etc/systemd/user/youtube-tracker.service`:
```ini
[Unit]
Description=YouTube Tracker Automation
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user enable youtube-tracker.service
systemctl --user start youtube-tracker.service
```

### On Windows (Task Scheduler)
- Open Task Scheduler
- Create Basic Task
- Trigger: On a schedule
- Action: `python C:\path\to\automation.py`
- Settings: "Run task as soon as possible after a scheduled start is missed"

## 🎓 How It Works (Internals)

### Scheduling Engine
The `scheduler.py` module:
- Registers tasks with times and recurrence
- Runs a background thread checking every 60 seconds
- Calculates next run times dynamically
- No external cron or system services needed

### Task Wrapper
`automation.py` provides wrappers that:
- Report task start/end to status dashboard
- Catch exceptions and log them
- Update health status
- Return results for logging

### Logging Pipeline
`logger.py` sends events to:
- **Console**: Human-readable, INFO+ level
- **tracker.log**: Rotating file, all levels
- **tasks.jsonl**: JSON event stream, machine-readable

## 🔐 Security Notes

- `client_secret.json` and `token.json` are **private** — never commit to Git
- Add them to `.gitignore` (done for you)
- OAuth token is stored locally and refreshed automatically
- No data leaves your machine except API calls to Google

## 📞 Troubleshooting

### "No channel found for this authenticated account"
- You're not logged into the YouTube channel's Google account
- Run `python automation.py --once` to trigger re-auth

### "Sheet 'YT Track Log' not found"
- Spreadsheet doesn't exist or is named differently
- Ensure `data/AiOre_Prompt_Variant_Tracker.xlsx` exists

### "Tasks running but no new uploads detected"
- API quota might be exhausted (unlikely at 1-3 calls/week)
- Check `logs/tracker.log` for API errors

### "Want to test without waiting for schedule"
- Run `python automation.py --once` to execute tasks immediately

## 📈 Next Steps

1. ✅ Set up OAuth and create spreadsheet
2. ✅ Start automation: `python automation.py`
3. ✅ Check status regularly: `python automation.py --status`
4. 📊 Monitor `logs/status.json` in a dashboard (optional)
5. 🔔 Add Slack/email alerts (extend `status_dashboard.py`)

## 📄 License

Personal use — modify and extend as needed.

---

**Built with simplicity and reliability in mind.** No cron complexity, no cloud services, no magic. Just Python.
