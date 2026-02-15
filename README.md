# ANSE — Agent State & Event Engine

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)

**Connect an LLM to hardware. Enforce safety rules. Log everything.**

ANSE is a control relay for autonomous agents. You write hardware rules, ANSE enforces them, and your agent reads sensors and sends commands via WebSocket.

---

## Start Here (30 seconds)

```yaml
# 1. Define state
sensors:
  motion_detected: false
  temperature_c: 27.3

actuators:
  fan_state: off

# 2. Define safety rules
rules:
  - if: motion_detected == false
    then: deny fan  # Don't cool empty houses
  
  - if: temperature_c > 40
    then: force fan on  # Auto-cool on overheat
```

```python
# 3. Agent connects and acts
agent = await connect("ws://localhost:8001")
state = await agent.get_state()

# Read: {motion_detected: false, temperature_c: 27.3, ...}
# Send: Command to turn fan on
# ANSE checks rules → Command rejected (house is empty)
# Agent adapts based on the rejection
```

---

## Why ANSE Exists

**Problem:** You have an LLM that should control hardware, but safety rules live nowhere and actions aren't logged.

ANSE solves this:
- **One place for rules** — YAML, not scattered code
- **One place for state** — JSON, not five different systems
- **One API for agents** — WebSocket, not custom protocols
- **Full audit trail** — Every decision logged and hashed

---

## What You Can Build

- Home automation with occupancy rules
- Robotics with collision detection and emergency stops
- IoT systems with rate limiting and permissions
- Research with reproducible, logged agent-environment interaction

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Quick Start

**Start the backend:**
```bash
python backend/websocket_backend.py
```
Listens on `ws://localhost:8001`

**(Optional) Run the dashboard:**
```bash
cd dashboard && python -m http.server 8002
```
Open `http://localhost:8002/` to watch events in real-time.

**Run an example agent:**
```bash
python examples/demo_agent.py
```

---

## Core Concepts

### Sensors
Input devices (cameras, temperature sensors, motion detectors, etc.) that emit readings.

### State Store
A timestamped JSON object that captures the current state of all sensors and actuators:
```json
{
  "timestamp": "2026-02-15T12:34:56Z",
  "sensors": {
    "temperature_c": 27.3,
    "motion_detected": false
  },
  "actuators": {
    "fan_state": "off"
  }
}
```

### Safety Rules
YAML-based rules that validate all commands before they execute. Rules can:
- Block commands: `if motion==false, deny fan`
- Auto-trigger: `if temp > 40, force fan on`
- Emit alerts: `if pressure > 100psi, alert`

Rules always run before commands reach actuators.

### Actuators
Hardware outputs (motors, heaters, relays, etc.). Controlled by commands or direct rule triggers. All operations logged.

### Agents
External processes (LLM agents, scripts, etc.) that:
- Connect via WebSocket to `ws://localhost:8001`
- Read current state
- Send commands (which ANSE validates against rules)
- Observe rejections and adapt behavior

---

## How Agents Connect

**ANSE manages state and validates commands. Your agent decides what to do.**

Your agent connects to the WebSocket backend and:

```python
import asyncio
import json
import websockets

async def my_agent():
    uri = "ws://localhost:8001"
    async with websockets.connect(uri) as ws:
        # 1. Receive state updates from sensors
        async for message in ws:
            event = json.loads(message)
            
            # 2. Make decisions based on state
            if event["type"] == "sensor":
                distance = event["data"]["value"]
                if distance < 10:
                    # 3. Send commands (ANSE validates)
                    command = {
                        "action": "execute_actuator",
                        "actuator": "movement",
                        "state": "STOP"
                    }
                    await ws.send(json.dumps(command))

asyncio.run(my_agent())
```

That's the whole pattern: **read state → decide → send command → ANSE validates → agent sees result**.

---

## Architecture

```
┌──────────────────────────┐
│  Your Agent (LLM/Script) │
│   WebSocket Connection   │
└───────────┬──────────────┘
            │
            ↕ ws://localhost:8001
            │
┌───────────────────────────────────┐
│      ANSE Control Relay           │
├───────────────────────────────────┤
│  Sensors → State Store            │
│  State Store → Rule Engine        │
│  Rule Engine → Actuators          │
│  All Events → Audit Log           │
└───────────────────────────────────┘
            │
            ↓
        Hardware
```

---

## Built-In Tools

| Tool | Purpose |
|------|---------|
| `capture_frame()` | Capture camera frame (640×480) |
| `list_cameras()` | List available cameras |
| `analyze_frame()` | Edge/corner detection, color histogram |
| `record_audio()` | Record from microphone |
| `list_audio_devices()` | List microphones and speakers |
| `analyze_audio()` | FFT frequency analysis, RMS, peak |
| `say()` | Text-to-speech synthesis |
| `get_voices()` | List TTS voices |

All tools have simulated equivalents (set `ANSE_SIMULATE=1` to test without hardware).

---

## Safety & Audit

Safety is built-in, not bolted-on:

| Feature | Details |
|---------|---------|
| **Rules** | Block, allow, or trigger commands based on state |
| **Permissions** | Per-agent scopes for camera, mic, network, filesystem |
| **Rate Limiting** | Per-tool limits (e.g., 30 camera calls/min) |
| **Audit Trail** | Immutable JSONL log with SHA256 hashes |
| **Isolation** | Per-agent quotas prevent interference |

Audit log entry:
```json
{
  "timestamp": "2026-02-14T10:30:45Z",
  "agent_id": "agent-001",
  "tool": "capture_frame",
  "status": "success",
  "duration_ms": 145
}
```

---

## Plugins

Add custom sensors, actuators, or tools.

**YAML plugin (5 minutes):**
```yaml
# plugins/temp_sensor.yaml
name: temp_sensor
description: Temperature sensor

tools:
  - name: read_temp
    description: Read temperature
    handler: |
      return {"temp_c": 23.5, "timestamp": datetime.now().isoformat()}
```

**Python plugin:**
```python
# plugins/my_plugin.py
from anse.plugin import SensorPlugin

class MyPlugin(SensorPlugin):
    name = "my_plugin"
    async def read_sensor(self):
        return {"status": "ok", "value": 42}
```

See [docs/PLUGINS.md](docs/PLUGINS.md) for complete guide.

---

## What ANSE Is NOT

- **Not a VLA model** — No vision+language+action branches
- **Not a world model** — No neural networks, no inference
- **Not a planning system** — No motion planning or autonomous reasoning
- **Not AGI** — Deterministic rule enforcement

ANSE is: **A deterministic control relay that enforces rules and logs everything.**

---

## Documentation

| Guide | Audience |
|-------|----------|
| [QUICKSTART.md](docs/QUICKSTART.md) | Get started in 5 minutes |
| [API.md](docs/API.md) | WebSocket method reference |
| [DESIGN.md](docs/DESIGN.md) | Architecture deep-dive |
| [PLUGINS.md](docs/PLUGINS.md) | Extend with custom tools |
| [AUDIT_REPORT_FEB_2026.md](docs/AUDIT_REPORT_FEB_2026.md) | What's implemented |
| [PHASE_4_ROADMAP.md](docs/PHASE_4_ROADMAP.md) | Future features |
| [WHAT_ANSE_IS.md](docs/WHAT_ANSE_IS.md) | Project rationale |

All docs in [docs/](docs/) folder.

---

## Project Status

| Component | Status |
|-----------|--------|
| Core engine | ✅ Stable (tested, production-ready) |
| Sensor tools | ✅ Complete (7 tools) |
| Safety rules | ✅ Complete |
| Audit logging | ✅ Complete (SHA256 hashing) |
| WebSocket API | ✅ Complete |
| Dashboard | ✅ Complete (HTML/CSS/JS, zero deps) |
| Tests | ✅ Complete (111+ passing) |
| Documentation | ✅ Complete (8 guides) |

---

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

All 111+ tests passing.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for reporting issues and submitting PRs.

---

## License

MIT License — See [LICENSE](LICENSE)

---

## Citation

```bibtex
@software{anse2026,
  title={ANSE: Agent State & Event Engine},
  author={13thrule},
  year={2026},
  url={https://github.com/13thrule/ANSE-Agent-State-Event-Engine}
}
```

---

**Status:** Stable and production-ready  
**Python:** 3.8+ | **Platform:** Windows, macOS, Linux  
**Last Updated:** February 2026
