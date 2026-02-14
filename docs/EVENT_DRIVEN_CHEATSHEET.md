# Event-Driven Development Cheat Sheet

Quick reference for ANSE event-driven development patterns.

---

## Mental Models

### The Nervous System (Wrong Way vs. Right Way)

❌ **Wrong — Polling Brain:**
```
Agent: "What's happening?" → System: "Status X"
Agent: "What's happening?" → System: "Status X"  (same answer!)
Agent: "What's happening?" → System: "Status X"  (wasteful)
```

✅ **Right — Event-Driven Nervous System:**
```
Sensor: "Motion!" → Agent reacts immediately
Sensor: (silent) → Agent idle, using no resources
Sensor: "Temperature high!" → Agent reacts
```

---

## Essential Code Patterns

### Pattern 1: Basic Agent

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        async for message in ws:
            event = json.loads(message)
            print(f"Event: {event}")

asyncio.run(main())
```

### Pattern 2: Event Handler

```python
async for message in ws:
    msg = json.loads(message)
    if msg.get("type") == "world_model_update":
        for event in msg.get("events", []):
            if event["type"] == "sensor_reading":
                await handle_sensor(event)
            elif event["type"] == "tool_result":
                await handle_result(event)
```

### Pattern 3: Calling Tools

```python
# Connect to engine, then:
await engine.call_tool("my_tool", {"arg": "value"})

# Tool call will be recorded as event
# Tool result will be another event
```

### Pattern 4: Writing Memory

```python
await engine.remember("observation", {
    "content": "Detected 5 objects",
    "confidence": 0.95
})
```

---

## Event Types Reference

```json
// Sensor reading
{"type": "sensor_reading", "sensor": "motion", "value": true}

// Tool call
{"type": "tool_call", "tool": "capture_frame", "args": {...}}

// Tool result
{"type": "tool_result", "tool": "capture_frame", "result": {...}}

// Reflex triggered
{"type": "reflex_triggered", "reflex_id": "emergency_stop", "sensor": "collision"}

// Memory stored
{"type": "memory_stored", "agent_id": "explorer", "content": "..."}

// World model update (wraps events)
{"type": "world_model_update", "events": [...]}
```

---

## Do's and Don'ts

### ✅ DO
```python
# Listen to events
async for event in stream:
    await process(event)

# Use async/await
async def my_function():
    result = await other_function()
    return result

# Handle missing fields safely
value = event.get("sensor", None)

# Create background tasks for long operations
asyncio.create_task(slow_operation())

# Reconnect on disconnect
except websockets.ConnectionClosed:
    ws = await websockets.connect(url)
```

### ❌ DON'T
```python
# DON'T poll with while True
while True:
    data = await get_status()

# DON'T sleep for timing
await asyncio.sleep(5)  # except in tests

# DON'T use setInterval
setInterval(fetchData, 5000)

# DON'T access missing fields
value = event["sensor"]  # Crashes if missing!

# DON'T block event loop
result = blocking_call()  # Use create_task()

# DON'T forget to await
function_call()  # Missing await!
result = gather(tasks)  # Should be await
```

---

## Configuration

### Environment Variables

```bash
# Use simulated hardware (for testing)
ANSE_SIMULATE=1

# Engine URL
ANSE_ENGINE_URL=ws://127.0.0.1:8765

# World model file location
ANSE_WORLD_MODEL_PATH=/tmp/anse_world_model.jsonl

# Debug logging
ANSE_DEBUG=1
```

### Plugin YAML

```yaml
# plugins/my_plugin/plugin.yaml
name: My Plugin
version: "1.0"
python_module: my_plugin.plugin
tools:
  - name: my_tool
    description: What it does
    input:
      type: object
      properties:
        arg1: {type: string}
```

---

## Debugging Tricks

### Check Events in Real Time

```python
async for message in ws:
    print(json.dumps(json.loads(message), indent=2))
```

### Read World Model Log

```bash
# JSON Lines format (one event per line)
tail -100 /tmp/anse_world_model.jsonl | jq .
```

### Verify Connection

```python
try:
    async with websockets.connect(url) as ws:
        print("✓ Connected")
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f"✓ Received: {msg}")
except asyncio.TimeoutError:
    print("✗ No response")
except ConnectionRefusedError:
    print("✗ Engine not running")
```

### Trace Event Flow

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

async for message in ws:
    event = json.loads(message)
    logger.debug(f"Event: {event['type']}")
```

---

## Common Operations

### Start Engine
```bash
python -m anse.engine_core
```

### Run Agent
```bash
python my_agent.py
```

### Run with Simulation
```bash
ANSE_SIMULATE=1 python my_agent.py
```

### Run Dashboard
```bash
cd operator_ui
python app.py
```

### Test with Pytest
```bash
pytest tests/
pytest tests/test_agent.py::test_motion_handler  # Single test
pytest -v --tb=short  # Verbose with short tracebacks
```

### Profile Memory
```bash
python -m memory_profiler my_agent.py
```

---

## Performance Benchmarks

| Operation | Target | Typical |
|-----------|--------|---------|
| Event processing | < 1ms | 0.2ms |
| WebSocket message | < 5ms | 1ms |
| Tool call recording | < 10ms | 3ms |
| Reflex reaction | < 50ms | 10ms |
| Agent decision | < 1s | 0.5s |
| Dashboard update | < 100ms | 30ms |
| Idle CPU usage | < 5% | 2% |
| Memory per agent | < 50MB | 20MB |

### Optimization Tips

**If CPU high:**
1. Check for polling loops (should have 0)
2. Profile with `cProfile`: `python -m cProfile my_agent.py`
3. Check event handler is truly async (no blocking calls)

**If memory growing:**
1. Check for circular references
2. Review memory_profiler output
3. Verify world model isn't unbounded

**If latency high:**
1. Check WebSocket network latency: `ping engine_host`
2. Check agent event handler time
3. Check tool execution time

---

## Testing Template

```python
import pytest
import asyncio
from my_agent import MyAgent

@pytest.mark.asyncio
async def test_sensor_handling():
    agent = MyAgent()
    
    # Create test event
    event = {
        "type": "sensor_reading",
        "sensor": "motion",
        "value": True,
        "timestamp": 1234567890
    }
    
    # Verify agent handles it
    result = await agent.on_event(event)
    # assert result.action == "something"

@pytest.mark.asyncio
async def test_integration():
    # Start engine in subprocess
    # Connect agent
    # Send test events
    # Verify world model updated
    pass
```

---

## Learning Path

1. **5 min:** Read this cheat sheet
2. **15 min:** Run `agent_demo.py`, watch events
3. **30 min:** Read [EVENT_DRIVEN_ARCHITECTURE.md](EVENT_DRIVEN_ARCHITECTURE.md)
4. **45 min:** Build simple agent following template above
5. **1 hour:** Add your own sensor type
6. **2 hours:** Convert an existing polling system

---

## Common Mistakes

| Mistake | ❌ Wrong | ✅ Right |
|---------|---------|----------|
| **Polling** | `while True: ...` | `async for event in ...` |
| **Async** | `function()` | `await function()` |
| **Nesting** | `event["value"]` | `event.get("value")` |
| **Sleep** | `await asyncio.sleep(1)` | Remove it (event timing) |
| **Blocking** | `sync_call()` in handler | `create_task()` instead |
| **Intervals** | `setInterval(fn, 1000)` | `ws.onmessage = fn` |

---

## Quick Start (60 Seconds)

```python
# 1. Import
import asyncio, json, websockets

# 2. Define handler
async def handle(event):
    if event["type"] == "sensor_reading":
        print(f"Sensor {event['sensor']}: {event['value']}")

# 3. Main loop
async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        async for msg in ws:
            event = json.loads(msg)
            await handle(event)

# 4. Run
asyncio.run(main())
```

---

## Documentation Map

| Need | Read |
|------|------|
| **Learn basics** | [QUICKSTART.md](QUICKSTART.md) |
| **Architecture** | [EVENT_DRIVEN_ARCHITECTURE.md](EVENT_DRIVEN_ARCHITECTURE.md) |
| **Convert code** | [MIGRATION_POLLING_TO_EVENTS.md](MIGRATION_POLLING_TO_EVENTS.md) |
| **Build system** | [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) |
| **Fix problems** | [TROUBLESHOOTING_EVENT_DRIVEN.md](TROUBLESHOOTING_EVENT_DRIVEN.md) |
| **API reference** | [API.md](API.md) |
| **Make plugin** | [PLUGINS.md](PLUGINS.md) |

---

## Emergency Commands

```bash
# Engine crashed? Start fresh:
ps aux | grep python | grep engine_core | awk '{print $2}' | xargs kill -9
python -m anse.engine_core

# Stuck agent? Restart:
pkill -f my_agent.py
python my_agent.py

# Clear world model (WARNING: deletes history):
rm /tmp/anse_world_model.jsonl

# Check what's connected:
lsof -i :8765  # Linux/Mac
netstat -an | grep 8765  # Windows

# View full event log:
cat /tmp/anse_world_model.jsonl | jq .

# Pretty print logs:
jq '.' < /tmp/anse_world_model.jsonl
```

---

## Remember

The core insight: **LISTEN, DON'T ASK**

- Don't: `while True: status = get_status()`
- Do: `async for event in event_stream: handle(event)`

This changes **everything:**
- ✅ Faster responses
- ✅ Lower power usage
- ✅ Scales better
- ✅ More reliable
- ✅ Easier to debug
