"""Operator UI backend: Flask server for ANSE agent monitoring and approval."""

import os
import json
from datetime import datetime
from functools import wraps
from typing import Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

from .models import db, Agent, ApprovalToken, AuditEvent, init_db


def create_app(config=None):
    """Create and configure Flask app."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "OPERATOR_UI_DB", "sqlite:///operator_ui.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    if config:
        app.config.update(config)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        init_db(app)

    # CORS for dev
    CORS(app)

    # Configuration
    SECRET_KEY = os.getenv("OPERATOR_SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["SECRET_KEY"] = SECRET_KEY
    ANSE_ENGINE_URL = os.getenv("ANSE_ENGINE_URL", "ws://127.0.0.1:8765")

    # Authentication decorator
    def require_auth(f):
        """Require basic auth (dev only)."""

        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth:
                return jsonify({"error": "Missing authorization header"}), 401

            # Dev: simple username/password check
            expected_user = os.getenv("OPERATOR_USER", "admin")
            expected_pass = os.getenv("OPERATOR_PASSWORD", "admin")

            if auth.username != expected_user or auth.password != expected_pass:
                return jsonify({"error": "Invalid credentials"}), 401

            return f(*args, **kwargs)

        return decorated

    # Routes
    @app.route("/health", methods=["GET"])
    def health():
        """Health check."""
        return jsonify({"status": "running", "version": "0.2.0"}), 200

    @app.route("/api/health", methods=["GET"])
    @require_auth
    def api_health():
        """Overall system status."""
        return jsonify(
            {
                "status": "operational",
                "operator_ui": "running",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ), 200

    @app.route("/api/agents", methods=["GET"])
    @require_auth
    def list_agents():
        """List active agents."""
        agents = Agent.query.filter_by(status="active").all()
        return jsonify({"agents": [a.to_dict() for a in agents]}), 200

    @app.route("/api/agents/<agent_id>", methods=["GET"])
    @require_auth
    def get_agent(agent_id):
        """Get agent details."""
        agent = Agent.query.filter_by(id=agent_id).first()
        if not agent:
            return jsonify({"error": "Agent not found"}), 404

        return jsonify(agent.to_dict()), 200

    @app.route("/api/audit", methods=["GET"])
    @require_auth
    def list_audit():
        """Stream audit events (paginated JSONL)."""
        limit = request.args.get("limit", 50, type=int)
        agent_id = request.args.get("agent_id", None, type=str)
        tool_name = request.args.get("tool", None, type=str)

        query = AuditEvent.query.order_by(AuditEvent.timestamp.desc())

        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        if tool_name:
            query = query.filter_by(tool_name=tool_name)

        events = query.limit(limit).all()

        return jsonify(
            {"events": [e.to_dict() for e in reversed(events)], "count": len(events)}
        ), 200

    @app.route("/api/approve", methods=["POST"])
    @require_auth
    def issue_approval():
        """Issue an approval token."""
        data = request.get_json() or {}

        agent_id = data.get("agent_id")
        scope = data.get("scope")
        ttl_seconds = data.get("ttl_seconds", 300)

        if not agent_id or not scope:
            return jsonify({"error": "Missing agent_id or scope"}), 400

        agent = Agent.query.filter_by(id=agent_id).first()
        if not agent:
            return jsonify({"error": "Agent not found"}), 404

        # Generate token
        token_obj, token_string = ApprovalToken.generate(
            agent_id=agent_id,
            scope=scope,
            ttl_seconds=ttl_seconds,
            secret_key=SECRET_KEY,
        )

        db.session.add(token_obj)
        db.session.commit()

        return (
            jsonify(
                {
                    "token": token_string,
                    "expires_at": token_obj.expires_at.isoformat(),
                    "scope": scope,
                }
            ),
            201,
        )

    @app.route("/api/tokens/<agent_id>", methods=["GET"])
    @require_auth
    def list_tokens(agent_id):
        """List approval tokens for an agent."""
        tokens = ApprovalToken.query.filter_by(agent_id=agent_id).all()
        return jsonify({"tokens": [t.to_dict() for t in tokens]}), 200

    @app.route("/api/tokens/<token_id>/revoke", methods=["POST"])
    @require_auth
    def revoke_token(token_id):
        """Revoke an approval token."""
        token = ApprovalToken.query.filter_by(id=token_id).first()
        if not token:
            return jsonify({"error": "Token not found"}), 404

        token.revoked = True
        db.session.commit()

        return jsonify({"status": "revoked"}), 200

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404."""
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500."""
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
