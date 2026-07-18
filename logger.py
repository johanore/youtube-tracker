"""
logger.py
---------
Centralized logging system for YouTube tracker.
All events logged to both console and rotating file logs.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import LoggingConfig, LOG_DIR, LOG_RETENTION_DAYS

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing and analysis"""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    """Initialize logging system with file + console handlers"""
    logger = logging.getLogger("youtube_tracker")
    logger.setLevel(getattr(logging, LoggingConfig.LEVEL))
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LoggingConfig.LEVEL))
    console_formatter = logging.Formatter(LoggingConfig.LOG_FORMAT, LoggingConfig.DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating, JSON format for parsing)
    log_file = LOG_DIR / "tracker.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,              # Keep 5 backup files
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_formatter = logging.Formatter(LoggingConfig.LOG_FORMAT, LoggingConfig.DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Task-specific log file
    task_log_file = LOG_DIR / "tasks.jsonl"
    task_handler = RotatingFileHandler(
        task_log_file,
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=3,
    )
    task_handler.setLevel(logging.INFO)
    task_handler.setFormatter(JSONFormatter())
    task_logger = logging.getLogger("youtube_tracker.tasks")
    task_logger.addHandler(task_handler)
    
    return logger

def get_logger(name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"youtube_tracker.{name}")

def log_task_start(task_name):
    """Log the start of an automated task"""
    logger = get_logger("tasks")
    logger.info(f"Task started: {task_name}")
    return {
        "task": task_name,
        "start_time": datetime.utcnow().isoformat(),
    }

def log_task_end(task_context, status="success", details=None):
    """Log the end of an automated task"""
    logger = get_logger("tasks")
    task_context["end_time"] = datetime.utcnow().isoformat()
    task_context["status"] = status
    if details:
        task_context["details"] = details
    
    log_level = logging.ERROR if status == "error" else logging.INFO
    logger.log(log_level, f"Task ended: {task_context['task']}", extra=task_context)
    
    return task_context

def cleanup_old_logs():
    """Delete log files older than LOG_RETENTION_DAYS"""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=LoggingConfig.LOG_RETENTION_DAYS)
    
    for log_file in LOG_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff.timestamp():
            log_file.unlink()
            get_logger("cleanup").info(f"Deleted old log: {log_file}")
