"""
Production-ready LLM agent adapter.

Demonstrates how to connect OpenAI, Claude, and other LLMs
to ANSE for autonomous tool-calling agents.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Any
import websockets

logger = logging.getLogger(__name__)


class ProductionLLMAgent:
    """
    Autonomous LLM agent with tool calling.
    
    Connects to ANSE engine and uses function-calling to solve tasks.
    Supports OpenAI, Claude, and other function-calling models.
    """
    
    def __init__(
        self,
        agent_id: str,
        anse_uri: str = "ws://127.0.0.1:8765",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM agent.
        
        Args:
            agent_id: Unique agent identifier
            anse_uri: WebSocket URI of ANSE engine
            model: LLM model name (gpt-4, claude-3-sonnet, etc.)
            api_key: API key for LLM provider
        """
        self.agent_id = agent_id
        self.anse_uri = anse_uri
        self.model = model
        self.api_key = api_key
        self.websocket = None
        self.tools_schema = {}
        self.context_window = 4000
    
    async def connect(self) -> None:
        """Connect to ANSE engine."""
        logger.info(f"Connecting {self.agent_id} to ANSE at {self.anse_uri}")
        self.websocket = await websockets.connect(self.anse_uri)
        
        # Load available tools
        await self._load_tools()
    
    async def disconnect(self) -> None:
        """Disconnect from ANSE engine."""
        if self.websocket:
            await self.websocket.close()
    
    async def _load_tools(self) -> None:
        """Load tool schemas from ANSE."""
        await self.websocket.send(json.dumps({"method": "list_tools"}))
        response = json.loads(await self.websocket.recv())
        self.tools_schema = response.get("result", {})
        logger.info(f"Loaded {len(self.tools_schema)} tools")
    
    async def run(self, task: str, max_steps: int = 10) -> str:
        """
        Run autonomous task with function-calling loop.
        
        Args:
            task: Task description
            max_steps: Maximum planning steps
            
        Returns:
            Task completion message
        """
        logger.info(f"{self.agent_id}: Starting task: {task}")
        
        messages = [
            {
                "role": "user",
                "content": f"You are an autonomous agent with access to tools. Complete this task: {task}"
            }
        ]
        
        for step in range(max_steps):
            logger.info(f"  Step {step + 1}/{max_steps}")
            
            # Get LLM response
            tool_calls = await self._get_llm_response(messages)
            
            if not tool_calls:
                # LLM finished without calling tools
                logger.info(f"{self.agent_id}: Task completed")
                return f"✓ Completed: {task}"
            
            # Execute tools
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                logger.info(f"    Calling {tool_name}({json.dumps(tool_args, indent=2)[:50]}...)")
                
                # Call tool via ANSE
                result = await self._call_tool(tool_name, tool_args)
                
                # Add result to message history
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "thinking": f"Called {tool_name}",
                        "result": result
                    })
                })
        
        return f"✗ Max steps ({max_steps}) reached"
    
    async def _get_llm_response(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get response from LLM with function-calling.
        
        This is a placeholder - real implementation would call OpenAI, Claude, etc.
        
        Args:
            messages: Message history
            
        Returns:
            List of tool calls from LLM
        """
        # Placeholder: In production, call your LLM API here
        # For OpenAI: client.chat.completions.create(model=self.model, messages=messages, tools=...)
        # For Claude: client.messages.create(model=self.model, messages=messages, tools=...)
        
        logger.debug("Getting LLM response (placeholder - implement with real LLM API)")
        return []
    
    async def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool via ANSE engine.
        
        Args:
            tool_name: Tool name
            args: Tool arguments
            
        Returns:
            Tool result
        """
        call = {
            "agent_id": self.agent_id,
            "call_id": f"call-{id(asyncio.current_task())}",
            "tool": tool_name,
            "args": args
        }
        
        await self.websocket.send(json.dumps({"method": "call_tool", "params": call}))
        response = json.loads(await self.websocket.recv())
        
        if response.get("status") == "ok":
            return response.get("result", {})
        else:
            error = response.get("error", "unknown_error")
            logger.error(f"Tool call failed: {error}")
            return {"error": error}


async def main():
    """Example usage."""
    agent = ProductionLLMAgent(
        agent_id="llm-agent-001",
        model="gpt-4",
        api_key="sk-..."  # Set your API key
    )
    
    try:
        await agent.connect()
        
        # Example task
        result = await agent.run(
            "Take a photo of the room and describe what you see"
        )
        
        logger.info(result)
        
    finally:
        await agent.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
