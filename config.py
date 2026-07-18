"""
config.py
---------
Centralized configuration for YouTube tracker automation system.
All settings in one place — easy to adjust without touching code.
"""

import os
from pathlib import Path
from datetime import time

# Paths
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
TRACKER_FILE = DATA_DIR / "AiOre_Prompt_Variant_Tracker.xlsx"

# Create directories if they don't exist
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# API & Auth
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"
SHEET_NAME = "YT Track Log"

# YouTube API settings
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
UPLOADS_FETCH_LIMIT = 25  # Videos per API call
MAX_ROWS_IN_TRACKER = 50  # Spreadsheet capacity

# Column mapping (1-indexed, matches spreadsheet)
COLUMNS = {
    "TITLE": 1,
    "UPLOAD_DATE": 2,
    "STYLE_TAG": 3,
    "VIDEO_ID": 4,
    "VIEWS": 7,
    "RETENTION": 8,
    "SUBS": 9,
}
DATA_ROW_START = 5
DATA_ROW_END = 50

# Scheduling
class ScheduleConfig:
    """When to run each automation task"""
    # Run upload logger every day at 9 AM
    UPLOAD_LOGGER_TIME = time(hour=9, minute=0)
    UPLOAD_LOGGER_ENABLED = True
    
    # Run analytics pull every Monday at 10 AM (after videos have 7+ days of data)
    ANALYTICS_PULL_TIME = time(hour=10, minute=0)
    ANALYTICS_PULL_DAYS = [0]  # 0=Monday, 1=Tuesday, etc.
    ANALYTICS_PULL_ENABLED = True
    
    # Check system health every 6 hours
    HEALTH_CHECK_INTERVAL_HOURS = 6

# Analytics
class AnalyticsConfig:
    """YouTube Analytics API settings"""
    # Don't pull stats for videos younger than this
    MIN_DAYS_OLD = 14
    # Retry failed API calls up to this many times
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5

# Logging & Alerts
class LoggingConfig:
    """Logging and error notification settings"""
    # Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    LEVEL = "INFO"
    
    # Keep logs for this many days before cleanup
    LOG_RETENTION_DAYS = 30
    
    # Alert on errors (set email/webhook later)
    ALERT_ON_ERROR = True
    
    # Log file format
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Notifications (optional — extend with your own email/Slack/Discord)
class NotificationConfig:
    """Error & status notifications"""
    ENABLED = False  # Set to True if you add email/Slack
    
    # Placeholder for email config
    EMAIL_ENABLED = False
    EMAIL_TO = ""
    
    # Placeholder for webhook (Slack/Discord/etc.)
    WEBHOOK_ENABLED = False
    WEBHOOK_URL = ""

# Feature flags
FEATURES = {
    "AUTO_SCHEDULE": True,          # Run on a schedule
    "HEALTH_CHECKS": True,          # Monitor system health
    "AUTO_RETRY": True,             # Retry failed tasks
    "DETAILED_LOGGING": True,       # Extra debug info
    "STATUS_DASHBOARD": True,       # Generate status.json
}

# Performance tuning
PERFORMANCE = {
    "CACHE_TOKEN_SECONDS": 3600,    # Reuse auth token for 1 hour
    "MAX_PARALLEL_TASKS": 1,        # Run tasks sequentially (safer)
    "TIMEOUT_SECONDS": 300,         # Kill tasks after 5 min
}

def validate_config():
    """Check that required files exist before running"""
    errors = []
    
    if not CLIENT_SECRET_FILE.exists():
        errors.append(f"Missing {CLIENT_SECRET_FILE} — run YOUTUBE_SETUP first")
    
    if not TRACKER_FILE.exists():
        errors.append(f"Missing {TRACKER_FILE} — ensure spreadsheet is in {DATA_DIR}")
    
    return errors
