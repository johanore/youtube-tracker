"""
automation.py
-----------
Main entry point for the YouTube tracker automation system.
Runs both upload logging and analytics pulling on a schedule.

Usage:
    python automation.py          # Run with schedule (forever)
    python automation.py --once   # Run each task once
    python automation.py --status # Show system status
"""

import sys
import argparse
from datetime import datetime
import time

from config import ScheduleConfig, validate_config
from logger import setup_logging, get_logger, cleanup_old_logs
from scheduler import get_scheduler
from status_dashboard import get_dashboard, report_task_start, report_task_success, report_task_error

# Import the original scripts (refactored)
from yt_upload_logger import run_upload_logger
from yt_analytics_pull import run_analytics_pull

logger = setup_logging()
log = get_logger("automation")

def task_upload_logger():
    """Wrapper for upload logger task"""
    task_name = "upload_logger"
    report_task_start(task_name)
    try:
        result = run_upload_logger()
        report_task_success(task_name, "New uploads detected and logged", result)
    except Exception as e:
        report_task_error(task_name, str(e))
        log.error(f"Upload logger failed: {e}", exc_info=True)

def task_analytics_pull():
    """Wrapper for analytics pull task"""
    task_name = "analytics_pull"
    report_task_start(task_name)
    try:
        result = run_analytics_pull()
        report_task_success(task_name, "Analytics updated", result)
    except Exception as e:
        report_task_error(task_name, str(e))
        log.error(f"Analytics pull failed: {e}", exc_info=True)

def initialize_scheduler():
    """Set up all scheduled tasks"""
    scheduler = get_scheduler()
    
    # Register upload logger task
    if ScheduleConfig.UPLOAD_LOGGER_ENABLED:
        scheduler.add_task(
            name="upload_logger",
            callback=task_upload_logger,
            schedule_time=ScheduleConfig.UPLOAD_LOGGER_TIME,
            enabled=True,
        )
        log.info(f"✓ Upload logger scheduled for {ScheduleConfig.UPLOAD_LOGGER_TIME} daily")
    
    # Register analytics pull task
    if ScheduleConfig.ANALYTICS_PULL_ENABLED:
        scheduler.add_task(
            name="analytics_pull",
            callback=task_analytics_pull,
            schedule_time=ScheduleConfig.ANALYTICS_PULL_TIME,
            schedule_days=ScheduleConfig.ANALYTICS_PULL_DAYS,
            enabled=True,
        )
        log.info(f"✓ Analytics pull scheduled for {ScheduleConfig.ANALYTICS_PULL_TIME} on days {ScheduleConfig.ANALYTICS_PULL_DAYS}")

def run_once():
    """Run each task once (for testing/manual runs)"""
    log.info("Running tasks once...")
    task_upload_logger()
    time.sleep(2)
    task_analytics_pull()
    log.info("Done.")

def run_scheduled():
    """Run the scheduler continuously"""
    log.info("=" * 60)
    log.info("YouTube Tracker Automation System Started")
    log.info("=" * 60)
    
    initialize_scheduler()
    scheduler = get_scheduler()
    
    # Log initial status
    dashboard = get_dashboard()
    log.info(dashboard.get_summary())
    
    scheduler.start()
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(60)
            # Periodic cleanup
            if int(datetime.now().timestamp()) % 3600 == 0:  # Every hour
                cleanup_old_logs()
                dashboard.set_health("HEALTHY")
    
    except KeyboardInterrupt:
        log.info("\n" + "=" * 60)
        log.info("Shutting down gracefully...")
        log.info("=" * 60)
        scheduler.stop()
        log.info("Automation stopped.")

def show_status():
    """Display current system status"""
    dashboard = get_dashboard()
    print(dashboard.get_summary())
    
    scheduler = get_scheduler()
    print("\n=== Scheduled Tasks ===")
    for task_name, status in scheduler.get_status().items():
        print(f"\n{task_name}:")
        for key, value in status.items():
            print(f"  {key}: {value}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="YouTube Tracker Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automation.py              # Run scheduled tasks (forever)
  python automation.py --once       # Run each task once
  python automation.py --status     # Show system status
        """,
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run each task once and exit",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and exit",
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    errors = validate_config()
    if errors:
        log.error("Configuration errors:")
        for error in errors:
            log.error(f"  • {error}")
        sys.exit(1)
    
    # Execute requested action
    if args.status:
        show_status()
    elif args.once:
        run_once()
    else:
        run_scheduled()

if __name__ == "__main__":
    main()
