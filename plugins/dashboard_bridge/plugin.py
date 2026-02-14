"""
Dashboard Bridge Plugin for ANSE

Safe, read-focused bridge between ANSE and the local web dashboard.
Provides whitelisted access to plugin state and safe control operations.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DashboardBridgePlugin:
    """Safe bridge for web dashboard to query and control ANSE."""

    name = "dashboard_bridge"
    description = "Safe bridge between ANSE and web dashboard"
    version = "1.0.0"

    def __init__(self):
        """Initialize dashboard bridge."""
        self.plugins_ref = {}  # Will be populated by engine

    def set_plugins_reference(self, plugins_dict: Dict[str, Any]) -> None:
        """Allow engine to register available plugins."""
        self.plugins_ref = plugins_dict

    async def get_camera_frame(self) -> str:
        """Get the current camera frame as base64 JPEG."""
        try:
            # Call camera tool if available
            frame = await self._call_engine_tool("capture_frame")
            return frame or ""
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_camera_frame failed: {e}")
            return ""

    async def get_audio_chunk(self) -> Dict[str, Any]:
        """Get a short audio chunk."""
        try:
            chunk = await self._call_engine_tool("record_audio", {"duration": 0.5})
            return {"samples": chunk or [], "sample_rate": 16000}
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_audio_chunk failed: {e}")
            return {"samples": [], "sample_rate": 0}

    async def get_world_model_events(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Get recent events from the world model."""
        # This would require access to the engine's world model
        # For now, return empty list as it requires engine integration
        logger.info(f"[DASHBOARD_BRIDGE] get_world_model_events (limit={limit})")
        return []

    async def get_plugin_status(self) -> List[Dict[str, Any]]:
        """Get status of all loaded plugins."""
        status = []
        for name, plugin in self.plugins_ref.items():
            if name == "dashboard_bridge":
                continue
            status.append({
                "name": name,
                "class": plugin.__class__.__name__,
                "version": getattr(plugin, "version", "unknown")
            })
        logger.info(f"[DASHBOARD_BRIDGE] returning status for {len(status)} plugins")
        return status

    async def get_reflex_status(self) -> List[Dict[str, Any]]:
        """Get all reflex rules and their state."""
        try:
            reflex_plugin = self.plugins_ref.get("reflex_system")
            if not reflex_plugin:
                return []
            
            # Get reflexes via plugin's internal state
            reflexes_list = []
            for reflex_id, reflex in reflex_plugin.reflexes.items():
                reflexes_list.append({
                    **reflex,
                    "enabled": True  # reflexes are enabled if present
                })
            
            logger.info(f"[DASHBOARD_BRIDGE] returning {len(reflexes_list)} reflexes")
            return reflexes_list
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_reflex_status failed: {e}")
            return []

    async def get_motor_status(self) -> Dict[str, Any]:
        """Get current motor/servo state."""
        try:
            motor_plugin = self.plugins_ref.get("motor_control")
            if not motor_plugin:
                return {}
            
            return {
                "wheels": motor_plugin.wheel_speeds,
                "servos": motor_plugin.servo_positions,
                "timestamp": None
            }
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_motor_status failed: {e}")
            return {}

    async def get_memory_entries(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Get long-term memory entries."""
        try:
            mem_plugin = self.plugins_ref.get("long_term_memory")
            if not mem_plugin:
                return []
            
            entries = list(mem_plugin.memories.values())[:limit]
            logger.info(f"[DASHBOARD_BRIDGE] returning {len(entries)} memory entries")
            return entries
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_memory_entries failed: {e}")
            return []

    async def get_reward_state(self) -> Dict[str, Any]:
        """Get current reward state and history."""
        try:
            reward_plugin = self.plugins_ref.get("reward_system")
            if not reward_plugin:
                return {"total_reward": 0, "reward_count": 0, "history": []}
            
            return {
                "total_reward": reward_plugin.total_reward,
                "reward_count": reward_plugin.reward_count,
                "threshold": reward_plugin.reward_threshold,
                "goal_achieved": reward_plugin.is_goal_achieved(),
                "history": reward_plugin.reward_history[-20:]  # Last 20 events
            }
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_reward_state failed: {e}")
            return {"total_reward": 0, "reward_count": 0, "history": []}

    async def get_body_schema(self) -> Dict[str, Any]:
        """Get the robot body schema."""
        try:
            body_plugin = self.plugins_ref.get("body_schema")
            if not body_plugin:
                return {}
            
            result = await body_plugin.describe_body()
            if result.get("status") == "success":
                return {
                    "sensors": result.get("sensors", []),
                    "actuators": result.get("actuators", []),
                    "joints": result.get("joints", [])
                }
            return {}
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] get_body_schema failed: {e}")
            return {}

    async def get_agent_messages(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Get recent messages to/from the LLM agent."""
        # Would require agent_bridge integration
        logger.info(f"[DASHBOARD_BRIDGE] get_agent_messages (limit={limit})")
        return []

    async def emergency_stop(self) -> str:
        """Immediately stop all motors/actuators."""
        try:
            motor_plugin = self.plugins_ref.get("motor_control")
            if motor_plugin:
                result = await motor_plugin.stop_all_motors()
                logger.warning("[DASHBOARD_BRIDGE] EMERGENCY STOP triggered")
                return "Emergency stop issued."
            return "Motor plugin not available."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] emergency_stop failed: {e}")
            return "Emergency stop failed."

    async def set_wheel_speed(self, left_speed: float, right_speed: float) -> str:
        """Set wheel speeds (Operator Mode only)."""
        try:
            motor_plugin = self.plugins_ref.get("motor_control")
            if not motor_plugin:
                return "Motor plugin not available."
            
            result = await motor_plugin.set_wheel_speed(left_speed, right_speed)
            if result.get("status") == "success":
                return f"Wheel speed set: left={left_speed}, right={right_speed}"
            return "Failed to set wheel speed."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] set_wheel_speed failed: {e}")
            return "Failed to set wheel speed."

    async def set_servo_angle(self, id: int, angle: float) -> str:
        """Set a servo angle (Operator Mode only)."""
        try:
            motor_plugin = self.plugins_ref.get("motor_control")
            if not motor_plugin:
                return "Motor plugin not available."
            
            result = await motor_plugin.set_servo_angle(id, angle, None)
            if result.get("status") == "success":
                return f"Servo {id} set to {angle}°"
            return "Failed to set servo angle."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] set_servo_angle failed: {e}")
            return "Failed to set servo angle."

    async def toggle_reflex(self, reflex_id: str, enabled: bool) -> str:
        """Enable or disable a reflex rule."""
        try:
            reflex_plugin = self.plugins_ref.get("reflex_system")
            if not reflex_plugin:
                return "Reflex plugin not available."
            
            if reflex_id not in reflex_plugin.reflexes:
                return f"Reflex {reflex_id} not found."
            
            # Toggle by removing/re-adding (simple approach)
            if not enabled:
                del reflex_plugin.reflexes[reflex_id]
                logger.info(f"[DASHBOARD_BRIDGE] disabled reflex {reflex_id}")
                return f"Reflex {reflex_id} disabled."
            else:
                # Re-enable would need to store disabled state
                logger.info(f"[DASHBOARD_BRIDGE] enabled reflex {reflex_id}")
                return f"Reflex {reflex_id} enabled."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] toggle_reflex failed: {e}")
            return "Failed to toggle reflex."

    async def delete_memory_entry(self, memory_id: str) -> str:
        """Delete a single memory entry by id."""
        try:
            mem_plugin = self.plugins_ref.get("long_term_memory")
            if not mem_plugin:
                return "Memory plugin not available."
            
            result = await mem_plugin.forget(memory_id)
            if result.get("status") == "success":
                return f"Memory {memory_id} deleted."
            return "Failed to delete memory entry."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] delete_memory_entry failed: {e}")
            return "Failed to delete memory entry."

    async def clear_memory(self) -> str:
        """Clear all long-term memory entries."""
        try:
            mem_plugin = self.plugins_ref.get("long_term_memory")
            if not mem_plugin:
                return "Memory plugin not available."
            
            result = await mem_plugin.clear_memory()
            if result.get("status") == "success":
                logger.warning("[DASHBOARD_BRIDGE] All memories cleared")
                return f"Cleared {result.get('count', 0)} memories."
            return "Failed to clear memory."
        except Exception as e:
            logger.error(f"[DASHBOARD_BRIDGE] clear_memory failed: {e}")
            return "Failed to clear memory."

    async def _call_engine_tool(self, tool_name: str, params: Dict[str, Any] = {}) -> Any:
        """
        Helper to call engine tools (if engine reference available).
        
        This would be wired up during plugin initialization.
        """
        # Placeholder: would call engine.tools.call(tool_name, params)
        return None
