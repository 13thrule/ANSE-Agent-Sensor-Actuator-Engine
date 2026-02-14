# ANSE Event-Driven Architecture

## Overview

ANSE implements a **nervous system model** where agents and systems interact through an append-only event log, rather than continuous polling or request-response patterns.

Think of it like a biological nervous system:
- **Sensors** emit signals when stimulated (event emission)
- **Reflexes** react instantly without waiting for the brain (event handlers) 
- **The Brain** receives updates through the nervous system (world model)
- **Motor control** executes actions based on decisions (tool calls)
- **Memory** stores experiences for future reference (long-term memory)

All of this flows through the **world model**, which is the immutable, append-only event log that serves as the source of truth.

---

## Core Principles

### 1. No Polling

❌ **Don't do this:**
```python
while True:
    data = get_sensor()
    process(data)
    await asyncio.sleep(1)  # Wasteful polling
```

✅ **Do this:**
```python
async for event in event_stream:
    await process(event)  # React to events as they occur
```

### 2. World Model is Authority

All state changes flow through the world model:
```
Sensor capturesframe → World Model records event → Event pushed to subscribers → 
Agents react → Agent calls tool → World Model records tool call → Reflexes react
```

Never assume hardware state. Always trust the world model event log.

### 3. Event-Driven Agents

Agents don't periodically check what's happening. They listen:

```python
# Connect to ANSE
async with websockets.connect("ws://127.0.0.1:8765") as ws:
    # Listen for world model events
    async for message in ws:
        event = json.loads(message)
        if event.get("type") == "sensor_reading":
            await handle_sensor(event)
```

### 4. Reflexes are Fast Pathways

Reflexes react to world model events instantly (no LLM):

```python
# When temperature sensor emits a reading
async def process_world_model_event(event):
    if event["type"] == "sensor_reading" and event["sensor"] == "temp":
        if event["value"] > 80:  # Threshold crossed
            # INSTANT reaction - no LLM delay
            await call_tool("emergency_cooler_on")
```

### 5. Agents Make Strategic Decisions

Agents observe events and decide what to do:

```python
async def agent_loop():
    async for event in world_model_stream:
        # I perceive what happened
        if event["type"] == "motion_detected":
            # I decide to investigate
            frame = await call_tool("capture_frame")
            analysis = await call_tool("analyze_frame", {"frame_id": frame["id"]})
            # I remember the experience
            await call_tool("remember", {"content": analysis["summary"]})
```

### 6. All Actions are Audited

Every action is recorded to the world model with timestamps and hashes:

```json
{
  "type": "tool_call",
  "timestamp": "2026-02-14T10:30:45Z",
  "agent_id": "explorer-001",
  "tool": "capture_frame",
  "args_hash": "abc123...",
  "result_hash": "def456...",
  "status": "success",
  "duration_ms": 145
}
```

This enables complete replay and debugging.

---

## Event Types

### Sensor Events

Emitted when a sensor takes a reading:

```json
{
  "type": "sensor_reading",
  "sensor": "camera",
  "value": { "frame_id": "abc123", "width": 640, "height": 480 },
  "timestamp": 1707916245.123,
  "source_agent": null
}
```

### Reflex Events

Emitted when a reflex rule is triggered:

```json
{
  "type": "reflex_triggered",
  "reflex_id": "emergency-stop",
  "sensor": "collision_detector", 
  "threshold": 0.9,
  "value": 0.95,
  "action_tool": "emergency_stop",
  "timestamp": 1707916245.200
}
```

### Tool Call Events

Emitted when an agent calls a tool:

```json
{
  "type": "tool_call",
  "agent_id": "explorer-001",
  "call_id": "call-12345",
  "tool": "capture_frame",
  "args": { "camera_id": 0 },
  "timestamp": 1707916245.300
}
```

### Tool Result Events

Emitted when a tool completes:

```json
{
  "type": "tool_result",
  "call_id": "call-12345",
  "tool": "capture_frame",
  "status": "success",
  "result": { "frame_id": "xyz789", "width": 640, "height": 480 },
  "duration_ms": 145,
  "timestamp": 1707916245.450
}
```

### Memory Events

Emitted when long-term memory is written:

```json
{
  "type": "memory_stored",
  "memory_type": "observation",
  "agent_id": "explorer-001",
  "content": "Detected 42 motion events in the kitchen",
  "timestamp": 1707916245.500
}
```

---

## The Nervous System Model

```
┌─────────────────────────────────────────────────────────┐
│                    Agent (LLM/Script)                   │
│           Listens to world model events                 │
│           Makes decisions, calls tools                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ WebSocket (event stream)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  World Model (Brain)                    │
│           Append-only event log (source of truth)       │
│    • Sensor readings → • Tool calls → • Reflexes       │
│    • Memories → • Audit trail (immutable)               │
└────────────────┬──────────────────┬─────────────────────┘
                 │                  │
        ┌────────▼──────┐   ┌───────▼──────────┐
        │   Reflexes    │   │  Other Agents    │
        │  (Fast path)  │   │  (Subscribers)   │
        └────────────────┘   └──────────────────┘
                 ▼
        ┌──────────────────┐
        │   Tool Calls     │
        │  (Actuators)     │
        └──────────────────┘
```

---

## Pattern: Event-Driven Agent

Here's the recommended pattern for all ANSE agents:

```python
class MyAgent:
    async def run(self):
        # Connect to ANSE
        async with websockets.connect("ws://127.0.0.1:8765") as ws:
            # Listen for events (no polling!)
            async for message in ws:
                event = json.loads(message)
                
                # React to what happened
                if event.get("type") == "world_model_update":
                    for evt in event.get("events", []):
                        await self.on_event(evt)
    
    async def on_event(self, event):
        """React to a world model event."""
        if event["type"] == "sensor_reading":
            # Sensor emitted data
            pass
        elif event["type"] == "reflex_triggered":
            # A reflex fired
            pass
        elif event["type"] == "tool_result":
            # Another agent's tool completed
            pass
```

---

## Anti-Patterns (Don't Do This)

### ❌ Polling Loop
```python
# WRONG: Continuously check for updates
while True:
    status = await get_status()
    if status["changed"]:
        await handle(status)
    await asyncio.sleep(1)  # Wasteful!
```

### ❌ Continuous Sensor Reads
```python
# WRONG: Continuously poll a sensor
while True:
    frame = await capture_frame()  # Expensive!
    process(frame)
    await asyncio.sleep(2)
```

### ❌ Status Checking Loop
```python
# WRONG: Check reflexes repeatedly
while self.running:
    for reflex in self.reflexes:
        # Poll each reflex every 100ms
        if await reflex.check_threshold():
            await reflex.trigger()
    await asyncio.sleep(0.1)
```

### ✅ Correct: Event-Driven Reflexes
```python
# RIGHT: React to world model events
async def process_world_model_event(event):
    if event["type"] == "sensor_reading" and is_monitored(event["sensor"]):
        for reflex in self.reflexes:
            if reflex.sensor == event["sensor"]:
                if reflex.threshold_crossed(event["value"]):
                    await reflex.trigger()  # Instant reaction
```

---

## Benefits of Event-Driven Architecture

| Aspect | Polling | Event-Driven |
|--------|---------|--------------|
| **CPU Usage** | High (constant checking) | Low (reactive only) |
| **Latency** | Dependent on poll rate | Instant |
| **Scalability** | Single agent saturates quickly | Scales naturally |
| **Determinism** | Non-deterministic timing | Fully deterministic |
| **Auditability** | Harder to trace decisions | Complete event log |
| **Testing** | Requires mocking time | Replay events exactly |
| **Real-world match** | Doesn't match nervous systems | Mirrors biological systems |

---

## Debugging with Event Logs

Because all events are recorded, you can replay them:

```python
# Get the event log
events = await world_model.get_recent(100)

# Analyze what happened
for event in events:
    print(f"{event['timestamp']}: {event['type']} - {event.get('tool', '')}")

# Understand the sequence
# 10:30:45.001 - sensor_reading (motion_detected)
# 10:30:45.100 - reflex_triggered (motion_response)
# 10:30:45.200 - tool_call (capture_frame)
# 10:30:45.345 - tool_result (capture_frame success)
# 10:30:45.500 - agent_decision (investigate motion)
```

---

## Dashboard Subscriptions

The dashboard also uses event subscriptions, not polling:

```javascript
// Browser WebSocket client
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    
    // Server broadcasts world model events
    if (msg.type === "world_model_update") {
        updateUI(msg.events);  // No polling needed!
    }
};
```

---

## Conclusion

ANSE's event-driven architecture aligns with how embodied brains actually work:
- **Sensors emit signals** → World model records them
- **Reflexes react instantly** → No waiting for conscious thought
- **The brain decides** → Based on complete information in the world model
- **Actions execute** → Tools are called to change the world
- **Everything is audited** → Complete replay capability

This is fundamentally different from polling-based systems, and much more suitable for autonomous agents in dynamic environments.

---

## Further Reading

- [Plugin System](./PLUGINS.md) - How to add custom sensors
- [Safety & Audit](./API.md#safety) - How audit trails work
- [Agent Examples](../anse/examples/) - Reference implementations
- [Dashboard](../operator_ui/README.md) - Web UI for monitoring
