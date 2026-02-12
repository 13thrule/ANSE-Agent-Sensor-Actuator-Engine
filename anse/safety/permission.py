"""
Permission system for enforcing safety policies.
"""
import yaml
from pathlib import Path
from typing import Set, Dict, Any, Optional


class PermissionManager:
    """
    Enforces safety policies including scopes, approval requirements,
    and rate limits.
    """

    def __init__(self, policy_path: Optional[str] = None):
        if policy_path is None:
            policy_path = Path(__file__).parent / "safety_policy.yaml"
        
        with open(policy_path, 'r') as f:
            self.policy = yaml.safe_load(f)
        
        self._agent_scopes: Dict[str, Set[str]] = {}

    def register_agent(self, agent_id: str, scopes: Optional[Set[str]] = None) -> None:
        """
        Register an agent with specific scopes.
        
        Args:
            agent_id: Agent identifier
            scopes: Set of granted scopes, or None to use defaults
        """
        if scopes is None:
            scopes = set(self.policy.get("default_scopes", []))
        self._agent_scopes[agent_id] = scopes

    def check_permission(
        self, agent_id: str, tool_name: str, required_scope: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an agent has permission to use a tool.
        
        Args:
            agent_id: Agent identifier
            tool_name: Name of the tool
            required_scope: Scope required for this operation
            
        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        # If no agent scopes registered, use defaults
        if agent_id not in self._agent_scopes:
            self.register_agent(agent_id)
        
        agent_scopes = self._agent_scopes[agent_id]
        
        # If no specific scope required, allow
        if required_scope is None:
            return True, None
        
        # Check if scope is in sensitive list and not granted
        sensitive = set(self.policy.get("sensitive_scopes", []))
        if required_scope in sensitive and required_scope not in agent_scopes:
            return False, f"Missing required scope: {required_scope}"
        
        return True, None

    def requires_approval(self, tool_name: str, scope: Optional[str] = None) -> bool:
        """
        Check if a tool/scope requires human approval.
        
        Args:
            tool_name: Name of the tool
            scope: Optional scope being accessed
            
        Returns:
            True if approval is required
        """
        approval_list = self.policy.get("approval_required", [])
        
        if scope and scope in approval_list:
            return True
        
        if tool_name in approval_list:
            return True
        
        return False

    def get_rate_limit(self, tool_name: str) -> Optional[int]:
        """
        Get rate limit for a tool in calls per minute.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Rate limit or None if no limit configured
        """
        limits = self.policy.get("rate_limits", {})
        return limits.get(tool_name)

    def get_timeout(self, tool_name: str) -> float:
        """
        Get timeout for a tool execution.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Timeout in seconds
        """
        timeouts = self.policy.get("timeouts", {})
        return timeouts.get("default_call_timeout", 30.0)

    def grant_scope(self, agent_id: str, scope: str) -> None:
        """Grant an additional scope to an agent."""
        if agent_id not in self._agent_scopes:
            self.register_agent(agent_id)
        self._agent_scopes[agent_id].add(scope)

    def revoke_scope(self, agent_id: str, scope: str) -> None:
        """Revoke a scope from an agent."""
        if agent_id in self._agent_scopes:
            self._agent_scopes[agent_id].discard(scope)

    def get_agent_scopes(self, agent_id: str) -> Set[str]:
        """Get all scopes granted to an agent."""
        if agent_id not in self._agent_scopes:
            self.register_agent(agent_id)
        return self._agent_scopes[agent_id].copy()
