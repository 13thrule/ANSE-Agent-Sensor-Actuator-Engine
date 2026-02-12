"""Simulated sensors for ANSE - deterministic, hardware-free testing."""

import asyncio
import io
import json
import hashlib
import struct
from typing import Optional, Tuple
from PIL import Image
import numpy as np


def _generate_procedural_frame(
    width: int = 640,
    height: int = 480,
    seed: int = 0,
) -> bytes:
    """
    Generate a deterministic procedural frame.
    
    Uses seeded random generation to produce reproducible frames.
    Includes patterns, gradients, and checkerboard for visual variation.
    
    Args:
        width: Frame width in pixels
        height: Frame height in pixels
        seed: Random seed for determinism
        
    Returns:
        JPEG-encoded frame as bytes
    """
    np.random.seed(seed)
    
    # Create RGB image
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add checkerboard pattern
    cell_size = max(1, seed % 20 + 10)
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            color_val = (((x // cell_size) + (y // cell_size)) % 2) * 128 + 64
            frame[y:y+cell_size, x:x+cell_size] = [color_val, color_val, color_val]
    
    # Add gradient overlay
    gradient = np.linspace(0, 255, width, dtype=np.uint8)
    for y in range(height):
        frame[y, :, 0] = np.minimum(frame[y, :, 0].astype(int) + gradient // 2, 255).astype(np.uint8)
    
    # Add noise based on seed
    noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    frame = np.minimum(frame.astype(int) + noise // 4, 255).astype(np.uint8)
    
    # Add seed indicator text in corner (as pixel pattern)
    for i, digit in enumerate(str(seed % 10)):
        x_offset = 10 + i * 8
        y_offset = 10
        if x_offset < width and y_offset < height:
            frame[y_offset:y_offset+4, x_offset:x_offset+4] = [255, 255, 255]
    
    # Encode to JPEG
    pil_image = Image.fromarray(frame, mode='RGB')
    jpeg_buffer = io.BytesIO()
    pil_image.save(jpeg_buffer, format='JPEG', quality=85)
    return jpeg_buffer.getvalue()


def _generate_procedural_audio(
    text: str,
    duration_sec: float = 5.0,
    seed: int = 0,
) -> bytes:
    """
    Generate deterministic audio.
    
    Creates a simple WAV file with tone and silence based on seed.
    
    Args:
        text: Text to "synthesize" (used for seed variation)
        duration_sec: Audio duration in seconds
        seed: Random seed for determinism
        
    Returns:
        WAV-encoded audio as bytes
    """
    samplerate = 16000
    num_samples = int(samplerate * duration_sec)
    
    # Use seed to determine tone
    np.random.seed(seed + hash(text) % 100000)
    frequency = 440 + (seed % 100)  # A4 + variation
    
    # Generate tone with modulation
    t = np.linspace(0, duration_sec, num_samples)
    
    # Modulate amplitude based on text length
    amplitude_envelope = np.linspace(0.5, 0.1, num_samples)
    
    # Generate simple sine wave with noise
    audio = (0.3 * amplitude_envelope * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    audio += 0.05 * np.random.randn(num_samples).astype(np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    
    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Write WAV file
    wav_buffer = io.BytesIO()
    
    # WAV header
    channels = 1
    bytes_per_sample = 2
    byte_rate = samplerate * channels * bytes_per_sample
    block_align = channels * bytes_per_sample
    
    # RIFF header
    wav_buffer.write(b'RIFF')
    wav_buffer.write(struct.pack('<I', 36 + num_samples * bytes_per_sample))
    wav_buffer.write(b'WAVE')
    
    # fmt subchunk
    wav_buffer.write(b'fmt ')
    wav_buffer.write(struct.pack('<I', 16))  # Subchunk1Size
    wav_buffer.write(struct.pack('<H', 1))   # AudioFormat (1 = PCM)
    wav_buffer.write(struct.pack('<H', channels))
    wav_buffer.write(struct.pack('<I', samplerate))
    wav_buffer.write(struct.pack('<I', byte_rate))
    wav_buffer.write(struct.pack('<H', block_align))
    wav_buffer.write(struct.pack('<H', 16))  # BitsPerSample
    
    # data subchunk
    wav_buffer.write(b'data')
    wav_buffer.write(struct.pack('<I', num_samples * bytes_per_sample))
    wav_buffer.write(audio_int16.tobytes())
    
    return wav_buffer.getvalue()


async def simulate_camera(
    camera_id: int = 0,
    width: int = 640,
    height: int = 480,
    seed: Optional[int] = None,
) -> dict:
    """
    Simulate camera capture with deterministic procedural frame.
    
    Same interface as real capture_frame tool. Enables offline testing
    and reproducible debugging.
    
    Args:
        camera_id: Virtual camera ID (unused, for compatibility)
        width: Frame width
        height: Frame height
        seed: Random seed for reproducibility (if None, uses counter)
        
    Returns:
        Frame metadata dict matching real capture_frame response
    """
    if seed is None:
        seed = simulate_camera.counter
        simulate_camera.counter += 1
    
    try:
        frame_bytes = _generate_procedural_frame(width, height, seed)
        
        return {
            "status": "success",
            "format": "jpeg",
            "width": width,
            "height": height,
            "frame_id": f"sim-frame-{seed}",
            "frame_bytes": frame_bytes,
            "metadata": {
                "simulated": True,
                "seed": seed,
                "camera_id": camera_id,
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Simulated frame generation failed: {e}"
        }


# Frame counter for auto-incrementing seed
simulate_camera.counter = 0


async def simulate_microphone(
    duration_sec: float = 2.0,
    samplerate: int = 16000,
    channels: int = 1,
    seed: Optional[int] = None,
) -> dict:
    """
    Simulate microphone recording with deterministic audio.
    
    Same interface as real record_audio tool. Generates synthetic audio
    for testing without requiring audio hardware.
    
    Args:
        duration_sec: Recording duration
        samplerate: Sample rate (for compatibility, uses 16000)
        channels: Number of channels (for compatibility, uses mono)
        seed: Random seed for reproducibility (if None, uses counter)
        
    Returns:
        Audio metadata dict matching real record_audio response
    """
    # Validate inputs
    if duration_sec < 0.1:
        return {
            "status": "error",
            "error": "duration_too_short",
            "message": f"Duration must be at least 0.1s, got {duration_sec}s"
        }
    
    if duration_sec > 60:
        return {
            "status": "error",
            "error": "duration_too_long",
            "message": f"Duration must be at most 60s, got {duration_sec}s"
        }
    
    if seed is None:
        seed = simulate_microphone.counter
        simulate_microphone.counter += 1
    
    try:
        audio_bytes = _generate_procedural_audio("", duration_sec, seed)
        
        return {
            "status": "success",
            "format": "wav",
            "duration_sec": duration_sec,
            "samplerate": 16000,
            "channels": 1,
            "audio_id": f"sim-audio-{seed}",
            "audio_bytes": audio_bytes,
            "metadata": {
                "simulated": True,
                "seed": seed,
                "requested_duration": duration_sec,
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Simulated audio generation failed: {e}"
        }


# Audio counter for auto-incrementing seed
simulate_microphone.counter = 0


async def list_cameras_sim() -> dict:
    """Simulated list_cameras - returns virtual camera."""
    return {
        "status": "success",
        "cameras": [
            {
                "id": 0,
                "name": "Simulated Camera",
                "resolution": "640x480",
                "simulated": True
            }
        ]
    }


async def list_audio_devices_sim() -> dict:
    """Simulated list_audio_devices - returns virtual microphone."""
    return {
        "status": "success",
        "input_devices": [
            {
                "id": 0,
                "name": "Simulated Microphone",
                "channels": 1,
                "samplerate": 16000,
                "simulated": True
            }
        ],
        "output_devices": [
            {
                "id": 0,
                "name": "Simulated Speaker",
                "channels": 2,
                "samplerate": 44100,
                "simulated": True
            }
        ]
    }
