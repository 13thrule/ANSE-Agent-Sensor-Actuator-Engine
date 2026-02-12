"""
Audit logging module for ANSE.

Provides structured audit logging with:
- Agent ID tracking
- Call ID correlation
- Tool execution hashing (args_hash, result_hash)
- Timestamps
- Structured output (JSONL format)
"""
import json
import hashlib
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AuditLogger:
    """
    Structured audit logger for tool calls and agent actions.
    
    Logs:
    - agent_id: Which agent made the call
    - call_id: Unique call identifier
    - tool: Tool name
    - args_hash: SHA256 hash of tool arguments (first 8 chars)
    - result_hash: SHA256 hash of tool result (first 8 chars)
    - timestamp: UTC ISO timestamp
    - status: success | error | timeout
    - duration_ms: Execution time in milliseconds
    """

    def __init__(self, audit_file: Optional[str] = None, logger_name: str = "anse.audit"):
        """
        Initialize the audit logger.
        
        Args:
            audit_file: Path to JSONL audit file. If None, only logs to python logger.
            logger_name: Python logger name
        """
        self.audit_file = audit_file
        self.logger = logging.getLogger(logger_name)
        
        if self.audit_file:
            os.makedirs(os.path.dirname(os.path.abspath(self.audit_file)), exist_ok=True)
            self.logger.info(f"Audit logging to: {self.audit_file}")

    def log_tool_call(
        self,
        agent_id: str,
        call_id: str,
        tool: str,
        args: Dict[str, Any],
        result: Dict[str, Any],
        status: str = "success",
        duration_ms: float = 0.0,
    ) -> None:
        """
        Log a tool call with hashed arguments and results.
        
        Args:
            agent_id: Agent that made the call
            call_id: Unique call identifier
            tool: Tool name
            args: Tool arguments
            result: Tool result
            status: Execution status (success, error, timeout)
            duration_ms: Execution duration in milliseconds
        """
        args_hash = self._hash_dict(args)
        result_hash = self._hash_dict(result)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "call_id": call_id,
            "tool": tool,
            "args_hash": args_hash,
            "result_hash": result_hash,
            "status": status,
            "duration_ms": duration_ms,
        }
        
        # Write to file if configured
        if self.audit_file:
            self._write_audit_entry(log_entry)
        
        # Also log to python logger
        self.logger.info(
            f"[{agent_id}] {call_id}: {tool} -> {result_hash} ({status}) {duration_ms:.0f}ms"
        )

    def log_event(
        self,
        agent_id: str,
        call_id: str,
        event_type: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Log a general event (not necessarily a tool call).
        
        Args:
            agent_id: Agent ID
            call_id: Call ID
            event_type: Type of event (e.g., "agent_connect", "permission_denied")
            details: Event-specific details
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "call_id": call_id,
            "type": event_type,
            "details": details,
        }
        
        if self.audit_file:
            self._write_audit_entry(log_entry)
        
        self.logger.info(f"[{agent_id}] {call_id}: {event_type}")

    def log_permission_denied(
        self,
        agent_id: str,
        call_id: str,
        tool: str,
        reason: str,
    ) -> None:
        """
        Log a permission denial.
        
        Args:
            agent_id: Agent that was denied
            call_id: Call ID
            tool: Tool that was denied
            reason: Why it was denied (e.g., "rate_limit_exceeded")
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "call_id": call_id,
            "tool": tool,
            "event_type": "permission_denied",
            "reason": reason,
        }
        
        if self.audit_file:
            self._write_audit_entry(log_entry)
        
        self.logger.warning(f"[{agent_id}] DENIED {tool}: {reason}")

    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """Create a short SHA256 hash of a dictionary."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()[:8]

    def _write_audit_entry(self, entry: Dict[str, Any]) -> None:
        """Write an audit entry to the JSONL file."""
        if not self.audit_file:
            return
        
        try:
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except IOError as e:
            self.logger.error(f"Failed to write audit entry: {e}")

    def load_audit_log(self) -> list:
        """Load and parse all audit log entries."""
        if not self.audit_file or not os.path.exists(self.audit_file):
            return []
        
        entries = []
        try:
            with open(self.audit_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            return entries
        except IOError as e:
            self.logger.error(f"Failed to read audit log: {e}")
            return []

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent from audit log."""
        entries = self.load_audit_log()
        agent_entries = [e for e in entries if e.get("agent_id") == agent_id]
        
        total_calls = len([e for e in agent_entries if "tool" in e])
        successful = len([e for e in agent_entries if e.get("status") == "success"])
        failed = len([e for e in agent_entries if e.get("status") == "error"])
        denied = len([e for e in agent_entries if e.get("event_type") == "permission_denied"])
        
        total_time = sum(e.get("duration_ms", 0) for e in agent_entries if "duration_ms" in e)
        
        return {
            "agent_id": agent_id,
            "total_calls": total_calls,
            "successful": successful,
            "failed": failed,
            "denied": denied,
            "total_duration_ms": total_time,
            "avg_duration_ms": total_time / max(successful, 1),
        }
