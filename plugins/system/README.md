# System Plugins

Core system plugins: reflexes, UI integration, and other infrastructure.

## Current Plugins

### Reflex System
- `reflex_system/` - Fast, event-driven reactions
  - Triggered by world model sensor events
  - No LLM latency (instant responses)
  - Integrates with actuators
  - Examples: collision avoidance, temperature alerts, motion tracking

### Dashboard Bridge
- `dashboard_bridge/` - UI integration
  - Broadcasts world model state to web dashboard
  - Receives commands from UI
  - WebSocket server for real-time updates

## Creating a System Plugin

1. Create a folder with your plugin name
2. Implement `plugin.py` with async event handlers
3. Add `plugin.yaml` with metadata and tool definitions
4. Register in agent's plugin loader

## Key Patterns

### Event-Driven Reactions
```python
async def process_world_model_event(event):
    if event.type == "sensor_reading":
        if event.value > THRESHOLD:
            await my_actuator.trigger()
```

### Broadcasting to UI
```python
async def notify_dashboard(data):
    await websocket.broadcast({
        "type": "world_model_update",
        "data": data
    })
```

## Integration with Core

System plugins have direct access to:
- `world_model` - The immutable event log
- `agent_bridge` - Communication with agents
- `tool_registry` - Available tools

See [EVENT_DRIVEN_ARCHITECTURE.md](../../docs/EVENT_DRIVEN_ARCHITECTURE.md) for the nervous system model.
