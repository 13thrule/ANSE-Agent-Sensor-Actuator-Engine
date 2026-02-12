"""
Tests for health monitoring and diagnostics.
"""

import asyncio
import pytest

from anse.health import HealthMonitor, initialize_health_monitor, get_health_monitor


class TestHealthMonitor:
    """Test health monitoring functionality."""

    def test_initialize(self):
        """Test health monitor initialization."""
        monitor = HealthMonitor()
        assert monitor.start_time > 0
        assert monitor.event_count == 0
        assert len(monitor.recent_errors) == 0

    def test_record_event(self):
        """Test recording events."""
        monitor = HealthMonitor()
        
        monitor.record_event("call")
        assert monitor.event_count == 1
        assert monitor.last_event_time is not None
        
        monitor.record_event("call")
        assert monitor.event_count == 2

    def test_record_error(self):
        """Test recording errors."""
        monitor = HealthMonitor()
        
        monitor.record_error("capture_frame", "Camera not found", severity="error")
        assert len(monitor.recent_errors) == 1
        assert monitor.recent_errors[0]["tool"] == "capture_frame"
        assert monitor.recent_errors[0]["severity"] == "error"

    def test_recent_errors_limit(self):
        """Test that recent errors list respects max limit."""
        monitor = HealthMonitor()
        monitor.max_errors = 5
        
        for i in range(10):
            monitor.record_error(f"tool{i}", f"Error {i}")
        
        assert len(monitor.recent_errors) == 5
        # Should keep the last 5
        assert monitor.recent_errors[0]["tool"] == "tool5"

    def test_get_status(self):
        """Test getting health status."""
        monitor = HealthMonitor()
        monitor.record_event()
        
        status = monitor.get_status()
        
        assert status["status"] == "running"
        assert status["uptime_seconds"] >= 0
        assert status["version"] == "0.1.0"
        assert status["event_count"] == 1
        assert status["memory_mb"] > 0
        assert "timestamp" in status
        assert "python_version" in status

    def test_get_diagnostics(self):
        """Test getting detailed diagnostics."""
        monitor = HealthMonitor()
        
        diag = monitor.get_diagnostics()
        
        assert diag["status"] == "running"
        assert "disk" in diag
        assert "cpu" in diag
        assert "pid" in diag

    def test_format_uptime(self):
        """Test uptime formatting."""
        # Test seconds
        formatted = HealthMonitor._format_uptime(30)
        assert "30s" in formatted
        
        # Test minutes
        formatted = HealthMonitor._format_uptime(125)
        assert "2m" in formatted
        assert "5s" in formatted
        
        # Test hours
        formatted = HealthMonitor._format_uptime(3725)
        assert "1h" in formatted

    def test_global_monitor_instance(self):
        """Test global health monitor singleton."""
        monitor1 = get_health_monitor()
        monitor2 = get_health_monitor()
        
        assert monitor1 is monitor2

    def test_initialize_global_monitor(self):
        """Test initializing global monitor."""
        monitor = initialize_health_monitor()
        assert isinstance(monitor, HealthMonitor)
