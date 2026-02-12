"""
Tests for EngineCore and integration testing.
"""
import pytest
import asyncio
import json
import websockets
from anse.engine_core import EngineCore


@pytest.fixture
def engine():
    """Create an engine instance for testing."""
    core = EngineCore()
    return core


def test_engine_initialization():
    """Test that engine initializes properly."""
    core = EngineCore()
    
    assert core.tools is not None
    assert core.world is not None
    assert core.scheduler is not None
    assert core.bridge is not None
    assert core.permissions is not None
    
    # Check that tools were registered
    stats = core.get_stats()
    assert len(stats["tools"]) > 0
    assert "capture_frame" in stats["tools"]
    assert "record_audio" in stats["tools"]
    assert "say" in stats["tools"]


def test_list_tools(engine):
    """Test listing tools."""
    tools = engine.tools.list_tools()
    
    assert isinstance(tools, dict)
    assert "capture_frame" in tools
    assert "say" in tools
    assert "record_audio" in tools
    assert len(tools) == 6  # 6 built-in tools


def test_get_tool_info(engine):
    """Test retrieving info for a specific tool."""
    info = engine.tools.get_tool_info("say")
    
    assert info is not None
    assert "description" in info
    assert "schema" in info


def test_tool_registry_has_tools(engine):
    """Test tool registry operations."""
    assert engine.tools.has_tool("capture_frame")
    assert engine.tools.has_tool("say")
    assert not engine.tools.has_tool("nonexistent_tool")


def test_world_model_functionality(engine):
    """Test that world model stores events."""
    initial_stats = engine.world.get_stats()
    initial_count = initial_stats.get("total_events", 0)
    
    # Add an event
    event = {
        "agent_id": "test-agent",
        "type": "test_event",
        "data": "test"
    }
    engine.world.append_event(event)
    
    # Verify event was added
    new_stats = engine.world.get_stats()
    assert new_stats["total_events"] > initial_count


def test_scheduler_rate_limits(engine):
    """Test scheduler rate limit configuration."""
    stats = engine.scheduler.get_stats()
    
    assert "rate_limits" in stats
    assert "capture_frame" in stats["rate_limits"]
    assert "record_audio" in stats["rate_limits"]
    assert "say" in stats["rate_limits"]
    
    # Check limits are set correctly
    assert stats["rate_limits"]["capture_frame"]["limit"] == 30
    assert stats["rate_limits"]["record_audio"]["limit"] == 10
    assert stats["rate_limits"]["say"]["limit"] == 20
