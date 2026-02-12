# ANSE Design Documentation

## Architecture Overview

ANSE (Agent Nervous System Engine) provides a local, sandboxed environment where AI agents can access sensors (camera, microphone) and actuators (text-to-speech) through a clean API abstraction.

### Core Principles

1. **Tool-First Design** - All capabilities are exposed as callable functions. No automatic preprocessing.
2. **Agent Autonomy** - The agent decides when and which tools to call.
3. **Local by Default** - Raw sensor data stays on the local machine.
4. **Deterministic Execution** - Reproducible experiments via event logging.
5. **Minimal Safety** - Permission scopes, rate limits, and human approval for sensitive operations.

---

## System Components

### 1. EngineCore

**Responsibilities:**
- Initialize and coordinate all subsystems
- Register built-in tools
- Configure rate limits from policy
- Provide top-level statistics

**Key Methods:**
- `__init__(policy_path)` - Initialize engine with optional custom policy
- `run(host, port)` - Start the WebSocket server
- `get_stats()` - Retrieve system statistics

---

### 2. ToolRegistry

**Responsibilities:**
- Maintain a registry of available tools
- Store tool metadata (schema, sensitivity, cost hints)
- Execute tool functions

**Key Methods:**
- `register(name, func, schema, description, sensitivity, cost_hint)` - Register a tool
- `list_tools()` - Get metadata for all tools
- `call(name, args)` - Execute a tool
- `has_tool(name)` - Check if tool exists

**Tool Metadata:**
```python
{
    "func": async_function,
    "schema": {...},           # JSON Schema for parameters
    "description": "...",      # Human-readable description
    "sensitivity": "low|medium|high",
    "cost_hint": {
        "latency_ms": 200,
        "expensive": False
    }
}
```

---

### 3. WorldModel

**Responsibilities:**
- Maintain append-only event log
- Provide rolling history of observations
- Enable replay and debugging

**Key Methods:**
- `append_event(event)` - Add event to history
- `get_recent(n)` - Get last N events
- `get_events_for_agent(agent_id, n)` - Get agent-specific history

**Event Structure:**
```python
{
    "timestamp": 1234567890.123,
    "type": "tool_call|tool_result",
    "agent_id": "agent-1",
    "call_id": "c-0001",
    "tool": "capture_frame",
    "args": {...},
    "result": {...}
}
```

---

### 4. Scheduler

**Responsibilities:**
- Execute tool calls with timeouts
- Enforce rate limits
- Log calls and results to WorldModel

**Key Methods:**
- `set_rate_limit(tool_name, calls_per_minute)` - Configure rate limit
- `execute_call(agent_id, call_id, tool, args, timeout)` - Execute with safety checks
- `get_stats()` - Get execution statistics

**Rate Limiting:**
- Token bucket algorithm per tool
- Sliding window of 60 seconds
- Returns `rate_limited` error when exceeded

---

### 5. AgentBridge

**Responsibilities:**
- Expose tools via WebSocket server
- Handle JSON-RPC style requests
- Manage agent connections

**Key Methods:**
- `serve(host, port)` - Start WebSocket server
- `handle_client(websocket, path)` - Handle individual connections

**Supported Methods:**
- `list_tools` - Enumerate available tools
- `call_tool` - Execute a tool
- `get_tool_info` - Get detailed tool metadata
- `get_history` - Retrieve event history
- `ping` - Connectivity test

---

### 6. PermissionManager

**Responsibilities:**
- Enforce safety policy
- Manage agent scopes
- Determine approval requirements

**Key Methods:**
- `register_agent(agent_id, scopes)` - Register agent with permissions
- `check_permission(agent_id, tool, scope)` - Verify access
- `requires_approval(tool, scope)` - Check if human approval needed
- `get_rate_limit(tool)` - Get configured rate limit

**Policy Configuration:**
See `safety_policy.yaml` for:
- Default scopes
- Sensitive operations
- Rate limits
- Approval requirements
- Data retention policies

---

## Tool Implementation Pattern

All tools follow this pattern:

```python
async def tool_name(arg1: type1, arg2: type2 = default) -> Dict[str, Any]:
    """
    Tool description.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Result dictionary or error
    """
    # Validate inputs
    if invalid:
        return {"error": "error_type", "message": "..."}
    
    try:
        # Perform operation
        result = do_work()
        
        return {
            "field1": value1,
            "field2": value2,
        }
    except Exception as e:
        return {"error": "operation_failed", "message": str(e)}
```

**Key Requirements:**
- Must be async function
- Return dictionary (never raise exceptions to caller)
- Include error handling with informative error types
- Provide meaningful result fields

---

## Data Flow

### Tool Call Flow

```
Agent → WebSocket → AgentBridge → Scheduler → ToolRegistry → Tool
  ↓                                    ↓            ↓
  ←─────────────────────────────── Result ────── Result
                                       ↓
                                  WorldModel
                                  (event log)
```

1. Agent sends `call_tool` request via WebSocket
2. AgentBridge validates request structure
3. Scheduler checks rate limits and permissions
4. Scheduler logs call event to WorldModel
5. ToolRegistry executes the tool function
6. Scheduler logs result event to WorldModel
7. Result returned to agent via WebSocket

---

## Safety Mechanisms

### 1. Permission Scopes

Tools can require specific scopes:
- `camera:read:dev` - Development camera access
- `microphone:read:dev` - Development microphone access
- `network:outbound` - Network access (sensitive)
- `filesystem:write` - File writing (sensitive)

### 2. Rate Limiting

- Per-tool limits (calls per minute)
- Sliding window implementation
- Returns error when exceeded
- No request queuing (fail fast)

### 3. Timeouts

- Default 30-second timeout per tool
- Configurable per-tool or per-call
- Prevents runaway executions

### 4. Approval Requirements

Sensitive operations can require human approval:
- Network access
- Actuator control
- Filesystem writes

(Approval mechanism to be implemented in future version)

### 5. Data Retention

- Raw media files TTL: 1 hour
- Event logs TTL: 24 hours
- Storage quotas per agent

---

## Extensibility

### Adding New Tools

1. Implement async function following tool pattern
2. Register in `EngineCore._register_tools()`:

```python
self.tools.register(
    name="my_tool",
    func=my_tool_function,
    schema={...},
    description="What it does",
    sensitivity="low|medium|high",
    cost_hint={"latency_ms": 100}
)
```

3. Add to safety policy if needed:

```yaml
rate_limits:
  my_tool: 20
```

### Custom Tool Packages

Create tool packages in `anse/tools/`:

```python
# anse/tools/custom.py
async def my_custom_tool(param: str) -> Dict[str, Any]:
    # Implementation
    return {"result": "..."}
```

Then register in custom EngineCore subclass.

---

## Future Roadmap

### Short Term
- Persistent audit log with replay capability
- Simulated sensors for offline training
- Thread pool for blocking tool operations
- Better async handling throughout

### Medium Term
- SDR (software-defined radio) tool
- Browser automation tool
- Filesystem navigation tool
- Web UI for operator approvals
- Multi-agent isolation and quotas

### Long Term
- Language SDKs (JS, Go, Rust)
- Community tool marketplace
- Simulated environments for training
- Transfer learning benchmarks (sim → real)
- Distributed execution across machines

---

## Development Notes

### Testing Strategy

1. **Unit Tests** - Individual tool functions
2. **Integration Tests** - Full WebSocket protocol
3. **Load Tests** - Rate limiting and concurrent agents
4. **Security Tests** - Permission enforcement

### Dependencies

**Core:**
- `websockets` - WebSocket server
- `pyyaml` - Policy configuration

**Tools:**
- `opencv-python` - Camera access
- `sounddevice` - Microphone access
- `soundfile` - Audio file I/O
- `pyttsx3` - Text-to-speech
- `numpy` - Array operations

### Performance Considerations

- All tools are async to avoid blocking
- Rate limiting prevents resource exhaustion
- Media files stored locally with TTL cleanup
- Event log uses bounded deque for memory efficiency

---

## Security Considerations

### Threat Model

**In Scope:**
- Malicious agent exceeding rate limits
- Agent attempting unauthorized operations
- Resource exhaustion attacks
- Data exfiltration via tool results

**Out of Scope (for v0):**
- Network-based attacks on WebSocket
- Multi-agent collision attacks
- Side-channel information leakage

### Mitigations

1. **Local-Only by Default** - No network tools in v0
2. **Rate Limiting** - Prevents DoS
3. **Timeouts** - Prevents hanging operations
4. **Scoped Permissions** - Least privilege model
5. **Event Logging** - Audit trail for forensics
6. **Data TTL** - Automatic cleanup of sensitive data

---

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Event Log

```python
core = EngineCore()
# ... after some operations ...
events = core.world.get_all_events()
for event in events:
    print(event)
```

### Monitor Rate Limits

```python
stats = core.scheduler.get_stats()
print(stats["rate_limits"])
```

---

## References

- JSON Schema: https://json-schema.org/
- WebSocket Protocol: https://websockets.readthedocs.io/
- OpenCV: https://docs.opencv.org/
- PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
