"""
Unit tests for individual tools.
"""
import pytest
import asyncio
import os
import tempfile
from anse.tools.video import capture_frame, list_cameras
from anse.tools.audio import record_audio, list_audio_devices
from anse.tools.tts import say, get_voices


def test_list_cameras():
    """Test camera listing (may return empty if no cameras)."""
    result = asyncio.run(list_cameras())
    
    assert "cameras" in result
    assert "count" in result
    assert isinstance(result["cameras"], list)
    assert result["count"] == len(result["cameras"])


def test_capture_frame_no_camera():
    """Test frame capture when camera might not be available."""
    async def _test():
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await capture_frame(camera_id=0, out_dir=tmpdir)
            
            # Either succeeds with frame data or fails gracefully
            if "error" in result:
                assert result["error"] in ["camera_unavailable", "capture_failed"]
            else:
                assert "frame_id" in result
                assert "path" in result
                assert os.path.exists(result["path"])
    
    asyncio.run(_test())


def test_list_audio_devices():
    """Test audio device listing."""
    result = asyncio.run(list_audio_devices())
    
    # May fail if sounddevice not installed
    if "error" in result:
        assert "not installed" in result["error"]
    else:
        assert "devices" in result
        assert "count" in result
        assert isinstance(result["devices"], list)


def test_record_audio_invalid_duration():
    """Test audio recording with invalid duration."""
    result = asyncio.run(record_audio(duration=-1))
    
    assert "error" in result
    assert result["error"] == "invalid_duration"


def test_record_audio_too_long():
    """Test audio recording with excessive duration."""
    result = asyncio.run(record_audio(duration=100))
    
    assert "error" in result
    assert result["error"] == "invalid_duration"


def test_say_empty_text():
    """Test TTS with empty text."""
    result = asyncio.run(say(""))
    
    assert "error" in result
    assert result["error"] == "empty_text"


def test_say_text_too_long():
    """Test TTS with excessively long text."""
    long_text = "x" * 1001

def test_say_text_too_long():
    """Test TTS with text that's too long."""
    long_text = "x" * 1001  # Over 1000 chars
    result = asyncio.run(say(long_text))
    
    assert "error" in result
    assert result["error"] == "text_too_long"


def test_say_valid_text():
    """Test TTS with valid text."""
    result = asyncio.run(say("Hello test", rate=200, volume=0.5))
    
    # May fail if pyttsx3 not available or audio system not available
    if "error" in result:
        assert "not installed" in result["error"] or "speech_failed" in result["error"]
    else:
        assert result["spoken"] is True
        assert result["text"] == "Hello test"
        assert result["rate"] == 200
        assert result["volume"] == 0.5


def test_get_voices():
    """Test TTS voice listing."""
    result = asyncio.run(get_voices())
    
    # May fail if pyttsx3 not installed
    if "error" in result:
        assert "not installed" in result["error"]
    else:
        assert "voices" in result
        assert "count" in result
        assert isinstance(result["voices"], list)


# Integration test for tool registry
def test_tool_registry_integration():
    """Test tools work with ToolRegistry."""
    from anse.tool_registry import ToolRegistry
    
    registry = ToolRegistry()
    
    # Register a test tool
    registry.register(
        name="test_say",
        func=say,
        schema={"type": "object", "properties": {"text": {"type": "string"}}},
        description="Test TTS",
        sensitivity="low"
    )
    
    # Verify registration
    assert registry.has_tool("test_say")
    
    # Call the tool
    async def _call():
        return await registry.call("test_say", {"text": "test"})
    
    result = asyncio.run(_call())
    
    # Should either succeed or fail gracefully
    assert isinstance(result, dict)
