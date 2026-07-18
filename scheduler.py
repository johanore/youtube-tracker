"""
scheduler.py
------------
Simple but powerful task scheduler for automation.
Runs tasks on a schedule without cron or external dependencies.
"""

import time
import threading
from datetime import datetime, timedelta
from config import ScheduleConfig
from logger import get_logger

logger = get_logger("scheduler")

class Task:
    """A scheduled task that runs at specific times"""
    
    def __init__(self, name, callback, schedule_time=None, schedule_days=None, enabled=True):
        """
        Args:
            name: Task identifier (e.g. 'upload_logger')
            callback: Function to call when task runs
            schedule_time: datetime.time object (e.g., time(9, 0) for 9 AM)
            schedule_days: List of weekdays (0=Monday, 6=Sunday), None=every day
            enabled: Whether this task is active
        """
        self.name = name
        self.callback = callback
        self.schedule_time = schedule_time
        self.schedule_days = schedule_days or list(range(7))  # Every day by default
        self.enabled = enabled
        self.last_run = None
        self.next_run = self._calculate_next_run()
    
    def _calculate_next_run(self):
        """Calculate when this task should next run"""
        if not self.schedule_time:
            return None
        
        now = datetime.now()
        scheduled = now.replace(
            hour=self.schedule_time.hour,
            minute=self.schedule_time.minute,
            second=0,
            microsecond=0,
        )
        
        # If scheduled time has passed today, schedule for tomorrow
        if scheduled <= now:
            scheduled += timedelta(days=1)
        
        # Find next matching weekday
        while scheduled.weekday() not in self.schedule_days:
            scheduled += timedelta(days=1)
        
        return scheduled
    
    def should_run(self):
        """Check if this task should run now"""
        if not self.enabled or not self.next_run:
            return False
        
        now = datetime.now()
        return now >= self.next_run
    
    def run(self):
        """Execute this task and update schedule"""
        logger.info(f"Running task: {self.name}")
        try:
            self.callback()
            self.last_run = datetime.now()
            logger.info(f"Task completed: {self.name}")
        except Exception as e:
            logger.error(f"Task failed: {self.name} - {e}", exc_info=True)
        finally:
            self.next_run = self._calculate_next_run()

class Scheduler:
    """Main scheduler that manages and runs all tasks"""
    
    def __init__(self, check_interval_seconds=60):
        """
        Args:
            check_interval_seconds: How often to check if tasks need to run
        """
        self.tasks = {}
        self.check_interval = check_interval_seconds
        self.running = False
        self.thread = None
    
    def register_task(self, task):
        """Register a task with the scheduler"""
        self.tasks[task.name] = task
        logger.info(f"Registered task: {task.name}")
    
    def add_task(self, name, callback, schedule_time=None, schedule_days=None, enabled=True):
        """Convenience method to create and register a task in one call"""
        task = Task(name, callback, schedule_time, schedule_days, enabled)
        self.register_task(task)
        return task
    
    def start(self):
        """Start the scheduler (runs in background thread)"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"Scheduler started (check interval: {self.check_interval}s)")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Main scheduler loop (runs in background thread)"""
        logger.debug("Scheduler loop started")
        
        while self.running:
            try:
                now = datetime.now()
                
                # Check each task
                for task in self.tasks.values():
                    if task.should_run():
                        task.run()
                
                # Log next scheduled tasks (every 10 checks)
                if int(now.timestamp()) % (self.check_interval * 10) == 0:
                    self._log_next_tasks()
                
                # Sleep before next check
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def _log_next_tasks(self):
        """Log upcoming scheduled tasks (for debugging)"""
        upcoming = sorted(
            [(t.name, t.next_run) for t in self.tasks.values() if t.next_run],
            key=lambda x: x[1],
        )[:3]
        
        if upcoming:
            msg = " | ".join([f"{name} @ {run_time.strftime('%H:%M')}" for name, run_time in upcoming])
            logger.debug(f"Next scheduled: {msg}")
    
    def get_status(self):
        """Get current status of all tasks"""
        status = {}
        for name, task in self.tasks.items():
            status[name] = {
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "schedule": f"{task.schedule_time} on days {task.schedule_days}" if task.schedule_time else "manual",
            }
        return status

# Global scheduler instance
_scheduler = None

def get_scheduler():
    """Get or create the global scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler(check_interval_seconds=60)
    return _scheduler
