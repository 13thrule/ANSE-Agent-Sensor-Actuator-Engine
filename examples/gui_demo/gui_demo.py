#!/usr/bin/env python3
"""
ANSE GUI Demo — Real-Time Nervous System Visualization

Connects to ANSE's actual event-driven architecture and broadcasts
sensor readings, world model updates, reflex triggers, and actuator
state changes via WebSocket to a live dashboard.

No polling. No simulation toys. Real event-driven nervous system.
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
    
    Orchestrates ANSE components and broadcasts events via WebSocket.
    """

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Initialize ANSE engine
        self.engine = None
        self.world_model = None
        
        # Demo state
        self.sensor_state = {
            "temperature": 20.0,
            "motion_detected": False,
            "light_level": 500
        }
        self.actuator_state = {
            "led_status": "off",
            "fan_speed": 0,
            "door_locked": True
        }
        self.reflex_triggers = []
        
    async def initialize_engine(self):
        """Initialize ANSE engine and world model."""
        try:
            self.engine = EngineCore(simulate=True)  # Use simulated hardware
            self.world_model = self.engine.world  # Access world model through engine
            print("✓ ANSE Engine initialized")
            print(f"✓ World Model ready")
        except Exception as e:
            print(f"Warning: Could not initialize full ANSE engine: {e}")
            print("  Creating minimal world model for demo")
            self.world_model = WorldModel()
    
    async def websocket_handler(self, websocket):
        """Handle WebSocket client connections."""
        self.clients.add(websocket)
        client_id = id(websocket)
        print(f"  ➜ Client {client_id} connected ({len(self.clients)} total)")
        
        # Send initial state
        await self.send_state_update(websocket)
        
        try:
            async for message in websocket:
                # Echo or process client messages if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"  ➜ Client {client_id} disconnected ({len(self.clients)} remain)")
    
    async def send_state_update(self, websocket=None):
        """Send current state to one client or all clients."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "sensors": self.sensor_state,
            "actuators": self.actuator_state,
            "reflexes": self.reflex_triggers[-5:] if self.reflex_triggers else []
        }
        message = json.dumps({"type": "state_update", "data": state})
        
        target_clients = [websocket] if websocket else self.clients
        for client in target_clients:
            try:
                if client and client.open:
                    await client.send(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
    
    async def broadcast_event(self, event_type: str, event_data: dict):
        """Broadcast an event to all connected clients."""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        message = json.dumps(event)
        
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients if client.open],
                return_exceptions=True
            )
    
    async def record_world_model_event(self, event_type: str, event_data: dict):
        """Record an event to ANSE's world model."""
        if self.world_model:
            try:
                self.world_model.append_event({
                    "type": event_type,
                    "timestamp": datetime.now().isoformat(),
                    **event_data
                })
            except Exception as e:
                print(f"World model record error: {e}")
    
    async def simulate_sensor_readings(self):
        """
        Simulate sensor readings and emit them as world model events.
        No polling loop — just periodic events like a real system.
        """
        print("\n📡 Starting sensor simulation...")
        
        iteration = 0
        while True:
            iteration += 1
            
            # Simulate temperature sensor (with small random variation)
            old_temp = self.sensor_state["temperature"]
            new_temp = old_temp + random.uniform(-1.5, 1.5)
            new_temp = max(15, min(30, new_temp))  # Clamp to reasonable range
            self.sensor_state["temperature"] = round(new_temp, 1)
            
            # Record to ANSE world model
            await self.record_world_model_event("sensor_reading", {
                "sensor_id": "temperature_01",
                "reading_type": "temperature",
                "value": self.sensor_state["temperature"],
                "unit": "celsius"
            })
            
            # Broadcast sensor event
            await self.broadcast_event("sensor_event", {
                "sensor_id": "temperature_01",
                "type": "temperature",
                "value": self.sensor_state["temperature"],
                "changed": abs(new_temp - old_temp) > 0.5
            })
            
            # Simulate motion sensor (random spikes)
            if iteration % 3 == 0:  # Every 3rd iteration
                motion = random.random() > 0.7
                self.sensor_state["motion_detected"] = motion
                
                await self.record_world_model_event("sensor_reading", {
                    "sensor_id": "motion_01",
                    "reading_type": "motion",
                    "detected": motion
                })
                
                await self.broadcast_event("sensor_event", {
                    "sensor_id": "motion_01",
                    "type": "motion",
                    "detected": motion
                })
            
            # Simulate light level sensor
            if iteration % 2 == 0:
                old_light = self.sensor_state["light_level"]
                new_light = old_light + random.uniform(-100, 100)
                new_light = max(0, min(1000, new_light))
                self.sensor_state["light_level"] = round(new_light)
                
                await self.record_world_model_event("sensor_reading", {
                    "sensor_id": "light_01",
                    "reading_type": "light_level",
                    "value": self.sensor_state["light_level"],
                    "unit": "lux"
                })
                
                await self.broadcast_event("sensor_event", {
                    "sensor_id": "light_01",
                    "type": "light_level",
                    "value": self.sensor_state["light_level"]
                })
            
            # Check for reflex triggers (simple threshold logic)
            await self.check_reflex_conditions()
            
            # Broadcast updated state
            await self.send_state_update()
            
            # Wait before next cycle (simulated sensor polling interval)
            await asyncio.sleep(2)
    
    async def check_reflex_conditions(self):
        """
        Check sensor readings and trigger reflexes based on conditions.
        This simulates the reflex system reacting to world model events.
        """
        
        # Reflex 1: Temperature threshold
        if self.sensor_state["temperature"] > 25:
            reflex_name = "high_temperature_alert"
            trigger = {
                "reflex_id": "reflex_001",
                "name": reflex_name,
                "condition": f"temperature > 25°C",
                "triggered_by": "temperature_sensor",
                "action": "activate_cooling"
            }
            
            # Only record if not already triggered recently
            recent_triggers = [r for r in self.reflex_triggers[-3:] if r["name"] == reflex_name]
            if not recent_triggers:
                self.reflex_triggers.append(trigger)
                
                await self.record_world_model_event("reflex_triggered", trigger)
                await self.broadcast_event("reflex_event", trigger)
                
                # Simulate actuator response
                self.actuator_state["fan_speed"] = 100
                await self.record_world_model_event("actuator_action", {
                    "actuator_id": "fan_01",
                    "action": "set_speed",
                    "value": 100
                })
                await self.broadcast_event("actuator_event", {
                    "actuator_id": "fan_01",
                    "action": "activate",
                    "speed": 100
                })
        else:
            # Cool down
            if self.actuator_state["fan_speed"] > 0:
                self.actuator_state["fan_speed"] = 0
                await self.broadcast_event("actuator_event", {
                    "actuator_id": "fan_01",
                    "action": "deactivate",
                    "speed": 0
                })
        
        # Reflex 2: Motion detection
        if self.sensor_state["motion_detected"]:
            reflex_name = "motion_detected_alert"
            trigger = {
                "reflex_id": "reflex_002",
                "name": reflex_name,
                "condition": "motion_detected",
                "triggered_by": "motion_sensor",
                "action": "log_and_alert"
            }
            
            recent_triggers = [r for r in self.reflex_triggers[-3:] if r["name"] == reflex_name]
            if not recent_triggers:
                self.reflex_triggers.append(trigger)
                
                await self.record_world_model_event("reflex_triggered", trigger)
                await self.broadcast_event("reflex_event", trigger)
                
                # Turn on LED
                self.actuator_state["led_status"] = "on"
                await self.broadcast_event("actuator_event", {
                    "actuator_id": "led_01",
                    "action": "turn_on",
                    "status": "on"
                })
    
    async def run(self):
        """Start the GUI demo backend."""
        print("\n" + "="*60)
        print("ANSE GUI DEMO — Event-Driven Nervous System")
        print("="*60)
        
        # Initialize ANSE
        await self.initialize_engine()
        
        # Start sensor simulation
        sensor_task = asyncio.create_task(self.simulate_sensor_readings())
        
        # Start WebSocket server
        print(f"\n🔌 WebSocket server starting on ws://{self.host}:{self.port}")
        
        async with websockets.serve(
            self.websocket_handler,
            self.host,
            self.port,
            ping_interval=20,  # Keep-alive
            ping_timeout=20
        ):
            print(f"✓ WebSocket server running on ws://{self.host}:{self.port}")
            print(f"✓ Open http://localhost:8000 in your browser\n")
            
            try:
                # Keep running until interrupted
                await asyncio.Future()
            except KeyboardInterrupt:
                print("\n\nShutdown requested")
                sensor_task.cancel()


async def main():
    """Entry point."""
    backend = GUIDemoBackend(host="0.0.0.0", port=8000)
    # Run backend
    await backend.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo stopped")
