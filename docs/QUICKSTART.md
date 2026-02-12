# ANSE Quick Start Guide

Get up and running with ANSE in 5 minutes.

## Installation

### 1. Clone and Install

```bash
# Clone or download the repository
cd anse_project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install ANSE
pip install -e .
```

### 2. Verify Installation

```bash
python -c "import anse; print(anse.__version__)"
# Should print: 0.1.0
```

---

## Running Your First Agent

### Terminal 1: Start the Engine

```bash
# Start ANSE engine on default port (8765)
python -m anse.engine_core
```

You should see:
```
INFO - Starting ANSE engine on 127.0.0.1:8765
INFO - Registered 6 tools
INFO - AgentBridge listening on ws://127.0.0.1:8765
```

### Terminal 2: Run the Demo Agent

```bash
# Run the scripted demo agent
python anse/examples/scripted_agent.py
```

The agent will:
1. List available tools
2. Capture a camera frame
3. Record 2 seconds of audio
4. Speak using text-to-speech
5. Retrieve event history

**Note:** If you don't have a camera/microphone, the tools will fail gracefully with error messages.

---

## Exploring the API

### Using Python (Async)

```python
import asyncio
import json
import websockets

async def explore():
    uri = "ws://127.0.0.1:8765"
    
    async with websockets.connect(uri) as ws:
        # List all tools
        await ws.send(json.dumps({"method": "list_tools"}))
        response = json.loads(await ws.recv())
        print("Available tools:", list(response["result"].keys()))
        
        # Call a tool
        call = {
            "agent_id": "explorer",
            "call_id": "call-1",
            "tool": "say",
            "args": {"text": "Hello from ANSE!"}
        }
        await ws.send(json.dumps({"method": "call_tool", "params": call}))
        result = json.loads(await ws.recv())
        print("Result:", result)

asyncio.run(explore())
```

### Using wscat (Command Line)

Install wscat: `npm install -g wscat`

```bash
# Connect to ANSE
wscat -c ws://127.0.0.1:8765

# List tools
> {"method": "list_tools"}

# Call a tool
> {"method": "call_tool", "params": {"agent_id": "cli", "call_id": "1", "tool": "say", "args": {"text": "test"}}}

# Get history
> {"method": "get_history", "params": {"n": 5}}
```

---

## Understanding the Output

### Successful Tool Call

```json
{
  "status": "ok",
  "call_id": "call-001",
  "result": {
    "frame_id": "abc123...",
    "path": "/tmp/anse/abc123.jpg",
    "width": 1920,
    "height": 1080
  }
}
```

### Failed Tool Call

```json
{
  "status": "error",
  "call_id": "call-001",
  "error": "camera_unavailable"
}
```

### Rate Limited

```json
{
  "status": "error",
  "call_id": "call-001",
  "error": "rate_limited"
}
```

---

## Available Tools (v0)

| Tool | Description | Rate Limit |
|------|-------------|------------|
| `capture_frame` | Capture camera image | 30/min |
| `list_cameras` | List camera devices | None |
| `record_audio` | Record microphone audio | 10/min |
| `list_audio_devices` | List audio devices | None |
| `say` | Text-to-speech | 20/min |
| `get_voices` | List TTS voices | None |

---

## Customizing Configuration

### Custom Port

```bash
python -m anse.engine_core --port 9000
```

### Custom Safety Policy

1. Copy default policy:
```bash
cp anse/safety/safety_policy.yaml my_policy.yaml
```

2. Edit `my_policy.yaml`:
```yaml
rate_limits:
  capture_frame: 60  # Increase to 60 calls/min
  say: 10           # Decrease to 10 calls/min
```

3. Run with custom policy:
```bash
python -m anse.engine_core --policy my_policy.yaml
```

---

## Testing Your Setup

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

### Check System Status

```python
from anse.engine_core import EngineCore

core = EngineCore()
stats = core.get_stats()

print(f"Tools: {stats['tools']}")
print(f"Events logged: {stats['events']}")
print(f"Total calls: {stats['scheduler']['total_calls']}")
```

---

## Troubleshooting

### "Module not found: cv2"

Camera tools require OpenCV:
```bash
pip install opencv-python
```

### "Module not found: sounddevice"

Audio tools require sounddevice:
```bash
pip install sounddevice soundfile
```

### "Could not connect to ANSE engine"

Make sure the engine is running:
```bash
python -m anse.engine_core
```

### Camera not detected

Check available cameras:
```python
import cv2
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: available")
        cap.release()
```

### Audio device not found

List audio devices:
```python
import sounddevice as sd
print(sd.query_devices())
```

---

## Next Steps

1. **Read the API docs** - See `docs/API.md` for full protocol details
2. **Explore the design** - See `docs/DESIGN.md` for architecture
3. **Create custom tools** - Add your own sensors/actuators
4. **Integrate with LLM** - See `examples/llm_agent_adapter.py`

---

## Getting Help

- Check the documentation in `docs/`
- Review example agents in `anse/examples/`
- Examine test cases in `tests/`
- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

---

## Example Use Cases

### Computer Vision Agent

```python
# Agent that analyzes its environment
async def vision_agent():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        # Capture frame
        call = {..., "tool": "capture_frame"}
        await ws.send(json.dumps({"method": "call_tool", "params": call}))
        result = await ws.recv()
        
        # Process image (send to vision model)
        # Speak what you see
        call = {..., "tool": "say", "args": {"text": description}}
```

### Voice Assistant

```python
# Agent that listens and responds
async def voice_assistant():
    while True:
        # Record audio
        # Transcribe audio (with Whisper)
        # Process command
        # Speak response
```

### Monitoring Agent

```python
# Agent that periodically checks environment
async def monitor():
    while True:
        # Capture frame every 5 seconds
        # Detect anomalies
        # Alert via speech if needed
        await asyncio.sleep(5)
```

---

Happy building! 🚀
