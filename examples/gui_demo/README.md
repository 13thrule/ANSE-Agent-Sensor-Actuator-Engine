# ANSE GUI Demo — Real-Time Nervous System Visualization

A minimal but **completely real** demonstration of ANSE's event-driven architecture.

**No simulation toys. No toy WebSockets. This connects directly to ANSE's world model, reflexes, and actuators.**

## Quick Test: See the Nervous System Working

Want to see it work first, without the GUI?

```bash
cd examples/gui_demo
python demo_simple.py
```

This shows the **three phases of the nervous system**:
1. **SENSOR**: Distance readings gradually approaching (50→5cm)
2. **REFLEX**: Proximity alarm triggers when too close (< 10cm)
3. **ACTUATOR**: Movement control responds (IDLE → STOPPED → MOVING)

**Output example:**
```
[0] Distance:  50.0cm (state: IDLE)
[1] Distance:  44.5cm (state: IDLE)
...
[8] Distance:   5.0cm -> REFLEX TRIGGERED (too close!) -> STOP
[9] Distance:  10.5cm (state: STOPPED)
[10] Distance:  16.0cm -> REFLEX CLEARED (safe now) -> RESUME
```

All 24 events recorded to ANSE world model. ✅

## What This Demo Shows

The dashboard visualizes ANSE as a nervous system in real time:

- **📡 Sensor Input** — Live sensor readings (temperature, motion, light)
- **🌍 World Model** — Current state of the agent's environment
- **⚡ Reflexes** — Instant reactions triggered by sensor conditions
- **🎛️ Actuator State** — Current state of motors, lights, cooling systems
- **📋 Event Log** — Real-time stream of all events with timeline visualization

## How It Works

1. **Backend (Python)**
   - Imports ANSE's real `EngineCore` and `WorldModel`
   - Simulates sensor readings using deterministic values
   - Checks reflex conditions based on world model state
   - Broadcasts all events via WebSocket

2. **Frontend (HTML/JS)**
   - Connects to WebSocket at `ws://localhost:8000`
   - Receives events in real time
   - Updates five panels as events arrive
   - Shows visual timeline and detailed event log

## Running the Demo

### Option 1: Quick Start (Automatic Browser)

```bash
cd examples/gui_demo
python server.py
```

This will:
- Start the WebSocket server (port 8000)
- Start the HTTP server (port 8001)
- Open your browser to http://localhost:8001/index.html
- Stream ANSE events in real time

### Option 2: Manual

**Terminal 1 — Start the backend:**
```bash
cd examples/gui_demo
python gui_demo.py
```

**Terminal 2 — Start the HTTP server:**
```bash
cd examples/gui_demo
python -m http.server 8001
```

**Browser:**
```
http://localhost:8001/index.html
```

## Architecture

```
┌─────────────────────────────────────────┐
│  ANSE Engine (Python Backend)            │
├─────────────────────────────────────────┤
│  • Real EngineCore                       │
│  • Real WorldModel (event store)         │
│  • Sensor simulation (deterministic)     │
│  • Reflex conditions (threshold checks)  │
│  • Actuator state tracking               │
└────────────┬────────────────────────────┘
             │ WebSocket (ws://localhost:8000)
             ▼
┌─────────────────────────────────────────┐
│  Frontend (HTML/JS)                      │
├─────────────────────────────────────────┤
│  • Real-time event stream listener       │
│  • Five dashboard panels                 │
│  • Timeline visualization               │
│  • Event log (last 50 events)            │
└─────────────────────────────────────────┘
     │
     ▼ display
┌─────────────────────────────────────────┐
│  Browser Dashboard                       │
│                                          │
│  [Sensors] [World Model] [Reflexes]    │
│  [Actuators]                             │
│  [Timeline + Event Log]                 │
└─────────────────────────────────────────┘
```

## Understanding the Event Flow

### Sensor Events (every 2 seconds)

Temperature, motion, and light sensors emit readings:

```json
{
  "type": "sensor_event",
  "data": {
    "sensor_id": "temperature_01",
    "value": 23.5,
    "changed": true
  }
}
```

### Reflex Triggers (when thresholds are exceeded)

When temperature > 25°C, the cooling reflex activates:

```json
{
  "type": "reflex_event",
  "data": {
    "reflex_id": "reflex_001",
    "name": "high_temperature_alert",
    "triggered_by": "temperature_sensor",
    "action": "activate_cooling"
  }
}
```

### Actuator Actions (in response to reflexes)

The fan activates in response:

```json
{
  "type": "actuator_event",
  "data": {
    "actuator_id": "fan_01",
    "action": "activate",
    "speed": 100
  }
}
```

## What's Real About This Demo

✅ **Real ANSE world model** — Not a toy event list  
✅ **Real reflex system** — Actual threshold-based reactions  
✅ **Real event streaming** — WebSocket broadcasts actual events  
✅ **Real sensor simulation** — Deterministic but realistic readings  
✅ **Real actuator state** — Tracks actual actuator conditions  

## What's Simulated (By Design)

⚙️ **Sensor readings** — Deterministic pseudo-random values (no hardware)  
⚙️ **Actuator hardware** — Virtual state tracking (no real motors)  
⚙️ **Network** — Local WebSocket (no remote server)  

The simulation is **intentional and realistic** — real ANSE plugins work the same way.

## Customizing the Demo

### Add More Sensors

Edit `gui_demo.py` in `simulate_sensor_readings()`:

```python
# Simulate humidity sensor
humidity = 45 + random.uniform(-5, 5)
await self.broadcast_event("sensor_event", {
    "sensor_id": "humidity_01",
    "type": "humidity",
    "value": humidity
})
```

### Add More Reflexes

Edit `check_reflex_conditions()`:

```python
# Reflex: High humidity alert
if self.sensor_state.get("humidity", 0) > 70:
    reflex = {
        "reflex_id": "reflex_003",
        "name": "high_humidity_alert",
        "action": "activate_dehumidifier"
    }
    await self.broadcast_event("reflex_event", reflex)
```

### Change the Theme

Edit `index.html` CSS variables in `<style>`:

```css
/* Change primary color */
--primary: #00d9ff;  /* Change from cyan */
```

## Recording a Demo Video

To record a 20-40 second demo:

1. Start the server: `python server.py`
2. Wait for events to start streaming (2-3 seconds)
3. Record your screen for 30 seconds
4. Stop when you've captured:
   - Sensor readings changing
   - A reflex triggered
   - Actuators responding

The visual timeline makes the demo very clear and compelling.

## Files in This Directory

```
gui_demo/
├── gui_demo.py          # Python backend (ANSE integration)
├── server.py            # HTTP + WebSocket server wrapper
├── index.html           # Web dashboard (browser)
└── README.md            # This file
```

## Requirements

```bash
pip install websockets
```

(ANSE's dependencies are already installed in the main project)

## Troubleshooting

**"Connection refused" in browser?**
- Make sure `python gui_demo.py` is running
- Check that port 8000 is not blocked by firewall

**Blank screen?**
- Check browser console (F12) for JavaScript errors
- Verify WebSocket connection in Network tab

**No events appearing?**
- Wait 2-3 seconds for first sensor reading
- Check that ANSE engine initialized successfully (look for ✓ logs)

## Advanced: Connecting Real Hardware

Once comfortable with this demo, you can:

1. Replace `simulate=True` with `simulate=False` in `gui_demo.py`
2. Register real sensor plugins in the `initialize_engine()` method
3. Connect real ANSE plugins (camera, microphone, etc.)
4. The dashboard will automatically show real data

The same code works for both simulated and real hardware. That's the power of ANSE's plugin system.

## Next Steps

- Explore [EVENT_DRIVEN_ARCHITECTURE.md](../../docs/EVENT_DRIVEN_ARCHITECTURE.md) for how the nervous system works
- Check [IMPLEMENTATION_CHECKLIST.md](../../docs/IMPLEMENTATION_CHECKLIST.md) to build real agents
- Look at plugin examples in [plugins/sensors/](../../plugins/sensors/)

**Questions?** See [CONTRIBUTING.md](../../docs/CONTRIBUTING.md)
