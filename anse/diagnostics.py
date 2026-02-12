"""
ANSE Diagnostics CLI - Check engine health and connectivity.

Usage:
    python -m anse.diagnostics [--host HOST] [--port PORT] [--verbose]
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime

import websockets


class Diagnostics:
    """Run diagnostic checks on ANSE engine."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765, verbose: bool = False):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.verbose = verbose
        self.checks_passed = 0
        self.checks_failed = 0

    async def run(self):
        """Run all diagnostic checks."""
        print("\n" + "=" * 60)
        print("ANSE Diagnostics v0.1.0")
        print("=" * 60 + "\n")

        # Check 1: WebSocket connectivity
        await self._check_websocket_connection()

        # Check 2: Health endpoint
        await self._check_health_endpoint()

        # Check 3: Diagnostics endpoint
        await self._check_diagnostics_endpoint()

        # Check 4: List tools
        await self._check_list_tools()

        # Check 5: Tool info
        await self._check_tool_info()

        # Summary
        self._print_summary()

    async def _check_websocket_connection(self):
        """Check if WebSocket server is reachable."""
        self._print_check("WebSocket Connectivity", f"{self.uri}")

        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(json.dumps({"method": "ping"}))
                response = json.loads(await ws.recv())
                if response.get("result") == "pong":
                    self._print_pass("Connected successfully")
                    self.checks_passed += 1
                else:
                    self._print_fail(f"Unexpected response: {response}")
                    self.checks_failed += 1
        except Exception as e:
            self._print_fail(f"{type(e).__name__}: {e}")
            self.checks_failed += 1

    async def _check_health_endpoint(self):
        """Check health endpoint."""
        self._print_check("Health Endpoint", "engine.health()")

        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(json.dumps({"method": "health"}))
                response = json.loads(await ws.recv())

                if "result" in response:
                    health = response["result"]
                    status = health.get("status", "unknown")
                    uptime = health.get("uptime_readable", "?")
                    memory = health.get("memory_mb", "?")

                    if status == "running":
                        self._print_pass(
                            f"Status={status}, Uptime={uptime}, Memory={memory}MB"
                        )
                        self.checks_passed += 1

                        if self.verbose:
                            self._print_verbose_json(health)
                    else:
                        self._print_fail(f"Status={status}")
                        self.checks_failed += 1
                else:
                    self._print_fail(f"No result in response: {response}")
                    self.checks_failed += 1

        except Exception as e:
            self._print_fail(f"{type(e).__name__}: {e}")
            self.checks_failed += 1

    async def _check_diagnostics_endpoint(self):
        """Check diagnostics endpoint."""
        self._print_check("Diagnostics Endpoint", "engine.diagnostics()")

        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(json.dumps({"method": "diagnostics"}))
                response = json.loads(await ws.recv())

                if "result" in response:
                    diag = response["result"]
                    memory = diag.get("memory_mb", "?")
                    cpu = diag.get("cpu_percent", "?")
                    events = diag.get("event_count", 0)

                    self._print_pass(f"Memory={memory}MB, CPU={cpu}%, Events={events}")
                    self.checks_passed += 1

                    if self.verbose:
                        self._print_verbose_json(diag)
                else:
                    self._print_fail(f"No result in response: {response}")
                    self.checks_failed += 1

        except Exception as e:
            self._print_fail(f"{type(e).__name__}: {e}")
            self.checks_failed += 1

    async def _check_list_tools(self):
        """Check tool listing."""
        self._print_check("Tool Registry", "list_tools()")

        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(json.dumps({"method": "list_tools"}))
                response = json.loads(await ws.recv())

                if "result" in response:
                    tools = response["result"]
                    tool_count = len(tools)
                    tool_names = [t.get("name", "?") for t in tools]

                    self._print_pass(f"Found {tool_count} tools: {', '.join(tool_names)}")
                    self.checks_passed += 1

                    if self.verbose:
                        self._print_verbose_json(tools)
                else:
                    self._print_fail(f"No result in response: {response}")
                    self.checks_failed += 1

        except Exception as e:
            self._print_fail(f"{type(e).__name__}: {e}")
            self.checks_failed += 1

    async def _check_tool_info(self):
        """Check tool info endpoint."""
        self._print_check("Tool Info Endpoint", "get_tool_info(capture_frame)")

        try:
            async with websockets.connect(self.uri) as ws:
                await ws.send(
                    json.dumps(
                        {"method": "get_tool_info", "params": {"tool": "capture_frame"}}
                    )
                )
                response = json.loads(await ws.recv())

                if "result" in response:
                    info = response["result"]
                    name = info.get("name", "?")
                    desc = info.get("description", "?")

                    self._print_pass(f"Tool={name}, Desc={desc[:50]}...")
                    self.checks_passed += 1

                    if self.verbose:
                        self._print_verbose_json(info)
                else:
                    self._print_fail(f"No result in response: {response}")
                    self.checks_failed += 1

        except Exception as e:
            self._print_fail(f"{type(e).__name__}: {e}")
            self.checks_failed += 1

    def _print_check(self, name: str, detail: str = ""):
        """Print a check header."""
        print(f"\n[CHECK] {name}")
        if detail:
            print(f"  └─ {detail}")

    def _print_pass(self, msg: str):
        """Print a passing check."""
        print(f"  ✓ {msg}")

    def _print_fail(self, msg: str):
        """Print a failing check."""
        print(f"  ✗ {msg}")

    def _print_verbose_json(self, data):
        """Print JSON data in verbose mode."""
        print(f"  {json.dumps(data, indent=4)}")

    def _print_summary(self):
        """Print summary of checks."""
        total = self.checks_passed + self.checks_failed
        percentage = (
            100 * self.checks_passed // total if total > 0 else 0
        )

        print("\n" + "=" * 60)
        print(f"Summary: {self.checks_passed}/{total} checks passed ({percentage}%)")
        print("=" * 60 + "\n")

        if self.checks_failed == 0:
            print("✓ All diagnostics passed! Engine is healthy.")
            return 0
        else:
            print(
                f"✗ {self.checks_failed} diagnostic(s) failed. Check engine logs for details."
            )
            return 1


async def main():
    """Parse args and run diagnostics."""
    parser = argparse.ArgumentParser(
        description="ANSE Diagnostics - Check engine health and connectivity"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Engine host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8765, help="Engine port (default: 8765)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose output"
    )

    args = parser.parse_args()

    diag = Diagnostics(host=args.host, port=args.port, verbose=args.verbose)
    exit_code = await diag.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
