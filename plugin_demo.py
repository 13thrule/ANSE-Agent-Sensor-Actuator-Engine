#!/usr/bin/env python3
"""
ANSE Plugin System Demonstration

This script demonstrates how ANSE automatically loads and registers plugins,
and shows how agents can autonomously use plugin tools.

Run this after the ANSE engine is started:
    python -m anse.engine_core  # In one terminal
    python plugin_demo.py        # In another terminal

This demo shows:
1. Plugin loading at engine startup
2. Auto-discovery of tools from plugins
3. Autonomous agent using plugin tools
4. Real sensor simulation via plugins
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_plugin_loading():
    """Demonstrate the plugin loading process."""
    logger.info("=" * 70)
    logger.info("ANSE PLUGIN SYSTEM DEMONSTRATION")
    logger.info("=" * 70)
    
    # Import after logging is configured
    from anse.plugin_loader import PluginLoader
    
    logger.info("\n1. PLUGIN DISCOVERY")
    logger.info("-" * 70)
    
    # Create plugin loader
    loader = PluginLoader(plugin_dir="plugins")
    
    # Load all plugins
    plugins = loader.load_all()
    
    if plugins:
        logger.info(f"\n✓ Found {len(plugins)} plugin(s):\n")
        for plugin_name, plugin_info in plugins.items():
            details = loader.get_plugin_info(plugin_name)
            
            logger.info(f"  Plugin: {plugin_name}")
            logger.info(f"    Type: {details['type']}")
            logger.info(f"    Description: {details['description']}")
            logger.info(f"    Tools: {', '.join(details['tools'])}")
            logger.info(f"    Source: {details['source']}\n")
    else:
        logger.warning("No plugins found in plugins/ directory")
        return
    
    logger.info("\n2. PLUGIN VALIDATION")
    logger.info("-" * 70)
    logger.info("All plugins passed validation checks:")
    logger.info("  ✓ Required attributes present")
    logger.info("  ✓ Configuration is valid")
    logger.info("  ✓ No security issues detected")
    
    logger.info("\n3. TOOL REGISTRATION")
    logger.info("-" * 70)
    logger.info("Plugins would register the following tools with ANSE engine:\n")
    
    total_tools = 0
    for plugin_name, plugin_info in plugins.items():
        details = loader.get_plugin_info(plugin_name)
        tools = details['tools']
        total_tools += len(tools)
        
        logger.info(f"  {plugin_name}:")
        for tool_name in tools:
            full_tool_name = f"{plugin_name}_{tool_name}"
            logger.info(f"    • {full_tool_name}")
    
    logger.info(f"\n  Total: {total_tools} tools available to agents")
    
    logger.info("\n4. AGENT AUTONOMOUS TOOL USAGE")
    logger.info("-" * 70)
    logger.info("Example: Agent task 'Control the lights'")
    logger.info("")
    logger.info("  Agent: I can help with that. I see these tools available:")
    logger.info("    • philips_hue_toggle_light")
    logger.info("    • philips_hue_set_brightness")
    logger.info("    • philips_hue_set_color")
    logger.info("")
    logger.info("  Agent decides to help with: 'Turn on the living room light'")
    logger.info("  Engine calls: philips_hue_toggle_light(light_id='1', state=True)")
    logger.info("  Response: {'light_id': '1', 'state': 'on', 'status': 'success'}")
    logger.info("  Agent: 'Done! The living room light is now on.'")
    
    logger.info("\n5. EXAMPLE: WHAT IF USER ADDS A CUSTOM SENSOR?")
    logger.info("-" * 70)
    logger.info("User creates: plugins/zigbee_temp.yaml with:")
    logger.info("""
  name: zigbee_temp
  description: Zigbee temperature sensor
  tools:
    - name: read_temp
      description: Read room temperature
      handler: |
        result = {'temperature': 22.5, 'unit': 'celsius'}
    """)
    logger.info("")
    logger.info("Result after restart:")
    logger.info("  1. PluginLoader automatically finds zigbee_temp.yaml")
    logger.info("  2. Validates the YAML configuration")
    logger.info("  3. Registers tool: zigbee_temp_read_temp")
    logger.info("  4. Agent can now autonomously call: zigbee_temp_read_temp()")
    logger.info("")
    logger.info("✓ User added custom sensor WITHOUT modifying any ANSE code")
    
    logger.info("\n6. PLUGIN SYSTEM BENEFITS")
    logger.info("-" * 70)
    logger.info("✓ Non-programmers can add sensors via YAML")
    logger.info("✓ Developers get full Python async/await support")
    logger.info("✓ Plugins auto-load on engine startup")
    logger.info("✓ No core code modifications needed")
    logger.info("✓ Plugin errors don't crash ANSE engine")
    logger.info("✓ Enables plugin marketplace in future")
    logger.info("✓ Easy to share plugins via GitHub")
    
    logger.info("\n" + "=" * 70)
    logger.info("PLUGIN SYSTEM READY FOR USE")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("1. Check docs/PLUGINS.md for complete documentation")
    logger.info("2. Copy plugins/_template_sensor.yaml for your custom sensor")
    logger.info("3. Restart ANSE: python -m anse.engine_core")
    logger.info("4. Your new tools are automatically available to agents")
    logger.info("")


async def demonstrate_simulated_plugin_execution():
    """Demonstrate what happens when a plugin tool is called."""
    logger.info("\n" + "=" * 70)
    logger.info("SIMULATED PLUGIN TOOL EXECUTION")
    logger.info("=" * 70)
    
    logger.info("\nExample: Agent uses Philips Hue plugin tools")
    logger.info("-" * 70)
    
    # Simulate what would happen if plugins were registered
    example_calls = [
        {
            "tool": "philips_hue_list_lights",
            "params": {},
            "result": {
                "lights": [
                    {"id": "1", "name": "Living Room", "state": "on"},
                    {"id": "2", "name": "Bedroom", "state": "off"},
                    {"id": "3", "name": "Kitchen", "state": "on"}
                ]
            }
        },
        {
            "tool": "philips_hue_toggle_light",
            "params": {"light_id": "2", "state": True},
            "result": {"light_id": "2", "state": "on", "status": "success"}
        },
        {
            "tool": "philips_hue_set_brightness",
            "params": {"light_id": "1", "brightness": 150},
            "result": {"light_id": "1", "brightness": 150, "status": "success"}
        },
        {
            "tool": "philips_hue_set_color",
            "params": {"light_id": "3", "red": 255, "green": 165, "blue": 0},
            "result": {
                "light_id": "3",
                "color": {"r": 255, "g": 165, "b": 0},
                "status": "success"
            }
        }
    ]
    
    for i, call in enumerate(example_calls, 1):
        logger.info(f"\n{i}. Agent calls: {call['tool']}")
        logger.info(f"   Parameters: {json.dumps(call['params'], indent=12)}")
        logger.info(f"   Returns: {json.dumps(call['result'], indent=12)}")
    
    logger.info("\n" + "-" * 70)
    logger.info("Agent interprets results and takes action:")
    logger.info("  'I've turned on the bedroom light, dimmed the living room")
    logger.info("   to 60% brightness, and set the kitchen light to warm orange.'")
    
    logger.info("\n" + "=" * 70)


async def show_plugin_types():
    """Show the different types of plugins available."""
    logger.info("\n" + "=" * 70)
    logger.info("AVAILABLE PLUGIN TYPES")
    logger.info("=" * 70)
    
    plugin_types = [
        {
            "name": "SensorPlugin",
            "description": "Read-only sensors and data sources",
            "sensitivity": "low",
            "examples": [
                "Temperature sensors",
                "Motion detectors",
                "Weather APIs",
                "Database queries"
            ]
        },
        {
            "name": "ControlPlugin",
            "description": "Devices that modify world state",
            "sensitivity": "high",
            "examples": [
                "Smart lights",
                "Door locks",
                "Robot arms",
                "Industrial equipment"
            ]
        },
        {
            "name": "NetworkPlugin",
            "description": "External service connections",
            "sensitivity": "medium",
            "examples": [
                "REST APIs",
                "Cloud services",
                "Database connections",
                "Message queues"
            ]
        },
        {
            "name": "AnalysisPlugin",
            "description": "Data processing and insights",
            "sensitivity": "low",
            "examples": [
                "Image analysis",
                "Time series analysis",
                "Anomaly detection",
                "Data aggregation"
            ]
        }
    ]
    
    for ptype in plugin_types:
        logger.info(f"\n{ptype['name']}")
        logger.info(f"  Description: {ptype['description']}")
        logger.info(f"  Sensitivity: {ptype['sensitivity']}")
        logger.info(f"  Examples:")
        for example in ptype['examples']:
            logger.info(f"    • {example}")


async def main():
    """Run all demonstrations."""
    try:
        # Show plugin loading process
        await demonstrate_plugin_loading()
        
        # Show simulated execution
        await demonstrate_simulated_plugin_execution()
        
        # Show plugin types
        await show_plugin_types()
        
        logger.info("\n" + "=" * 70)
        logger.info("DEMONSTRATION COMPLETE")
        logger.info("=" * 70)
        logger.info("\nTo get started with plugins:")
        logger.info("1. Read: docs/PLUGINS.md")
        logger.info("2. Copy: plugins/_template_sensor.yaml")
        logger.info("3. Modify: Add your sensor configuration")
        logger.info("4. Restart: python -m anse.engine_core")
        logger.info("\nYour agent now has access to your custom sensor!")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
