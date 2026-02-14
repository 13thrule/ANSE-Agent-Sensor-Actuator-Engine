# ANSE — Agent Nervous System Engine

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

> **Build autonomous agents that use cameras, microphones, and custom tools.**

ANSE is a local runtime engine for building autonomous agents with sensor access and tool calling. Instead of manually wiring sensor drivers and agent logic, define your tools once and agents discover + use them autonomously.

**[Project Status](#-project-status) | [Folder Map](#-folder-overview) | [Docs](#-documentation-map) | [Quick Start](#quick-start) | [Architecture](#architecture)**

---

## 🔄 Project Status

**ANSE is in active development** — the architecture is stable, but components are being reorganized for clarity.

| Component | Status | Notes |
|-----------|--------|-------|
| **Core Engine** | ✅ Stable | Engine core, world model, scheduler, tool registry, audit logging all working |
| **Event-Driven Architecture** | ✅ Complete | Refactored from polling to nervous system model; fully async/await |
| **Plugin System** | 🔄 Reorganizing | Plugin code is complete; being categorized into sensors/actuators/cognition/system |
| **Documentation Suite** | ✅ Complete | 6 new guides (2,123 lines) covering event-driven patterns, troubleshooting, migration |
| **Backend (WebSocket)** | ✅ Complete | Pure event server with dashboard support; production-ready |
| **Dashboard** | ✅ Complete | Real-time UI with 5 panels (sensor, actuator, world model, reflex, event log) |
| **Examples** | ⏳ Coming Soon | Examples folder created; full tutorial code coming next |
| **Tests** | ✅ Complete | Unit tests passing; integration tests in place |

**What's ready to use:** Core engine, world model, tool system, audit logging, plugin registration, safety/permissions  
**What's being refined:** Dashboard UI, plugin examples, documentation guides (those are written, not code)  
**What's coming next:** Example agents, dashboard completion, performance optimization

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

## 🔍 What's Working vs. What's In Progress

**✅ Fully Functional & Stable:**
- Core engine (world model, scheduler, tool registry)
- Event-driven nervous system (async/await, event streaming)
- Plugin system (YAML and Python plugins)
- Sensor tools (camera, audio, TTS with analysis)
- Simulated tools (deterministic testing without hardware)
- Safety & permissions system (scopes, rate limiting, audit logs)
- Audit trail (immutable JSONL, SHA256 hashing)
- Operator UI (Flask admin dashboard)
- Tests (unit and integration tests passing)

**🔄 In Progress (Code Complete, UI Being Updated):**
- Dashboard rewrite (moving from polling setInterval to WebSocket events)
- Example agents (structure in place, tutorial code being added)
- Event-driven reflexes (code working, documentation complete)

**⏳ Coming Next (No ETA, But Planned):**
- Extended example library (full agent walkthroughs)
- Performance optimization & benchmarking
- Additional sensor/actuator templates
- Network tools (HTTP, DNS, ping)
- Filesystem tools (sandboxed safe access)
- Browser automation tools

---

## 📂 Folder Overview

Here's what each folder contains and its maturity level:

### Core System
| Folder | Purpose | Maturity |
|--------|---------|----------|
| **[anse/](anse/)** | Core engine, world model, scheduler, async runtime | ✅ Stable |
| **[tests/](tests/)** | Unit and integration tests | ✅ Stable |
| **[operator_ui/](operator_ui/)** | Flask admin dashboard, approvals, audit logs | ✅ Stable |

### Plugins (Organized by Role)
| Folder | Purpose | Maturity |
|--------|---------|----------|
| **[plugins/sensors/](plugins/sensors/)** | Sensor templates + examples (Arduino, Modbus, Hue, etc.) | ✅ Complete |
| **[plugins/actuators/](plugins/actuators/)** | Motor control and actuator interfaces | ✅ Complete |
| **[plugins/cognition/](plugins/cognition/)** | Body schema, long-term memory, reward system | ✅ Complete |
| **[plugins/system/](plugins/system/)** | Reflex system, dashboard bridge, infrastructure | ✅ Complete |

### UI & Presentation
| Folder | Purpose | Maturity |
|--------|---------|----------|
| **[dashboard/](dashboard/)** | Production web dashboard (HTML/CSS/JS) — real-time event panels | ✅ Complete |
| **[backend/](backend/)** | Pure WebSocket server for dashboard backend — production deployment ready | ✅ Complete |
| **[examples/gui_demo/](examples/gui_demo/)** | Reference demo implementation | ✅ Reference |

### Documentation
| Folder | Purpose | Maturity |
|--------|---------|----------|
| **[docs/](docs/)** | All guides, references, API docs (21 files) | ✅ Complete |
| **[scripts/](scripts/)** | Utility scripts for setup, debug, deploy | ⏳ Coming Soon |

---

## 📚 Documentation Map

ANSE has six comprehensive event-driven architecture guides. **Here's when to use each:**

### 🚀 **Just Starting?**
1. **[QUICKSTART.md](docs/QUICKSTART.md)** (5 min read)
   - Install and run the demo
   - See your first agent in action
   - Tests passing? You're good to go.

2. **[EVENT_DRIVEN_ARCHITECTURE.md](docs/EVENT_DRIVEN_ARCHITECTURE.md)** (15 min read)
   - How ANSE works as a nervous system
   - Event flow, world model, reflexes, agents
   - Core principles and patterns

### 🔧 **Building Something?**
3. **[IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md)** (step-by-step guide)
   - Structured 6-phase approach (10-20 days)
   - Build agents, sensors, actuators step-by-step
   - Includes code templates and testing strategies

4. **[EVENT_DRIVEN_CHEATSHEET.md](docs/EVENT_DRIVEN_CHEATSHEET.md)** (quick reference)
   - 5-minute patterns you'll use constantly
   - Copy-paste ready code examples
   - Do's and don'ts

### 🔄 **Migrating Existing Code?**
5. **[MIGRATION_POLLING_TO_EVENTS.md](docs/MIGRATION_POLLING_TO_EVENTS.md)** (practical guide)
   - Convert polling loops to event listeners
   - Before/after code examples
   - Performance gains (25x latency, 82% CPU reduction)

### 🛠️ **Debugging Issues?**
6. **[TROUBLESHOOTING_EVENT_DRIVEN.md](docs/TROUBLESHOOTING_EVENT_DRIVEN.md)** (problem solver)
   - 5 major problem categories with solutions
   - Debugging checklist (8 steps)
   - Hardware polling detection methods

### 📖 **Other Resources**
- **[DESIGN.md](docs/DESIGN.md)** — Architecture deep-dive (system components, async patterns)
- **[API.md](docs/API.md)** — Complete API reference
- **[PLUGINS.md](docs/PLUGINS.md)** — Building custom sensors and tools

---

## Repository Guide

**New to ANSE?** Start here to navigate the repo:

| Folder | Purpose |
|--------|---------|
| **[anse/](anse/)** | Core engine: world model, scheduler, tool registry, plugins |
| **[plugins/](plugins/)** | Sensor, actuator, cognition, and system plugins organized by category |
| **[backend/](backend/)** | WebSocket server for dashboard — pure event broadcaster |
| **[dashboard/](dashboard/)** | Production web dashboard — real-time nervous system visualization |
| **[examples/](examples/)** | Example implementations and tutorial code |
| **[docs/](docs/)** | Complete documentation: guides, references, troubleshooting |
| **[operator_ui/](operator_ui/)** | Flask admin dashboard for approvals and audit logs |
| **[tests/](tests/)** | Unit and integration tests |
| **[scripts/](scripts/)** | Utility scripts (setup, deployment, debugging) |

**Quick Navigation:**
- 🚀 [Quick Start](#quick-start) — Get running in 30 seconds
- 📊 [Dashboard](QUICK_START.md) — Real-time event visualization
- 📚 [Event-Driven Architecture](docs/EVENT_DRIVEN_ARCHITECTURE.md) — How ANSE works
- 🔧 [Backend Setup](backend/README.md) — Production deployment
- 👀 [Screenshots Guide](SCREENSHOTS.md) — Visual walkthrough

---

## The Nervous System Model

ANSE implements an event-driven nervous system where sensors emit events, reflexes react instantly, agents make decisions based on the world model, and all actions are audited. No polling loops. No continuous checks. All behavior flows through the immutable world model event log.

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

See [docs/PLUGINS.md](docs/PLUGINS.md) for the complete plugin development guide.

---

## Project Structure

```
anse/                                  # Core engine
├── engine_core.py                    # Main orchestrator
├── agent_bridge.py                   # WebSocket server
├── tool_registry.py                  # Tool management
├── scheduler.py                      # Rate limiting & scheduling
├── world_model.py                    # Event store (JSONL)
├── audit.py                          # Audit logging with hashing
├── health.py                         # Health monitoring
├── tools/
│   ├── video.py                      # Camera tools
│   ├── audio.py                      # Audio tools
│   └── tts.py                        # Text-to-speech
├── examples/
│   ├── event_driven_agent.py         # Reference event-driven implementation
│   ├── scripted_agent.py             # Simple sequential example
│   └── llm_agent_adapter.py          # LLM integration template
└── safety/
    ├── permission.py                 # Permission enforcement
    └── safety_policy.yaml            # Policy configuration

plugins/                               # Extensible plugin system
├── sensors/                          # Sensor plugins
│   ├── _template_sensor.py           # Python template
│   ├── _template_sensor.yaml         # YAML template
│   └── example_*.yaml                # Example hardware
├── actuators/                        # Actuator plugins (motors, controllers)
│   └── motor_control/                # Motor control interface
├── cognition/                        # Higher-level reasoning plugins
│   ├── body_schema/                  # Spatial self-awareness
│   ├── long_term_memory/             # Experience storage
│   └── reward_system/                # Learning & reinforcement
└── system/                           # Core system plugins
    ├── reflex_system/                # Fast event-driven reactions
    └── dashboard_bridge/             # UI integration

examples/                              # Example applications
├── README.md                         # Guide to examples (coming soon)
└── (future: full agent examples, tutorials)

docs/                                  # Complete documentation
├── QUICKSTART.md                     # Getting started
├── EVENT_DRIVEN_ARCHITECTURE.md      # Nervous system model
├── EVENT_DRIVEN_CHEATSHEET.md        # Quick reference
├── MIGRATION_POLLING_TO_EVENTS.md    # Polling→Events guide
├── IMPLEMENTATION_CHECKLIST.md       # Step-by-step guide
├── TROUBLESHOOTING_EVENT_DRIVEN.md   # Problem solving
├── DESIGN.md                         # Architecture deep-dive
├── API.md                            # API reference
├── PLUGINS.md                        # Plugin development guide
├── INSTALLATION.md                   # Setup instructions
└── (more docs for different topics)

dashboard_ui/                          # Web monitoring dashboard
├── dashboard.html                    # Main interface
├── dashboard_client.ts               # WebSocket client
├── DashboardExample.svelte           # Component template
└── README.md                         # Status & roadmap

operator_ui/                           # Admin dashboard
├── app.py                            # Flask backend
├── models.py                         # Database models
├── routes/                           # API endpoints
├── templates/                        # HTML
├── static/                           # CSS/JS
└── requirements.txt                  # Dependencies

scripts/                               # Utility scripts
├── README.md                         # Script guide
└── (future: setup, deployment, debug tools)

tests/                                 # Unit & integration tests
├── test_engine_core.py
├── test_tools.py
├── test_health.py
└── (more test modules)
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

## 🛣️ Roadmap

### Current (February 2026)
- ✅ Event-driven nervous system architecture
- ✅ Plugin system with categorized organization
- ✅ Comprehensive documentation suite (6 guides)
- 🔄 Dashboard rewrite (WebSocket events, remove polling)
- 🔄 Example agents (structure in place, code coming)

### Next (March 2026)
- Complete dashboard rewrite with event listeners
- Full tutorial examples in `examples/` folder
- Performance benchmarking and optimization
- Extended plugin library (more sensor/actuator templates)

### Future (Q2 2026)
- Network tools (HTTP, ping, DNS)
- Filesystem tools (safe sandboxed access)
- Browser automation tools
- Real-world sensor integrations
- Cloud deployment guides

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed development plan.

---

## Development Status

**Phase 1 ✅** — Core engine, event-driven architecture, plugin system, audit logging  
**Phase 2 ✅** — Multi-agent isolation, safety & permissions, comprehensive documentation  
**Phase 3 🔄** — Dashboard rewrite, example agents, extended tools (in progress)  
**Phase 4 ⏳** — Network tools, filesystem tools, browser automation (coming next)

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

## 📖 Full Documentation Index

**See [Documentation Map](#-documentation-map) above for when to use each guide.**

Complete reference:
- **[Quick Start Guide](docs/QUICKSTART.md)** — Install, run demo, verify setup
- **[Event-Driven Architecture](docs/EVENT_DRIVEN_ARCHITECTURE.md)** — Core nervous system model (complete)
- **[Event-Driven Cheat Sheet](docs/EVENT_DRIVEN_CHEATSHEET.md)** — Quick reference, copy-paste patterns
- **[Migration from Polling to Events](docs/MIGRATION_POLLING_TO_EVENTS.md)** — Convert existing code (with examples)
- **[Implementation Checklist](docs/IMPLEMENTATION_CHECKLIST.md)** — Structured 6-phase guide (10-20 days)
- **[Troubleshooting Event-Driven Issues](docs/TROUBLESHOOTING_EVENT_DRIVEN.md)** — Problem solving & debugging
- **[Architecture & Design](docs/DESIGN.md)** — Engine internals, component interactions
- **[API Reference](docs/API.md)** — Tool schemas, method signatures, JSON-RPC interface
- **[Plugin Development](docs/PLUGINS.md)** — Building sensors, actuators, cognitive plugins
- **[Roadmap](docs/ROADMAP.md)** — Future features and development timeline
- **[Installation Guide](docs/INSTALLATION.md)** — Detailed setup for each platform
- **[Autonomous Agent Demo](docs/AUTONOMOUS_AGENT_UPDATE.md)** — How the working example works internally

---

## Contributing

Contributions welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
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
