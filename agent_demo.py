#!/usr/bin/env python
"""Autonomous agent that uses ANSE as intended."""

import sys
import asyncio
from datetime import datetime
from anse.engine_core import EngineCore
from anse.tools.analysis import analyze_frame, analyze_audio


class AutonomousAgent:
    """Agent that uses ANSE engine directly (async)."""

    def __init__(self, agent_id="autonomous-agent-001"):
        self.agent_id = agent_id
        self.engine = EngineCore()
        self.memory = []
        self.captured_data = {}  # Store captured frame/audio paths
        
        # Register analysis tools
        self.engine.tools.register(
            name="analyze_frame",
            func=analyze_frame,
            schema={
                "type": "object",
                "properties": {
                    "frame_id": {"type": "string", "description": "Frame ID from capture_frame"},
                    "frame_path": {"type": "string", "description": "Path to the JPEG file"}
                },
                "required": ["frame_id", "frame_path"]
            },
            description="Analyze a captured frame to verify it's real data",
            sensitivity="low"
        )
        
        self.engine.tools.register(
            name="analyze_audio",
            func=analyze_audio,
            schema={
                "type": "object",
                "properties": {
                    "audio_id": {"type": "string", "description": "Audio ID from record_audio"},
                    "audio_path": {"type": "string", "description": "Path to the WAV file"}
                },
                "required": ["audio_id", "audio_path"]
            },
            description="Analyze recorded audio to verify it's real data",
            sensitivity="low"
        )

    def discover_tools(self):
        """Discover available tools from ANSE."""
        print("\n📋 Discovering available tools...")
        tools_list = self.engine.tools.list_tools()
        
        print(f"✓ Found {len(tools_list)} tools:")
        for name, info in tools_list.items():
            print(f"  - {name}: {info.get('description', 'N/A')}")
        
        return tools_list

    async def call_tool(self, tool_name, **kwargs):
        """Call a tool and get result."""
        print(f"\n🔧 Calling {tool_name}({kwargs})...")
        
        try:
            # Call tool via registry (async)
            result = await self.engine.tools.call(tool_name, kwargs)
            print(f"✓ {tool_name} completed")
            
            # Store captured data for later analysis
            if tool_name == "capture_frame" and result and "path" in result:
                self.captured_data["frame"] = {
                    "id": result.get("frame_id"),
                    "path": result.get("path")
                }
            elif tool_name == "record_audio" and result and "path" in result:
                self.captured_data["audio"] = {
                    "id": result.get("audio_id"),
                    "path": result.get("path")
                }
            
            if result:
                # Show detailed analysis results
                if tool_name.startswith("analyze_"):
                    print(f"\n  📊 Analysis Results:")
                    if "message" in result:
                        print(f"     {result['message']}")
                    
                    # Show specific metrics
                    if "edge_detection" in result:
                        print(f"     Edges detected: {result['edge_detection']['edges_found']}")
                        print(f"     Edge density: {result['edge_detection']['edge_density_percent']}%")
                    if "corner_detection" in result:
                        print(f"     Corners found: {result['corner_detection']['corners_found']}")
                    if "color_analysis" in result:
                        colors = result['color_analysis']
                        print(f"     Avg Color: RGB({colors.get('avg_red', 0)}, {colors.get('avg_green', 0)}, {colors.get('avg_blue', 0)})")
                    if "frequency_analysis" in result:
                        print(f"     Dominant frequencies: {result['frequency_analysis']['dominant_frequencies_hz']} Hz")
                    if "audio_statistics" in result:
                        stats = result['audio_statistics']
                        print(f"     RMS Energy: {stats.get('rms_energy', 0)}")
                        print(f"     Peak Amplitude: {stats.get('peak_amplitude', 0)}")
                        if "dynamic_range_db" in stats:
                            print(f"     Dynamic Range: {stats['dynamic_range_db']} dB")
                else:
                    result_str = str(result)[:150]
                    print(f"  Result: {result_str}")
            
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "action": tool_name,
                "args": kwargs,
                "result": result,
            })
            return result
        except Exception as e:
            print(f"✗ Error calling {tool_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def execute_task(self, task_description):
        """Execute a task by making autonomous decisions."""
        print(f"\n🎯 Task: {task_description}")
        print("=" * 60)

        # Demonstrate autonomous decision-making
        if "capture" in task_description.lower() or "see" in task_description.lower():
            print("\n💭 Agent reasoning: User wants me to capture visual data")
            print("   Decision: Call capture_frame() to see what's available")
            await self.call_tool("capture_frame")
            
            # Analyze the captured frame to prove we have real data
            if "frame" in self.captured_data:
                print("\n💭 Agent reasoning: I captured a frame, now let me verify it's real data")
                print("   Decision: Analyze the frame file")
                frame = self.captured_data["frame"]
                await self.call_tool("analyze_frame", frame_id=frame["id"], frame_path=frame["path"])

        if "record" in task_description.lower() or "listen" in task_description.lower():
            print("\n💭 Agent reasoning: User wants me to record audio")
            print("   Decision: Call record_audio() with 2 second duration")
            await self.call_tool("record_audio", duration=2.0)
            
            # Analyze the recorded audio to prove we have real data
            if "audio" in self.captured_data:
                print("\n💭 Agent reasoning: I recorded audio, now let me verify it's real data")
                print("   Decision: Analyze the audio file")
                audio = self.captured_data["audio"]
                await self.call_tool("analyze_audio", audio_id=audio["id"], audio_path=audio["path"])

        if "speak" in task_description.lower() or "say" in task_description.lower():
            print("\n💭 Agent reasoning: User wants me to speak")
            print("   Decision: Call say() to produce speech")
            message = "Hello, I am an autonomous agent powered by ANSE. I can see, hear, and speak!"
            await self.call_tool("say", text=message)

        if ("list" in task_description.lower() or 
            "discover" in task_description.lower() or 
            "what" in task_description.lower() or
            "show" in task_description.lower()):
            print("\n💭 Agent reasoning: User wants to know capabilities")
            print("   Decision: Reviewing available tools")
            tools = self.discover_tools()
            print(f"\n📊 Agent can access {len(tools)} tools")

        print("\n" + "=" * 60)
        print(f"✓ Task complete. Agent memory ({len(self.memory)} events)")
        print(f"   Captured data: frame={self.captured_data.get('frame') is not None}, audio={self.captured_data.get('audio') is not None}")

    def show_memory(self):
        """Display agent's memory of actions."""
        if not self.memory:
            print("\n📝 No events in memory yet")
            return
            
        print("\n📝 Agent Memory Log:")
        print("=" * 60)
        for i, event in enumerate(self.memory, 1):
            print(f"\n  Event {i}:")
            print(f"    Time: {event['timestamp']}")
            print(f"    Action: {event['action']}")
            print(f"    Args: {event['args']}")
            if event.get("result"):
                result_str = str(event["result"])[:100]
                print(f"    Result: {result_str}...")

    async def run(self, task):
        """Run the agent."""
        print("✓ ANSE Engine initialized")
        
        # Discover capabilities
        self.discover_tools()

        # Execute task
        await self.execute_task(task)

        # Show memory
        self.show_memory()

        print("\n✓ Agent completed task")


async def main():
    """Main entry point."""
    print("🤖 ANSE Autonomous Agent")
    print("=" * 60)

    # Create agent
    agent = AutonomousAgent()

    # Task to execute
    task = "I can see, listen, and speak. Show me what you can do!"

    # Run agent
    try:
        await agent.run(task)
    except Exception as e:
        print(f"\n✗ Agent error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
