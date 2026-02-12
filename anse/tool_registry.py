"""
ToolRegistry - Central registry of available tools/capabilities.
"""
from typing import Dict, Any, Callable, Optional, Awaitable
import inspect


class ToolRegistry:
    """
    Manages registration and execution of tools available to agents.
    Each tool has a schema, sensitivity level, and cost hint.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Awaitable[Dict[str, Any]]],
        schema: Dict[str, Any],
        description: str = "",
        sensitivity: str = "low",
        cost_hint: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a tool for agent use.

        Args:
            name: Unique tool identifier
            func: Async function implementing the tool
            schema: JSON Schema describing tool parameters
            description: Human-readable description
            sensitivity: Security level - "low", "medium", "high"
            cost_hint: Dict with latency_ms, expensive, etc.
        """
        if not inspect.iscoroutinefunction(func):
            raise ValueError(f"Tool function '{name}' must be async")

        self._tools[name] = {
            "func": func,
            "schema": schema,
            "description": description,
            "sensitivity": sensitivity,
            "cost_hint": cost_hint or {},
        }

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Return metadata for all registered tools.

        Returns:
            Dict mapping tool names to their metadata (excluding the func itself)
        """
        return {
            name: {
                "description": tool["description"],
                "schema": tool["schema"],
                "sensitivity": tool["sensitivity"],
                "cost_hint": tool["cost_hint"],
            }
            for name, tool in self._tools.items()
        }

    async def call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool.

        Args:
            name: Tool name
            args: Tool arguments matching the schema

        Returns:
            Tool execution result

        Raises:
            KeyError: If tool not found
            Exception: Any error from tool execution
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")

        tool = self._tools[name]
        return await tool["func"](**args)

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific tool."""
        if name not in self._tools:
            return None
        tool = self._tools[name]
        return {
            "description": tool["description"],
            "schema": tool["schema"],
            "sensitivity": tool["sensitivity"],
            "cost_hint": tool["cost_hint"],
        }
