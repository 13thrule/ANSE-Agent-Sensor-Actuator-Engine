#!/usr/bin/env python
"""
Minimal ANSE Agent Example

Demonstrates how to:
1. Connect to ANSE WebSocket backend (ws://localhost:8001)
2. Listen for sensor and world model events
3. Send a safe actuator command
4. Observe the audit trail

Usage:
    python backend/websocket_backend.py  # Terminal 1
    python demo_agent.py                 # Terminal 2
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

WS_URL = "ws://localhost:8001"

async def run():
    """Connect to ANSE backend and interact with the nervous system."""
    try:
        async with websockets.connect(WS_URL) as ws:
            print(f"✓ Connected to {WS_URL}")
            agent_id = "demo-agent-001"
            
            # Announce agent presence (optional, but good practice)
            hello = {
                "type": "agent_hello",
                "agent_id": agent_id,
                "capabilities": ["observe", "act"],
                "version": "0.1"
            }
            print(f"\n📤 Sending hello: {json.dumps(hello, indent=2)}")
            await ws.send(json.dumps(hello))

            # Start listener task that runs in background
            async def listener():
                """Listen for incoming events from the backend."""
                event_count = 0
                try:
                    while True:
                        msg = await ws.recv()
                        event_count += 1
                        try:
                            data = json.loads(msg)
                            event_type = data.get("type", "unknown")
                            
                            # Pretty print incoming events
                            print(f"\n📥 Event #{event_count} ({event_type}):")
                            print(json.dumps(data, indent=2)[:500])  # Truncate for readability
                            
                        except json.JSONDecodeError:
                            print(f"\n📥 Event #{event_count} (raw): {msg[:200]}")
                            
                except asyncio.CancelledError:
                    print(f"\n✓ Listener stopped after receiving {event_count} events")
                    
            # Start the listener in background
            listener_task = asyncio.create_task(listener())
            
            # Wait for backend to send initial events
            print("\n⏳ Waiting 2 seconds for initial events...")
            await asyncio.sleep(2)

            # Send a safe actuator command
            # This is a constrained, validated action that won't harm the system
            cmd = {
                "type": "actuator_action",
                "agent_id": agent_id,
                "action": {
                    "name": "move_forward",
                    "params": {
                        "distance_m": 0.1,
                        "speed_m_s": 0.1
                    }
                },
                "meta": {
                    "reason": "demo safe movement",
                    "timestamp": time.time(),
                    "sent_at": datetime.utcnow().isoformat()
                }
            }
            print(f"\n📤 Sending actuator command: {json.dumps(cmd, indent=2)}")
            await ws.send(json.dumps(cmd))

            # Keep listening to see the result
            print("\n⏳ Listening for response (3 seconds)...")
            await asyncio.sleep(3)
            
            # Stop listener
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass

    except ConnectionRefusedError:
        print(f"✗ Could not connect to {WS_URL}")
        print("  Make sure backend is running: python backend/websocket_backend.py")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("ANSE Demo Agent")
    print("=" * 60)
    print(f"\nConnecting to ANSE backend at {WS_URL}...\n")
    
    asyncio.run(run())
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
