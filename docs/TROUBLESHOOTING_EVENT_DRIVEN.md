# Event-Driven Troubleshooting Guide

This guide helps you diagnose and fix issues when working with ANSE's event-driven architecture.

---

## Common Issues

### Problem: "My agent doesn't respond to sensor changes"

**Symptoms:**
- Agent runs but never processes sensor events
- Console shows no output when sensors change
- Dashboard shows events but your code doesn't react

**Root Causes:**

1. **Not listening to WebSocket messages** — Agent exits immediately instead of awaiting events

   **❌ Wrong:**
   ```python
   async with websockets.connect("ws://127.0.0.1:8765") as ws:
       # Missing async for loop!
       pass  # Function exits immediately
   ```

   **✅ Right:**
   ```python
   async with websockets.connect("ws://127.0.0.1:8765") as ws:
       async for message in ws:  # Keeps listening
           event = json.loads(message)
           await handle(event)
   ```

2. **Not parsing event structure correctly** — Missing nesting levels

   **❌ Wrong:**
   ```python
   async for message in ws:
       event = json.loads(message)
       # Error: event is often {"type": "world_model_update", "events": [...]}
       if event["type"] == "sensor_reading":  # Wrong key!
           pass
   ```

   **✅ Right:**
   ```python
   async for message in ws:
       msg = json.loads(message)
       if msg.get("type") == "world_model_update":
           for event in msg.get("events", []):
               if event["type"] == "sensor_reading":
                   handle_sensor(event)
   ```

3. **Checking wrong event type** — Event types don't match your regex

   **✅ Valid event types:**
   - `sensor_reading` — Sensor emitted a value
   - `reflex_triggered` — Reflex fired
   - `tool_call` — Agent called a tool
   - `tool_result` — Tool returned a value
   - `memory_stored` — Agent wrote to memory
   - `world_model_update` — Server pushing batch of events

   **Check:** Print event types to verify what's coming through:
   ```python
   async for message in ws:
       msg = json.loads(message)
       if msg.get("type") == "world_model_update":
           for event in msg.get("events", []):
               print(f"Event type: {event['type']}")  # Debug output
   ```

**Solution:**
1. Verify WebSocket connection is open: `print("Connected!")` inside the `async with` block
2. Add debug prints for every message received
3. Check event structure with `json.dumps(event, indent=2)`
4. Compare against docs/EVENT_DRIVEN_ARCHITECTURE.md examples

---

### Problem: "Hardware polling is still happening (LED constantly blinking)"

**Symptoms:**
- Camera LED stays on constantly
- CPU usage high even at idle
- Battery drains quickly on mobile

**Root Causes:**

1. **Dashboard still polling for hardware state** — Calling `get_detected_devices()` in a loop

   **Check:** Open browser console, look for repeated network requests to `/api/detected-devices`

   **✅ Should be:** Dashboard calls once on startup, then listens for server-pushed updates

2. **Browser tab running setInterval() polling** — Periodic AJAX requests

   **Check:** Search your code for:
   ```javascript
   setInterval(loadData, 2000)  // ❌ This is polling!
   ```

   **Should be:**
   ```javascript
   ws.onmessage = (msg) => updateUI(JSON.parse(msg.data))  // ✅ This is event-driven
   ```

3. **Agent polling for sensor state** — `while True` loop with `sleep()`

   **Check:** Look for `while True:` or `while self.running:` in your agent code

   **Solution:** Replace with event listener:
   ```python
   # ❌ Remove this:
   while True:
       data = await get_sensor()
       process(data)
       await asyncio.sleep(1)

   # ✅ Use this:
   async for event in event_stream:
       if event["type"] == "sensor_reading":
           process(event)
   ```

**Verification:**
```bash
# On Windows, watch for OpenCV camera access
Get-Process | Where-Object {$_.Handles -gt 100} | Select-Object ProcessName, Handles

# On Linux, watch for /dev/video access frequency
inotifywait -m /dev/video0 | head -20  # Should be sparse, not continuous
```

**Solution:**
1. Remove all `setInterval()` calls from dashboard
2. Remove all `while True: ... await asyncio.sleep()` loops from agents
3. Replace with `async for message in websocket_stream:`
4. Test: Hardware should only be queried on-demand

---

### Problem: "Reflexes aren't reacting to sensor events"

**Symptoms:**
- Sensor readings show in world model
- Reflex conditions are met
- But reflex actions don't fire

**Root Causes:**

1. **Reflex system not receiving events** — Missing integration between world model and reflexes

   **Check:** Look for `process_world_model_event()` method being called

   **In engine_core.py:**
   ```python
   # Should have something like:
   async def on_world_model_event(event):
       if event.get("type") == "sensor_reading":
           await reflex_system.process_world_model_event(event)
   ```

2. **Reflex condition logic is wrong** — Threshold check is inverted

   **❌ Wrong:**
   ```python
   if event["value"] < 80 and sensor_should_trigger_HIGH:  # Backwards!
       await trigger()
   ```

   **✅ Right:**
   ```python
   if event["value"] > 80:  # Sensor exceeded threshold
       await trigger()
   ```

3. **Missing reflex rule match** — Reflex configured for different sensor name

   **Check:** Verify sensor names match between:
   - Sensor emission: `event["sensor"] = "temperature"`
   - Reflex config: `sensor: "temperature"` ✅ (must match)

   **Common mismatches:**
   - `"temp"` vs `"temperature"`
   - `"motion"` vs `"motion_detected"`
   - `"cam0"` vs `"camera_0"`

**Solution:**
1. Add debug logging to `process_world_model_event()`:
   ```python
   async def process_world_model_event(self, event):
       print(f"Reflex received: {event}")  # Debug
       for reflex in self.reflexes:
           print(f"Checking {reflex.sensor} against {event['sensor']}")
   ```

2. Check `plugins/reflex_system/example.yaml` for syntax errors
3. Verify sensor names in logs match your reflex rules

---

### Problem: "Agent sometimes misses events"

**Symptoms:**
- Event shows in world model but agent didn't process it
- Happens unpredictably
- More frequent when multiple clients connected

**Root Causes:**

1. **Event buffer overflow** — More events generated than agent can consume

   **Why:** Server broadcasts every 3 seconds; if 100 events accumulate faster than agent processes them, buffer fills

   **Check:**
   ```python
   # If this logs delays, you're falling behind:
   async for message in ws:
       start = time.time()
       payload = json.loads(message)
       process_time = time.time() - start
       if process_time > 1:  # Processing taking too long
           print(f"Warning: Slow processing: {process_time}s")
   ```

2. **Blocking I/O in event handler** — Processing events synchronously

   **❌ Wrong:**
   ```python
   async for message in ws:
       event = json.loads(message)
       result = process_sync(event)  # Blocks event loop!
       await send_result(result)
   ```

   **✅ Right:**
   ```python
   async for message in ws:
       event = json.loads(message)
       # Create background task instead of blocking
       asyncio.create_task(process_async(event))
   ```

3. **WebSocket connection dying silently** — Connection lost without exception

   **Check:** Wrap in try/except:
   ```python
   try:
       async for message in ws:
           ...
   except websockets.ConnectionClosed:
       print("WebSocket closed, reconnecting...")
       # Reconnect logic here
   ```

**Solution:**
1. Make all event handlers truly async — no blocking calls
2. Monitor event processing time with timestamps
3. Consider batching slow operations:
   ```python
   pending_tasks = []
   async for message in ws:
       event = json.loads(message)
       if event["type"] == "sensor_reading":
           # Non-blocking: start task but don't await
           pending_tasks.append(asyncio.create_task(process(event)))
           # Clean up completed tasks
           pending_tasks = [t for t in pending_tasks if not t.done()]
   ```

---

### Problem: "Dashboard shows old data after reconnect"

**Symptoms:**
- Browser refreshes or tab comes back to focus
- Dashboard shows stale information
- Events are lost between reconnects

**Root Causes:**

1. **Missing event history on reconnect** — Client reconnects but doesn't get past events

   **Why:** Server only broadcasts events as they happen; connects in progress don't get history

   **Check:** World model should have persistent event log

   **Solution:** On first connection, fetch recent events:
   ```python
   async with websockets.connect(...) as ws:
       # Get recent history
       history = await get_world_model_events(limit=100)
       process_all(history)
       
       # Now listen for new events
       async for message in ws:
           ...
   ```

2. **Server-side event buffer too small** — Old events are pruned

   **Check:** Look for `trim_world_model()` calls in dashboard_server.py

   **Increase buffer:**
   ```python
   # In dashboard_server.py, increase limit:
   events = await self.plugins["dashboard_bridge"].get_world_model_events(limit=1000)  # Was 10
   ```

**Solution:**
1. Implement persistent world model storage (JSONL file)
2. On client reconnect, fetch full history first
3. Increase server-side event buffer

---

### Problem: "Tool calls aren't being reflected in world model"

**Symptoms:**
- Agent calls a tool with `call_tool("do_something")`
- Tool actually executes (you can see effects)
- But `tool_call` event doesn't appear in world model

**Root Causes:**

1. **Tool calls happening outside event loop** — Called directly instead of through world model

   **❌ Wrong:**
   ```python
   # Calling tool directly, not recorded
   result = await tool_registry.call("capture_frame", {})
   ```

   **✅ Right:**
   ```python
   # Calling through engine, which records event
   result = await engine.call_tool("capture_frame", {})
   ```

2. **Engine tool wrapper not recording events** — Missing audit trail logic

   **Check:** In engine_core.py, tool_registry.call() should record to world model:
   ```python
   async def call_tool(self, name, args):
       # Record tool call
       call_id = await self.world_model.record({
           "type": "tool_call",
           "tool": name,
           "args": args,
       })
       # Execute tool
       result = await self.tools[name](**args)
       # Record result
       await self.world_model.record({
           "type": "tool_result",
           "call_id": call_id,
           "result": result,
       })
       return result
   ```

**Solution:**
1. Always call tools through `engine.call_tool()`, not directly
2. Verify `world_model.record()` is being called for all tool activity
3. Check world model file for tool_call entries

---

## Debugging Checklist

When something isn't working:

- [ ] **Verify connection:** Can agent connect to WebSocket? Add `print("Connected!")` 
- [ ] **Check event types:** Print every message received. Compare against docs
- [ ] **Monitor CPU/disk:** Is polling happening somewhere? Check system activity
- [ ] **Inspect world model:** Read `/tmp/anse_world_model.jsonl` (or wherever it's stored)
- [ ] **Check logs:** Are there error messages in engine or agent stderr?
- [ ] **Test in isolation:** Can dashboard receive events without your agent?
- [ ] **Test timing:** Are events being emitted fast enough?
- [ ] **Verify event structure:** `json.dumps(msg, indent=2)` to see exact format

---

## Getting Help

When reporting issues, include:

1. **Full error message** — Copy/paste traceback
2. **Minimal reproducer** — Smallest code that fails
3. **World model excerpt** — Last 20 lines of `/tmp/anse_world_model.jsonl`
4. **Event log** — What events were received before failure?
5. **System info** — Windows/Mac/Linux, Python version, hardware

Example issue report:
```
Agent doesn't process motion events

Reproducer:
```python
async with websockets.connect("ws://127.0.0.1:8765") as ws:
    async for msg in ws:
        print(msg)
```

Expected: Prints events when sensor is triggered
Actual: Prints nothing, even after manual trigger

World model: (paste last 30 lines)
```

---

## References

- [Event-Driven Architecture](EVENT_DRIVEN_ARCHITECTURE.md) — Complete pattern guide
- [Quick Start](QUICKSTART.md) — Working examples
- [API Reference](API.md) — Method signatures
