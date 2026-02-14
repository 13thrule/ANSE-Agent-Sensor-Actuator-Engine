# ANSE Dashboard + Backend - Quick Start

**Get everything running in 2 commands (across 2 terminals)**

---

## Prerequisites

- Python 3.7+
- ANSE project installed
- Dependencies: `pip install -r requirements.txt`

---

## Start in 30 Seconds

### Terminal 1: Backend Server
```bash
python backend/websocket_backend.py
```

**Wait for this output** (shows server is ready):
```
✓ ANSE Engine initialized
✓ World Model ready
✓ WebSocket server running on ws://localhost:8001
Waiting for connections...
```

---

### Terminal 2: Dashboard HTTP Server
```bash
cd dashboard
python -m http.server 8002
```

**Output** (shows server is ready):
```
Serving HTTP on 0.0.0.0 port 8002 (http://0.0.0.0:8002/) ...
```

---

### Open Browser

👉 **Go to: `http://localhost:8002/`**

You should see:
- **Sensor Panel**: Distance readings (50cm → 5cm → 50cm repeating)
- **Actuator Panel**: Motor state (IDLE, STOPPED, MOVING)
- **World Model Panel**: Brain's interpreted state
- **Reflex Panel**: Triggered rules (proximity_safeguard, clear_to_move)
- **Event Log**: All events in real-time

---

## What's Happening?

```
Terminal 1 (Backend):
  └─ Runs ANSE nervous system simulation
     ├─ Sensor emits distance readings every 1.5s
     ├─ Brain interprets as SAFE or DANGER
     ├─ Reflexes trigger based on conditions
     ├─ Actuator executes (STOP or MOVE)
     └─ Broadcasts events via WebSocket

Terminal 2 (Dashboard HTTP):
  └─ Just serves the HTML/CSS/JS files on port 8002

Browser:
  └─ Loads from http://localhost:8002/
     └─ Connects to WebSocket at ws://localhost:8001
        └─ Receives events from backend
           └─ Displays in real-time
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ Backend: ws://localhost:8001 (Terminal 1)           │
│ • ANSE EngineCore                                   │
│ • Nervous system simulation                         │
│ • WebSocket event broadcaster                       │
└─────────────────────┬───────────────────────────────┘
                      │ ws:// (WebSocket events)
                      ↓
┌─────────────────────────────────────────────────────┐
│ Your Web Browser (http://localhost:8002/)           │
│ • Dashboard UI (HTML/CSS/JS)                        │
│ • Real-time panel updates                           │
│ • Event log display                                 │
└─────────────────────────────────────────────────────┘
                      ↑ HTTP serving
                      │
┌─────────────────────────────────────────────────────┐
│ Dashboard HTTP Server (Terminal 2, port 8002)       │
│ • Serves HTML/CSS/JavaScript files                  │
└─────────────────────────────────────────────────────┘
```

---

## What You're Seeing

### Sensor Panel
Shows **distance sensor readings** (in cm):
- Pattern cycles: 50 → 5 → 50 (repeat)
- Update rate: Every 1.5 seconds
- This is the "nervous system's touch sensation"

### Actuator Panel
Shows **motor state**:
- **IDLE**: No sensor data yet
- **STOPPED**: Distance < 10cm (danger detected!)
- **MOVING**: Distance > 15cm (safe to move)

### World Model Panel
Shows **what the brain thinks** about the world:
- `distance_cm`: Latest sensor reading
- `safe`: Boolean (true = safe, false = danger)
- `actuator_state`: Current motor state
- `last_reflex`: Which safety rule triggered last

### Reflex Panel
Shows **which safety rules were triggered**:
- **proximity_safeguard**: Triggers when distance < 10cm
- **clear_to_move**: Triggers when distance > 15cm

### Event Log
**Chronological record** of:
- Every sensor reading
- Every world model update
- Every reflex decision
- Every actuator command

---

## Customization

### Change Port Numbers

**Backend (default: 8001)**
```python
# Edit backend/websocket_backend.py, line ~271:
backend = ANSEWebSocketBackend(
    host="0.0.0.0",
    port=9000,  # ← Change this
    debug=False
)
```

**Dashboard (default: 8002)**
```bash
cd dashboard
python -m http.server 9001  # ← Different port
```

Then in dashboard, update `/dashboard/js/app.js`:
```javascript
window.dashboard = new ANSEDashboard({
    wsUrl: 'ws://localhost:9000',  // ← Match backend port
    autoConnect: true
});
```

---

### Enable Debug Logging

**Backend debug mode**:
```python
# Edit backend/websocket_backend.py, line ~271:
backend = ANSEWebSocketBackend(
    host="0.0.0.0",
    port=8001,
    debug=True  # ← Enable timing logs
)
```

Then run backend again - you'll see detailed timing info.

---

### Modify Sensor Simulation

**Change distance range**:
```python
# Edit backend/websocket_backend.py, line ~160:
# Approach pattern
self.distance = max(5, 50 - (iteration * 5.5))  # ← Change 5, 50, 5.5

# Recede pattern
self.distance = min(50, 5 + ((iteration - 8) * 5.5))  # ← Change values
```

**Change reflex thresholds**:
```python
# Edit backend/websocket_backend.py, line ~195:
if self.distance < 10 and self.movement_state != "STOPPED":  # ← Change 10
    # trigger STOP

if self.distance > 15 and self.movement_state != "MOVING":  # ← Change 15
    # trigger MOVING
```

---

## Troubleshooting

### "Connection refused on ws://localhost:8001"
- Backend not running? Check Terminal 1
- Is backend printing "Waiting for connections..."?
- If not, try: `python backend/websocket_backend.py`

### "Address already in use"
- Port 8001 or 8002 already used?
- Find process: `netstat -ano | findstr ":8001"`
- Kill process: `taskkill /PID <PID> /F`
- Then try again

### "No events showing in dashboard"
- Dashboard connected? Check browser console (F12)
- Look for WebSocket connection in Network tab
- Should show messages being received

### Dashboard is blank
- Check browser console (F12 → Console tab)
- Look for JavaScript errors
- Try hard refresh: Ctrl+Shift+R

---

## Next Steps

### Learn More
- See `backend/README.md` for backend details
- See `dashboard/README.md` for dashboard architecture
- See `examples/gui_demo/` for original demo

### Production Deployment
- Run backend on edge device/IoT hardware
- Serve dashboard from web server
- See `backend/README.md` for Docker, Nginx, Systemd setup

### Customize Further
- Add new sensors to backend
- Add new panel types to dashboard
- Connect to real ANSE reflexes and actuators

---

## Command Cheat Sheet

```bash
# Start backend
python backend/websocket_backend.py

# Start dashboard (from dashboard dir)
cd dashboard && python -m http.server 8002

# Open in browser
http://localhost:8002

# View backend logs (with debug=True)
python backend/websocket_backend.py

# Kill running server
Ctrl+C (in the terminal)

# Test backend individually
python -c "from backend.websocket_backend import ANSEWebSocketBackend; print('✓ Backend imports successfully')"

# Check ports in use
netstat -ano | findstr ":8001"
netstat -ano | findstr ":8002"
```

---

## Architecture Overview

The complete system has **3 layers**:

1. **Backend Layer** (port 8001)
   - ANSE EngineCore (nervous system)
   - WebSocket server
   - Event broadcasting
   - Sensor simulation + Reflex logic + Actuator execution

2. **Transport Layer**
   - WebSocket protocol
   - Real-time event delivery
   - Stateless (easy to scale)

3. **Frontend Layer** (port 8002)
   - HTML/CSS/JavaScript
   - Real-time UI updates
   - 5 panel types
   - Event logging

**Key Design**: Each layer can be replaced independently:
- Backend → swap with your own ANSE implementation
- Transport → swap with HTTP polling or gRPC if needed
- Frontend → build your own dashboard UI

---

## Success Criteria

✅ Backend terminal shows "Waiting for connections..."  
✅ Dashboard loads at http://localhost:8002/  
✅ Panels appear (sensor, actuator, world model, reflex, event log)  
✅ Distance values update every 1.5 seconds  
✅ Actuator state changes (IDLE → STOPPED → MOVING)  
✅ Event log shows new events appearing  

If all checked: **You're done!** 🎉

---

*ANSE Dashboard + Backend - Running and streaming events in real-time.* ✨
