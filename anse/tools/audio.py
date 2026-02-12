"""
Audio recording tool - microphone access for agents.
"""
import asyncio
import os
import uuid
from typing import Dict, Any


def _blocking_record_audio(
    duration: float,
    samplerate: int,
    channels: int,
    out_dir: str,
) -> Dict[str, Any]:
    """Blocking implementation of audio recording."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as e:
        return {"error": f"missing_dependency: {str(e)}"}
    
    if duration <= 0 or duration > 60:
        return {"error": "invalid_duration", "message": "Duration must be between 0 and 60 seconds"}
    
    try:
        os.makedirs(out_dir, exist_ok=True)
        
        # Generate unique filename
        audio_id = uuid.uuid4().hex
        fname = f"{audio_id}.wav"
        path = os.path.join(out_dir, fname)
        
        # Record audio
        recording = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=channels,
            dtype='int16'
        )
        sd.wait()  # Wait for recording to complete
        
        # Save to file
        sf.write(path, recording, samplerate)
        
        return {
            "audio_id": audio_id,
            "path": path,
            "duration": duration,
            "samplerate": samplerate,
            "channels": channels,
        }
    except Exception as e:
        return {"error": "recording_failed", "message": str(e)}


async def record_audio(
    duration: float = 2.0,
    samplerate: int = 16000,
    channels: int = 1,
    out_dir: str = "/tmp/anse",
) -> Dict[str, Any]:
    """
    Record audio from the default microphone.
    
    Non-blocking wrapper that runs the blocking sounddevice call in a thread pool.
    
    Args:
        duration: Recording duration in seconds
        samplerate: Sample rate in Hz (default: 16000)
        channels: Number of audio channels (default: 1 for mono)
        out_dir: Output directory for saved audio files
        
    Returns:
        Dict containing audio_id and path, or error information
    """
    return await asyncio.to_thread(_blocking_record_audio, duration, samplerate, channels, out_dir)


def _blocking_list_audio_devices() -> Dict[str, Any]:
    """Blocking implementation of listing audio devices."""
    try:
        import sounddevice as sd
    except ImportError:
        return {"error": "sounddevice not installed"}
    
    try:
        devices = sd.query_devices()
        
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    "id": i,
                    "name": device['name'],
                    "channels": device['max_input_channels'],
                    "samplerate": device['default_samplerate'],
                })
        
        return {
            "devices": input_devices,
            "count": len(input_devices),
            "default": sd.default.device[0] if sd.default.device else None,
        }
    except Exception as e:
        return {"error": str(e)}


async def list_audio_devices() -> Dict[str, Any]:
    """
    List available audio input devices.
    
    Non-blocking wrapper that runs the blocking sounddevice call in a thread pool.
    
    Returns:
        Dict containing list of available audio devices
    """
    return await asyncio.to_thread(_blocking_list_audio_devices)
