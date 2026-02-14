#!/usr/bin/env python3
"""
ANSE WebSocket Backend - Standalone Event Server

Production-ready WebSocket server that:
- Runs the ANSE nervous system simulation
- Broadcasts real-time events to connected clients
- Emits sensor readings, reflex triggers, actuator actions, world model updates

This is a PURE WebSocket backend (no HTTP, no HTML serving).
The ANSE Dashboard connects to this backend via WebSocket.

Usage:
    python backend/websocket_backend.py

Connect:
    ws://localhost:8001  (from web client)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for ANSE imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from anse.engine_core import EngineCore
    from anse.world_model import WorldModel
except ImportError as e:
    print(f"Error: Cannot import ANSE modules: {e}")
    print("Make sure you're running from the ANSE project directory")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("Error: Missing websockets library")
    print("Install with: pip install websockets")
    sys.exit(1)


class ANSEWebSocketBackend:
    """
    Pure WebSocket backend for ANSE Dashboard.
    
    Simulates a complete nervous system:
    1. SENSOR PHASE     → Distance sensor emits readings
    2. WORLD MODEL      → Readings recorded to brain state
    3. REFLEX PHASE     → Check if conditions trigger reflexes
    4. ACTUATOR PHASE   → Execute motor commands
    5. BROADCAST        → Send all events to dashboard clients
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8001, debug: bool = False):
        """Initialize the WebSocket backend."""
        self.host = host
        self.port = port
        self.debug = debug
        self.clients = set()

        # ANSE engine
        self.engine = None
        self.world_model = None

        # Simulated sensor state (distance in cm)
        self.distance = 50  # Starts at safe distance

        # Simulated actuator state
        self.movement_state = "IDLE"  # IDLE, MOVING, STOPPED

        # Track active reflexes
        self.last_reflex = None

    async def initialize_engine(self) -> bool:
        """Initialize ANSE engine with world model."""
        try:
            self.engine = EngineCore(simulate=True)
            self.world_model = self.engine.world
            self._log("✓ ANSE Engine initialized")
            self._log("✓ World Model ready")
            return True
        except Exception as e:
            self._log(f"⚠ Could not initialize ANSE engine: {e}")
            self._log("  Using standalone WorldModel for demo")
            self.world_model = WorldModel()
            return False

    async def websocket_handler(self, websocket, path=None):
        """Handle a new WebSocket client connection."""
        client_id = id(websocket)
        self.clients.add(websocket)
        self._log(f"→ Client {client_id} connected ({len(self.clients)} total)")

        try:
            # Send current state to new client
            await self.broadcast_world_model_snapshot(target=websocket)

            # Keep connection alive
            async for message in websocket:
                # Echo or process client messages if needed (none expected in this version)
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            self._log(f"← Client {client_id} disconnected ({len(self.clients)} remain)")

    async def broadcast_to_clients(self, message: dict, target=None):
        """Send a message to one client or all connected clients."""
        message_json = json.dumps(message)
        target_clients = [target] if target else self.clients

        if target_clients:
            await asyncio.gather(
                *[
                    client.send(message_json)
                    for client in target_clients
                    if client and not client.closed
                ],
                return_exceptions=True
            )

    async def broadcast_world_model_snapshot(self, target=None):
        """
        Broadcast the current world model state (brain snapshot).
        This is what the dashboard's World Model panel displays.
        """
        snapshot = {
            "type": "worldmodel",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "distance_cm": round(self.distance, 1),
                "safe": self.distance > 10,
                "actuator_state": self.movement_state,
                "last_reflex": self.last_reflex or "none",
                "total_events": len(self.world_model.get_recent(100))
                if self.world_model
                else 0,
            },
        }
        await self.broadcast_to_clients(snapshot, target=target)

    async def record_and_broadcast_event(self, event_type: str, event_data: dict):
        """Record an event to world model AND broadcast to all clients."""
        # Build complete event
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **event_data
        }

        # Record to ANSE world model
        if self.world_model:
            self.world_model.append_event(event)

        # Broadcast event to all clients
        await self.broadcast_to_clients(event)

        # Also send updated world model snapshot (brain state)
        await self.broadcast_world_model_snapshot()

    async def simulate_distance_sensor(self):
        """
        SENSOR PHASE: Simulate a distance sensor that varies over time.
        
        Pattern:
        - Gradually approach (50cm → 5cm)
        - Trigger reflex (distance < 10cm)
        - Gradually recede (5cm → 50cm)
        - Clear reflex (distance > 15cm)
        - Repeat
        """
        self._log("[SENSOR] Distance sensor simulation starting")
        self._log("[SENSOR] Pattern: 50cm → 5cm (approach) → 50cm (recede)")
        self._log("")

        iteration = 0
        while True:
            iteration += 1

            # Simulate object approaching then receding
            if iteration < 8:
                # Approach: 50 > 5 cm (in ~7 iterations)
                self.distance = max(5, 50 - (iteration * 5.5))
            else:
                # Recede: 5 > 50 cm (in ~10 iterations)
                self.distance = min(50, 5 + ((iteration - 8) * 5.5))
                if iteration > 18:
                    iteration = 0  # Reset cycle

            # Broadcast sensor reading
            await self.record_and_broadcast_event("sensor", {
                "sensor_name": "distance_sensor",
                "sensor_type": "distance",
                "value": round(self.distance, 1),
            })

            # REFLEX PHASE: Check conditions and trigger reflexes
            await self.check_and_trigger_reflexes()

            # Log progress every 5 events
            if self.world_model:
                event_count = len(self.world_model.get_recent(100))
                if event_count % 5 == 0:
                    self._log(
                        f"[DEMO] {event_count} events recorded, "
                        f"distance={self.distance:.1f}cm, state={self.movement_state}"
                    )

            # Sensor reads approximately every 1.5 seconds
            await asyncio.sleep(1.5)

    async def check_and_trigger_reflexes(self):
        """
        REFLEX PHASE: Check world state and trigger reflexes.
        
        Reflex rules:
        - If distance < 10cm: STOP (proximity safeguard)
        - If distance > 15cm and stopped: RESUME (clear to move)
        """

        # Reflex 1: Proximity Safeguard
        # "If object too close, stop immediately!"
        if self.distance < 10 and self.movement_state != "STOPPED":
            self.last_reflex = "proximity_safeguard"
            await self.record_and_broadcast_event("reflex", {
                "reflex_name": "proximity_safeguard",
                "condition": "distance < 10cm",
                "triggered": True,
            })

            # Execute the action
            await self.execute_actuator_action("STOP")

        # Reflex 2: Clear to Move
        # "If object far away and we were stopped, resume movement"
        elif self.distance > 15 and self.movement_state == "STOPPED":
            self.last_reflex = "clear_to_move"
            await self.record_and_broadcast_event("reflex", {
                "reflex_name": "clear_to_move",
                "condition": "distance > 15cm",
                "triggered": True,
            })

            # Execute the action
            await self.execute_actuator_action("MOVING")
        else:
            # No reflex triggered
            if self.last_reflex is not None:
                self.last_reflex = None

    async def execute_actuator_action(self, action: str):
        """
        ACTUATOR PHASE: Execute an actuator action.
        
        Actions:
        - "STOP" → movement_state = STOPPED
        - "MOVING" → movement_state = MOVING
        """
        old_state = self.movement_state

        if action == "STOP":
            self.movement_state = "STOPPED"
        elif action == "MOVING":
            self.movement_state = "MOVING"

        # Broadcast actuator action
        await self.record_and_broadcast_event("actuator", {
            "actuator_name": "movement",
            "actuator_type": "motor",
            "state": self.movement_state,
        })

    async def run(self):
        """Start the WebSocket backend server."""
        print("\n" + "=" * 70)
        print("ANSE WebSocket Backend - Production Event Server".center(70))
        print("=" * 70)
        print()

        # Initialize ANSE
        await self.initialize_engine()

        # Start the sensor simulation task
        sensor_task = asyncio.create_task(self.simulate_distance_sensor())

        # Start WebSocket server
        self._log(f"Starting WebSocket server on ws://{self.host}:{self.port}...")

        async with websockets.serve(
            self.websocket_handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=20,
        ):
            self._log(f"✓ WebSocket server running on ws://{self.host}:{self.port}")
            print()
            self._log("Dashboard connection:")
            self._log(f"  ws://localhost:{self.port}")
            print()
            self._log("Waiting for connections...")
            print()

            try:
                # Keep running until interrupted
                await asyncio.Future()
            except KeyboardInterrupt:
                print("\n")
                self._log("Shutdown requested...")
                sensor_task.cancel()
                print()

    def _log(self, message: str):
        """Print a log message with timestamp."""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
        else:
            print(message)


async def main():
    """Entry point for the backend server."""
    # Create and run backend
    backend = ANSEWebSocketBackend(
        host="0.0.0.0",
        port=8001,
        debug=False  # Set to True for detailed logging
    )
    await backend.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBackend stopped")
