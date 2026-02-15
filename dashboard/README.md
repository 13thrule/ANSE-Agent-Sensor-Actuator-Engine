# ANSE Dashboard

**Production-Ready Real-Time Monitoring Dashboard for ANSE (Agent State & Event Engine)**

The ANSE Dashboard is a plugin-driven web interface that provides real-time visibility into the ANSE agent's perception, decision-making, and actions. It dynamically creates panels for active sensors, actuators, reflexes, and world model state.

## Features

✨ **Real-Time Event Streaming**
- Connects to ANSE backend via WebSocket
- Live updates for sensor readings, reflex triggers, actuator commands, and world model changes
- Low-latency event distribution to dashboard panels

🔌 **Plugin-Driven Architecture**
- Dynamically creates panels for active plugins
- Supports unlimited sensor types (distance, temperature, camera, microphone, etc.)
- Supports unlimited actuator types (movement, speaker, TTS, etc.)
- Auto-discovers new plugins on connection

📊 **Built-In Panel Types**

1. **Sensor Panel** - Real-time sensor readings
   - Current value display
   - Min/Max/Average statistics
   - Sparkline chart visualization
   - Per-plugin auto-cleanup

2. **Actuator Panel** - Actuator state and command history
   - Current state badge (IDLE, MOVING, STOPPED, ERROR)
   - Command count and last-executed timestamp
   - State transition history with duration tracking
   - Smooth animations on state changes

3. **State Panel** - Current hardware state
   - Current sensor readings
   - Safety status (SAFE/DANGER)
   - Active actuator state
   - Last triggered reflex
   - Distance trend indicators (↗ CLOSER, ↘ FARTHER, → STABLE)
   - Color-coded safety (green/red)
   - State history (last 10 snapshots)

4. **Rules Panel** - Validation and action tracking
   - Active rules with conditions
   - Recent rule history
   - Trigger count per rule
   - Time duration in current state

5. **Event Log Panel** - System event stream
   - Real-time event display with timestamps
   - Filterable by event type (all/sensor/reflex/actuator/worldmodel)
   - Expandable event details with JSON data
   - Auto-scrolling with toggle option
   - Color-coded event types
   - Clear button to reset log

🎨 **Modern UI**
- Clean, professional dark theme
- Responsive grid layout
- Smooth animations and transitions
- Color-coded state indicators
- Custom scrollbars and form elements
- Mobile-responsive (single column on small screens)

## Directory Structure

```
dashboard/
├── index.html                # Main entry point
├── css/
│   ├── styles.css           # Main styles, header, layout
│   ├── panels.css           # Panel and component styles
│   └── animations.css       # Keyframe animations
└── js/
    ├── websocket.js         # WebSocket connection manager
    ├── app.js               # Main application controller
    └── panels/
        ├── panelManager.js  # Panel lifecycle management
        ├── basePanel.js     # Base panel class
        ├── sensorPanel.js   # Sensor visualization
        ├── actuatorPanel.js # Actuator state display
        ├── worldmodelPanel.js # Interpreted state
        ├── reflexPanel.js   # Reflex tracking
        └── eventlogPanel.js # Event stream viewer
```

## Getting Started

### 1. Start the ANSE Backend

Ensure your ANSE backend is running with WebSocket enabled on `ws://localhost:8000`:

```python
# Start your ANSE server
python your_anse_server.py
```

### 2. Open the Dashboard

Simply open the dashboard in your browser:

```
file:///path/to/dashboard/index.html
```

Or serve it via HTTP:

```bash
# Python
python -m http.server 8001 --directory dashboard

# OR Node.js
npx http-server dashboard -p 8001

# OR Live Server (VS Code extension)
# Right-click index.html → Open with Live Server
```

Then navigate to: `http://localhost:8001/`

### 3. Connect to Backend

Click the **"Connect"** button in the top right, or let it auto-connect on page load.

## Architecture

### Event Flow

```
ANSE Backend
    ↓ (WebSocket)
ANSEWebSocketManager
    ↓ (Event routing)
PanelManager
    ↓ (Per-event-type)
Specific Panels (Sensor, Actuator, World Model, etc.)
    ↓ (DOM updates)
Browser Display
```

### Message Format

All messages from ANSE backend follow this structure:

```typescript
{
  type: "sensor" | "reflex" | "actuator" | "worldmodel" | "system",
  timestamp: "2026-02-14T12:34:56.789Z",
  data: {
    // Type-specific data
    // See panel implementations for expected fields
  }
}
```

### Panel System

Each panel type extends `BasePanel` and implements:
- `getTitle()` - Panel header text
- `getContentHTML()` - Initial HTML structure
- `onRender()` - Setup after DOM insertion
- `onUpdate(event)` - Handle incoming events
- `onDestroy()` - Cleanup before removal

## Configuration

### WebSocket URL

Modify the URL in `js/app.js`:

```javascript
window.dashboard = new ANSEDashboard({
    wsUrl: 'ws://localhost:8000',  // ← Change this
    autoConnect: true
});
```

### Panel Container

Change the target container in `js/panels/panelManager.js`:

```javascript
const manager = new PanelManager('#panels-container');  // ← Change selector
```

## Event Types

### Sensor Event
```json
{
  "type": "sensor",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "sensor_name": "distance_sensor",
    "sensor_type": "distance",
    "value": 45.2
  }
}
```

### Reflex Event
```json
{
  "type": "reflex",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "reflex_name": "proximity_alert",
    "condition": "distance < 10cm",
    "triggered": true
  }
}
```

### Actuator Event
```json
{
  "type": "actuator",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "actuator_name": "movement",
    "actuator_type": "motor",
    "state": "MOVING"
  }
}
```

### World Model Event
```json
{
  "type": "worldmodel",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "distance_cm": 45.2,
    "safe": true,
    "actuator_state": "MOVING",
    "last_reflex": "proximity_alert",
    "total_events": 127
  }
}
```

### System Event
```json
{
  "type": "system",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "event_type": "plugin_loaded",
    "plugin_name": "camera_plugin",
    "plugin_type": "sensor"
  }
}
```

## Customization

### Adding a Custom Panel

1. Create `js/panels/customPanel.js`:

```javascript
class CustomPanel extends BasePanel {
    constructor(panelId, config) {
        super(panelId, config);
        this.panelType = 'custom';
    }

    getTitle() {
        return '📌 Custom Panel';
    }

    getContentHTML() {
        return '<div>Your content here</div>';
    }

    onUpdate(event) {
        // Handle event updates
    }
}

window.CustomPanel = CustomPanel;
```

2. Register in `js/app.js`:

```javascript
this.panelManager.registerPanel('custom', CustomPanel);
```

3. Include script in `index.html`:

```html
<script src="js/panels/customPanel.js"></script>
```

### Styling Custom Panels

Add CSS in `css/panels.css`:

```css
.custom-panel {
    /* Your styles */
}

.custom-content {
    /* Panel content styles */
}
```

## Performance

- **Event Batching**: Dashboard automatically batches updates (configurable)
- **Memory Management**: Keeps only recent event history (max 100 events per panel)
- **Efficient Rendering**: Only visible panels update on events
- **Optimized Scrolling**: Custom scrollbars with smooth performance
- **GPU Acceleration**: CSS animations use hardware acceleration

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires WebSocket support and ES6+ JavaScript features.

## Troubleshooting

### Dashboard Not Connecting

1. Check ANSE backend is running: `http://localhost:8000/health`
2. Check browser console for errors (F12)
3. Verify WebSocket URL in `js/app.js`
4. Check CORS headers from ANSE backend

### Panels Not Updating

1. Verify events are being sent by ANSE backend
2. Check panel data structure matches expected format
3. Look at Network tab in DevTools to see WebSocket messages
4. Check browser console for JavaScript errors

### Performance Issues

1. Reduce max event history: Edit panel max history sizes
2. Disable sensor charts if not needed
3. Use event filtering to reduce panel updates
4. Check browser resource usage (Task Manager)

## Integration with ANSE

The dashboard expects ANSE backend to:

1. Expose WebSocket on `ws://localhost:8000`
2. Send events in the documented message format
3. Include proper timestamp and type fields
4. Send world model snapshots after each event

See ANSE documentation for WebSocket integration details.

## License

Same as ANSE project. See LICENSE file.

## Contributing

To contribute improvements, panels, or features:

1. Follow existing code style
2. Add comments explaining complex logic
3. Test with multiple event types
4. Update this README with new features

---

**ANSE Dashboard** - Real-time visualization of agent-hardware state and event flow.
