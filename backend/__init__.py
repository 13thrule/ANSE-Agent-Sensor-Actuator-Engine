"""ANSE WebSocket Backend

Production-ready WebSocket event server for the ANSE Dashboard.

This module provides:
- ANSEWebSocketBackend: Pure WebSocket server for real-time events
- Event broadcasting: Sensor, reflex, actuator, world model events
- ANSE integration: Connects to EngineCore for nervous system simulation

Quick start:
    python -m backend.websocket_backend

Or import for custom integration:
    from backend.websocket_backend import ANSEWebSocketBackend
"""

__version__ = "1.0.0"
__author__ = "ANSE Project"

from .websocket_backend import ANSEWebSocketBackend

__all__ = ["ANSEWebSocketBackend"]
