"""
status_dashboard.py
-------------------
Real-time system health monitoring and status reporting.
Writes status.json for monitoring what the automation is doing.
"""

import json
from datetime import datetime
from pathlib import Path
from config import LOG_DIR, DATA_DIR
from logger import get_logger

logger = get_logger("status")

STATUS_FILE = LOG_DIR / "status.json"

class StatusDashboard:
    """Tracks system health and task completion"""
    
    def __init__(self):
        self.status = {
            "system_started": datetime.utcnow().isoformat(),
            "last_update": None,
            "tasks": {},
            "health": "HEALTHY",
            "errors": [],
        }
        self.load_or_create()
    
    def load_or_create(self):
        """Load existing status or create new one"""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r") as f:
                    self.status = json.load(f)
                logger.debug(f"Loaded existing status from {STATUS_FILE}")
            except Exception as e:
                logger.warning(f"Could not load status file: {e}, creating new")
                self._save()
        else:
            self._save()
    
    def update_task(self, task_name, status, message="", details=None):
        """Update status for a specific task"""
        self.status["tasks"][task_name] = {
            "status": status,  # "running", "success", "error", "skipped"
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }
        self.status["last_update"] = datetime.utcnow().isoformat()
        self._save()
        logger.info(f"Task '{task_name}' status: {status}")
    
    def add_error(self, error_msg):
        """Log an error to the status"""
        self.status["errors"].append({
            "message": error_msg,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.status["health"] = "DEGRADED"
        self._save()
        logger.error(f"Status error: {error_msg}")
    
    def set_health(self, health_state):
        """Set overall system health: HEALTHY, DEGRADED, or CRITICAL"""
        self.status["health"] = health_state
        self.status["last_update"] = datetime.utcnow().isoformat()
        self._save()
    
    def get_summary(self):
        """Return human-readable summary"""
        lines = [
            "=== YouTube Tracker Status ===",
            f"Health: {self.status['health']}",
            f"Last updated: {self.status['last_update']}",
            "",
            "Recent tasks:",
        ]
        
        for task_name, task_status in list(self.status["tasks"].items())[-5:]:
            status = task_status["status"]
            emoji = "✓" if status == "success" else "✗" if status == "error" else "⊘"
            lines.append(f"  {emoji} {task_name}: {status}")
            if task_status["message"]:
                lines.append(f"     {task_status['message']}")
        
        if self.status["errors"]:
            lines.append(f"\nRecent errors ({len(self.status['errors'])})")
            for error in self.status["errors"][-3:]:
                lines.append(f"  • {error['message']}")
        
        return "\n".join(lines)
    
    def _save(self):
        """Write status to JSON file"""
        try:
            with open(STATUS_FILE, "w") as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

# Global instance
_dashboard = None

def get_dashboard():
    """Get or create the global status dashboard"""
    global _dashboard
    if _dashboard is None:
        _dashboard = StatusDashboard()
    return _dashboard

def report_task_start(task_name):
    """Report that a task is starting"""
    dashboard = get_dashboard()
    dashboard.update_task(task_name, "running", "Task in progress")

def report_task_success(task_name, message="", details=None):
    """Report that a task completed successfully"""
    dashboard = get_dashboard()
    dashboard.update_task(task_name, "success", message, details)

def report_task_error(task_name, error_message, details=None):
    """Report that a task failed"""
    dashboard = get_dashboard()
    dashboard.update_task(task_name, "error", error_message, details)
    dashboard.add_error(f"{task_name}: {error_message}")

def report_task_skip(task_name, reason=""):
    """Report that a task was skipped"""
    dashboard = get_dashboard()
    dashboard.update_task(task_name, "skipped", reason)
