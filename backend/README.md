# ANSE WebSocket Backend

**Production-ready WebSocket event server for the ANSE Dashboard**

This is a pure WebSocket backend that:
- Runs the ANSE nervous system simulation
- Broadcasts real-time events to all connected clients
- Emits sensor readings, reflex triggers, actuator actions, world model updates

No HTTP serving, no HTML files - just clean WebSocket events.

## Quick Start

### 1. Start the Backend

```bash
python backend/websocket_backend.py
```

You should see:
```
======================================================================
ANSE WebSocket Backend - Production Event Server
======================================================================

✓ ANSE Engine initialized
✓ World Model ready

Starting WebSocket server on ws://0.0.0.0:8001...
✓ WebSocket server running on ws://localhost:8001

Dashboard connection:
  ws://localhost:8001

Waiting for connections...
```

### 2. Start the Dashboard (separate terminal)

```bash
cd dashboard
python -m http.server 8002
```

Then open: `http://localhost:8002/`

### 3. The Backend Automatically Connects

The dashboard at port 8002 connects to the WebSocket backend at `ws://localhost:8001`.

Panels appear automatically as events flow in real-time.

---

## Architecture

The backend implements a complete **nervous system**:

```
┌─────────────────────────────────────────────────┐
│ 1. SENSOR PHASE                                 │
│    Distance sensor emits readings every 1.5s    │
│    Values: 50cm → 5cm → 50cm (repeating)        │
└──────────────────┬──────────────────────────────┘
                   │ sensor event
                   ↓
┌─────────────────────────────────────────────────┐
│ 2. WORLD MODEL                                  │
│    Brain records sensor reading                 │
│    Updates interpreted state (safe/danger)      │
└──────────────────┬──────────────────────────────┘
                   │ world model event
                   ↓
┌─────────────────────────────────────────────────┐
│ 3. REFLEX PHASE                                 │
│    Check conditions:                            │
│    • distance < 10cm  → trigger:  proximity     │
│    • distance > 15cm  → trigger:  clear_to_move│
└──────────────────┬──────────────────────────────┘
                   │ reflex event
                   ↓
┌─────────────────────────────────────────────────┐
│ 4. ACTUATOR PHASE                               │
│    Execute motor command:                       │
│    • STOP (when danger)                         │
│    • MOVING (when safe)                         │
└──────────────────┬──────────────────────────────┘
                   │ actuator event
                   ↓
┌─────────────────────────────────────────────────┐
│ 5. BROADCAST                                    │
│    Send all events to connected WebSocket       │
│    clients (Dashboard, tools, other listeners)  │
└─────────────────────────────────────────────────┘
```

---

## Event Types

The backend broadcasts 5 event types:

### 1. Sensor Event
```json
{
  "type": "sensor",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "sensor_name": "distance_sensor",
    "sensor_type": "distance",
    "value": 42.5
  }
}
```

### 2. World Model Event
```json
{
  "type": "worldmodel",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "distance_cm": 42.5,
    "safe": true,
    "actuator_state": "MOVING",
    "last_reflex": "clear_to_move",
    "total_events": 127
  }
}
```

### 3. Reflex Event
```json
{
  "type": "reflex",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "reflex_name": "proximity_safeguard",
    "condition": "distance < 10cm",
    "triggered": true
  }
}
```

### 4. Actuator Event
```json
{
  "type": "actuator",
  "timestamp": "2026-02-14T12:34:56.789Z",
  "data": {
    "actuator_name": "movement",
    "actuator_type": "motor",
    "state": "STOPPED"
  }
}
```

### 5. World Model Update (broadcast after each event)
Same structure as Event Type 2 - provides complete brain state snapshot.

---

## Configuration

### Change Port

Edit `backend/websocket_backend.py`, line ~271:

```python
backend = ANSEWebSocketBackend(
    host="0.0.0.0",
    port=8001,  # ← Change this
    debug=False
)
```

Then update dashboard connection in `dashboard/js/app.js`:

```javascript
window.dashboard = new ANSEDashboard({
    wsUrl: 'ws://localhost:8001',  // ← Change this
    autoConnect: true
});
```

### Enable Debug Logging

Set `debug=True` in the backend:

```python
backend = ANSEWebSocketBackend(
    host="0.0.0.0",
    port=8001,
    debug=True  # ← Enable timing info
)
```

---

## Customization

### Change Sensor Values

Edit `backend/websocket_backend.py`, the `simulate_distance_sensor()` method:

```python
# Line ~160
if iteration < 8:
    # Approach pattern (change thresholds)
    self.distance = max(5, 50 - (iteration * 5.5))
else:
    # Recede pattern (change thresholds)
    self.distance = min(50, 5 + ((iteration - 8) * 5.5))
```

### Change Reflex Rules

Edit `check_and_trigger_reflexes()` method:

```python
# Line ~195
if self.distance < 10 and self.movement_state != "STOPPED":  # ← Change threshold
    # Change reflex name
    self.last_reflex = "proximity_safeguard"
    # etc.
```

### Add More Sensors

1. Create a new async method `simulate_temperature_sensor()` or similar
2. Call it as another task in the `run()` method
3. Each sensor broadcasts its own events

---

## Performance

| Metric | Value |
|--------|-------|
| Event Rate | ~1 per 1.5s (configurable) |
| WebSocket Ping | Every 20s |
| Memory | Minimal (< 5MB) |
| CPU | Negligible (mostly sleeping) |
| Max Clients | Limited by system resources (tested up to 100+) |

---

## Monitoring

### Check Connected Clients

The backend logs client connections/disconnections:

```
→ Client 2108787935568 connected (3 total)
← Client 2108787797968 disconnected (2 remain)
```

### Watch Event Flow

With `debug=True`, see event timestamps:

```
[12:34:56] [event] sensor reading received
[12:34:56] [broadcast] 3 clients notified
[12:34:57] [reflex] proximity check: distance=8.5cm < 10cm → TRIGGER
```

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.7+

# Install dependencies
pip install websockets

# Verify ANSE is installed
python -c "from anse.engine_core import EngineCore"
```

### Dashboard won't connect

```bash
# 1. Backend must be running
#    ps aux | grep websocket_backend.py

# 2. Check port 8001
#    netstat -ano | findstr ":8001"

# 3. Check browser console (F12) for WebSocket errors

# 4. Verify dashboard points to correct URL:
#    Look in dashboard/js/app.js line ~330
```

### Events not flowing

```bash
# 1. Check backend logs for errors
#    Add debug=True for more info

# 2. Verify EventBroadcast is working
#    Backend should print "[DEMO] X events recorded..." every 5 events

# 3. Check browser Network tab
#    WebSocket should show incoming messages
```

---

## Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/anse-backend.service`:

```ini
[Unit]
Description=ANSE WebSocket Backend
After=network.target

[Service]
Type=simple
User=anse
WorkingDirectory=/opt/anse
ExecStart=/usr/bin/python3 backend/websocket_backend.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable anse-backend
sudo systemctl start anse-backend
sudo systemctl status anse-backend
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8001

CMD ["python", "backend/websocket_backend.py"]
```

```bash
docker build -t anse-backend .
docker run -p 8001:8001 anse-backend
```

### Nginx Proxy (WebSocket)

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location /ws {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
```

---

## Architecture Philosophy

This backend is intentionally **simple and focused**:

✓ **One job**: Broadcast nervous system events  
✓ **No HTTP**: Pure WebSocket, no HTML files  
✓ **No dependencies**: Only `websockets` library  
✓ **Testable**: Easy to mock and test events  
✓ **Extensible**: Add sensors/reflexes without breaking Dashboard  
✓ **Production-ready**: Error handling, client cleanup, reconnection support  

---

## Comparison: Backend vs Demo

| Aspect | Backend | Demo Server |
|--------|---------|------------|
| Purpose | Production event server | Quick validation |
| Serves HTML | ❌ No | ✅ Yes |
| WebSocket | ✅ Yes | ✅ Yes |
| Location | `/backend/` | `/examples/gui_demo/` |
| Use For | Production Dashboard | Learning/Testing |

Both work! The backend is cleaner for production.

---

## Next Steps

1. **Start both services**:
   - Terminal 1: `python backend/websocket_backend.py`
   - Terminal 2: `cd dashboard && python -m http.server 8002`

2. **Open dashboard**: `http://localhost:8002/`

3. **Watch events flow** in real-time

4. **Deploy to production** using systemd/Docker (see above)

---

*ANSE WebSocket Backend - Clean, simple, production-ready event server.* ✨
