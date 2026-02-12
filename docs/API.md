# ANSE API Documentation

## WebSocket Protocol

ANSE exposes tools to agents via a WebSocket server using a simple JSON-RPC style protocol.

### Connection

```javascript
ws://127.0.0.1:8765
```

All messages are JSON-encoded objects sent over the WebSocket connection.

---

## Methods

### 1. list_tools

List all available tools with their metadata.

**Request:**
```json
{
  "method": "list_tools"
}
```

**Response:**
```json
{
  "result": {
    "capture_frame": {
      "description": "Capture an RGB frame from camera",
      "schema": {...},
      "sensitivity": "medium",
      "cost_hint": {"latency_ms": 200, "expensive": false}
    },
    "say": {
      "description": "Speak text using text-to-speech",
      "schema": {...},
      "sensitivity": "low",
      "cost_hint": {"latency_ms": 500, "expensive": false}
    }
  }
}
```

---

### 2. call_tool

Execute a specific tool.

**Request:**
```json
{
  "method": "call_tool",
  "params": {
    "agent_id": "agent-1",
    "call_id": "c-0001",
    "tool": "capture_frame",
    "args": {
      "camera_id": 0
    }
  }
}
```

**Success Response:**
```json
{
  "status": "ok",
  "call_id": "c-0001",
  "result": {
    "frame_id": "abc123...",
    "path": "/tmp/anse/abc123.jpg",
    "width": 1920,
    "height": 1080,
    "channels": 3
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "call_id": "c-0001",
  "error": "rate_limited"
}
```

Possible error types:
- `rate_limited` - Tool call rate limit exceeded
- `timeout` - Tool execution exceeded timeout
- `tool_not_found` - Requested tool does not exist
- `invalid_args` - Tool arguments do not match schema

---

### 3. get_tool_info

Get detailed information about a specific tool.

**Request:**
```json
{
  "method": "get_tool_info",
  "params": {
    "tool": "capture_frame"
  }
}
```

**Response:**
```json
{
  "result": {
    "description": "Capture an RGB frame from camera",
    "schema": {
      "type": "object",
      "properties": {
        "camera_id": {"type": "integer", "default": 0},
        "out_dir": {"type": "string", "default": "/tmp/anse"}
      }
    },
    "sensitivity": "medium",
    "cost_hint": {"latency_ms": 200, "expensive": false}
  }
}
```

---

### 4. get_history

Retrieve recent events for the calling agent.

**Request:**
```json
{
  "method": "get_history",
  "params": {
    "n": 10
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "type": "tool_call",
      "timestamp": 1234567890.123,
      "agent_id": "agent-1",
      "call_id": "c-0001",
      "tool": "capture_frame",
      "args": {}
    },
    {
      "type": "tool_result",
      "timestamp": 1234567890.456,
      "agent_id": "agent-1",
      "call_id": "c-0001",
      "result": {
        "status": "ok",
        "result": {...}
      }
    }
  ]
}
```

---

### 5. ping

Simple connectivity test.

**Request:**
```json
{
  "method": "ping"
}
```

**Response:**
```json
{
  "result": "pong"
}
```

---

## Available Tools (v0)

### capture_frame

Capture an RGB frame from a camera.

**Arguments:**
- `camera_id` (integer, default: 0) - Camera device ID
- `out_dir` (string, default: "/tmp/anse") - Output directory

**Returns:**
- `frame_id` - Unique frame identifier
- `path` - File path to saved image
- `width` - Image width in pixels
- `height` - Image height in pixels
- `channels` - Number of color channels

**Rate Limit:** 30 calls/minute

---

### list_cameras

List available camera devices.

**Arguments:** None

**Returns:**
- `cameras` - List of camera IDs
- `count` - Number of available cameras

---

### record_audio

Record audio from the microphone.

**Arguments:**
- `duration` (number, default: 2.0) - Recording duration in seconds (max: 60)
- `samplerate` (integer, default: 16000) - Sample rate in Hz
- `channels` (integer, default: 1) - Number of audio channels
- `out_dir` (string, default: "/tmp/anse") - Output directory

**Returns:**
- `audio_id` - Unique audio identifier
- `path` - File path to saved audio
- `duration` - Actual recording duration
- `samplerate` - Sample rate used
- `channels` - Number of channels

**Rate Limit:** 10 calls/minute

---

### list_audio_devices

List available audio input devices.

**Arguments:** None

**Returns:**
- `devices` - List of device info objects
- `count` - Number of available devices
- `default` - Default device ID

---

### say

Speak text using text-to-speech.

**Arguments:**
- `text` (string, required) - Text to speak (max: 1000 chars)
- `rate` (integer, default: 200) - Speech rate in words per minute
- `volume` (number, default: 1.0) - Volume level (0.0 to 1.0)

**Returns:**
- `spoken` - Boolean indicating success
- `text` - Text that was spoken
- `length` - Length of text
- `rate` - Rate used
- `volume` - Volume used

**Rate Limit:** 20 calls/minute

---

### get_voices

List available TTS voices.

**Arguments:** None

**Returns:**
- `voices` - List of voice info objects
- `count` - Number of available voices

---

## Error Handling

All errors are returned as JSON objects with an `error` field:

```json
{
  "error": "error_type",
  "message": "Human-readable description"
}
```

Common error types:
- `invalid_json` - Request was not valid JSON
- `unknown_method` - Method not recognized
- `missing_tool_name` - Tool name not provided
- `internal_error` - Unexpected server error

---

## Safety and Rate Limiting

- Tools have rate limits enforced per minute
- Sensitive operations may require additional scopes
- All tool calls and results are logged to the world model
- Raw media files have a TTL of 1 hour by default

See `safety_policy.yaml` for detailed safety configuration.
