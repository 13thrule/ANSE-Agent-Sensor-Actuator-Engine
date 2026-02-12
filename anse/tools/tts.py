"""
Text-to-speech tool - audio output for agents.
"""
from typing import Dict, Any
import asyncio


async def say(text: str, rate: int = 200, volume: float = 1.0) -> Dict[str, Any]:
    """
    Speak text using text-to-speech.
    
    Args:
        text: Text to speak
        rate: Speech rate in words per minute (default: 200)
        volume: Volume level 0.0 to 1.0 (default: 1.0)
        
    Returns:
        Dict indicating success or error
    """
    if not text or len(text.strip()) == 0:
        return {"error": "empty_text", "message": "Text cannot be empty"}
    
    if len(text) > 1000:
        return {"error": "text_too_long", "message": "Text limited to 1000 characters"}
    
    try:
        import pyttsx3
    except ImportError:
        return {"error": "pyttsx3 not installed"}
    
    try:
        # Run in thread to avoid blocking
        def _speak():
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        
        # Execute in thread pool to keep async
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _speak)
        
        return {
            "spoken": True,
            "text": text,
            "length": len(text),
            "rate": rate,
            "volume": volume,
        }
        
    except Exception as e:
        return {"error": "speech_failed", "message": str(e)}


async def get_voices() -> Dict[str, Any]:
    """
    List available TTS voices.
    
    Returns:
        Dict containing available voices
    """
    try:
        import pyttsx3
    except ImportError:
        return {"error": "pyttsx3 not installed"}
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        for voice in voices:
            voice_list.append({
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages if hasattr(voice, 'languages') else [],
            })
        
        engine.stop()
        
        return {
            "voices": voice_list,
            "count": len(voice_list),
        }
        
    except Exception as e:
        return {"error": "pyttsx3 not installed", "message": str(e)}
