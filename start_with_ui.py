#!/usr/bin/env python3
"""
Start ANSE engine with operator-ui console.

This script launches:
1. ANSE engine (WebSocket on 127.0.0.1:8765)
2. Operator-ui Flask server (HTTP on 127.0.0.1:5000)
3. Audit sync loop

Usage:
    python start_with_ui.py
    python start_with_ui.py --engine-port 8765 --ui-port 5000
    python start_with_ui.py --ui-host 0.0.0.0 --ui-port 5000 --debug
"""

import asyncio
import sys
import argparse
import os
from multiprocessing import Process
from pathlib import Path

# Add anse to path
sys.path.insert(0, str(Path(__file__).parent))

from anse.engine_core import EngineCore
from anse.audit import AuditLogger
from anse.operator_ui_bridge import serve_operator_ui, get_operator_ui_bridge


async def run_engine(host: str, port: int, audit_file: str) -> None:
    """Run ANSE engine."""
    engine = EngineCore()
    await engine.bridge.serve(host, port)


def run_ui(host: str, port: int, debug: bool) -> None:
    """Run operator-ui server."""
    try:
        serve_operator_ui(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"Error starting operator-ui: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start ANSE engine with operator-ui console"
    )
    parser.add_argument(
        "--engine-host",
        default="127.0.0.1",
        help="ANSE engine host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--engine-port",
        type=int,
        default=8765,
        help="ANSE engine port (default: 8765)"
    )
    parser.add_argument(
        "--ui-host",
        default="127.0.0.1",
        help="Operator-ui server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--ui-port",
        type=int,
        default=5000,
        help="Operator-ui server port (default: 5000)"
    )
    parser.add_argument(
        "--audit-file",
        default="audit.jsonl",
        help="Audit log file path (default: audit.jsonl)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for operator-ui"
    )

    args = parser.parse_args()

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║         ANSE Engine with Operator Console                 ║
    ╚═══════════════════════════════════════════════════════════╝

    Starting components:
    
    1. ANSE Engine
       WebSocket: ws://{args.engine_host}:{args.engine_port}
       Audit Log: {args.audit_file}
    
    2. Operator-UI Console
       HTTP: http://{args.ui_host}:{args.ui_port}
       Username: admin
       Password: admin
    
    Control+C to stop all services.
    """)

    # Start operator-ui in a separate process
    ui_process = Process(
        target=run_ui,
        args=(args.ui_host, args.ui_port, args.debug),
        daemon=True
    )
    ui_process.start()

    try:
        # Run engine in main process
        asyncio.run(run_engine(args.engine_host, args.engine_port, args.audit_file))
    except KeyboardInterrupt:
        print("\nShutting down...")
        ui_process.terminate()
        ui_process.join(timeout=5)
        if ui_process.is_alive():
            ui_process.kill()
        sys.exit(0)


if __name__ == "__main__":
    main()
