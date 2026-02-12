"""
AgentBridge - WebSocket server exposing tools to agents via JSON-RPC.
"""
import asyncio
import json
import logging
from typing import Optional
import websockets
from websockets.server import WebSocketServerProtocol

from anse.tool_registry import ToolRegistry
from anse.world_model import WorldModel
from anse.scheduler import Scheduler
from anse.safety.permission import PermissionManager

logger = logging.getLogger(__name__)


class AgentBridge:
    """
    WebSocket server that exposes tool registry to agents.
    Implements a simple JSON-RPC style protocol.
    """

    def __init__(
        self,
        tools: ToolRegistry,
        world: WorldModel,
        scheduler: Scheduler,
        permissions: Optional[PermissionManager] = None,
    ):
        self.tools = tools
        self.world = world
        self.scheduler = scheduler
        self.permissions = permissions or PermissionManager()

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """
        Handle a single WebSocket client connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        agent_id = f"agent-{id(websocket)}"
        logger.info(f"Agent {agent_id} connected from {websocket.remote_address}")

        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self._handle_request(agent_id, request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(
                        json.dumps({"error": "invalid_json", "message": "Could not parse JSON"})
                    )
                except Exception as e:
                    logger.error(f"Error handling request: {e}", exc_info=True)
                    await websocket.send(
                        json.dumps({"error": "internal_error", "message": str(e)})
                    )

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Agent {agent_id} disconnected")
        finally:
            logger.info(f"Agent {agent_id} connection closed")

    async def _handle_request(self, agent_id: str, request: dict) -> dict:
        """
        Process a single request from an agent.
        
        Args:
            agent_id: Identifier of the calling agent
            request: Request dictionary with 'method' and optional 'params'
            
        Returns:
            Response dictionary
        """
        method = request.get("method")

        if method == "list_tools":
            return {"result": self.tools.list_tools()}

        elif method == "call_tool":
            params = request.get("params", {})
            agent_id_override = params.get("agent_id", agent_id)
            call_id = params.get("call_id", "unknown")
            tool = params.get("tool")
            args = params.get("args", {})

            if not tool:
                return {"error": "missing_tool_name", "call_id": call_id}

            # Execute via scheduler (handles rate limiting, timeouts, logging)
            result = await self.scheduler.execute_call(
                agent_id=agent_id_override,
                call_id=call_id,
                tool=tool,
                args=args,
            )

            return result

        elif method == "get_history":
            params = request.get("params", {})
            n = params.get("n", 10)
            return {"result": self.world.get_events_for_agent(agent_id, n)}

        elif method == "get_tool_info":
            params = request.get("params", {})
            tool_name = params.get("tool")
            if not tool_name:
                return {"error": "missing_tool_name"}
            
            info = self.tools.get_tool_info(tool_name)
            if info is None:
                return {"error": "tool_not_found", "tool": tool_name}
            return {"result": info}

        elif method == "ping":
            return {"result": "pong"}

        else:
            return {"error": "unknown_method", "method": method}

    async def serve(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        """
        Start the WebSocket server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting AgentBridge on {host}:{port}")
        
        async with websockets.serve(self.handle_client, host, port):
            logger.info(f"AgentBridge listening on ws://{host}:{port}")
            await asyncio.Future()  # Run forever
