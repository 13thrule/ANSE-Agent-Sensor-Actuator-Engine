# ANSE Dashboard Bridge

Safe, read-focused bridge between ANSE and a local web dashboard. Provides real-time access to robot state and safe control operations.

## Overview

The Dashboard Bridge plugin exposes a curated set of tools for web-based dashboards, with built-in:
- **Read-only access** to robot state (camera, audio, motors, memory, reflexes, rewards)
- **Safe control** with permission scopes and rate limiting
- **Operator Mode** toggle in the GUI (manual vs. autonomous)
- **Emergency stop** button for immediate motor shutdown

## Quick Start

### 1. Enable the Plugin

The plugin automatically loads as part of ANSE. No additional configuration needed.

### 2. Connect from Frontend

```typescript
import { connect, call } from './dashboard_client';

// Connect to ANSE WebSocket
await connect();

// Call dashboard_bridge tools
const frame = await call('get_camera_frame');
const motors = await call('get_motor_status');
```

### 3. Use in Svelte/React

See `DashboardExample.svelte` for a complete example with:
- Live camera feed
- Motor control (Operator Mode)
- Reflex status
- Long-term memory browser
- Reward system tracking
- Plugin inventory

## Available Tools

### Read-Only (Safe)

| Tool | Description | Rate Limit |
|------|-------------|-----------|
| `get_camera_frame` | Base64 JPEG camera feed | 30/min |
| `get_audio_chunk` | Audio PCM samples | 20/min |
| `get_motor_status` | Current wheel speeds, servo angles | 20/min |
| `get_reflex_status` | All configured reflex rules | 20/min |
| `get_memory_entries` | Long-term memory store | 20/min |
| `get_reward_state` | Reward total, history, goal status | 20/min |
| `get_body_schema` | Robot sensors, actuators, joints | 20/min |
| `get_plugin_status` | Loaded plugins and versions | 20/min |
| `get_world_model_events` | Recent world model log | 20/min |
| `get_agent_messages` | LLM agent chat history | 20/min |

### Control (Operator Mode)

| Tool | Description | Rate Limit | Safety |
|------|-------------|-----------|--------|
| `set_wheel_speed` | Set left/right wheel speeds (-100 to 100) | 10/min | Hardware |
| `set_servo_angle` | Set servo position (0-180°) | 10/min | Hardware |
| `emergency_stop` | Stop all motors immediately | 5/min | Hardware |
| `toggle_reflex` | Enable/disable a reflex rule | 5/min | System |
| `delete_memory_entry` | Delete single memory | 5/min | System |
| `clear_memory` | Clear all memories | 1/min | System |

## Architecture

```
ANSE Engine
    ↓
[Dashboard Bridge Plugin]
    ↓
WebSocket JSON-RPC (port 8765)
    ↓
Web Frontend (Svelte/React)
```

### Plugin Integration

The Dashboard Bridge reads state directly from other plugins:

- **Motor Control** → wheel speeds, servo positions
- **Reflex System** → active reflex rules
- **Long-Term Memory** → stored memories
- **Reward System** → total reward, history
- **Body Schema** → sensors, actuators, joints

No additional modifications needed—the bridge wraps existing plugin state.

## Frontend Client

### `dashboard_client.ts`

Minimal WebSocket JSON-RPC client (< 200 lines):

```typescript
import { connect, call, disconnect } from './dashboard_client';

// Connect
await connect();

// Call tools
const result = await call('get_motor_status');

// Disconnect
disconnect();
```

**Features:**
- Auto-reconnect hooks (easily extensible)
- Request timeout support
- Push notification support (for future features)
- TypeScript types included

### Environment Variables

```env
VITE_ANSE_WS=ws://127.0.0.1:8765  # Override WebSocket URL
```

## Example: Live Camera Feed

```svelte
<script>
  import { call } from './dashboard_client';

  let frame = '';

  async function loadFrame() {
    frame = await call('get_camera_frame');
  }
</script>

<button on:click={loadFrame}>Refresh</button>
<img src={`data:image/jpeg;base64,${frame}`} alt="Camera" />
```

## Example: Motor Control

```typescript
// Only works if GUI is in Operator Mode
await call('set_wheel_speed', {
  left_speed: 50,
  right_speed: 30
});

await call('set_servo_angle', {
  id: 1,
  angle: 90
});
```

## Example: Memory Browser

```typescript
// List memories
const entries = await call('get_memory_entries', { limit: 20 });

// Delete one
await call('delete_memory_entry', { memory_id: 'abc123' });

// Clear all (with confirmation!)
await call('clear_memory');
```

## Operator Mode

The GUI has two modes:

1. **View Mode (👁️)** - Read-only, no motor control
2. **Operator Mode (⚠️)** - Can set wheel speeds, servo angles

This prevents accidental commands. In Operator Mode:
- `set_wheel_speed` and `set_servo_angle` are enabled
- Emergency stop is always available
- All commands are logged

## Security

### Permission Scopes

All tools are assigned scopes:
- `public`: Read-only, no restrictions
- `hardware`: Motor/actuator control, rate-limited
- `system`: System state changes, rate-limited

### Rate Limiting

- Hardware tools (motors): 5-10 calls/min
- System tools (memory, reflex): 1-5 calls/min
- Read tools: 20-30 calls/min

### Operator Mode Toggle

Control operations require Operator Mode to be active in the GUI, adding a second confirmation layer.

## Extending the Bridge

To add a new tool to the dashboard:

1. Add method to `DashboardBridgePlugin`:
   ```python
   async def new_tool(self, param1: str) -> Dict[str, Any]:
       result = await self.plugins_ref["some_plugin"].method()
       return result
   ```

2. Add YAML schema in `plugin.yaml`:
   ```yaml
   - name: new_tool
     description: Tool description
     parameters:
       type: object
       properties:
         param1:
           type: string
   ```

3. Call from frontend:
   ```typescript
   await call('new_tool', { param1: 'value' });
   ```

## Troubleshooting

### WebSocket not connecting
- Ensure ANSE is running on port 8765
- Check `VITE_ANSE_WS` environment variable
- Verify firewall rules

### Motor commands not working
- Switch GUI to **Operator Mode**
- Check rate limiting (10 calls/min max)
- Verify Motor Control plugin is loaded

### Memory operations failing
- Check Long-Term Memory plugin is active
- Verify memory IDs are valid
- Clear memory has 1/min rate limit

## Next Steps

- **Integrate into your UI framework** - Copy `DashboardExample.svelte` as a template
- **Add custom tools** - Extend the bridge with domain-specific controls
- **Set up authentication** - Add token-based auth to WebSocket if needed
- **Deploy to production** - Use HTTPS/WSS and proper CORS headers
