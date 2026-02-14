# Operator UI & Approval Console MVP

The Operator UI is a web-based dashboard for monitoring ANSE agents in real-time, managing approval tokens, and reviewing audit logs.

## ⚠️ Event-Driven Architecture

ANSE is built on an **event-driven nervous system model**, not polling. The Operator UI currently uses polling (`setInterval` every 2 seconds) for simplicity, with visibility detection to pause when the tab is hidden.

**For production use**, the Operator UI should be refactored to:
1. Subscribe to ANSE WebSocket event stream
2. React to `world_model_update` events pushed by the server
3. Remove all `setInterval()` polling loops

See [docs/EVENT_DRIVEN_ARCHITECTURE.md](../docs/EVENT_DRIVEN_ARCHITECTURE.md) for the complete nervous system model.

## Features

✅ **Real-time Agent Monitoring** - Live list of active agents with status
✅ **Audit Log Viewer** - Searchable history of all tool calls and events  
✅ **Approval Token Management** - Issue, revoke, and manage access tokens
✅ **Dark Theme Dashboard** - Professional, responsive UI
✅ **Basic Authentication** - Dev mode with simple username/password
✅ **REST API** - Full JSON REST API for integration

## Quick Start

### Installation

```bash
pip install -r operator_ui/requirements.txt
```

### Running the Operator UI

```bash
# Option 1: Start with ANSE engine
python start_with_ui.py

# Option 2: Start just the operator-ui server
python -m operator_ui.app
```

The UI will be available at: **http://127.0.0.1:5000**

**Default credentials:**
- Username: `admin`
- Password: `admin`

## Architecture

```
operator_ui/
├── app.py                 # Flask application and routes
├── models.py              # SQLAlchemy ORM models
├── requirements.txt       # Python dependencies
├── __init__.py
├── routes/                # API route modules (future)
├── static/
│   ├── dashboard.js       # Frontend JavaScript
│   └── styles.css         # Dark theme CSS
└── templates/
    └── index.html         # HTML dashboard
```

## API Reference

All API endpoints require HTTP Basic Authentication (`username:password`).

### Health & Status

```http
GET /health
```
Public health check (no auth required).

```json
{
  "status": "running",
  "version": "0.2.0"
}
```

### Agents

```http
GET /api/agents
```
List all active agents.

```json
{
  "agents": [
    {
      "id": "agent-001",
      "agent_type": "scripted",
      "status": "active",
      "created_at": "2026-02-12T10:30:00",
      "last_heartbeat": "2026-02-12T10:35:00",
      "metadata": {}
    }
  ]
}
```

```http
GET /api/agents/{agent_id}
```
Get details for a specific agent.

### Audit Log

```http
GET /api/audit?limit=50&agent_id=agent-001&tool=capture_frame
```
Retrieve audit events with optional filtering.

**Parameters:**
- `limit` (integer): Max events to return (default: 50)
- `agent_id` (string): Filter by agent ID
- `tool` (string): Filter by tool name

```json
{
  "events": [
    {
      "id": 1,
      "timestamp": "2026-02-12T10:30:00",
      "agent_id": "agent-001",
      "tool_name": "capture_frame",
      "status": "success",
      "details": {
        "frame_id": "frame-001",
        "width": 640,
        "height": 480
      }
    }
  ],
  "count": 1
}
```

### Approval Tokens

```http
POST /api/approve
```
Issue a new approval token.

```json
{
  "agent_id": "agent-001",
  "scope": "camera,microphone",
  "ttl_seconds": 300
}
```

Response:
```json
{
  "token": "abc123...",
  "expires_at": "2026-02-12T10:35:00",
  "scope": "camera,microphone"
}
```

```http
GET /api/tokens/{agent_id}
```
List all tokens for an agent.

```http
POST /api/tokens/{token_id}/revoke
```
Revoke a token (mark as inactive).

## Using Approval Tokens

Approval tokens allow temporary access to sensitive tools:

1. **Issue Token** - Admin issues token via dashboard
2. **Pass Token** - Agent includes token in tool call
3. **Verify & Execute** - Engine validates token before executing tool

```python
# Example: Agent calling camera with approval token
call = {
    "agent_id": "agent-001",
    "call_id": "call-001",
    "tool": "capture_frame",
    "args": {},
    "approval_token": "abc123:agent-001:camera:1707727200"
}
```

## Security

### Development Mode

- **Basic Auth**: Simple username/password validation
- **Default Credentials**: admin/admin
- **Tokens**: HMAC-SHA256 signed with configurable secret key

### Production Recommendations

1. **Use HTTPS** - Encrypt traffic in transit
2. **Strong Passwords** - Use complex, unique credentials
3. **Change Default Secret** - Set `OPERATOR_SECRET_KEY` environment variable
4. **Implement OAuth 2.0** - For enterprise deployments
5. **API Rate Limiting** - Prevent token brute-force attacks
6. **Audit Logging** - Monitor admin actions
7. **Token Rotation** - Short TTL for sensitive operations

## Configuration

### Environment Variables

```bash
# Database path
export OPERATOR_UI_DB="operator_ui.db"

# Authentication
export OPERATOR_USER="admin"
export OPERATOR_PASSWORD="admin"
export OPERATOR_SECRET_KEY="change-me-in-production"

# Server
export FLASK_HOST="127.0.0.1"
export FLASK_PORT="5000"
export FLASK_ENV="production"
```

### Flask Configuration

See [operator_ui/app.py](app.py) for full configuration options.

## Frontend Dashboard

The dashboard provides real-time monitoring with three main tabs:

### Dashboard Tab
- Selected agent details (ID, type, status, heartbeat)
- System health indicators
- Recent events from selected agent

### Audit Log Tab
- Searchable log of all tool calls
- Filters by tool name, timestamp, status
- JSON details for each event

### Approval Console Tab
- Form to issue new tokens
- Scope selection (camera, microphone, filesystem, network)
- Active token list with revoke buttons
- Token expiration tracking

## Integration with ANSE Engine

The Operator UI integrates with the main ANSE engine via:

1. **operator_ui_bridge.py** - Syncs audit events to database
2. **AgentBridge** - Registers active agents
3. **Audit Logger** - Records all tool calls

```python
from anse.operator_ui_bridge import get_operator_ui_bridge

bridge = get_operator_ui_bridge()
bridge.register_agent("agent-001", "scripted")
bridge.sync_audit_events("audit.jsonl")
```

## Testing

Run comprehensive test suite:

```bash
# All tests
pytest tests/ -v

# Just operator-ui tests
pytest tests/test_operator_ui.py -v

# Specific test
pytest tests/test_operator_ui.py::test_issue_approval_success -v
```

**Test Coverage:**
- ✅ Authentication and authorization
- ✅ Agent management (list, get, register)
- ✅ Audit log retrieval and filtering
- ✅ Token generation and verification
- ✅ Token revocation and expiration
- ✅ Database models and serialization
- ✅ Error handling and validation

**Test Count:** 21 tests, 100% passing

## Development

### Adding New Routes

1. Create route handler in `app.py`
2. Add authentication decorator (`@require_auth`)
3. Return JSON responses
4. Add tests in `tests/test_operator_ui.py`

Example:
```python
@app.route("/api/custom", methods=["GET"])
@require_auth
def custom_endpoint():
    return jsonify({"result": "ok"}), 200
```

### Frontend Development

The frontend is pure HTML/CSS/JavaScript with no build step:

1. **index.html** - Page structure and forms
2. **styles.css** - Dark theme styling
3. **dashboard.js** - API calls and UI updates

No framework dependencies - just vanilla JavaScript. Easy to modify and extend.

## Troubleshooting

### "Cannot connect to ANSE engine"
- Ensure ANSE engine is running on 127.0.0.1:8765
- Check firewall settings if accessing remotely

### "Invalid credentials"
- Check username and password are correct
- Default: admin/admin
- Check environment variables

### "Agent not found when issuing token"
- Agent must be registered first
- Agent registers automatically on first connection
- Check agent is still connected

### Tokens not working
- Check token hasn't expired
- Verify correct secret key used for verification
- Check token format: `{id}:{agent_id}:{scope}:{expires_ts}`

## Performance

- **Agent List**: Fetched every 2 seconds
- **System Health**: Polled every 2 seconds
- **Audit Events**: Loaded on demand
- **Database**: SQLite in-memory for testing, file-based for production

## Roadmap

- [ ] WebSocket support for real-time updates
- [ ] OAuth 2.0 authentication
- [ ] Advanced filtering and search
- [ ] Token templates and policies
- [ ] Metrics and analytics dashboards
- [ ] Email notifications for token issuance
- [ ] Audit log export (PDF, CSV)
- [ ] Multi-user accounts and permissions

## License

MIT - See LICENSE file for details
