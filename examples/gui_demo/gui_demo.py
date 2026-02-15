#!/usr/bin/env python3
"""ANSE GUI Demo - Real State & Event System in Action

Shows ANSE as a true state-driven event system:
- Distance sensor emits readings to world model
- Reflex monitors world model for conditions
- Actuator responds to reflex triggers
- All events broadcast to GUI via WebSocket

One sensor, one rule, one actuator. Complete state-event flow.
"""

import asyncio
import json
import random
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for ANSE imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from anse.engine_core import EngineCore
    from anse.world_model import WorldModel
except ImportError as e:
    print(f"Error importing ANSE: {e}")
    print("Make sure you're running this from the ANSE project directory")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("Missing websockets. Install with: pip install websockets")
    sys.exit(1)


class GUIDemoBackend:
    """
    ANSE GUI Demo Backend
    
    State-driven event-based system:
    - Sensor emits readings to world model
    - Reflex monitors world model for conditions
    - Actuator responds to reflex triggers
    - All events broadcast to GUI
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Initialize ANSE engine
        self.engine = None
        self.world_model = None
        
        # Sensor state (what the sensor measures)
        self.distance = 50  # cm, starts at safe distance
        
        # Actuator state (what the actuator does)
        self.movement_state = "IDLE"  # IDLE, MOVING, STOPPED
        
        # World model state (brain's understanding)
        self.last_reflex = None  # Track the last reflex triggered
        
    async def initialize_engine(self):
        """Initialize ANSE engine with real plugins."""
        try:
            self.engine = EngineCore(simulate=True)
            self.world_model = self.engine.world
            print("[OK] ANSE Engine initialized")
            print(f"[OK] World Model ready")
            return True
        except Exception as e:
            print(f"[WARN] Could not initialize ANSE engine: {e}")
            print("  Creating minimal world model for demo")
            self.world_model = WorldModel()
            return False
    
    async def websocket_handler(self, websocket):
        """Handle WebSocket client connections."""
        self.clients.add(websocket)
        client_id = id(websocket)
        print(f"  Client {client_id} connected ({len(self.clients)} total)")
        
        # Send initial state
        await self.send_current_state(websocket)
        
        try:
            async for message in websocket:
                # Echo or process client messages if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"  >> Client {client_id} disconnected ({len(self.clients)} remain)")
    
    async def send_current_state(self, websocket=None):
        """Send current state snapshot to one client or all clients."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "sensors": {
                "distance": round(self.distance, 1),
                "safe": self.distance > 10
            },
            "actuators": {
                "movement": self.movement_state
            },
            "reflexes": []
        }
        message = json.dumps({"type": "state_update", "data": state})
        
        target_clients = [websocket] if websocket else self.clients
        for client in target_clients:
            try:
                if client:
                    await client.send(message)
            except Exception:
                pass  # Connection closed, that's fine
    
    async def broadcast_world_model_event(self, event_dict: dict):
        """Broadcast a world model event to all connected clients in GUI format."""
        event_type = event_dict.get("type", "unknown")
        
        # Convert to GUI message format
        if event_type == "sensor_reading":
            message = json.dumps({
                "type": "sensor_event",
                "timestamp": event_dict.get("timestamp"),
                "data": event_dict
            })
        elif event_type == "reflex_triggered":
            message = json.dumps({
                "type": "reflex_event",
                "timestamp": event_dict.get("timestamp"),
                "data": event_dict
            })
        elif event_type == "actuator_action":
            message = json.dumps({
                "type": "actuator_event",
                "timestamp": event_dict.get("timestamp"),
                "data": event_dict
            })
        else:
            message = json.dumps({
                "type": "state_update",
                "timestamp": event_dict.get("timestamp"),
                "data": event_dict
            })
        
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients if client],
                return_exceptions=True
            )
    
    async def broadcast_world_model_snapshot(self):
        """Broadcast the current world model state (brain snapshot) to all clients."""
        world_model_data = {
            "distance_cm": round(self.distance, 1),
            "safe": self.distance > 10,
            "actuator_state": self.movement_state,
            "last_reflex": self.last_reflex or "none",
            "total_events": len(self.world_model.get_recent(100)) if self.world_model else 0
        }
        
        snapshot = {
            "type": "world_model_update",
            "timestamp": datetime.now().isoformat(),
            "data": world_model_data
        }
        
        message = json.dumps(snapshot)
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients if client],
                return_exceptions=True
            )
    
    async def record_and_broadcast_event(self, event_type: str, event_data: dict):
        """Record event to world model AND broadcast to GUI."""
        # Record to ANSE world model
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **event_data
        }
        
        if self.world_model:
            self.world_model.append_event(event)
        
        # Broadcast to GUI
        await self.broadcast_world_model_event(event)
        
        # Broadcast world model snapshot (brain state)
        await self.broadcast_world_model_snapshot()
    
    async def simulate_distance_sensor(self):
        """
        Simulate a distance sensor that emits readings.
        
        This is the SENSOR phase (state input):
        Sensor > World Model
        """
        print("[SENSOR] Starting distance sensor simulation...")
        print("[SENSOR] Distance: 50cm (safe) > approaching > 5cm (dangerous) > receding > 50cm (safe)\n")
        
        iteration = 0
        while True:
            iteration += 1
            
            # Simulate distance varying (object approaching)
            # Eventually triggers the reflex (distance < 10cm = too close)
            if iteration < 8:
                # Gradually approach: 50 > 5 cm
                self.distance = max(5, 50 - (iteration * 5.5))
            else:
                # Then move away: 5 > 50 cm
                self.distance = min(50, 5 + ((iteration - 8) * 5.5))
                if iteration > 18:
                    iteration = 0  # Reset cycle
            
            # Record sensor reading to world model
            await self.record_and_broadcast_event("sensor_reading", {
                "sensor_id": "distance_sensor_01",
                "reading_type": "proximity",
                "distance_cm": round(self.distance, 1),
                "safe": self.distance > 10
            })
            
            # Check rules (RULE VALIDATION phase)
            await self.check_and_trigger_reflexes()
            
            # Send updated state snapshot
            await self.send_current_state()
            
            # Show progress every 5 events
            if self.world_model and len(self.world_model.get_recent(100)) % 5 == 0:
                event_count = len(self.world_model.get_recent(100))
                print(f"[DEMO] {event_count} events recorded, distance={self.distance:.1f}cm, state={self.movement_state}")
            
            await asyncio.sleep(1.5)  # Sensor reads every 1.5 seconds
    
    async def check_and_trigger_reflexes(self):
        """
        Check sensor conditions and trigger reflexes.
        
        This is the RULE VALIDATION phase:
        World Model > Reflex Check > Actuator Action
        """
        
        # Reflex 1: Proximity alert
        # "If distance < 10cm, STOP immediately"
        
        if self.distance < 10 and self.movement_state != "STOPPED":
            # Reflex triggered!
            self.last_reflex = "proximity_safeguard"
            await self.record_and_broadcast_event("reflex_triggered", {
                "reflex": "Proximity Alert",
                "condition": "distance < 10cm",
                "action": "STOP"
            })
            
            # Execute actuator action
            await self.execute_actuator_action("STOP")
        
        elif self.distance > 15 and self.movement_state == "STOPPED":
            # Safe zone again, can move
            self.last_reflex = "clear_to_move"
            await self.record_and_broadcast_event("reflex_triggered", {
                "reflex": "Clear to Move",
                "condition": "distance > 15cm",
                "action": "RESUME"
            })
            
            # Execute actuator action
            await self.execute_actuator_action("MOVING")
        else:
            # No reflex triggered
            if self.last_reflex is not None:
                self.last_reflex = None
    
    async def execute_actuator_action(self, action: str):
        """
        Execute an actuator action.
        
        This is the ACTUATOR phase of the nervous system:
        Reflex > Tool Call > State Update
        """
        
        old_state = self.movement_state
        
        if action == "STOP":
            self.movement_state = "STOPPED"
        elif action == "MOVING":
            self.movement_state = "MOVING"
        
        # Record actuator action to world model
        await self.record_and_broadcast_event("actuator_action", {
            "actuator_id": "movement_01",
            "tool": "movement_control",
            "action": action,
            "old_state": old_state,
            "new_state": self.movement_state
        })
    
    async def run(self):
        """Start the GUI demo backend."""
        print("\n" + "="*60)
        print("ANSE GUI DEMO - Real Nervous System")
        print("="*60)
        
        # Initialize ANSE
        await self.initialize_engine()
        
        # Start sensor simulation
        sensor_task = asyncio.create_task(self.simulate_distance_sensor())
        
        # Start WebSocket server
        print(f"\n[WEBSOCKET] Server starting on ws://{self.host}:{self.port}")
        
        async with websockets.serve(
            self.websocket_handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=20
        ):
            print(f"[OK] WebSocket server running on ws://{self.host}:{self.port}")
            print(f"[OK] Open http://localhost:8001/index.html in your browser\n")
            
            try:
                # Keep running until interrupted
                await asyncio.Future()
            except KeyboardInterrupt:
                print("\n\nShutdown requested")
                sensor_task.cancel()


async def main():
    """Entry point."""
    backend = GUIDemoBackend(host="0.0.0.0", port=8000)
    await backend.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo stopped")
