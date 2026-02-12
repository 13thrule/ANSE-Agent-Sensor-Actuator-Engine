# ANSE Plugin System Documentation

## Overview

ANSE's plugin system allows you to extend the platform with custom sensors, devices, and integrations **without modifying core code**. 

- 🎯 **Non-programmers**: Drop a YAML file in `plugins/` and restart
- 👨‍💻 **Developers**: Write Python classes with full async/await support
- 🔒 **Safe**: Plugins are validated and isolated
- 📦 **Easy to Share**: Plugins are just files or Python modules

## Quick Start (5 Minutes)

### 1. Copy a Template

For a simple sensor or API:
```bash
cp plugins/_template_sensor.yaml plugins/my_temperature.yaml
```

For complex logic or hardware:
```bash
cp plugins/_template_sensor.py plugins/my_device.py
```

### 2. Edit the Plugin

**YAML example** (`my_temperature.yaml`):
```yaml
name: my_temp_sensor
description: My temperature sensor
sensitivity: low

tools:
  - name: read_temp
    description: Read temperature
    handler: |
      result = {
          'temperature': 23.5,
          'unit': 'celsius'
      }
```

**Python example** (`my_device.py`):
```python
from anse.plugin import SensorPlugin

class MyTemperatureSensor(SensorPlugin):
    name = "my_temp_sensor"
    description = "My temperature sensor"
    
    async def read_temp(self):
        """Read temperature"""
        return {'temperature': 23.5, 'unit': 'celsius'}
```

### 3. Restart ANSE

```bash
# The plugin is auto-loaded at startup
python -m anse.engine_core
```

That's it! Your plugin tools are now available.

---

## How It Works

When ANSE starts, it:

1. **Scans** the `plugins/` directory
2. **Discovers** YAML and Python plugin files
3. **Validates** each plugin configuration
4. **Loads** and instantiates plugins
5. **Registers** all tools with the engine
6. **Reports** any errors (but doesn't crash)

If a plugin fails to load, ANSE logs the error and continues with remaining plugins.

---

## YAML Plugin Format

For simple sensors and integrations, use YAML.

### Minimal Example

```yaml
name: my_plugin
description: What this plugin does

tools:
  - name: do_something
    description: What the tool does
    returns: {result: success}
```

### Complete Example

```yaml
name: my_iot_device
description: IoT light controller
sensitivity: high              # low, medium, or high
rate_limit: 60                 # calls per minute
author: Your Name
version: "1.0.0"

tools:
  # Tool with static returns
  - name: list_lights
    description: List available lights
    returns:
      lights:
        - id: "1"
          name: "Living Room"
        - id: "2"
          name: "Bedroom"

  # Tool with parameters and handler
  - name: toggle_light
    description: Turn light on or off
    parameters:
      light_id:
        type: string
        required: true
      state:
        type: boolean
        required: true
    
    handler: |
      light_id = kwargs.get('light_id')
      state = kwargs.get('state')
      
      # Your logic here
      result = {
          'light_id': light_id,
          'state': state,
          'status': 'success'
      }
```

### Parameter Types

Parameters in YAML follow JSON Schema:

```yaml
tools:
  - name: set_value
    parameters:
      # String parameter
      name:
        type: string
        required: true
      
      # Integer parameter
      count:
        type: integer
        required: false
        default: 10
      
      # Number (float)
      brightness:
        type: number
        minimum: 0.0
        maximum: 1.0
      
      # Boolean
      enabled:
        type: boolean
        required: true
```

### Handler Code

The `handler:` field contains Python code that executes when the tool is called.

Available variables:
- `kwargs`: Dictionary of parameters passed to the tool
- `result`: What the tool returns (must be set)

Example:
```yaml
handler: |
  import math
  param1 = kwargs.get('param1', 'default')
  param2 = kwargs.get('param2', 10)
  
  # Do something
  calculated = param1 + param2
  
  result = {
      'input': param1,
      'output': calculated,
      'status': 'success'
  }
```

---

## Python Plugin Format

For complex logic, hardware control, or when you need libraries, use Python.

### Basic Plugin Class

```python
from anse.plugin import Plugin

class MyPlugin(Plugin):
    name = "my_plugin"
    description = "Does something"
    
    async def my_tool(self, param1: str = "default"):
        """Tool description goes here as docstring"""
        return {
            'param1': param1,
            'status': 'ok'
        }
```

Tool methods:
- Must be public (no leading underscore)
- Must be `async` (use `async def`)
- Parameters become tool parameters
- Docstring becomes tool description
- Return a dictionary

### Plugin Classes

ANSE provides base classes for different plugin types:

#### SensorPlugin
For read-only sensors and data sources:
```python
from anse.plugin import SensorPlugin

class TemperatureSensor(SensorPlugin):
    name = "temp_sensor"
    description = "Temperature sensor"
    sensitivity = "low"  # Read-only
    
    async def validate_connection(self) -> bool:
        """Check if sensor is connected"""
        return True
    
    async def get_temperature(self):
        """Read temperature"""
        return {'temperature': 23.5}
```

#### ControlPlugin
For devices that modify the world state:
```python
from anse.plugin import ControlPlugin

class SmartLight(ControlPlugin):
    name = "smart_light"
    description = "Smart light controller"
    sensitivity = "high"  # Can affect world
    
    async def get_status(self) -> dict:
        """Get current light status"""
        return {'state': 'on', 'brightness': 100}
    
    async def validate_action(self, action: str, **kwargs) -> bool:
        """Validate action is safe"""
        return True
    
    async def toggle(self):
        """Turn light on/off"""
        return {'state': 'toggled'}
```

#### NetworkPlugin
For external service integrations:
```python
from anse.plugin import NetworkPlugin

class CloudAPI(NetworkPlugin):
    name = "cloud_api"
    description = "Cloud service connector"
    
    async def test_connection(self) -> bool:
        """Test API connectivity"""
        return True
    
    async def fetch_data(self):
        """Fetch data from API"""
        return {'data': []}
```

#### AnalysisPlugin
For data processing and analysis:
```python
from anse.plugin import AnalysisPlugin

class DataAnalyzer(AnalysisPlugin):
    name = "analyzer"
    description = "Data analysis plugin"
    
    async def validate_input(self, data) -> bool:
        """Validate input data"""
        return isinstance(data, list)
    
    async def analyze(self, data):
        """Analyze data"""
        return {'mean': sum(data) / len(data)}
```

### Full Python Plugin Example

```python
from anse.plugin import SensorPlugin
import random

class EnvironmentalSensor(SensorPlugin):
    """Complete example: temperature and humidity sensor"""
    
    name = "env_sensor"
    description = "Environmental sensor (temperature & humidity)"
    sensitivity = "low"
    rate_limit = 60
    author = "Your Name"
    version = "1.0.0"
    
    def __init__(self):
        """Initialize sensor"""
        super().__init__()
        self.connected = False
        self.min_temp = 15
        self.max_temp = 30
    
    async def on_load(self):
        """Called when ANSE loads this plugin"""
        # Connect to sensor hardware
        self.connected = True
        print(f"[{self.name}] Connected to sensor")
    
    async def on_unload(self):
        """Called when ANSE unloads this plugin"""
        self.connected = False
        print(f"[{self.name}] Disconnected from sensor")
    
    async def validate_connection(self) -> bool:
        """Check if sensor is working"""
        return self.connected
    
    async def get_temperature(self, sensor_id: str = "1"):
        """Read temperature in Celsius"""
        if not self.connected:
            return {'error': 'Sensor not connected'}
        
        temp = self.min_temp + random.random() * (self.max_temp - self.min_temp)
        return {
            'sensor_id': sensor_id,
            'temperature': round(temp, 2),
            'unit': 'celsius'
        }
    
    async def get_humidity(self, sensor_id: str = "1"):
        """Read humidity percentage"""
        if not self.connected:
            return {'error': 'Sensor not connected'}
        
        humidity = 40 + random.random() * 50
        return {
            'sensor_id': sensor_id,
            'humidity': round(humidity, 1),
            'unit': 'percent'
        }
    
    async def get_all(self):
        """Get all readings at once"""
        temp = await self.get_temperature()
        humidity = await self.get_humidity()
        return {**temp, **humidity}
```

---

## Plugin Sensitivity Levels

Choose the right sensitivity for your plugin:

### Low (read-only)
```python
sensitivity = "low"
```
- Sensors, data sources, APIs
- No side effects
- Can't harm physical systems
- Examples: temperature sensor, weather API, database queries

### Medium (external requests)
```python
sensitivity = "medium"
```
- Network requests with side effects
- API writes that don't directly control hardware
- Examples: message sends, database updates, external API calls

### High (world-modifying)
```python
sensitivity = "high"
```
- Controls physical hardware
- Robotics, lights, locks, motors
- Can directly affect the environment
- Examples: robot arms, smart lights, door locks, industrial equipment

The sensitivity level affects:
- Rate limiting
- Audit logging detail
- Permission checks
- Cost estimates

---

## Plugin Lifecycle

### 1. Loading
```
anse/ starts
  ↓
plugin_loader.load_all()
  ↓
  Scans plugins/ directory
  Loads *.yaml files
  Loads *.py files
  ↓
plugin_loader.register_with_engine()
  ↓
  Validates each plugin
  Instantiates Python plugins
  Registers all tools
  ↓
anse/engine_core.py calls plugin.on_load()
  ↓
anse/ ready, plugins available
```

### 2. Execution
```
Agent calls tool: "my_plugin_read_sensor"
  ↓
Engine finds tool in registry
  ↓
Applies rate limits
  ↓
Executes async function
  ↓
Returns result
```

### 3. Unloading
```
anse/ shutting down
  ↓
For each plugin: plugin.on_unload()
  ↓
Connections closed, cleanup done
  ↓
anse/ stops
```

---

## Real-World Examples

### Example 1: Philips Hue Smart Lights

**File**: `plugins/philips_hue.yaml`

```yaml
name: hue_lights
description: Control Philips Hue smart lights

tools:
  - name: set_color
    description: Set light color and brightness
    parameters:
      light_id:
        type: integer
      red:
        type: integer
      green:
        type: integer
      blue:
        type: integer
      brightness:
        type: integer
    
    handler: |
      import requests
      
      light_id = kwargs.get('light_id')
      r = kwargs.get('red')
      g = kwargs.get('green')
      b = kwargs.get('blue')
      brightness = kwargs.get('brightness', 200)
      
      # Send to Hue bridge API
      # response = requests.put(
      #     f"http://hue-bridge/api/{api_key}/lights/{light_id}/state",
      #     json={"bri": brightness, "xy": rgb_to_xy(r, g, b)}
      # )
      
      result = {
          'light_id': light_id,
          'color': {'r': r, 'g': g, 'b': b},
          'brightness': brightness,
          'status': 'set'
      }
```

**Use in ANSE:**
```python
# Agent can now call:
await engine.tools.call("hue_lights_set_color", light_id=1, red=255, green=128, blue=0)
```

### Example 2: Arduino Robot Arm

**File**: `plugins/robot_arm.py`

```python
import serial
from anse.plugin import ControlPlugin

class RobotArm(ControlPlugin):
    name = "robot_arm"
    description = "6-axis robot arm via Arduino"
    sensitivity = "high"
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
    
    async def on_load(self):
        """Connect to Arduino"""
        self.serial_port = serial.Serial('/dev/ttyUSB0', 9600)
    
    async def on_unload(self):
        """Disconnect from Arduino"""
        if self.serial_port:
            self.serial_port.close()
    
    async def move_to_position(self, x: float, y: float, z: float):
        """Move arm to XYZ position in millimeters"""
        cmd = f"MOVE {x} {y} {z}\n"
        self.serial_port.write(cmd.encode())
        
        return {
            'target': {'x': x, 'y': y, 'z': z},
            'status': 'moving'
        }
    
    async def get_position(self):
        """Get current arm position"""
        self.serial_port.write(b"GETPOS\n")
        response = self.serial_port.readline().decode()
        
        x, y, z = map(float, response.split())
        return {'x': x, 'y': y, 'z': z}
    
    async def get_status(self) -> dict:
        """Get arm status"""
        return {'status': 'ready'}
    
    async def validate_action(self, action: str, **kwargs) -> bool:
        """Validate motion is safe"""
        # Check for workspace limits, collisions, etc.
        return True
```

---

## Best Practices

### 1. Name Your Plugins Clearly
```python
name = "zigbee_temperature"  # ✅ Good
name = "zt"                  # ❌ Too cryptic
name = "My Awesome Sensor"   # ❌ Spaces not allowed
```

### 2. Write Clear Descriptions
```python
description = "Read temperature from Zigbee wireless sensor network"  # ✅
description = "Temp sensor"  # ❌ Too vague
```

### 3. Handle Errors Gracefully
```python
async def read_sensor(self):
    """Read sensor - handle disconnection"""
    try:
        data = await self.device.read()
        return {'temperature': data['temp']}
    except ConnectionError:
        return {'error': 'Sensor disconnected'}
    except Exception as e:
        return {'error': str(e)}
```

### 4. Validate Parameters
```python
async def set_brightness(self, level: int):
    """Set brightness 0-255"""
    if not isinstance(level, int):
        return {'error': 'brightness must be integer'}
    
    level = max(0, min(255, level))  # Clamp
    return {'brightness': level}
```

### 5. Use Type Hints
```python
async def move(self, x: int, y: int, z: int) -> dict:
    """Type hints help ANSE understand parameters"""
    return {'position': {'x': x, 'y': y, 'z': z}}
```

### 6. Document Tools with Docstrings
```python
async def read_temperature(self, sensor_id: str = "1") -> dict:
    """Read temperature from sensor.
    
    Args:
        sensor_id: Which sensor to read (optional, defaults to first)
    
    Returns:
        dict with 'temperature' in Celsius and 'status'
    """
    return {'temperature': 23.5, 'status': 'ok'}
```

---

## Troubleshooting

### Plugin Not Loading

Check the logs when ANSE starts:
```
INFO: Found 3 plugin(s), registering...
INFO: ✓ Loaded plugin: my_plugin (yaml)
ERROR: Error registering plugin my_broken_plugin: ...
```

### Plugin Fails Validation

Ensure your plugin has:
- `name` attribute (required)
- `description` attribute (required)
- At least one tool defined
- Valid YAML or Python syntax

### Tools Not Showing Up

After adding a plugin, **restart ANSE**:
```bash
# Plugins only load at startup
python -m anse.engine_core
```

### Handler Code Not Working

Test the Python code in isolation:
```python
# Test your handler code
kwargs = {'param1': 'value'}
# Your handler code here...
print(result)  # Should output something
```

---

## Advanced: Sharing Plugins

### 1. Create a Plugin Directory

```
my-anse-plugins/
├── README.md
├── plugins/
│   ├── my_sensor.yaml
│   └── my_device.py
└── docs/
    └── SETUP.md
```

### 2. Add Documentation

Explain:
- What the plugin does
- Hardware/software requirements
- How to install dependencies
- Configuration needed
- Example usage

### 3. Share on GitHub

Others can then do:
```bash
# Clone your plugin repo
git clone https://github.com/yourname/my-anse-plugins.git

# Copy to ANSE plugins directory
cp -r my-anse-plugins/plugins/* /path/to/anse/plugins/

# Restart ANSE
python -m anse.engine_core
```

---

## Plugin API Reference

### Available Base Classes

- **Plugin**: Base class for all plugins
- **SensorPlugin**: Read-only sensors and data sources
- **ControlPlugin**: Devices that modify world state
- **NetworkPlugin**: External service connections
- **AnalysisPlugin**: Data processing plugins

### Plugin Attributes

| Attribute | Type | Required | Default |
|-----------|------|----------|---------|
| `name` | str | Yes | - |
| `description` | str | Yes | - |
| `sensitivity` | str | No | "low" |
| `rate_limit` | int | No | 60 |
| `author` | str | No | None |
| `version` | str | No | "1.0.0" |

### Plugin Methods

| Method | Purpose | Called When |
|--------|---------|-------------|
| `__init__()` | Initialize plugin | Plugin is instantiated |
| `on_load()` | Setup (async) | ANSE loads the plugin |
| `on_unload()` | Cleanup (async) | ANSE shuts down |
| `get_tools()` | Discover tools | (Auto-called) |
| `validate_connection()` | Check status | (SensorPlugin only) |
| `validate_action()` | Check safety | (ControlPlugin only) |
| `test_connection()` | Test API | (NetworkPlugin only) |
| `validate_input()` | Check data | (AnalysisPlugin only) |

---

## What's Next?

1. **Copy a template** from `plugins/_template_*`
2. **Fill in your sensor/device details**
3. **Restart ANSE** to auto-load
4. **Check the logs** to verify it loaded
5. **Share your plugin** with the community!

For questions, see the ANSE documentation or examples in `plugins/example_*`.
