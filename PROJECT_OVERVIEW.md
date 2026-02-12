# ANSE Project Overview

## Project Structure

```
anse/
├── README.md                   # Main project documentation
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # Contribution guidelines
├── pyproject.toml              # Package configuration
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── demo.py                     # Comprehensive demo script
│
├── anse/                       # Main package
│   ├── __init__.py
│   ├── engine_core.py          # Main orchestrator
│   ├── tool_registry.py        # Tool management
│   ├── scheduler.py            # Execution & rate limiting
│   ├── world_model.py          # Event logging
│   ├── agent_bridge.py         # WebSocket server
│   │
│   ├── tools/                  # Built-in tools
│   │   ├── __init__.py
│   │   ├── video.py            # Camera tools
│   │   ├── audio.py            # Microphone tools
│   │   └── tts.py              # Text-to-speech tools
│   │
│   ├── safety/                 # Security & permissions
│   │   ├── __init__.py
│   │   ├── permission.py       # Permission manager
│   │   └── safety_policy.yaml  # Safety configuration
│   │
│   └── examples/               # Example agents
│       ├── __init__.py
│       ├── scripted_agent.py   # Basic demo
│       └── llm_agent_adapter.py # LLM integration template
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_engine_core.py     # Integration tests
│   └── test_tools.py           # Unit tests
│
└── docs/                       # Documentation
    ├── QUICKSTART.md           # Getting started guide
    ├── API.md                  # API reference
    └── DESIGN.md               # Architecture details
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Agent (LLM/Script)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket (JSON-RPC)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      AgentBridge                             │
│  • WebSocket server                                          │
│  • Request/response handling                                 │
│  • Protocol translation                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Scheduler                               │
│  • Rate limiting (token bucket)                              │
│  • Timeout enforcement                                       │
│  • Event logging                                             │
│  • Call execution                                            │
└────┬────────────────────┬──────────────────┬────────────────┘
     │                    │                  │
     ▼                    ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ToolRegistry  │  │ WorldModel   │  │PermissionMgr │
│              │  │              │  │              │
│• Tool lookup │  │• Event log   │  │• Scope check │
│• Execution   │  │• History     │  │• Approval    │
└──────┬───────┘  └──────────────┘  └──────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│           Tool Implementations         │
├────────────┬──────────────┬────────────┤
│   Video    │    Audio     │    TTS     │
│            │              │            │
│• capture   │• record_audio│• say       │
│• list_cams │• list_devices│• get_voices│
└────────────┴──────────────┴────────────┘
       │            │             │
       ▼            ▼             ▼
┌────────────────────────────────────────┐
│        Hardware / OS Services          │
│  Camera  │  Microphone  │  Speakers    │
└────────────────────────────────────────┘
```

## Data Flow Example

```
1. Agent sends: {"method": "call_tool", "params": {"tool": "capture_frame"}}
                           ↓
2. AgentBridge receives request, validates JSON
                           ↓
3. Scheduler checks:
   - Rate limit OK? ✓
   - Permission OK? ✓
   - Timeout set: 30s
                           ↓
4. Scheduler logs to WorldModel: tool_call event
                           ↓
5. ToolRegistry executes: capture_frame()
                           ↓
6. Video tool:
   - Opens camera
   - Captures frame
   - Saves to /tmp/anse/abc123.jpg
   - Returns: {"frame_id": "abc123", "path": "..."}
                           ↓
7. Scheduler logs to WorldModel: tool_result event
                           ↓
8. Response sent to agent: {"status": "ok", "result": {...}}
```

## Key Features

### ✅ Implemented (v0)

- [x] WebSocket-based agent bridge
- [x] Tool registry with metadata
- [x] Camera capture (OpenCV)
- [x] Audio recording (sounddevice)
- [x] Text-to-speech (pyttsx3)
- [x] Rate limiting per tool
- [x] Event logging to WorldModel
- [x] Permission scopes
- [x] Timeout enforcement
- [x] Error handling
- [x] Scripted agent example
- [x] LLM adapter template
- [x] Unit tests
- [x] Integration tests
- [x] Comprehensive documentation

### 🔜 Short-term Roadmap

- [ ] Persistent audit log with replay
- [ ] Simulated sensors (for offline training)
- [ ] Thread pool for blocking operations
- [ ] Better async throughout
- [ ] Human approval workflow
- [ ] Media cleanup daemon (TTL enforcement)

### 🚀 Medium-term Roadmap

- [ ] SDR (software-defined radio) tool
- [ ] Browser automation tool
- [ ] Filesystem navigation tool
- [ ] Web UI for operator console
- [ ] Multi-agent isolation
- [ ] Resource quotas per agent
- [ ] Tool marketplace

### 🌟 Long-term Vision

- [ ] SDKs for other languages (JS, Go, Rust)
- [ ] Distributed execution
- [ ] Simulated environments
- [ ] Transfer learning benchmarks
- [ ] Community tool ecosystem

## Component Responsibilities

### EngineCore
Central orchestrator that initializes all subsystems and coordinates their operation.

### ToolRegistry
Manages the catalog of available tools and their execution. Each tool has:
- Async function implementation
- JSON Schema for parameters
- Sensitivity level (low/medium/high)
- Cost hint (latency, resource usage)

### Scheduler
Handles deterministic execution with:
- Rate limiting (calls per minute)
- Timeout enforcement (configurable)
- Event logging for replay
- Permission checks (future)

### WorldModel
Append-only event store containing:
- Tool calls (agent_id, tool, args, timestamp)
- Tool results (status, result/error, timestamp)
- Rolling history (last N events)
- Agent-specific filtering

### AgentBridge
WebSocket server exposing:
- list_tools - Enumerate capabilities
- call_tool - Execute a tool
- get_tool_info - Query tool metadata
- get_history - Retrieve event log
- ping - Health check

### PermissionManager
Enforces safety policy:
- Scope-based access control
- Rate limit configuration
- Approval requirements
- Data retention policies

## Technology Stack

- **Language**: Python 3.8+
- **Async**: asyncio, websockets
- **Vision**: OpenCV (cv2)
- **Audio**: sounddevice, soundfile
- **TTS**: pyttsx3
- **Config**: PyYAML
- **Testing**: pytest, pytest-asyncio

## Design Principles

1. **Tool-First**: Everything is a callable function
2. **Agent Autonomy**: Agent decides what to call
3. **Local by Default**: Data stays on machine
4. **Deterministic**: Reproducible via event log
5. **Minimal Safety**: Simple but effective controls

## Success Metrics (v0)

- ✓ Scripted agent completes look→listen→speak loop
- ✓ Capture latency < 500ms on dev hardware
- ✓ Engine runs 1+ hour without memory growth
- ✓ LLM can sequence 2+ tool calls successfully
- ✓ Rate limiting prevents DoS
- ✓ All tools handle errors gracefully

## Getting Started

1. **Install**: `pip install -r requirements.txt && pip install -e .`
2. **Run Engine**: `python -m anse.engine_core`
3. **Run Demo**: `python demo.py`
4. **Read Docs**: See `docs/QUICKSTART.md`

## Use Cases

### Computer Vision Agent
Agent analyzes its environment using camera and provides descriptions via speech.

### Voice Assistant
Agent listens via microphone, processes commands, and responds via TTS.

### Monitoring Agent
Periodic environment checks with anomaly detection and alerts.

### Research Platform
Train agents in simulation, then transfer to real sensors.

### Multi-Modal Learning
Agent learns to coordinate vision, audio, and speech.

## Contributing

See `CONTRIBUTING.md` for development setup and guidelines.

## License

MIT License - See `LICENSE` file.

---

**ANSE v0.1.0** - Agent Nervous System Engine
Built with ❤️ for embodied AI research
