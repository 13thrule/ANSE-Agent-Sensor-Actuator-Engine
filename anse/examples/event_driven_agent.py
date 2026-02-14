"""
Event-Driven Agent - The recommended pattern for ANSE agents.

This example demonstrates:
- Connecting via WebSocket
- Listening to world model events (not polling)
- Reacting to sensor readings
- Using tools when needed (on-demand, not continuously)
- Writing to long-term memory
- Respecting the nervous system model

This is the pattern all autonomous agents should follow.
No polling loops. No sleep(). No while True.
Just event -> react -> act.
"""
import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventDrivenAgent:
    """
    Agent that subscribes to world model events and reacts to them.
    
    This is how embodied agents should work:
    - Listen for sensor events from the world model
    - React immediately with reflexes or actions
    - Make strategic decisions based on observed events
    - Record decisions to long-term memory
    
    No polling. No continuous checking. All event-driven.
    """

    def __init__(
        self,
        uri: str = "ws://127.0.0.1:8765",
        agent_id: str = "event-driven-agent",
    ):
        """Initialize the agent."""
        self.uri = uri
        self.agent_id = agent_id
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.call_counter = 0

    async def connect(self) -> None:
        """Connect to ANSE engine."""
        logger.info(f"Connecting to ANSE at {self.uri}")
        self.websocket = await websockets.connect(self.uri)
        logger.info("✓ Connected to ANSE engine")

    async def disconnect(self) -> None:
        """Disconnect from ANSE engine."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from ANSE")

    async def call_tool(self, tool_name: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a tool via ANSE.
        
        Args:
            tool_name: Name of the tool to call
            args: Tool arguments (optional)
            
        Returns:
            Tool result dictionary
        """
        if args is None:
            args = {}
        
        self.call_counter += 1
        call_id = f"call-{self.call_counter}"
        
        request = {
            "method": "call_tool",
            "params": {
                "agent_id": self.agent_id,
                "call_id": call_id,
                "tool": tool_name,
                "args": args
            }
        }
        
        # Send request
        await self.websocket.send(json.dumps(request))
        
        # Wait for response
        response = json.loads(await self.websocket.recv())
        
        if response.get("status") == "ok":
            logger.debug(f"✓ {tool_name} completed")
            return response.get("result", {})
        else:
            logger.error(f"✗ {tool_name} failed: {response.get('error')}")
            return {"error": response.get("error")}

    async def remember(self, memory_type: str, content: str) -> None:
        """
        Write something to long-term memory.
        
        Args:
            memory_type: Category (e.g., "observation", "decision", "error")
            content: The memory content
        """
        result = await self.call_tool(
            "long_term_memory_remember",
            {
                "memory_type": memory_type,
                "content": content
            }
        )
        
        if not result.get("error"):
            logger.info(f"📝 Remembered: {memory_type}")

    async def listen_and_react(self) -> None:
        """
        Listen for world model events and react to them.
        
        This is the main agent loop. It's reactive, not polling:
        - Wait for world model event
        - Process the event
        - Take action if needed
        - Repeat forever
        
        This is fundamentally different from:
        
            while True:
                data = wait_for_input()
                process()
                sleep(1)
        
        Instead, we use WebSocket as a nerve signal pathway.
        """
        logger.info("🧠 Starting event-driven agent loop")
        logger.info("Listening for world model events...")
        
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    
                    # Skip responses to our own tool calls
                    if event.get("id"):
                        continue
                    
                    # Handle server-pushed events
                    if event.get("type") == "world_model_update":
                        await self._handle_world_model_event(event)
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse event")
                    
        except asyncio.CancelledError:
            logger.info("Agent stopping...")
        except Exception as e:
            logger.error(f"Agent error: {e}")

    async def _handle_world_model_event(self, event: Dict[str, Any]) -> None:
        """
        React to a world model event.
        
        The world model tells us what happened in the environment:
        - Sensor readings: "camera detected motion"
        - Reflex triggers: "temperature exceeded threshold"
        - Other agent actions: "robot arm moved"
        - Our own actions: "we called capture_frame"
        
        We react by:
        1. Evaluating the event relevance
        2. Deciding what to do
        3. Taking action (call tools, remember, etc.)
        """
        events = event.get("events", [])
        
        for evt in events:
            evt_type = evt.get("type", "unknown")
            evt_data = evt.get("data", {})
            
            logger.info(f"📡 Event: {evt_type}")
            
            # Example reactions to different event types
            if evt_type == "sensor_reading":
                await self._on_sensor_reading(evt_data)
            
            elif evt_type == "reflex_triggered":
                await self._on_reflex(evt_data)
            
            elif evt_type == "tool_call":
                await self._on_tool_call(evt_data)
            
            else:
                logger.debug(f"Unhandled event type: {evt_type}")

    async def _on_sensor_reading(self, data: Dict[str, Any]) -> None:
        """React to sensor data from the world model."""
        sensor_name = data.get("sensor")
        value = data.get("value")
        
        logger.info(f"   Sensor: {sensor_name} = {value}")
        
        # Example: If camera detected motion, capture frame for analysis
        if sensor_name == "camera" and value > 0.5:
            logger.info("   → Motion detected! Capturing frame...")
            frame_result = await self.call_tool("capture_frame")
            
            if not frame_result.get("error"):
                # Analyze the frame
                analysis = await self.call_tool(
                    "analyze_frame",
                    {"frame_id": frame_result.get("frame_id")}
                )
                
                # Remember what we saw
                edges = analysis.get("edges", 0)
                corners = analysis.get("corners", 0)
                await self.remember(
                    "observation",
                    f"Detected {edges} edges and {corners} corners in motion"
                )

    async def _on_reflex(self, data: Dict[str, Any]) -> None:
        """React to a reflex being triggered."""
        reflex_id = data.get("reflex_id")
        sensor = data.get("sensor")
        value = data.get("value")
        
        logger.info(f"   Reflex: {reflex_id} triggered by {sensor}={value}")
        
        # Remember the reflex event
        await self.remember(
            "reflex_event",
            f"Reflex {reflex_id} triggered when {sensor} reached {value}"
        )

    async def _on_tool_call(self, data: Dict[str, Any]) -> None:
        """React to a tool call (could be by us or another agent)."""
        agent_id = data.get("agent_id")
        tool = data.get("tool")
        
        logger.info(f"   Tool call: {agent_id} called {tool}")
        
        # If another agent did something, we might react
        if agent_id != self.agent_id:
            logger.info(f"   → Another agent acted! Recording observation...")
            await self.remember(
                "observation",
                f"Agent {agent_id} called {tool}"
            )

    async def run(self) -> None:
        """Main entry point."""
        try:
            await self.connect()
            
            # Start listening to events
            await self.listen_and_react()
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await self.disconnect()


async def main():
    """Run the event-driven agent."""
    agent = EventDrivenAgent(agent_id="embodied-explorer")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
