"""Integration between ANSE engine and operator-ui."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import operator-ui components
try:
    from operator_ui.app import create_app, db
    from operator_ui.models import AuditEvent, Agent
    OPERATOR_UI_AVAILABLE = True
except ImportError:
    OPERATOR_UI_AVAILABLE = False


class OperatorUIBridge:
    """Bridge between ANSE engine and operator-ui database."""

    def __init__(self, operator_ui_db_path: Optional[str] = None):
        """
        Initialize the bridge.

        Args:
            operator_ui_db_path: Path to operator-ui SQLite database.
                                If None, uses default location.
        """
        self.db_path = operator_ui_db_path or "operator_ui.db"
        self.app = None
        self.last_synced_event_id = 0

    def initialize(self) -> bool:
        """Initialize Flask app and database."""
        if not OPERATOR_UI_AVAILABLE:
            return False

        config = {
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        }

        self.app = create_app(config)
        return True

    def sync_audit_events(self, audit_file: str, limit: int = 100) -> int:
        """
        Sync ANSE audit log events to operator-ui database.

        Args:
            audit_file: Path to ANSE audit JSONL file
            limit: Maximum events to sync in one call

        Returns:
            Number of events synced
        """
        if not self.app or not OPERATOR_UI_AVAILABLE:
            return 0

        if not os.path.exists(audit_file):
            return 0

        count = 0
        with self.app.app_context():
            try:
                with open(audit_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            event_data = json.loads(line)
                            
                            # Skip already-synced events (could use line number for efficiency)
                            if count >= limit:
                                break

                            # Ensure agent exists
                            agent_id = event_data.get('agent_id')
                            if agent_id:
                                agent = Agent.query.filter_by(id=agent_id).first()
                                if not agent:
                                    agent = Agent(
                                        id=agent_id,
                                        agent_type='unknown',
                                        status='active'
                                    )
                                    db.session.add(agent)

                            # Create audit event from ANSE log
                            event = AuditEvent.from_audit_event(event_data)
                            db.session.add(event)
                            count += 1

                        except json.JSONDecodeError:
                            continue

                db.session.commit()
                return count

            except Exception as e:
                db.session.rollback()
                print(f"Error syncing audit events: {e}")
                return 0

    def register_agent(self, agent_id: str, agent_type: str = "unknown") -> bool:
        """
        Register an active agent in the operator-ui database.

        Args:
            agent_id: Agent identifier
            agent_type: Type of agent (e.g., 'scripted', 'llm')

        Returns:
            True if successful
        """
        if not self.app or not OPERATOR_UI_AVAILABLE:
            return False

        with self.app.app_context():
            try:
                agent = Agent.query.filter_by(id=agent_id).first()
                if not agent:
                    agent = Agent(
                        id=agent_id,
                        agent_type=agent_type,
                        status='active'
                    )
                    db.session.add(agent)
                else:
                    agent.status = 'active'

                db.session.commit()
                return True

            except Exception as e:
                db.session.rollback()
                print(f"Error registering agent: {e}")
                return False

    def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent (mark as inactive).

        Args:
            agent_id: Agent identifier

        Returns:
            True if successful
        """
        if not self.app or not OPERATOR_UI_AVAILABLE:
            return False

        with self.app.app_context():
            try:
                agent = Agent.query.filter_by(id=agent_id).first()
                if agent:
                    agent.status = 'inactive'
                    db.session.commit()
                return True

            except Exception as e:
                db.session.rollback()
                print(f"Error deregistering agent: {e}")
                return False


# Global bridge instance
_bridge: Optional[OperatorUIBridge] = None


def get_operator_ui_bridge(db_path: Optional[str] = None) -> Optional[OperatorUIBridge]:
    """Get or create the operator-ui bridge."""
    global _bridge
    if _bridge is None and OPERATOR_UI_AVAILABLE:
        _bridge = OperatorUIBridge(db_path)
        _bridge.initialize()
    return _bridge


def serve_operator_ui(
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
) -> None:
    """
    Start the operator-ui Flask server.

    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    if not OPERATOR_UI_AVAILABLE:
        print("Operator UI not available. Install operator_ui dependencies:")
        print("  pip install -r operator_ui/requirements.txt")
        return

    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # CLI entry point
    import argparse

    parser = argparse.ArgumentParser(description="Start ANSE operator-ui server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    serve_operator_ui(host=args.host, port=args.port, debug=args.debug)
