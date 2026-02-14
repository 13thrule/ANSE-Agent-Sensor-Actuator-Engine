# ANSE Dashboard - Quick Start Guide

## 30-Second Setup

### 1. Ensure Backend is Running
```bash
# Your ANSE server should be running on ws://localhost:8000
python your_anse_server.py
```

### 2. Open Dashboard
Navigate to:
```
file:///path/to/anse_project/dashboard/index.html
```

Or serve via HTTP:
```bash
python -m http.server 8001 --directory dashboard
# Then visit: http://localhost:8001/
```

### 3. Click Connect
Click the blue **"Connect"** button in the top right.

### 4. Watch Live Data
Panels appear automatically for:
- 📡 Sensor readings
- ⚙️ Actuator states
- 🧠 Brain state (world model)
- ⚡ Reflexes triggered
- 📋 Complete event log

---

## What You're Seeing

### Header
- **Logo** - ANSE branding
- **Connection Status** - Green glow = connected, gray = disconnected
- **Connect Button** - Toggle connection

### Stats Bar
- **Panels** - Number of active panels
- **Events** - Total events received
- **Uptime** - Time connected
- **Status** - Connection state

### Main Grid

Panels are arranged in a responsive grid:

```
┌─────────────────────┐  ┌──────────────────┐
│  World Model        │  │  Reflexes        │
│  Brain State        │  │  Recent Triggers │
└─────────────────────┘  └──────────────────┘

┌─────────────────────┐  ┌──────────────────┐
│  Sensor: Distance   │  │  Actuator: Motor │
│  Real-time Values   │  │  State + History │
└─────────────────────┘  └──────────────────┘

┌──────────────────────────────────────────┐
│  Event Log                               │
│  All events with filtering               │
└──────────────────────────────────────────┘
```

---

## Panel Guide

### 🧠 World Model Panel
**What it shows**: Your agent's interpreted perception and state

- **Distance** - Current sensor reading (cm)
- **Safety** - SAFE (green) or DANGER (red)
- **Actuator** - Current movement state
- **Last Reflex** - Which reflex is active
- **Events** - Total nervous system events

**Bonus**: Distance trend indicator
- ↗ CLOSER - Object approaching (orange)
- ↘ FARTHER - Object receding (blue)  
- → STABLE - Not moving (gray)

**History**: Shows last 5 state snapshots

### ⚡ Reflexes Panel
**What it shows**: Automatic reactions triggered

- **Active Reflexes** - Currently executing
- **Trigger Count** - How many times triggered
- **Duration** - How long active
- **History** - Recent trigger events

### 📡 Sensor Panels
**What it shows**: Real-time sensor data

Created automatically for each active sensor:
- Distance sensor → distance in cm
- Temperature sensor → °C reading
- Camera → image dimensions
- etc.

**Displays**:
- Current value (large, colored)
- Min/Max/Average
- Sparkline chart

### ⚙️ Actuator Panels
**What it shows**: Motor/movement states

Created automatically for each active actuator:
- Motor → movement state
- Speaker → audio output
- etc.

**Displays**:
- State badge (IDLE, MOVING, STOPPED, ERROR)
- Command count
- Last execution time
- State history

### 📋 Event Log
**What it shows**: Complete real-time event stream

**Features**:
- Filter by type (All/Sensors/Reflexes/Actuators/World Model)
- Click "Details" to see JSON data
- Auto-scroll toggle
- Clear button to reset

---

## Common Tasks

### I want to see what sensors are active
→ Look at the sensor panels that appear. Each sensor type gets its own panel.

### I want to track a specific reflex
→ Open the **Reflexes** panel. It shows active reflexes and their trigger history.

### I want to see the agent's internal state
→ Check the **World Model** panel. It shows distance, safety status, last reflex, and trend.

### I want to debug issues
→ Filter the **Event Log** to see specific event types. Expand "Details" to see raw data.

### I want to record what happened
→ Screenshot the dashboard or open DevTools (F12) → Network tab to capture WebSocket messages.

### I want to know if sensor is working
→ Open the sensor panel. If no new values appear, the sensor may not be emitting events.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F12 | Open Developer Tools |
| Ctrl+Shift+K | Focus Event Log filter |
| Ctrl+L | Clear Event Log |

---

## Tips & Tricks

### 1. Multi-Monitor Setup
Serve dashboard on one screen, open DevTools on another:
```bash
python -m http.server 8001 --directory dashboard
# Browser 1: http://localhost:8001/ (fullscreen)
# Browser 2: http://localhost:8001/ (with DevTools)
```

### 2. Dark Room Monitoring
The dashboard is designed for dark environments. Perfect for 24/7 monitoring.

### 3. Event Log Filtering
Use filter buttons to focus on specific event types:
- "All" - See everything
- "Sensors" - Only sensor readings
- "Reflexes" - Only reflex triggers
- "Actuators" - Only motor commands
- "World Model" - Only brain state updates

### 4. Performance
- If dashboard feels slow, click "Clear" in Event Log
- Disable unused panels by closing the server and removing panel creation code
- Use sensor chart sparingly (high CPU)

### 5. Mobile Viewing
Dashboard adapts to mobile screens:
```
# Phone
1 panel per row, single column

# Tablet
2 panels per row

# Desktop
3-4 panels per row
```

---

## Expected Data Format

Your ANSE backend should send messages like:

```json
{
  "type": "sensor",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "sensor_name": "distance",
    "sensor_type": "distance",
    "value": 45.2
  }
}
```

Event types:
- **sensor** - Sensor reading
- **reflex** - Reflex trigger/clear
- **actuator** - Motor command
- **worldmodel** - Brain state snapshot
- **system** - Plugin load/unload

---

## Troubleshooting

### Dashboard won't connect
```
✗ Check backend is running on localhost:8000
✗ Check firewall allows connections
✗ Restart both backend and browser
```

### Panels appear but don't update
```
✗ Verify backend is sending events
✗ Check browser console (F12) for errors
✗ Look at Network tab to see messages
```

### Event log shows nothing
```
✗ Check backend is actually generating events
✗ Verify reflex is triggered in code
✗ Confirm actuator is executing
```

### Dashboard is slow
```
✗ Close other browser tabs
✗ Clear event log history
✗ Reduce update frequency in backend
```

---

## Next Level

### Add Custom Panels
See `DASHBOARD_ARCHITECTURE.md` for how to create custom panels.

### Change Colors
Edit CSS variables in `dashboard/css/styles.css`:
```css
:root {
    --primary-color: #00d4ff;      /* Change cyan */
    --secondary-color: #00ff00;    /* Change green */
    --danger-color: #ff3333;       /* Change red */
}
```

### Deploy Remotely
1. Serve dashboard from a web server
2. Update WebSocket URL in `js/app.js` to point to production backend
3. Open in any browser on your network

### Record Events
Use browser DevTools → Network tab to capture all WebSocket messages.

---

## Support

**Issues?**

1. Check browser console (F12) for errors
2. Look at Network tab to see WebSocket messages
3. Verify backend is sending correct JSON format
4. Check `DASHBOARD_ARCHITECTURE.md` for detailed docs

---

**ANSE Dashboard Ready!** 🚀

Your agent's nervous system is now visible, live, and ready to monitor.
