"""
Body Schema Plugin for ANSE

Provides a self-model of robot hardware: what sensors, actuators, and joints
the robot has, and what they can do.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BodySchemaPlugin:
    """Robot self-model and hardware registry."""

    name = "body_schema"
    description = "Robot self-model defining available sensors, actuators, and joints"
    version = "1.0.0"

    def __init__(self):
        """Initialize body schema with default components."""
        self.sensors: Dict[str, Dict[str, Any]] = {
            "camera": {
                "name": "camera",
                "type": "sensor",
                "description": "RGB camera for vision",
                "resolution": "640x480",
                "fps": 30,
                "range": "0-inf"
            },
            "microphone": {
                "name": "microphone",
                "type": "sensor",
                "description": "Audio input device",
                "sample_rate": 16000,
                "channels": 1
            },
            "sonar": {
                "name": "sonar",
                "type": "sensor",
                "description": "Ultrasonic distance sensor",
                "range_min_cm": 2,
                "range_max_cm": 400
            }
        }

        self.actuators: Dict[str, Dict[str, Any]] = {
            "wheels": {
                "name": "wheels",
                "type": "actuator",
                "description": "Differential drive wheels",
                "max_speed": 100,
                "speed_range": "-100 to 100"
            },
            "speaker": {
                "name": "speaker",
                "type": "actuator",
                "description": "Text-to-speech output",
                "max_text_length": 1000
            }
        }

        self.joints: Dict[str, Dict[str, Any]] = {
            "servo_1": {
                "name": "servo_1",
                "type": "joint",
                "description": "Position 1 servo",
                "min_angle": 0,
                "max_angle": 180,
                "speed": "variable"
            },
            "servo_2": {
                "name": "servo_2",
                "type": "joint",
                "description": "Position 2 servo",
                "min_angle": 0,
                "max_angle": 180,
                "speed": "variable"
            }
        }

    async def describe_body(self) -> Dict[str, Any]:
        """
        Get complete description of robot hardware.

        Returns:
            Dict with sensors, actuators, and joints
        """
        return {
            "status": "success",
            "sensors": list(self.sensors.values()),
            "actuators": list(self.actuators.values()),
            "joints": list(self.joints.values()),
            "component_count": len(self.sensors) + len(self.actuators) + len(self.joints)
        }

    async def describe_sensor(self, sensor_name: str) -> Dict[str, Any]:
        """
        Get detailed info about a specific sensor.

        Args:
            sensor_name: Name of sensor

        Returns:
            Sensor description dict
        """
        if sensor_name in self.sensors:
            return {
                "status": "success",
                "component": self.sensors[sensor_name].copy()
            }
        else:
            return {
                "status": "error",
                "message": f"Sensor '{sensor_name}' not found",
                "available_sensors": list(self.sensors.keys())
            }

    async def describe_actuator(self, actuator_name: str) -> Dict[str, Any]:
        """
        Get detailed info about a specific actuator.

        Args:
            actuator_name: Name of actuator

        Returns:
            Actuator description dict
        """
        if actuator_name in self.actuators:
            return {
                "status": "success",
                "component": self.actuators[actuator_name].copy()
            }
        else:
            return {
                "status": "error",
                "message": f"Actuator '{actuator_name}' not found",
                "available_actuators": list(self.actuators.keys())
            }

    async def describe_joint(self, joint_name: str) -> Dict[str, Any]:
        """
        Get detailed info about a specific joint.

        Args:
            joint_name: Name of joint

        Returns:
            Joint description dict
        """
        if joint_name in self.joints:
            return {
                "status": "success",
                "component": self.joints[joint_name].copy()
            }
        else:
            return {
                "status": "error",
                "message": f"Joint '{joint_name}' not found",
                "available_joints": list(self.joints.keys())
            }

    async def register_component(
        self,
        component_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new sensor, actuator, or joint.

        Args:
            component_type: 'sensor', 'actuator', or 'joint'
            name: Component name
            properties: Optional properties dict

        Returns:
            Confirmation dict
        """
        component = {
            "name": name,
            "type": component_type,
            **(properties or {})
        }

        if component_type == "sensor":
            self.sensors[name] = component
            logger.info(f"[BODY_SCHEMA] Registered sensor: {name}")
        elif component_type == "actuator":
            self.actuators[name] = component
            logger.info(f"[BODY_SCHEMA] Registered actuator: {name}")
        elif component_type == "joint":
            self.joints[name] = component
            logger.info(f"[BODY_SCHEMA] Registered joint: {name}")
        else:
            return {
                "status": "error",
                "message": f"Unknown component type: {component_type}"
            }

        return {
            "status": "success",
            "message": f"Registered {component_type}: {name}",
            "component": component
        }
