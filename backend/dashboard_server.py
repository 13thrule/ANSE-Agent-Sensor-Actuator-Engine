#!/usr/bin/env python3
"""
ANSE Dashboard WebSocket Server

Runs ANSE engine with all plugins and exposes a WebSocket JSON-RPC interface
for the web dashboard to connect to.

Usage:
    python dashboard_server.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

from plugins.dashboard_bridge.plugin import DashboardBridgePlugin
from plugins.motor_control.plugin import MotorControlPlugin
from plugins.reflex_system.plugin import ReflexSystemPlugin
from plugins.long_term_memory.plugin import LongTermMemoryPlugin
from plugins.body_schema.plugin import BodySchemaPlugin
from plugins.reward_system.plugin import RewardSystemPlugin

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ANSEDashboardServer:
    """Simple ANSE engine with WebSocket JSON-RPC server for dashboard."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        """Initialize server."""
        self.host = host
        self.port = port
        self.plugins = {}
        self.clients = set()
        self.next_request_id = 1
        
        logger.info(f"Initializing ANSE Dashboard Server on {host}:{port}")
        
        # Initialize plugins
        self._init_plugins()

    def _init_plugins(self):
        """Initialize all plugins."""
        logger.info("Loading plugins...")
        
        # Core plugins
        self.plugins["motor_control"] = MotorControlPlugin()
        self.plugins["reflex_system"] = ReflexSystemPlugin()
        self.plugins["long_term_memory"] = LongTermMemoryPlugin()
        self.plugins["body_schema"] = BodySchemaPlugin()
        self.plugins["reward_system"] = RewardSystemPlugin()
        
        # Dashboard bridge (last, so it has access to all plugins)
        dashboard = DashboardBridgePlugin()
        dashboard.set_plugins_reference(self.plugins)
        dashboard.set_engine_reference(self)
        self.plugins["dashboard_bridge"] = dashboard
        
        logger.info(f"Loaded {len(self.plugins)} plugins: {', '.join(self.plugins.keys())}")

    async def handle_client(self, websocket):
        """Handle incoming WebSocket connection."""
        logger.info(f"Client connected")
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                request = None
                try:
                    request = json.loads(message)
                    response = await self._handle_request(request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    }))
                except Exception as e:
                    logger.error(f"Error handling request: {e}", exc_info=True)
                    req_id = request.get("id") if request else None
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": str(e)},
                        "id": req_id
                    }))
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
            logger.info(f"Client disconnected")

    async def _handle_request(self, request: Dict) -> Dict:
        """Handle JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")
        
        # Parse method as plugin.tool
        parts = method.split(".")
        if len(parts) != 2:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": req_id
            }
        
        plugin_name, tool_name = parts
        
        if plugin_name not in self.plugins:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Plugin {plugin_name} not found"},
                "id": req_id
            }
        
        plugin = self.plugins[plugin_name]
        
        if not hasattr(plugin, tool_name):
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method {method} not found"},
                "id": req_id
            }
        
        try:
            tool = getattr(plugin, tool_name)
            
            # Call with params
            if asyncio.iscoroutinefunction(tool):
                result = await tool(**params)
            else:
                result = tool(**params)
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            }
        except TypeError as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": f"Invalid parameters: {str(e)}"},
                "id": req_id
            }
        except Exception as e:
            logger.error(f"Error calling {method}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": req_id
            }

    async def broadcast_world_model_events(self):
        """Broadcast world model events to all connected clients every 3 seconds."""
        while True:
            try:
                await asyncio.sleep(3)
                
                # Get current world model events
                events = await self.plugins["dashboard_bridge"].get_world_model_events(limit=10)
                
                # Broadcast to all connected clients
                if self.clients and events:
                    message = json.dumps({
                        "type": "world_model_update",
                        "events": events
                    })
                    
                    # Send to all connected clients
                    disconnected = set()
                    for client in self.clients:
                        try:
                            await client.send(message)
                        except Exception as e:
                            logger.warning(f"Failed to send to client: {e}")
                            disconnected.add(client)
                    
                    # Clean up disconnected clients
                    self.clients -= disconnected
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(1)

    async def start(self):
        """Start WebSocket server."""
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        
        import websockets
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"✅ Dashboard server running at ws://{self.host}:{self.port}")
            logger.info(f"📊 Open dashboard.html in your browser")
            
            # Start background event broadcast
            broadcast_task = asyncio.create_task(self.broadcast_world_model_events())
            
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                logger.info("Shutting down...")
            finally:
                broadcast_task.cancel()


async def main():
    """Main entry point."""
    try:
        import websockets
    except ImportError:
        logger.error("websockets library not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
        import websockets
    
    server = ANSEDashboardServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
