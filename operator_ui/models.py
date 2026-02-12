"""Database models for operator UI: agents, sessions, and approval tokens."""

import os
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Agent(db.Model):
    """Active agent session."""

    __tablename__ = "agents"

    id = db.Column(db.String(64), primary_key=True)
    agent_type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_heartbeat = db.Column(db.DateTime, default=datetime.utcnow)
    agent_metadata = db.Column(db.JSON, default={})

    tokens = db.relationship("ApprovalToken", back_populates="agent", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON."""
        return {
            "id": self.id,
            "agent_type": self.agent_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "metadata": self.agent_metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create from JSON."""
        return cls(
            id=data.get("id"),
            agent_type=data.get("agent_type", "unknown"),
            status=data.get("status", "active"),
            agent_metadata=data.get("metadata", {}),
        )


class ApprovalToken(db.Model):
    """Signed approval token for sensitive tool access."""

    __tablename__ = "approval_tokens"

    id = db.Column(db.String(64), primary_key=True)
    agent_id = db.Column(db.String(64), db.ForeignKey("agents.id"), nullable=False)
    scope = db.Column(db.String(256), nullable=False)  # e.g., "camera,microphone"
    token_hash = db.Column(db.String(256), nullable=False)  # HMAC-SHA256
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)

    agent = db.relationship("Agent", back_populates="tokens")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON (without token hash)."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "scope": self.scope,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked": self.revoked,
            "is_valid": not self.revoked and self.expires_at > datetime.utcnow(),
        }

    @classmethod
    def generate(
        cls,
        agent_id: str,
        scope: str,
        ttl_seconds: int = 300,
        secret_key: Optional[str] = None,
    ) -> tuple["ApprovalToken", str]:
        """
        Generate a new approval token.

        Returns (token_object, token_string)
        """
        token_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        token_string = f"{token_id}:{agent_id}:{scope}:{int(expires_at.timestamp())}"
        token_hash = hmac.new(
            secret_key.encode() if secret_key else b"default-secret",
            token_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        token_obj = cls(
            id=token_id,
            agent_id=agent_id,
            scope=scope,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return token_obj, token_string

    @classmethod
    def verify(
        cls,
        token_string: str,
        secret_key: Optional[str] = None,
    ) -> tuple[Optional["ApprovalToken"], bool]:
        """
        Verify token validity.

        Returns (token_object, is_valid)
        """
        try:
            parts = token_string.split(":")
            if len(parts) != 4:
                return None, False

            token_id, agent_id, scope, expires_ts = parts
            expires_at = datetime.fromtimestamp(int(expires_ts))

            # Check expiration
            if expires_at <= datetime.utcnow():
                return None, False

            # Verify signature
            token_sig = hmac.new(
                secret_key.encode() if secret_key else b"default-secret",
                token_string.encode(),
                hashlib.sha256,
            ).hexdigest()

            # Look up token in database
            token_obj = cls.query.filter_by(id=token_id, agent_id=agent_id).first()
            if not token_obj or token_obj.revoked:
                return None, False

            # Verify signature matches
            if not hmac.compare_digest(token_sig, token_obj.token_hash):
                return None, False

            return token_obj, True
        except Exception:
            return None, False


class AuditEvent(db.Model):
    """Audit log entry (synchronized from ANSE engine)."""

    __tablename__ = "audit_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    agent_id = db.Column(db.String(64), db.ForeignKey("agents.id"), index=True)
    tool_name = db.Column(db.String(64), index=True)
    status = db.Column(db.String(32), index=True)  # success, error, pending
    severity = db.Column(db.String(32), default="normal")  # low, normal, high, critical
    input_args = db.Column(db.JSON, default={})  # JSON-serialized input arguments
    output = db.Column(db.JSON, default={})  # JSON-serialized output/result
    details = db.Column(db.JSON, default={})  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "severity": self.severity,
            "input_args": json.dumps(self.input_args) if isinstance(self.input_args, dict) else self.input_args,
            "output": json.dumps(self.output) if isinstance(self.output, dict) else self.output,
            "details": self.details or {},
        }

    @classmethod
    def from_audit_event(cls, event: Dict[str, Any]) -> "AuditEvent":
        """Create from ANSE audit event."""
        timestamp = event.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            timestamp=timestamp or datetime.utcnow(),
            agent_id=event.get("agent_id"),
            tool_name=event.get("tool"),
            status=event.get("status", "unknown"),
            severity=event.get("severity", "normal"),
            input_args=event.get("input_args", {}),
            output=event.get("output", {}),
            details=event,
        )



def init_db(app) -> None:
    """Initialize database."""
    with app.app_context():
        db.create_all()
