"""
Health check and status monitoring for ANSE engine.

Provides system status, uptime, resource usage, and recent error tracking.
"""

import asyncio
import psutil
import platform
import time
from datetime import datetime
from typing import Dict, List, Optional
import json


class HealthMonitor:
    """Tracks engine health metrics and system status."""

    def __init__(self):
        self.start_time = time.time()
        self.recent_errors: List[Dict] = []
        self.max_errors = 10
        self.last_event_time: Optional[float] = None
        self.event_count = 0
        self.process = psutil.Process()

    def record_event(self, event_type: str = "call"):
        """Record that an event occurred."""
        self.last_event_time = time.time()
        self.event_count += 1

    def record_error(self, tool_name: str, error: str, severity: str = "warning"):
        """Record an error for monitoring."""
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "error": error,
            "severity": severity,  # "info", "warning", "error"
        }
        self.recent_errors.append(error_record)
        # Keep only recent errors
        if len(self.recent_errors) > self.max_errors:
            self.recent_errors.pop(0)

    def get_status(self) -> Dict:
        """Return current health status as JSON-serializable dict."""
        uptime_seconds = time.time() - self.start_time
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent(interval=0.1)

        return {
            "status": "running",
            "uptime_seconds": int(uptime_seconds),
            "uptime_readable": self._format_uptime(uptime_seconds),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "memory_mb": round(memory_info.rss / (1024 * 1024), 1),
            "cpu_percent": round(cpu_percent, 1),
            "event_count": self.event_count,
            "last_event_time": (
                datetime.fromtimestamp(self.last_event_time).isoformat()
                if self.last_event_time
                else None
            ),
            "recent_errors": self.recent_errors,
            "error_count": len(self.recent_errors),
        }

    def get_diagnostics(self) -> Dict:
        """Return detailed diagnostics for troubleshooting."""
        status = self.get_status()
        
        try:
            disk_usage = psutil.disk_usage("/")
            disk_info = {
                "total_gb": round(disk_usage.total / (1024**3), 1),
                "used_gb": round(disk_usage.used / (1024**3), 1),
                "free_gb": round(disk_usage.free / (1024**3), 1),
                "percent_used": disk_usage.percent,
            }
        except Exception as e:
            disk_info = {"error": str(e)}

        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_info = {
                "count": cpu_count,
                "frequency_mhz": round(cpu_freq.current) if cpu_freq else None,
            }
        except Exception as e:
            cpu_info = {"error": str(e)}

        return {
            **status,
            "disk": disk_info,
            "cpu": cpu_info,
            "pid": self.process.pid,
        }

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def initialize_health_monitor() -> HealthMonitor:
    """Initialize the global health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


async def get_health_status() -> Dict:
    """Get current health status (async wrapper)."""
    monitor = get_health_monitor()
    return monitor.get_status()


async def get_diagnostics() -> Dict:
    """Get detailed diagnostics (async wrapper)."""
    monitor = get_health_monitor()
    return monitor.get_diagnostics()
