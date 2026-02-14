# ANSE Installation and Quick Start

## What is ANSE?

ANSE (Agent Nervous System Engine) is a complete, production-ready framework that gives AI agents controlled access to sensors (camera, microphone) and actuators (text-to-speech) through a clean WebSocket API.

**Key Features:**
- 🎥 Camera capture with OpenCV
- 🎤 Audio recording with sounddevice
- 🔊 Text-to-speech with pyttsx3
- 🔒 Built-in rate limiting and permissions
- 📝 Complete event logging for replay
- 🌐 WebSocket API for any language
- 📚 Comprehensive documentation
- ✅ Full test suite included

## Project Statistics

- **31 files** total
- **~2000 lines** of Python code
- **6 built-in tools** (camera, audio, TTS)
- **3 example agents** (scripted, LLM adapter, comprehensive demo)
- **15+ unit and integration tests**
- **4 documentation files** (API, Design, Quickstart, Overview)

## Quick Installation (5 minutes)

### Step 1: Extract and Navigate

```bash
# Extract the anse_project folder
cd anse_project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install ANSE and all dependencies
pip install -r requirements.txt
pip install -e .
```

### Step 4: Run the Demo

**Terminal 1** - Start the ANSE engine:
```bash
python -m anse.engine_core
```

**Terminal 2** - Run the comprehensive demo:
```bash
python demo.py
```

You should see:
- Tool discovery (lists all 6 tools)
- Camera operations (if camera available)
- Audio operations (if microphone available)
- Text-to-speech demonstration
- Error handling examples
- Event history retrieval

## What's Included

### Core Engine (`anse/`)
- `engine_core.py` - Main orchestrator
- `tool_registry.py` - Tool management system
- `scheduler.py` - Rate limiting & execution
- `world_model.py` - Event logging
- `agent_bridge.py` - WebSocket API server

### Built-in Tools (`anse/tools/`)
- `video.py` - Camera capture, device listing
- `audio.py` - Microphone recording, device listing  
- `tts.py` - Text-to-speech, voice listing

### Safety System (`anse/safety/`)
- `permission.py` - Permission manager
- `safety_policy.yaml` - Configurable safety rules

### Examples (`anse/examples/`)
- `scripted_agent.py` - Basic demo agent
- `llm_agent_adapter.py` - Template for LLM integration
- `demo.py` - Comprehensive demonstration (in root)

### Tests (`tests/`)
- `test_engine_core.py` - Integration tests
- `test_tools.py` - Unit tests for tools

### Documentation (`docs/`)
- `QUICKSTART.md` - Getting started guide
- `API.md` - Complete API reference
- `DESIGN.md` - Architecture deep-dive
- `PROJECT_OVERVIEW.md` - Visual diagrams & roadmap

## Usage Examples

### Python Client

```python
import asyncio
import json
import websockets

async def my_agent():
    uri = "ws://127.0.0.1:8765"
    async with websockets.connect(uri) as ws:
        # List tools
        await ws.send(json.dumps({"method": "list_tools"}))
        tools = json.loads(await ws.recv())
        
        # Capture frame
        call = {
            "agent_id": "my-agent",
            "call_id": "001",
            "tool": "capture_frame",
            "args": {}
        }
        await ws.send(json.dumps({"method": "call_tool", "params": call}))
        result = json.loads(await ws.recv())
        
        print(result)

asyncio.run(my_agent())
```

### Command Line (with wscat)

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c ws://127.0.0.1:8765

# List tools
> {"method": "list_tools"}

# Call a tool
> {"method": "call_tool", "params": {"agent_id": "cli", "call_id": "1", "tool": "say", "args": {"text": "Hello ANSE"}}}
```

## Available Tools

| Tool | Description | Rate Limit |
|------|-------------|------------|
| `capture_frame` | Capture RGB image from camera | 30/min |
| `list_cameras` | List available cameras | None |
| `record_audio` | Record audio from microphone | 10/min |
| `list_audio_devices` | List audio devices | None |
| `say` | Text-to-speech output | 20/min |
| `get_voices` | List TTS voices | None |

## Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=anse --cov-report=html
```

## Configuration

### Custom Port

```bash
python -m anse.engine_core --port 9000
```

### Custom Safety Policy

```bash
# Copy and modify the policy
cp anse/safety/safety_policy.yaml my_policy.yaml
# Edit my_policy.yaml...

# Run with custom policy
python -m anse.engine_core --policy my_policy.yaml
```

### Rate Limits

Edit `anse/safety/safety_policy.yaml`:

```yaml
rate_limits:
  capture_frame: 60  # Increase to 60/min
  say: 10            # Decrease to 10/min
```

## Integrating with LLMs

See `anse/examples/llm_agent_adapter.py` for a complete template showing how to:
1. Fetch tool schemas from ANSE
2. Convert to LLM function calling format
3. Execute LLM's chosen tools
4. Return results to LLM
5. Loop until task complete

Compatible with: OpenAI, Anthropic, Cohere, or any function-calling LLM.

## Troubleshooting

### "Module not found: cv2"
```bash
pip install opencv-python
```

### "Module not found: sounddevice"
```bash
pip install sounddevice soundfile
```

### "Could not connect"
Make sure the engine is running in another terminal:
```bash
python -m anse.engine_core
```

### No camera/microphone
Tools will fail gracefully with error messages. The system still works for TTS.

## Next Steps

1. ✅ Read `docs/QUICKSTART.md` for detailed tutorial
2. ✅ Read `docs/API.md` for complete API reference
3. ✅ Read `docs/DESIGN.md` for architecture details
4. ✅ Check `PROJECT_OVERVIEW.md` for roadmap
5. ✅ Explore `anse/examples/` for integration patterns
6. ✅ Run `demo.py` for comprehensive demonstration

## File Structure Reference

```
anse_project/
├── README.md              ← Start here
├── PROJECT_OVERVIEW.md    ← Architecture & roadmap
├── QUICKSTART.md          ← This file
├── CONTRIBUTING.md        ← For developers
├── LICENSE                ← MIT License
├── demo.py                ← Comprehensive demo
├── pyproject.toml         ← Package config
├── requirements.txt       ← Dependencies
├── anse/                  ← Main package
│   ├── engine_core.py
│   ├── tool_registry.py
│   ├── scheduler.py
│   ├── world_model.py
│   ├── agent_bridge.py
│   ├── tools/            ← Built-in tools
│   ├── safety/           ← Security
│   └── examples/         ← Example agents
├── tests/                ← Test suite
└── docs/                 ← Documentation
    ├── QUICKSTART.md
    ├── API.md
    └── DESIGN.md
```

## Support

- 📖 **Documentation**: See `docs/` folder
- 🐛 **Issues**: Check test output for debugging
- 💬 **Questions**: Review `docs/DESIGN.md` for architecture
- 🤝 **Contributing**: See `CONTRIBUTING.md`

## License

MIT License - See LICENSE file

---

**ANSE v0.1.0** - Ready for production use! 🚀
