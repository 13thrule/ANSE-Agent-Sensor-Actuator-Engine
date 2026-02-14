# Dashboard UI

Real-time monitoring interface for ANSE agents and the world model.

## Status

**In Progress**: Transitioning from polling → event-driven architecture

The dashboard is being rewritten to use WebSocket events instead of polling.

### Current Files

- `dashboard.html` - Main web interface
- `dashboard_client.ts` - TypeScript WebSocket client (being refactored)
- `DashboardExample.svelte` - Example Svelte component

### Coming Next

- Full event-driven event listener (no polling)
- Component for sensor readings
- Plugin status monitor
- World model subscription view
- Tool execution dashboard

### Architecture

See [EVENT_DRIVEN_ARCHITECTURE.md](../docs/EVENT_DRIVEN_ARCHITECTURE.md) for the nervous system model that powers real-time updates.

### Related

- [dashboard_server.py](../dashboard_server.py) - WebSocket server (broadcasts world model every 3 seconds)
- [operator_ui/](../operator_ui/) - Flask-based admin interface
