"""
LLM Agent Adapter - Template for connecting an LLM to ANSE tools.

This demonstrates how to present tools to an LLM via function calling
and execute the LLM's chosen actions through the ANSE bridge.

Supports both demo mode and real LLM integration (OpenAI, Anthropic, etc.)
"""
import asyncio
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
import websockets
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAgentAdapter:
    """
    Adapter that connects an LLM to ANSE via function calling.
    
    Features:
    - Tool schema conversion for LLM function calling
    - Call execution and result collection
    - Context window management (recent events + tool results)
    - Audit logging with hashes
    - Support for multiple LLM backends
    """

    def __init__(
        self,
        uri: str = "ws://127.0.0.1:8765",
        agent_id: str = "llm-agent",
        context_window: int = 5,
    ):
        """
        Initialize the LLM adapter.
        
        Args:
            uri: WebSocket URI of the ANSE engine
            agent_id: Unique identifier for this agent
            context_window: Number of recent events to keep in context
        """
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.tools_metadata: Dict[str, Any] = {}
        self.agent_id = agent_id
        self.call_counter = 0
        self.context_window = context_window
        self.event_history: List[Dict[str, Any]] = []  # (agent_id, call_id, tool, timestamp, result_hash)

    async def connect(self) -> None:
        """Connect to the ANSE engine."""
        logger.info(f"Connecting to ANSE at {self.uri}")
        self.websocket = await websockets.connect(self.uri)
        
        # Fetch available tools
        await self._fetch_tools()

    async def disconnect(self) -> None:
        """Disconnect from the ANSE engine."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from ANSE")

    async def _fetch_tools(self) -> None:
        """Fetch tool metadata from ANSE."""
        await self.websocket.send(json.dumps({"method": "list_tools"}))
        response = json.loads(await self.websocket.recv())
        self.tools_metadata = response.get("result", {})
        logger.info(f"Loaded {len(self.tools_metadata)} tools")

    def get_tool_schemas_for_llm(self) -> List[Dict[str, Any]]:
        """
        Convert ANSE tool metadata to LLM function calling format.
        
        Returns:
            List of tool schemas in LLM-compatible format
        """
        llm_tools = []
        
        for tool_name, metadata in self.tools_metadata.items():
            llm_tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": metadata.get("description", ""),
                    "parameters": metadata.get("schema", {}),
                }
            })
        
        return llm_tools

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool via ANSE.
        
        Args:
            tool_name: Name of the tool to call
            args: Tool arguments
            
        Returns:
            Tool execution result
        """
        self.call_counter += 1
        call_id = f"{self.agent_id}-call-{self.call_counter:04d}"
        
        # Hash args for audit trail
        args_hash = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()[:8]
        
        call = {
            "agent_id": self.agent_id,
            "call_id": call_id,
            "tool": tool_name,
            "args": args
        }
        
        logger.info(f"[{call_id}] Calling tool: {tool_name} (args_hash: {args_hash})")
        
        await self.websocket.send(json.dumps({"method": "call_tool", "params": call}))
        response = json.loads(await self.websocket.recv())
        
        # Hash result for audit trail
        result = response.get("result", {})
        result_hash = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:8]
        
        # Log to event history
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "call_id": call_id,
            "tool": tool_name,
            "args_hash": args_hash,
            "result_hash": result_hash,
            "status": response.get("status", "unknown"),
        }
        self.event_history.append(event)
        
        # Keep context window limited
        if len(self.event_history) > self.context_window:
            self.event_history.pop(0)
        
        if response.get("status") == "ok":
            logger.info(f"✓ [{call_id}] {tool_name} succeeded (result_hash: {result_hash})")
            return result
        else:
            logger.error(f"✗ [{call_id}] {tool_name} failed: {response.get('error')}")
            return {"error": response.get("error")}

    def get_context_for_llm(self) -> str:
        """
        Get formatted context for the LLM including recent events.
        
        Returns:
            Formatted context string with event history
        """
        context = "Recent agent actions:\n"
        for event in self.event_history[-self.context_window:]:
            context += f"  - [{event['call_id']}] {event['tool']}: {event['status']} @ {event['timestamp']}\n"
        return context

    async def run_demo_loop(self, max_iterations: int = 10) -> None:
        """
        Run a simple demo agent loop.
        
        Args:
            max_iterations: Maximum number of loop iterations
        """
        logger.info("Starting LLM agent demo loop")
        
        # Simulate LLM choosing tools
        demo_sequence = [
            ("list_cameras", {}),
            ("capture_frame", {"camera_id": 0}),
            ("say", {"text": "I have captured an image and can see my environment"}),
        ]
        
        for tool_name, args in demo_sequence:
            logger.info(f"\n--- LLM chooses to call: {tool_name} ---")
            result = await self.call_tool(tool_name, args)
            logger.info(f"Result: {result}")
            
            # Show context
            logger.info("Current context:\n" + self.get_context_for_llm())
            await asyncio.sleep(0.5)
        
        logger.info("\n✓ Demo loop completed")

    async def run_with_openai(self, task: str, max_iterations: int = 10) -> None:
        """
        Run agent loop with real OpenAI LLM integration.
        
        Requires: pip install openai
        
        Args:
            task: The task description for the LLM
            max_iterations: Maximum loop iterations
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            return
        
        client = AsyncOpenAI()
        
        # Get tool schemas
        tools = self.get_tool_schemas_for_llm()
        
        # Initialize conversation
        messages = [
            {
                "role": "user",
                "content": task,
            }
        ]
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n=== Iteration {iteration} ===")
            logger.info(f"Context: {self.get_context_for_llm()}")
            
            # Call LLM with tools
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Check if LLM wants to call tools
            if response.stop_reason == "tool_calls":
                for tool_call in response.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM calls: {tool_name}({tool_args})")
                    
                    # Execute tool
                    result = await self.call_tool(tool_name, tool_args)
                    
                    # Add to messages for next LLM call
                    messages.append({"role": "assistant", "content": response.content or ""})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(result),
                    })
            else:
                # LLM is done
                logger.info(f"✓ LLM completed: {response.choices[0].message.content}")
                break
        
        logger.info(f"\n=== Completed in {iteration} iterations ===")


async def main_demo():
    """Run demo mode."""
    adapter = LLMAgentAdapter()
    
    try:
        await adapter.connect()
        await adapter.run_demo_loop()
    except (ConnectionRefusedError, OSError) as e:
        logger.error("Could not connect to ANSE engine. Is it running?")
        logger.error("Start the engine with: python -m anse.engine_core")
        logger.error(f"Details: {e}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await adapter.disconnect()


def main():
    """CLI entry point."""
    import sys
    
    logger.info("LLM Agent Adapter")
    logger.info("=" * 60)
    
    if "--openai" in sys.argv:
        logger.info("Running with OpenAI LLM integration")
        task = input("Enter task for LLM: ")
        asyncio.run(main_with_openai(task))
    else:
        logger.info("Running in demo mode")
        logger.info("To use with OpenAI, run: python llm_agent_adapter.py --openai")
        asyncio.run(main_demo())


async def main_with_openai(task: str):
    """Main function for OpenAI mode."""
    adapter = LLMAgentAdapter()
    
    try:
        await adapter.connect()
        await adapter.run_with_openai(task)
    except (ConnectionRefusedError, OSError) as e:
        logger.error("Could not connect to ANSE engine. Is it running?")
        logger.error("Start the engine with: python -m anse.engine_core")
        logger.error(f"Details: {e}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await adapter.disconnect()


if __name__ == "__main__":
    main()
