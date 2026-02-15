"""
ANSE Plugin Template - Python Implementation

Copy this file and customize it for your sensor, device, or integration.
Rename to: my_plugin_name.py

For simpler plugins, use the YAML template: _template_sensor.yaml
For complex logic, environment detection, or library dependencies, use Python.

IMPORTANT: ANSE is EVENT-DRIVEN, not polling-based
============================================

✅ DO:
  - Implement tool methods that are called ON-DEMAND
  - Emit events to world model when sensor readings change
  - React to events from reflexes or other agents
  - Reference: docs/EVENT_DRIVEN_ARCHITECTURE.md

❌ DON'T:
  - Create polling loops (while True, setInterval, etc.)
  - Continuously read sensors in background
  - Sleep-based timing (use events instead)
  - Assume tools will be called periodically
"""

import random
import time
from typing import Dict, Any, Optional
from anse.plugin import SensorPlugin


class ExampleTemperatureSensor(SensorPlugin):
    """Example temperature sensor plugin.
    
    Demonstrates how to build a Python-based plugin for ANSE.
    This would normally connect to real hardware or an external service.
    
    EVENT-DRIVEN PATTERN:
    ====================
    1. Tools (get_temperature, get_humidity, etc.) are called ON-DEMAND
       when agents or reflexes need data - never called continuously
    
    2. If this sensor detects important state changes, emit events:
       await self.engine.world_model.record({
           "type": "sensor_reading",
           "sensor": "temperature",
           "value": temp,
           "timestamp": time.time()
       })
    
    3. The world model broadcasts these events to:
       - Reflexes (which react instantly to thresholds)
       - Agents (which process events and make decisions)
       - Dashboard (which updates UI based on events)
    
    4. No polling loops! Tools are called as needed, not continuously.
    """
    
    # Required: Plugin name (used in tool registration as: plugin_name_tool_name)
    name = "example_temp"
    
    # Required: Plugin description
    description = "Simulated temperature sensor with humidity and status monitoring"
    
    # Optional: Plugin metadata
    sensitivity = "low"  # Read-only sensor
    rate_limit = 60  # Allow 60 calls per minute
    author = "Your Name"
    version = "1.0.0"
    
    def __init__(self):
        """Initialize the temperature sensor plugin."""
        super().__init__()
        
        # Initialize any hardware connections, configuration, etc.
        self.connected = False
        self.min_temp = 15
        self.max_temp = 35
        
        print(f"[{self.name}] Initialized")
    
    async def on_load(self) -> None:
        """Called when ANSE loads this plugin.
        
        Use this for async initialization like:
        - Connecting to hardware
        - Discovering devices
        - Initializing connections
        """
        self.connected = True
        print(f"[{self.name}] Loaded and connected")
    
    async def on_unload(self) -> None:
        """Called when ANSE unloads this plugin.
        
        Use this to clean up:
        - Close connections
        - Save state
        - Stop threads
        """
        self.connected = False
        print(f"[{self.name}] Unloaded")
    
    async def validate_connection(self) -> bool:
        """Validate that the sensor is connected and working."""
        return self.connected
    
    # Tools are discovered automatically from public async methods
    # Each method becomes a tool with this naming: plugin_name_method_name
    
    async def get_temperature(self, sensor_id: str = "default") -> Dict[str, Any]:
        """Read current temperature from the sensor.
        
        Args:
            sensor_id: Which sensor to read from (optional)
        
        Returns:
            Dictionary with temperature, unit, and status
        """
        # Simulate reading sensor
        temperature = round(
            self.min_temp + random.random() * (self.max_temp - self.min_temp), 
            2
        )
        
        return {
            "temperature": temperature,
            "unit": "celsius",
            "sensor_id": sensor_id,
            "status": "ok"
        }
    
    async def get_humidity(self, sensor_id: str = "default") -> Dict[str, Any]:
        """Read current humidity from the sensor.
        
        Args:
            sensor_id: Which sensor to read from (optional)
        
        Returns:
            Dictionary with humidity percentage
        """
        humidity = round(40 + random.random() * 50, 1)
        
        return {
            "humidity_percent": humidity,
            "sensor_id": sensor_id,
            "status": "ok"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall sensor status and health metrics."""
        return {
            "status": "connected" if self.connected else "disconnected",
            "battery_percent": random.randint(50, 100),
            "last_reading": "2026-02-12T10:30:00Z",
            "uptime_hours": 48,
            "firmware_version": "2.1.0"
        }
    
    async def get_sensor_data(self) -> Dict[str, Any]:
        """Get all sensor readings at once."""
        temp = await self.get_temperature()
        humidity = await self.get_humidity()
        status = await self.get_status()
        
        return {
            "temperature": temp["temperature"],
            "humidity": humidity["humidity_percent"],
            "status": status["status"],
            "battery": status["battery_percent"]
        }
    
    async def emit_reading_event(self) -> Dict[str, Any]:
        """EXAMPLE: Emit a sensor reading event to the world model.
        
        This demonstrates how to emit events for reflexes and agents to react to.
        You would call this when the sensor detects important changes.
        
        In a real implementation, you might:
        1. Poll sensor occasionally (on-demand, not in a loop)
        2. Compare new reading to last reading
        3. If significant change, emit event to world model
        4. Reflexes listening for temperature events react instantly
        5. Agents listening for temperature events process and decide
        """
        if not self.engine:
            return {"error": "Engine not available"}
        
        # Get current reading
        reading = await self.get_temperature()
        temperature = reading["temperature"]
        
        # Emit sensor reading event to world model
        # This will be broadcast to reflexes, agents, and dashboard
        event = {
            "type": "sensor_reading",
            "sensor": self.name,  # e.g., "example_temp"
            "value": temperature,
            "unit": "celsius",
            "timestamp": time.time(),
            "metadata": {
                "sensor_id": "default",
                "source": "real_sensor"
            }
        }
        
        # Record to world model (will be broadcast to all subscribers)
        await self.engine.world_model.record(event)
        
        return {
            "status": "event_emitted",
            "event_type": "sensor_reading",
            "value": temperature,
            "timestamp": event["timestamp"]
        }


# ============================================================================
# Python Plugin Guidelines
# ============================================================================
#
# EVENT-DRIVEN ARCHITECTURE
# ==========================
# ANSE is a state-driven control relay, not a passive monitoring system:
# - Tools are endpoints called ON-DEMAND (by agents or reflexes)
# - Do NOT create polling loops or background threads
# - DO emit events when sensor readings change/arrive
# - DO let reflexes/agents react to events naturally
# See: docs/EVENT_DRIVEN_ARCHITECTURE.md
#
# 1. Inheritance:
#    - Sensor plugins: inherit from SensorPlugin
#    - Control plugins: inherit from ControlPlugin
#    - Network plugins: inherit from NetworkPlugin
#    - Analysis plugins: inherit from AnalysisPlugin
#    - Generic: inherit from Plugin
#
# 2. Required Attributes:
#    - name: str (lowercase, alphanumeric, underscore/dash)
#    - description: str
#
# 3. Optional Attributes:
#    - sensitivity: "low", "medium", or "high"
#    - rate_limit: int (calls per minute)
#    - author: str
#    - version: str
#
# 4. Methods:
#    - Public async methods become tools automatically
#    - Private methods (start with _) are not exposed
#    - on_load(): Called when plugin loads (use for initialization)
#    - on_unload(): Called when plugin unloads (use for cleanup)
#    - validate_connection(): Override for sensors/controls
#
# 5. Tool Discovery:
#    All public async methods are automatically registered as tools:
#      plugin_name_method_name
#    
#    Tool parameters are extracted from method signature.
#    Tool description comes from docstring.
#
# 6. Return Values:
#    All tools should return dictionaries with:
#    - Clear key names (temperature, status, error, etc.)
#    - Simple types (str, int, float, bool, dict, list)
#    - No circular references
#
# 7. Event Emission (Best Practice):
#    When sensor reading arrives or state changes:
#      await self.engine.world_model.record({
#          "type": "sensor_reading",
#          "sensor": "my_sensor",
#          "value": reading_value,
#          "timestamp": time.time()
#      })
#    
#    This triggers:
#    - Reflexes listening for this sensor to react
#    - Agents to receive update via event stream
#    - Dashboard to refresh with new data
#
# 8. Anti-Patterns (DON'T DO THIS):
#    ❌ while True: reading = await sensor.read()  # Polling!
#    ❌ asyncio.sleep() for timing (use events)
#    ❌ setInterval() in JavaScript plugins
#    ❌ Periodic health checks
#    ❌ Background data collection loops
#    
#    ✅ Tools ready for on-demand calls
#    ✅ Emit events when data available
#    ✅ Let reflexes/agents pull when needed
#
# ============================================================================
