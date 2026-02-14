# Event-Driven Implementation Checklist

This document provides a step-by-step checklist for implementing event-driven ANSE agents, components, and systems.

---

## Phase 1: Understanding (Days 1-2)

### Knowledge Base
- [ ] Read [EVENT_DRIVEN_ARCHITECTURE.md](EVENT_DRIVEN_ARCHITECTURE.md) — Complete overview of nervous system model
- [ ] Read [MIGRATION_POLLING_TO_EVENTS.md](MIGRATION_POLLING_TO_EVENTS.md) — Pattern conversions
- [ ] Review [anse/examples/event_driven_agent.py](../anse/examples/event_driven_agent.py) — Reference implementation
- [ ] Review [docs/QUICKSTART.md](QUICKSTART.md) — Working examples

### Conceptual Understanding
- [ ] **Polling** — Understand why continuous checking (while loops + sleep) is wasteful
- [ ] **Events** — Understand reactive model where systems emit signals
- [ ] **World Model** — Understand immutable event log as source of truth
- [ ] **Reflexes** — Understand instant reactions vs. LLM decisions
- [ ] **Audit Trail** — Understand complete event history for debugging/replay

### Mental Model Check
Ask yourself:
- [ ] Can you explain why event-driven is better than polling? (hint: efficiency + latency)
- [ ] Do you understand the WebSocket event subscription pattern?
- [ ] Can you identify polling anti-patterns in existing code?
- [ ] Can you explain the difference between server-push vs. client-pull?

**Stop and reread if:** You're not 100% comfortable with the mental shift from "ask for status" to "listen for events"

---

## Phase 2: Setup (Day 3)

### Environment
- [ ] Python 3.8+ installed
- [ ] ANSE source code cloned: `git clone https://github.com/13thrule/ANSE-Agent-Nervous-System-Engine`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Engine can start: `python -m anse.engine_core` (should not crash)

### Workspace Organization
- [ ] Create `/agent` directory for your custom agents
- [ ] Create `/sensors` directory for custom sensor plugins (if needed)
- [ ] Create `/logs` directory for debugging output
- [ ] Setup `.gitignore` for Python: `__pycache__/`, `*.pyc`, `venv/`, `.env`

### Testing Infrastructure
- [ ] Create `/tests` directory for test files
- [ ] Create separate test environment: `python -m venv test_env`
- [ ] Install test dependencies: `pip install pytest pytest-asyncio`

---

## Phase 3: Implementation (Days 4-7)

### Code Structure Template

Use this template for all event-driven agents:

```python
# src/agents/my_agent.py

import asyncio
import json
import websockets
from typing import Any, Dict

class MyAgent:
    def __init__(self, engine_url: str = "ws://127.0.0.1:8765"):
        self.engine_url = engine_url
        self.websocket = None
    
    async def connect(self) -> None:
        """Connect to ANSE engine."""
        self.websocket = await websockets.connect(self.engine_url)
    
    async def disconnect(self) -> None:
        """Disconnect from engine."""
        if self.websocket:
            await self.websocket.close()
    
    async def listen(self) -> None:
        """Main event loop."""
        if not self.websocket:
            await self.connect()
        
        try:
            async for message in self.websocket:
                await self.on_message(message)
        except websockets.ConnectionClosed:
            print("Connection lost, reconnecting...")
            await self.connect()
            await self.listen()
    
    async def on_message(self, message: str) -> None:
        """Process incoming event."""
        try:
            msg = json.loads(message)
            if msg.get("type") == "world_model_update":
                for event in msg.get("events", []):
                    await self.on_event(event)
        except json.JSONDecodeError:
            print(f"Failed to parse: {message}")
    
    async def on_event(self, event: Dict[str, Any]) -> None:
        """React to a specific event. Override in subclasses."""
        event_type = event.get("type")
        
        if event_type == "sensor_reading":
            await self.on_sensor_reading(event)
        elif event_type == "result":
            await self.on_tool_result(event)
        elif event_type == "reflex_triggered":
            await self.on_reflex(event)
    
    async def on_sensor_reading(self, event: Dict[str, Any]) -> None:
        """React to sensor data. Override for custom behavior."""
        print(f"Sensor {event['sensor']}: {event['value']}")
    
    async def on_tool_result(self, event: Dict[str, Any]) -> None:
        """React to tool completion. Override for custom behavior."""
        print(f"Tool {event['tool']} completed: {event['result']}")
    
    async def on_reflex(self, event: Dict[str, Any]) -> None:
        """React to reflex firing. Override for custom behavior."""
        print(f"Reflex {event['reflex_id']} triggered")
    
    async def run(self) -> None:
        """Run the agent (main entrypoint)."""
        await self.listen()


# Usage
if __name__ == "__main__":
    agent = MyAgent()
    asyncio.run(agent.run())
```

### Implementation Checklist

For each component:

#### If Building an Agent:
- [ ] Create class extending base pattern (above)
- [ ] Implement `on_event()` handler for each event type you care about
- [ ] Handle `sensor_reading` events (most common)
- [ ] Handle `tool_result` events
- [ ] Add tool calling via `engine.call_tool()`
- [ ] Add memory writing via `engine.remember()`
- [ ] Connection management: reconnect on websocket close
- [ ] Error handling: try/except around JSON parsing and event processing
- [ ] Logging: add debug output for development
- [ ] **NO** polling loops (`while True`)
- [ ] **NO** `asyncio.sleep()` for timing (only for test delays)
- [ ] **NO** periodic status checks

#### If Building a Sensor Plugin:
- [ ] Define plugin in YAML: `plugins/my_sensor/plugin.yaml`
- [ ] Implement plugin class with `emit_reading()` method
- [ ] Emit events to world model: `await engine.world_model.record(event)`
- [ ] Event includes: `type`, `sensor`, `value`, `timestamp`
- [ ] No continuous polling: only emit when state changes
- [ ] Document sensor API in plugin README

#### If Building a Tool:
- [ ] Add tool function to `tool_registry`
- [ ] Tool should be async: `async def my_tool(arg1, arg2) -> result`
- [ ] Return result immediately (execution tracked separately)
- [ ] Document tool in tool registry
- [ ] No tool should poll hardware repeatedly

#### If Building a Reflex:
- [ ] Define in `plugins/reflex_system/rules.yaml`
- [ ] Specify: sensor, threshold condition, action tool
- [ ] Reflex system will handle event-driven triggering automatically
- [ ] Action should be idempotent (safe to fire multiple times)

#### If Building a Dashboard Component:
- [ ] Use WebSocket client: `ws = new WebSocket(...)`
- [ ] Listen for server-pushed events: `ws.onmessage = ...`
- [ ] **NO** polling intervals (`setInterval()`)
- [ ] **NO** periodic AJAX requests (`fetch()` in loop)
- [ ] Hardware queries on-demand only (button clicks)
- [ ] UI updates on event receipt, not timer

### Code Quality Checklist

- [ ] All async functions properly declared with `async def`
- [ ] All awaits present: `await function_call()` not just `function_call()`
- [ ] Event handler has `if/elif` chain for different event types
- [ ] `.get()` used for optional fields: `event.get("value")`
- [ ] No blocking calls in event handler (use `asyncio.create_task()` if needed)
- [ ] Connection handling: reconnect logic on websocket close
- [ ] Graceful shutdown: cleanup on `Ctrl+C`
- [ ] Type hints present: `def foo(x: str) -> bool:`
- [ ] Docstrings on public methods
- [ ] No hardcoded values (use config files or env vars)

---

## Phase 4: Testing (Day 8)

### Unit Tests

```python
# tests/test_my_agent.py

import pytest
import asyncio
from src.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_sensor_reading_handling():
    agent = MyAgent()
    
    # Create fake sensor event
    event = {
        "type": "sensor_reading",
        "sensor": "motion",
        "value": True
    }
    
    # Verify handling (would need to expose processed data)
    result = await agent.on_sensor_reading(event)
    # assert result == expected


@pytest.mark.asyncio
async def test_reconnect_on_disconnect():
    agent = MyAgent()
    # Simulate connection loss
    # Verify reconnection happens
    pass
```

### Integration Tests

- [ ] Start engine in subprocess: `subprocess.Popen("python -m anse.engine_core")`
- [ ] Agent connects and receives events
- [ ] Verify events processed in order
- [ ] Verify tool calls recorded in world model
- [ ] Verify reconnection after engine restart

### Performance Tests

- [ ] Event processing: < 1ms per event
- [ ] WebSocket throughput: > 1000 events/second
- [ ] Memory stable: no growth over 1000 events
- [ ] No CPU spike: agent idle uses < 5% CPU

### Manual Testing

1. **Terminal 1 — Start engine:**
   ```bash
   python -m anse.engine_core
   ```

2. **Terminal 2 — Start agent:**
   ```bash
   python src/agents/my_agent.py
   ```

3. **Terminal 3 — Trigger sensor:**
   ```python
   import asyncio
   from anse.engine_core import ANSEEngine
   
   async def trigger():
       engine = ANSEEngine()
       await engine.world_model.record({
           "type": "sensor_reading",
           "sensor": "motion",
           "value": True
       })
   
   asyncio.run(trigger())
   ```

4. **Verify:** Agent logs reaction to event in Terminal 2

---

## Phase 5: Documentation (Day 9)

For each new component, create:

### README.md (in component directory)
- [ ] Purpose: What does this do?
- [ ] Architecture: How does it work?
- [ ] Events: What events does it handle?
- [ ] Example usage: Copy-pasteable code
- [ ] Configuration: Any settings?

### Docstrings (in code)
- [ ] Module docstring at top
- [ ] Class docstring explaining purpose
- [ ] Method docstring for public methods
- [ ] Example in docstring for complex methods

### Example Script
- [ ] Create `/examples/my_agent_example.py`
- [ ] Runnable standalone
- [ ] Comments explaining event flow
- [ ] Works with simulated hardware: `ANSE_SIMULATE=1`

---

## Phase 6: Validation (Day 10)

### Final Checklist

**Architecture:**
- [ ] Can clearly explain nervous system model
- [ ] Can identify any remaining polling anti-patterns
- [ ] Understand world model as source of truth
- [ ] Understand reflex system event-driven triggering

**Code Quality:**
- [ ] No `while True` loops (except intentional broadcast loop)
- [ ] No `asyncio.sleep()` except in tests
- [ ] No `setInterval()` or periodic `fetch()`
- [ ] All async code properly marked async/await
- [ ] Error handling: try/except in event handlers
- [ ] Logging: debug prints for development

**Testing:**
- [ ] Unit tests pass: `pytest tests/`
- [ ] Integration test passes: engine + agent communicate
- [ ] Manual test passes: agent reacts to triggered events
- [ ] No memory leaks: run overnight, check memory stable

**Documentation:**
- [ ] README explains purpose
- [ ] Code is self-documenting (clear names)
- [ ] Example script is runnable
- [ ] Events documented in code/docs

**Performance:**
- [ ] CPU < 5% at idle
- [ ] No continuous hardware polling
- [ ] < 100ms latency from event to reaction
- [ ] Handles 1000+ events/second

### Sign-Off

Person completing: _________________ Date: _____________

- [ ] All items complete
- [ ] No warnings or TODOs left in code  
- [ ] Ready for production use

---

## Common Pitfalls to Avoid

### ❌ Polling Anti-Patterns

```python
# DON'T: Poll for status
while True:
    status = await get_status()
    await asyncio.sleep(1)

# DON'T: Check conditions repeatedly
while self.running:
    for reflex in self.reflexes:
        if await reflex.check():
            await reflex.trigger()
    await asyncio.sleep(0.1)

# DON'T: Periodic hardware queries
setInterval(() => {
    fetch("/api/hardware/status")
}, 5000)
```

### ❌ Common Event Handler Mistakes

```python
# DON'T: Forget to unwrap events
async for msg in ws:
    if msg["type"] == "sensor_reading":  # Wrong nesting!

# DON'T: Crash on missing fields
value = msg["value"]  # Use .get() instead

# DON'T: Block the event loop
result = blocking_call()  # Use asyncio.create_task()

# DON'T: Ignore connection errors
async for msg in ws:
    # No exception handling
```

### ❌ Testing Anti-Patterns

```python
# DON'T: Sleep to wait for events
time.sleep(1)
assert event_received  # Flaky!

# DON'T: Test polling behavior
agent.poll_interval = 0.1
time.sleep(0.2)

# DON'T: Mock entire world model
with patch('world_model') as mock:
    # Too much mocking
```

---

## Success Criteria

Your event-driven system is working correctly when:

✅ **No polling** — No `while True`, no `setInterval()`, no repeated `sleep()` calls
✅ **Instant reactions** — Agent reacts to events in < 100ms
✅ **Low resource usage** — CPU < 5% at idle, memory stable
✅ **Deterministic** — Same event sequence always produces same output
✅ **Auditable** — World model event log shows complete execution history
✅ **Scalable** — Add more agents without overloading system
✅ **Testable** — Can replay events to reproduce any scenario

---

## Deployment Checklist

Before going to production:

- [ ] Run all tests: `pytest tests/`
- [ ] No Python warnings: `python -W all agent.py`
- [ ] Linting passes: `flake8 src/`
- [ ] Type hints check: `mypy src/`
- [ ] Memory profiling: 24-hour test, no leaks
- [ ] Load test: 100 events/second for 1 hour
- [ ] Documentation complete and reviewed
- [ ] Example working with real hardware
- [ ] Example working with simulated hardware
- [ ] Security review: no credential leaks, no injection vulnerabilities
- [ ] Error handling: all error paths tested
- [ ] Logging: sufficient for debugging production issues
- [ ] Monitoring: metrics exposed for alerting

---

## Quick Reference

### Event Types You'll Handle

```python
# Sensor emitted a reading
{
    "type": "sensor_reading",
    "sensor": "motion",
    "value": True
}

# Tool was called
{
    "type": "tool_call",
    "tool": "capture_frame",
    "args": {...}
}

# Tool completed
{
    "type": "tool_result",
    "tool": "capture_frame",
    "result": {...}
}

# Reflex fired
{
    "type": "reflex_triggered",
    "reflex_id": "emergency_stop",
    "sensor": "collision"
}

# Agent remembered something
{
    "type": "memory_stored",
    "agent_id": "explorer",
    "content": "found treasure"
}
```

### Essential Imports

```python
import asyncio
import json
import websockets
from typing import Dict, Any, Optional
```

### Essential Pattern

```python
async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        async for message in ws:
            event = json.loads(message)
            await process(event)

asyncio.run(main())
```

---

## Further Resources

- [EVENT_DRIVEN_ARCHITECTURE.md](EVENT_DRIVEN_ARCHITECTURE.md) — Detailed explanation
- [MIGRATION_POLLING_TO_EVENTS.md](MIGRATION_POLLING_TO_EVENTS.md) — Converting existing code
- [TROUBLESHOOTING_EVENT_DRIVEN.md](TROUBLESHOOTING_EVENT_DRIVEN.md) — Problem solving
- [anse/examples/](../anse/examples/) — Working examples
- [docs/QUICKSTART.md](QUICKSTART.md) — Getting started
- [docs/API.md](API.md) — API reference
