"""
Scripted Agent - Demonstrates basic tool usage via the agent bridge.
This agent follows a predetermined sequence: list tools, capture frame,
record audio, and speak.
"""
import asyncio
import json
import logging
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_scripted_agent(uri: str = "ws://127.0.0.1:8765"):
    """
    Run a scripted agent that demonstrates tool usage.
    
    Args:
        uri: WebSocket URI of the ANSE engine
    """
    logger.info(f"Connecting to ANSE engine at {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to engine")
            
            # Step 1: List available tools
            logger.info("Step 1: Listing available tools")
            await websocket.send(json.dumps({"method": "list_tools"}))
            response = json.loads(await websocket.recv())
            tools = response.get("result", {})
            logger.info(f"Available tools: {list(tools.keys())}")
            
            # Step 2: Capture a frame
            logger.info("Step 2: Capturing camera frame")
            call = {
                "agent_id": "scripted-demo",
                "call_id": "call-001",
                "tool": "capture_frame",
                "args": {}
            }
            await websocket.send(json.dumps({"method": "call_tool", "params": call}))
            response = json.loads(await websocket.recv())
            
            if response.get("status") == "ok":
                result = response.get("result", {})
                logger.info(f"✓ Frame captured: {result.get('frame_id')}")
                logger.info(f"  Path: {result.get('path')}")
                logger.info(f"  Size: {result.get('width')}x{result.get('height')}")
            else:
                logger.error(f"✗ Frame capture failed: {response.get('error')}")
            
            # Step 3: Record audio
            logger.info("Step 3: Recording audio (2 seconds)")
            call = {
                "agent_id": "scripted-demo",
                "call_id": "call-002",
                "tool": "record_audio",
                "args": {"duration": 2.0}
            }
            await websocket.send(json.dumps({"method": "call_tool", "params": call}))
            response = json.loads(await websocket.recv())
            
            if response.get("status") == "ok":
                result = response.get("result", {})
                logger.info(f"✓ Audio recorded: {result.get('audio_id')}")
                logger.info(f"  Path: {result.get('path')}")
                logger.info(f"  Duration: {result.get('duration')}s")
            else:
                logger.error(f"✗ Audio recording failed: {response.get('error')}")
            
            # Step 4: Speak text
            logger.info("Step 4: Speaking text via TTS")
            call = {
                "agent_id": "scripted-demo",
                "call_id": "call-003",
                "tool": "say",
                "args": {"text": "Hello from the scripted agent! ANSE is now operational."}
            }
            await websocket.send(json.dumps({"method": "call_tool", "params": call}))
            response = json.loads(await websocket.recv())
            
            if response.get("status") == "ok":
                result = response.get("result", {})
                logger.info(f"✓ Text spoken: {result.get('spoken')}")
            else:
                logger.error(f"✗ Speech failed: {response.get('error')}")
            
            # Step 5: Get history
            logger.info("Step 5: Retrieving event history")
            await websocket.send(json.dumps({"method": "get_history", "params": {"n": 10}}))
            response = json.loads(await websocket.recv())
            events = response.get("result", [])
            logger.info(f"Retrieved {len(events)} events from history")
            
            logger.info("✓ Scripted agent completed successfully!")
            
    except (ConnectionRefusedError, OSError) as e:
        logger.error("Could not connect to ANSE engine. Is it running?")
        logger.error("Start the engine with: python -m anse.engine_core")
        logger.error(f"Details: {e}")
    except Exception as e:
        logger.error(f"Error running scripted agent: {e}", exc_info=True)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run scripted ANSE agent demo")
    parser.add_argument(
        "--uri",
        default="ws://127.0.0.1:8765",
        help="WebSocket URI of ANSE engine"
    )
    
    args = parser.parse_args()
    
    asyncio.run(run_scripted_agent(args.uri))


if __name__ == "__main__":
    main()
