"""
ANSE Plugin Template - Python Implementation

Copy this file and customize it for your sensor, device, or integration.
Rename to: my_plugin_name.py

For simpler plugins, use the YAML template: _template_sensor.yaml
For complex logic, environment detection, or library dependencies, use Python.
"""

import random
from typing import Dict, Any, Optional
from anse.plugin import SensorPlugin


class ExampleTemperatureSensor(SensorPlugin):
    """Example temperature sensor plugin.
    
    Demonstrates how to build a Python-based plugin for ANSE.
    This would normally connect to real hardware or an external service.
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


# ============================================================================
# Python Plugin Guidelines
# ============================================================================
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
#    - on_load(): Called when plugin loads
#    - on_unload(): Called when plugin unloads
#    - validate_connection(): Override for sensors/controls
#
# 5. Tool Discovery:
#    All public async methods are automatically registered as tools:
#      my_plugin_method_name
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
# ============================================================================
