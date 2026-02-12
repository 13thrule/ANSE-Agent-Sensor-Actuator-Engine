# ANSE — Agent Nervous System Engine

> Give AI agents direct access to hardware sensors and tools with safety guardrails, rate limiting, and audit logging.

## What is ANSE?

ANSE is a Python framework that lets AI agents (LLMs, scripted bots, or RL agents) directly call hardware tools—cameras, microphones, speakers, and more—while maintaining security, privacy, and determinism.

**Real-world use cases:**
- AI assistants that can see (via webcam), hear (via microphone), and speak (via TTS)
- Agents that detect and interact with physical hardware in real-time  
- Research platforms for studying emergent agent behavior with embodied tools
- Sandboxed local execution (no cloud required, data stays on device)

## Core Features

| Feature | Details |
|---------|---------|
| **6 Built-in Tools** | `capture_frame`, `record_audio`, `say`, `list_cameras`, `list_audio_devices`, `get_voices` |
| **WebSocket API** | Agents connect via `ws://127.0.0.1:8765` using JSON-RPC protocol |
| **Async-First** | Non-blocking I/O using Python `asyncio` with thread pooling for blocking operations |
| **Rate Limiting** | Per-tool limits (30, 10, 20 calls/min) prevent resource exhaustion |
| **Audit Logging** | SHA256-hashed call records for compliance, privacy-preserving statistics |
| **Event Store** | JSONL append-only persistence for replay, determinism, and debugging |
| **Permission System** | Configurable permission scopes (can extend with YAML policies) |
| **Fully Tested** | 16 integration tests covering core engine, tools, and scheduler |

## Architecture

```
┌─────────────────┐
│   AI Agent      │ (LLM, scripted, RL)
│  (via WebSocket)│
└────────┬────────┘
         │ JSON-RPC
         ▼
┌─────────────────────────────────────┐
│   AgentBridge (WebSocket Server)    │ Handles client connections
├─────────────────────────────────────┤
│   EngineCore (Orchestrator)         │ Manages subsystems
├─────────────────────────────────────┤
│ ToolRegistry │ Scheduler │ RateLimits│ Executes tools with limits
├─────────────────────────────────────┤
│ WorldModel  │ AuditLogger │ Safety   │ Persistence, logging, policies
├─────────────────────────────────────┤
│   Tools (video, audio, tts, etc)    │ Hardware access
└─────────────────────────────────────┘
         │
         ▼
    Hardware
   (cameras, mics,
    speakers, etc)
```

## Installation

```bash
# Clone or download ANSE
cd anse_project

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify install
pytest tests/ -v
```

## Quick Start

### Start the Engine

```python
from anse.engine_core import EngineCore
import asyncio

async def main():
    engine = EngineCore()
    print(f"Engine running on ws://127.0.0.1:8765")
    tools = engine.list_tools()
    print(f"Tools: {[t['name'] for t in tools]}")
    
    # Keep engine running
    await engine.run()

asyncio.run(main())
```

### Connect with WebSocket

```python
import asyncio
import json
import websockets

async def agent():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        # List tools
        await ws.send(json.dumps({"method": "list_tools"}))
        tools = json.loads(await ws.recv())
        print(f"Available tools: {tools}")
        
        # Capture frame
        await ws.send(json.dumps({
            "method": "call_tool",
            "params": {"tool": "capture_frame"}
        }))
        result = json.loads(await ws.recv())
        print(f"Result: {result}")

asyncio.run(agent())
```

## API Commands

### Tool Management
```json
{"method": "list_tools"}
{"method": "get_tool_info", "params": {"tool": "capture_frame"}}
```

### Tool Execution
```json
{"method": "call_tool", "params": {"tool": "capture_frame"}}
{"method": "call_tool", "params": {"tool": "say", "args": {"text": "Hello!"}}}
{"method": "call_tool", "params": {"tool": "record_audio", "args": {"duration_sec": 5}}}
```

### History & Status
```json
{"method": "get_history", "params": {"limit": 10}}
{"method": "ping"}
```

## Available Tools

### Vision
- **`capture_frame()`** — Capture RGB frame from first camera (max 30 calls/min)
- **`list_cameras()`** — Enumerate available camera devices

### Audio  
- **`record_audio(duration_sec)`** — Record audio for N seconds, max 60 sec (max 10 calls/min)
- **`list_audio_devices()`** — Enumerate available microphones
- **`say(text)`** — Text-to-speech output (max 20 calls/min, max 1000 chars)
- **`get_voices()`** — List available TTS voices

## Project Structure

```
anse_project/
├── anse/
│   ├── __init__.py
│   ├── engine_core.py        # Main orchestrator
│   ├── agent_bridge.py       # WebSocket server
│   ├── tool_registry.py      # Tool registration & execution
│   ├── scheduler.py          # Rate limiting & scheduling
│   ├── world_model.py        # Event persistence
│   ├── audit.py              # Audit logging with hashing
│   ├── tools/                # Hardware adapters
│   │   ├── video.py          # Camera capture (async-safe)
│   │   ├── audio.py          # Microphone recording (async-safe)
│   │   └── tts.py            # Text-to-speech (async-safe)
│   ├── examples/             # Example agents
│   │   ├── scripted_agent.py # Simple scripted example
│   │   └── llm_agent_adapter.py # LLM integration template
│   └── safety/               # Security & policies
│       ├── permission.py      # Permission enforcement
│       └── safety_policy.yaml # Policy configuration
├── tests/
│   ├── test_engine_core.py   # Engine tests
│   └── test_tools.py         # Tool tests
├── docs/
│   ├── DESIGN.md             # Architecture details
│   ├── API.md                # Complete API reference
│   └── QUICKSTART.md         # Quick reference guide
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Dependencies

- `websockets` — WebSocket protocol for agent communication
- `opencv-python` — Camera capture
- `sounddevice` & `soundfile` — Audio recording
- `pyttsx3` — Text-to-speech
- `PyYAML` — Policy configuration
- `pytest` — Testing (dev only)

## Safety & Rate Limiting

Each tool has configurable rate limits:
- `capture_frame`: 30 calls/min
- `record_audio`: 10 calls/min  
- `say`: 20 calls/min

Audit logs store:
- **Call details** (hashed args for privacy)
- **Timestamps**
- **Agent identity**
- **Result status**

All data is stored locally in JSONL format (append-only, replay-able).

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Tests cover:
- Engine initialization and tool registration
- Rate limiting enforcement
- Tool execution (with/without hardware)
- Event persistence
- Audit logging

## Design Philosophy

**Three core principles:**

1. **Agent First** — Tools expose capabilities as functions. Agents decide what to call, when, and how.
2. **Local & Safe** — All data stays on device. Rate limits and permission scopes prevent abuse.
3. **Deterministic** — Append-only event store enables replay, debugging, and reproducible research.

## Extending ANSE

To add a new tool:

1. Create a tool function in `anse/tools/`:
```python
async def my_tool(param: str) -> dict:
    """Description."""
    return {"status": "success", "data": result}
```

2. Register in `ToolRegistry`:
```python
registry.register("my_tool", my_tool, metadata={...})
```

3. Tool is automatically exposed via WebSocket API.

## License

See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Documentation

- [DESIGN.md](docs/DESIGN.md) — Architecture, design patterns, async safety
- [API.md](docs/API.md) — Complete API reference with examples
- [QUICKSTART.md](docs/QUICKSTART.md) — Hands-on quick reference guide

---

**Status:** Production-ready with 16 passing tests.  
**Python:** 3.11+  
**Platform:** Windows, macOS, Linux
