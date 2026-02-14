# ANSE — Agent Nervous System Engine

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

> **Build autonomous agents that use cameras, microphones, and custom tools.**

ANSE is a local runtime engine for building autonomous agents with sensor access and tool calling. Instead of manually wiring sensor drivers and agent logic, define your tools once and agents discover + use them autonomously.

**[Quick Start](#quick-start) | [Run Demo](#run-the-demo) | [Architecture](#architecture) | [Plugins](#plugin-system) | [Docs](#documentation)**

---

## What Is ANSE?

ANSE is an open-source **local agent engine** providing:

- **📸 Camera tools** — capture frames, analyze edges/corners/colors
- **🎤 Audio tools** — record audio, analyze frequencies and amplitude
- **🔊 TTS tools** — text-to-speech with multiple voices
- **🔌 Plugin system** — add custom sensors via YAML or Python
- **🔒 Safety** — rate limiting, permission scopes, audit logging
- **♻️ Simulation mode** — deterministic offline testing without hardware
- **🎛️ Operator UI** — web dashboard for monitoring + approvals
- **📝 Audit trail** — immutable event logs with SHA256 hashing

**Build with ANSE if you need:**
- Agents that capture real sensor data and respond autonomously
- Consistent APIs for testing with simulated sensors and deploying with real hardware
- On-device autonomous systems without cloud dependencies
- Tool discovery and autonomous tool use
- Complete audit trails and reproducibility

---

## Quick Start

### Install

```bash
git clone https://github.com/13thrule/ANSE-Agent-Nervous-System-Engine
cd ANSE-Agent-Nervous-System-Engine
pip install -r requirements.txt
```

### Run the Demo (30 seconds)

**Terminal 1 — Start the engine:**
```bash
python -m anse.engine_core
```

**Terminal 2 — Run an autonomous agent:**
```bash
# With real hardware (camera/mic required)
python agent_demo.py

# Or with simulated hardware (no hardware needed)
ANSE_SIMULATE=1 python agent_demo.py
```

**What happens:**
- Agent discovers available tools
- Captures a frame from camera (or simulated)
- Analyzes the frame (edge/corner detection, color histogram)
- Records audio from microphone (or simulated)
- Analyzes audio (frequency spectrum, RMS, peak amplitude)
- Speaks a result using text-to-speech
- Logs everything to audit trail

---

## Run the Demo

**Terminal 1:**
```bash
python -m anse.engine_core
```

**Terminal 2:**
```bash
python agent_demo.py
```

**Sample output:**
```
✓ Calling capture_frame() → 640×480 RGB image
✓ Calling analyze_frame() → 9,866 edges | 554 corners | Avg color: BGR(43,52,71)

✓ Calling record_audio() → 2.0s @ 16kHz stereo
✓ Calling analyze_audio() → RMS: 0.0206 | Peak: 0.1689 | Freqs: [223, 219, 212] Hz

✓ Calling say() → "I can see, hear, and speak"

📝 Agent memory: 5 actions logged with timestamps
```

See [AUTONOMOUS_AGENT_UPDATE.md](AUTONOMOUS_AGENT_UPDATE.md) for implementation details.

---

## Plugin System (Extensible & Powerful)

ANSE's **plugin system is the core extensibility story** — add custom sensors without modifying the engine:

- **YAML Plugins:** Drop a config file in `plugins/` → agent discovers it automatically (perfect for non-programmers)
- **Python Plugins:** Async plugin classes with full type hints for complex integrations  
- **Auto-Registration:** Tools appear in `list_tools()` immediately after restart  
- **Same API:** Plugins use identical interface as built-in tools

**Include example plugins for:**
- Philips Hue smart lights
- Arduino robot arms  
- Industrial Modbus PLC  
- Custom temperature sensors  

See [Plugin System Details](#plugin-system) below and [docs/PLUGINS.md](docs/PLUGINS.md) for complete guide.

---

## Built-In Tools

### Hardware Tools

| Tool | Purpose |
|------|---------|
| `capture_frame()` | Capture RGB frame from camera (640×480) |
| `list_cameras()` | List available camera devices |
| `analyze_frame(frame_id, frame_path)` | Edge/corner detection, color histogram |
| `record_audio(duration=2.0)` | Record audio from microphone |
| `list_audio_devices()` | List microphones and speakers |
| `analyze_audio(audio_id, audio_path)` | FFT frequency analysis, RMS, peak |
| `say(text)` | Text-to-speech synthesis |
| `get_voices()` | List available TTS voices |

### Simulated Tools (for testing without hardware)

| Tool | Purpose |
|------|---------|
| `simulate_camera()` | Generate deterministic test frames |
| `simulate_microphone()` | Generate deterministic test audio |
| Auto-selected when `ANSE_SIMULATE=1` environment variable is set |

### Plugin System

Add custom sensors and tools by creating YAML or Python files in the `plugins/` directory. See [Plugin Examples](#plugin-examples).

---

## Safety & Audit (First-Class, Not Bolted-On)

Safety is built into the engine architecture, not a separate layer:

| Feature | Implementation |
|---------|----------------|
| **Permission Scopes** | Per-agent grants (camera, mic, network, filesystem) — deny by default |
| **Rate Limiting** | Hardware tools rate-limited (30, 10, 20 calls/min); per-agent buckets |
| **Approval Gates** | High-risk operations can require operator sign-off (built-in UI) |
| **Audit Trail** | Immutable JSONL log with SHA256 hashes — full provenance |
| **Local Storage** | Raw media stays local; no external transmission |
| **Isolation** | Per-agent quotas prevent one agent from impacting others |

**Example:** Cap camera at 30 calls/min per agent. Agent 1 hits limit → Agent 2 still works.

### Audit Log Format

```json
{
  "timestamp": "2026-02-14T10:30:45.123456Z",
  "agent_id": "agent-001",
  "call_id": "call-12345",
  "tool": "capture_frame",
  "args_hash": "abc123d...",
  "result_hash": "def456e...",
  "status": "success",
  "duration_ms": 145
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent (LLM / Script)                     │
│                   Connects via WebSocket                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ JSON-RPC
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  AgentBridge (WebSocket)                    │
│            handles_client() processes requests              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    EngineCore                               │
│  Initializes and coordinates all subsystems                 │
├─────────────────────────────────────────────────────────────┤
│  ToolRegistry  │  Scheduler  │  WorldModel  │  Audit Logger │
│   (tool        │  (execute,  │  (append-only│ (SHA256       │
│    metadata)   │   rate-limit│   event log) │  hashing)     │
├─────────────────────────────────────────────────────────────┤
│     PermissionManager    │       Safety Policy              │
│    (scopes, approval)    │      (YAML config)               │
├─────────────────────────────────────────────────────────────┤
│       Hardware Tools      │     Simulated Tools              │
│   (video, audio, TTS)     │  (deterministic seeds)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **EngineCore** — Orchestrator. Initializes scheduler, tool registry, world model, audit logger, and agent bridge. Loads plugins.
- **AgentBridge** — WebSocket JSON-RPC server. Handles `list_tools`, `call_tool`, `get_history`, `ping` from agents.
- **ToolRegistry** — Manages tool schemas, sensitivity labels, and execution routing. Registers built-in + plugin tools.
- **Scheduler** — Executes tool calls with per-tool rate limiting, timeouts, and call queuing.
- **WorldModel** — Append-only JSONL event store. Records all calls, results, timestamps. Enables replay and debugging.
- **AuditLogger** — Cryptographically signed JSONL audit trail. SHA256 hashes of inputs/outputs for non-repudiation.
- **PermissionManager** — Enforces YAML-based per-agent permission scopes. Deny-by-default policy.
- **PluginLoader** — Auto-discovers and registers YAML and Python plugins from `plugins/` directory.
- **Tools** — Async-safe implementations for hardware (video, audio, TTS) and simulated devices. All blocking I/O via `asyncio.to_thread()`.

---

## Design Principles

1. **Small, structured results** — Return IDs and metadata, not raw data blobs
2. **Local and auditable** — No external dependencies; full event trail on disk
3. **Agent autonomy** — Agents decide what to do; engine enforces safety
4. **Deterministic** — Event logs + seeded randomness enable replay and reproducibility
5. **Safe by default** — Rate limits, permission scopes, approval gates

---

## Safety & Audit

### Built-In Features

| Feature | Details |
|---------|---------|
| **Permission Scopes** | Per-agent grants for camera, mic, network, filesystem (deny by default) |
| **Rate Limiting** | Sensible defaults (30, 10, 20 calls/min) to prevent abuse |
| **Audit Trail** | Immutable JSONL log with SHA256 hashes for provenance |
| **Local Storage** | Raw media stored locally; no external data transmission |
| **Human Approval** | High-risk operations can require operator sign-off |

### Audit Log Format

```json
{
  "timestamp": "2026-02-14T10:30:45.123456Z",
  "agent_id": "agent-001",
  "call_id": "call-12345",
  "tool": "capture_frame",
  "args_hash": "abc123d...",
  "result_hash": "def456e...",
  "status": "success",
  "duration_ms": 145,
  "error": null
}
```

---

## Examples

### Training with Simulation, Deploying with Hardware

Simulated and real tools have **identical APIs** — develop and test offline, switch to hardware in production:

```python
from anse.engine_core import EngineCore

# Develop with simulated sensors (no hardware, deterministic, fast)
engine = EngineCore(simulate=True)
agent = MyAgent(engine)
agent.test_logic()

# Deploy with real hardware (same code, same API)
engine = EngineCore(simulate=False)
agent.run_production()
```

No code changes. Same tool calls work in both modes.

### IoT Device Control

Register custom sensors:

```bash
# Create plugins/temperature_sensor.yaml
python -m anse.engine_core
# Agent now sees and can call: temperature_sensor_read_temp()
```

### Multi-Agent System with Isolation

Run multiple agents on one engine with isolated resource quotas:

```python
engine = EngineCore()

agent1 = Agent(agent_id="robot-1", engine=engine)
agent2 = Agent(agent_id="robot-2", engine=engine)

# Each agent has its own:
# - Rate limit quota (e.g., 30 camera calls/min per agent)
# - CPU budget
# - Storage quota
# - Permission scopes (agent1 can use camera, agent2 cannot)
await asyncio.gather(agent1.run(), agent2.run())
```

---

## Operator UI

Monitor and approve agent actions via web dashboard:

```bash
cd operator_ui
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

**Features:**
- Live agent status dashboard
- Tool approval forms with scope controls
- Active token management
- Real-time event streaming
- Audit log viewer

---

## Plugin System

### YAML Plugins (5 minutes)

Create `plugins/my_sensor.yaml`:
```yaml
name: my_temperature_sensor
description: Custom temperature sensor
version: 0.1.0

tools:
  - name: read_temp
    description: Read current temperature in celsius
    handler: |
      return {
          'temperature': 23.5,
          'unit': 'celsius',
          'timestamp': datetime.now().isoformat()
      }
```

Restart the engine — agent can now call `my_temperature_sensor_read_temp()`.

### Python Plugins

```python
# plugins/my_plugin.py
import asyncio
from anse.plugin import SensorPlugin

class MyPlugin(SensorPlugin):
    name = "my_plugin"
    description = "Custom plugin"
    
    async def read_sensor(self):
        """Read from custom hardware."""
        # Your implementation
        return {"status": "ok", "value": 42}
```

### Plugin Examples

```
plugins/
├── _template_sensor.py              # Python plugin template
├── _template_sensor.yaml            # YAML template
├── example_philips_hue.yaml         # Philips Hue smart lights
├── example_arduino_servo.yaml       # Arduino robot arm
└── example_modbus_plc.yaml          # Industrial Modbus PLC
```

See [docs/PLUGINS.md](docs/PLUGINS.md) for complete guide.

---

## Project Structure

```
anse/
├── __init__.py
├── engine_core.py          # Main orchestrator
├── agent_bridge.py         # WebSocket server
├── tool_registry.py        # Tool management
├── scheduler.py            # Rate limiting & scheduling
├── world_model.py          # Event store (JSONL)
├── audit.py                # Audit logging with hashing
├── health.py               # Health monitoring
├── diagnostics.py          # Diagnostic endpoints
├── multiagent.py           # Per-agent quotas
├── plugin_loader.py        # Plugin system
├── tools/
│   ├── video.py            # Camera tools (async-safe)
│   ├── audio.py            # Audio tools (async-safe)
│   ├── tts.py              # Text-to-speech
│   ├── analysis.py         # Frame/audio analysis
│   ├── simulated.py        # Deterministic simulation
│   └── __init__.py
├── examples/
│   ├── scripted_agent.py   # Simple sequential example
│   └── llm_agent_adapter.py # LLM integration template
├── safety/
│   ├── permission.py       # Permission enforcement
│   └── safety_policy.yaml  # Policy configuration
└── operator_ui/            # Web dashboard
    ├── app.py              # Flask backend
    ├── models.py           # Database models
    ├── routes/             # API routes
    ├── templates/          # HTML templates
    └── static/             # CSS/JS
tests/
├── test_engine_core.py
├── test_tools.py
├── test_health.py
├── test_operator_ui.py
└── ...
docs/
├── API.md                  # API reference
├── DESIGN.md               # Architecture guide
├── PLUGINS.md              # Plugin development
└── QUICKSTART.md           # Getting started
```

---

## Installation & Testing

### Requirements

- Python 3.8+
- opencv-python
- sounddevice, soundfile
- pyttsx3 (text-to-speech)
- websockets
- PyYAML
- (optional) Flask, Flask-SQLAlchemy for Operator UI

### Install

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v
```

### Platform Notes

- **Windows**: May require restarting after OpenCV/sounddevice install
- **macOS**: Requires microphone permissions
- **Linux**: May need ALSA/PulseAudio configuration for audio

---

## API Reference

The engine exposes a WebSocket JSON-RPC interface on `ws://127.0.0.1:8765`.

### List Tools

```json
{"method": "list_tools"}
```

Returns all available tools with schemas.

### Call Tool

```json
{
  "method": "call_tool",
  "params": {
    "agent_id": "my-agent",
    "call_id": "call-001",
    "tool": "capture_frame",
    "args": {}
  }
}
```

### Get History

```json
{"method": "get_history", "params": {"limit": 10}}
```

Returns recent events from world model.

### Health Check

```json
{"method": "ping"}
```

Returns engine status and version.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Engine won't start | Check port 8765 is free: `netstat -an \| findstr :8765` (Windows), `lsof -i :8765` (macOS/Linux) |
| Camera not detected | Run `list_cameras()` to verify device availability; check permissions |
| Audio not recorded | Run `list_audio_devices()`; check microphone permissions |
| Simulated mode not working | Set `ANSE_SIMULATE=1` environment variable before starting |
| WebSocket connection refused | Ensure engine is running and firewall allows 8765 |
| Plugin not loading | Check plugin YAML syntax; restart engine after adding plugin |

---

## Performance

| Metric | Value |
|--------|-------|
| WebSocket latency | < 1 ms (local) |
| Tool execution | Hardware-dependent |
| Event log write | < 1 ms (JSONL append) |
| Memory footprint | ~50-100 MB (engine + tools) |
| Concurrent agents | Designed for multi-agent support; tested with 3+ agents per engine |

---

## Development Status

**Phase 1 ✅** — Health monitoring, operator UI, simulated sensors  
**Phase 2 ✅** — Multiagent isolation, LLM adapter template, audit/replay  
**Phase 3 🔄** — Network tools (http_get, ping), filesystem tools, browser tools (planned)

See [ROADMAP.md](ROADMAP.md) for detailed development plan.

---

## Extending ANSE

### Add a Tool

```python
# Create tool in anse/tools/my_tools.py
async def my_tool(param: str) -> dict:
    """Description of what this tool does."""
    # Use asyncio.to_thread() for blocking I/O
    result = await asyncio.to_thread(blocking_operation, param)
    return {"status": "success", "data": result}

# Register in engine_core.py
self.tools.register(
    "my_tool",
    my_tool,
    schema={"type": "object", "properties": {...}},
    description="What this tool does",
    sensitivity="public"
)
```

See [docs/API.md](docs/API.md) for complete examples.

---

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** — Hands-on tutorial
- **[Architecture & Design](docs/DESIGN.md)** — Deep dive into ANSE internals
- **[API Reference](docs/API.md)** — Complete tool and method documentation
- **[Plugin Development](docs/PLUGINS.md)** — Building custom sensors and tools
- **[Roadmap](ROADMAP.md)** — Future features and development plan
- **[Autonomous Agent Update](AUTONOMOUS_AGENT_UPDATE.md)** — Implementation details of demo agent

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Reporting issues
- Proposing features
- Submitting pull requests

---

## License

ANSE is released under the MIT License. See [LICENSE](LICENSE) for details.

---

## Citation

If you use ANSE in research, please cite:

```bibtex
@software{anse2026,
  title={ANSE: Agent Nervous System Engine},
  author={13thrule},
  year={2026},
  url={https://github.com/13thrule/ANSE-Agent-Nervous-System-Engine}
}
```

---

**Status:** Early-stage but stable — solid foundation, active development  
**Python:** 3.8+ | **License:** MIT | **Platform:** Windows, macOS, Linux  
**Last Updated:** February 2026
