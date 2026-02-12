"""Multiagent support with per-agent quotas and isolation."""

import asyncio
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class AgentQuota:
    """Per-agent resource quota."""
    
    agent_id: str
    cpu_budget_ms: float = 60000.0  # 60 seconds per minute
    storage_quota_mb: float = 500.0
    tool_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "capture_frame": 30,  # calls per minute
        "record_audio": 10,
        "say": 20,
    })
    
    # Runtime tracking
    cpu_used_ms: float = 0.0
    storage_used_mb: float = 0.0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    tool_calls: Dict[str, list] = field(default_factory=dict)  # tool_name -> [timestamps]
    
    def reset_if_needed(self, reset_interval_sec: int = 60) -> None:
        """Reset quotas if interval has passed."""
        now = datetime.utcnow()
        if (now - self.last_reset).total_seconds() > reset_interval_sec:
            self.cpu_used_ms = 0.0
            self.tool_calls.clear()
            self.last_reset = now
    
    def check_cpu_budget(self, additional_ms: float) -> bool:
        """Check if CPU budget allows additional usage."""
        self.reset_if_needed()
        return (self.cpu_used_ms + additional_ms) <= self.cpu_budget_ms
    
    def use_cpu(self, duration_ms: float) -> None:
        """Record CPU usage."""
        self.reset_if_needed()
        self.cpu_used_ms += duration_ms
    
    def check_tool_rate_limit(self, tool_name: str) -> bool:
        """Check if tool rate limit allows another call."""
        self.reset_if_needed()
        
        limit = self.tool_rate_limits.get(tool_name)
        if limit is None:
            return True  # No limit if not in dict
        
        # Clean up old timestamps (older than 60 seconds)
        now = time.time()
        if tool_name not in self.tool_calls:
            self.tool_calls[tool_name] = []
        
        self.tool_calls[tool_name] = [
            ts for ts in self.tool_calls[tool_name]
            if (now - ts) < 60.0
        ]
        
        return len(self.tool_calls[tool_name]) < limit
    
    def record_tool_call(self, tool_name: str) -> None:
        """Record a tool call for rate limiting."""
        self.reset_if_needed()
        
        if tool_name not in self.tool_calls:
            self.tool_calls[tool_name] = []
        
        self.tool_calls[tool_name].append(time.time())
    
    def get_stats(self) -> dict:
        """Get quota usage statistics."""
        self.reset_if_needed()
        
        return {
            "agent_id": self.agent_id,
            "cpu_used_ms": self.cpu_used_ms,
            "cpu_budget_ms": self.cpu_budget_ms,
            "cpu_percent": (self.cpu_used_ms / self.cpu_budget_ms) * 100,
            "storage_used_mb": self.storage_used_mb,
            "storage_quota_mb": self.storage_quota_mb,
            "storage_percent": (self.storage_used_mb / self.storage_quota_mb) * 100 if self.storage_quota_mb > 0 else 0,
            "tool_calls": {
                tool: len([ts for ts in self.tool_calls.get(tool, []) 
                          if (time.time() - ts) < 60.0])
                for tool in self.tool_rate_limits
            },
            "tool_limits": self.tool_rate_limits,
            "last_reset": self.last_reset.isoformat(),
        }


class MultiagentEngine:
    """Engine supporting multiple concurrent agents with isolation."""
    
    def __init__(self):
        """Initialize multiagent engine."""
        self.quotas: Dict[str, AgentQuota] = {}
        self.agents_online: set = set()
        self.lock = asyncio.Lock()
    
    def register_agent(self, agent_id: str, quota: Optional[AgentQuota] = None) -> AgentQuota:
        """
        Register an agent with optional custom quota.
        
        Args:
            agent_id: Unique agent identifier
            quota: Custom AgentQuota or None for defaults
            
        Returns:
            The AgentQuota for this agent
        """
        if agent_id not in self.quotas:
            self.quotas[agent_id] = quota or AgentQuota(agent_id=agent_id)
        
        self.agents_online.add(agent_id)
        return self.quotas[agent_id]
    
    def deregister_agent(self, agent_id: str) -> None:
        """Remove agent and clean up quotas."""
        self.agents_online.discard(agent_id)
        # Keep quota data for auditing (don't delete)
    
    def get_quota(self, agent_id: str) -> Optional[AgentQuota]:
        """Get quota for agent."""
        return self.quotas.get(agent_id)
    
    async def check_tool_access(
        self,
        agent_id: str,
        tool_name: str,
        estimated_duration_ms: float = 0.0,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if agent can call tool.
        
        Returns:
            (allowed, reason_if_denied)
        """
        async with self.lock:
            quota = self.get_quota(agent_id)
            if not quota:
                return False, "agent_not_registered"
            
            # Check rate limit
            if not quota.check_tool_rate_limit(tool_name):
                limit = quota.tool_rate_limits.get(tool_name, 0)
                return False, f"rate_limit_exceeded_{limit}_per_min"
            
            # Check CPU budget
            if estimated_duration_ms > 0 and not quota.check_cpu_budget(estimated_duration_ms):
                return False, "cpu_budget_exceeded"
            
            return True, None
    
    async def record_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        duration_ms: float = 0.0,
        storage_mb: float = 0.0,
    ) -> None:
        """Record a tool call for quota tracking."""
        async with self.lock:
            quota = self.get_quota(agent_id)
            if quota:
                quota.record_tool_call(tool_name)
                if duration_ms > 0:
                    quota.use_cpu(duration_ms)
                if storage_mb > 0:
                    quota.storage_used_mb += storage_mb
    
    def get_agent_stats(self, agent_id: str) -> Optional[dict]:
        """Get statistics for an agent."""
        quota = self.get_quota(agent_id)
        if quota:
            return quota.get_stats()
        return None
    
    def get_all_stats(self) -> dict:
        """Get statistics for all agents."""
        return {
            agent_id: quota.get_stats()
            for agent_id, quota in self.quotas.items()
        }
    
    def get_online_agents(self) -> list:
        """Get list of online agent IDs."""
        return list(self.agents_online)


# Global multiagent engine instance
_multiagent_engine: Optional[MultiagentEngine] = None


def get_multiagent_engine() -> MultiagentEngine:
    """Get or create global multiagent engine."""
    global _multiagent_engine
    if _multiagent_engine is None:
        _multiagent_engine = MultiagentEngine()
    return _multiagent_engine


def initialize_multiagent_engine() -> MultiagentEngine:
    """Initialize global multiagent engine."""
    return get_multiagent_engine()
