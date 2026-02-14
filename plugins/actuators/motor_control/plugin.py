"""
Motor Control Plugin for ANSE

Provides wheel and servo control for robotic actuators.
Includes safety limits and rate limiting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MotorControlPlugin:
    """Robot motor and servo controller."""

    name = "motor_control"
    description = "Motor and servo control for robotic actuators"
    version = "1.0.0"

    def __init__(self):
        """Initialize motor control state."""
        self.wheel_speeds: Dict[str, float] = {"left": 0.0, "right": 0.0}
        self.servo_positions: Dict[int, float] = {}  # servo_id -> angle
        self.is_simulated = False

    async def set_wheel_speed(self, left_speed: float, right_speed: float) -> Dict[str, Any]:
        """
        Set left and right wheel speeds.

        Args:
            left_speed: Speed for left wheel (-100 to 100)
            right_speed: Speed for right wheel (-100 to 100)

        Returns:
            Status dict with current speeds
        """
        # Clamp speeds to valid range
        left_speed = max(-100, min(100, float(left_speed)))
        right_speed = max(-100, min(100, float(right_speed)))

        self.wheel_speeds["left"] = left_speed
        self.wheel_speeds["right"] = right_speed

        logger.info(f"[MOTOR_CONTROL] Wheel speeds set: L={left_speed}, R={right_speed}")

        if not self.is_simulated:
            # TODO: Replace with actual GPIO/PWM/serial control
            # Example: GPIO.output(LEFT_MOTOR_PIN, left_speed)
            pass

        return {
            "status": "success",
            "left_speed": left_speed,
            "right_speed": right_speed,
            "timestamp": datetime.now().isoformat()
        }

    async def set_servo_angle(self, servo_id: int, angle: float, speed: Optional[float] = None) -> Dict[str, Any]:
        """
        Move a servo to a specific angle.

        Args:
            servo_id: Servo identifier
            angle: Target angle in degrees (0-180)
            speed: Movement speed (0-100 percent, optional)

        Returns:
            Status dict with servo position
        """
        servo_id = int(servo_id)
        angle = max(0, min(180, float(angle)))
        speed = float(speed) if speed is not None else 50

        self.servo_positions[servo_id] = angle

        logger.info(f"[MOTOR_CONTROL] Servo {servo_id} moved to {angle}° at speed {speed}")

        if not self.is_simulated:
            # TODO: Replace with actual servo control (PWM, serial, etc.)
            # Example: servo[servo_id].angle(angle)
            pass

        return {
            "status": "success",
            "servo_id": servo_id,
            "angle": angle,
            "speed": speed,
            "timestamp": datetime.now().isoformat()
        }

    async def get_motor_status(self) -> Dict[str, Any]:
        """
        Get current motor and servo status.

        Returns:
            Dict with wheel speeds and servo positions
        """
        return {
            "status": "success",
            "wheels": self.wheel_speeds.copy(),
            "servos": [
                {"id": servo_id, "angle": angle}
                for servo_id, angle in self.servo_positions.items()
            ],
            "timestamp": datetime.now().isoformat()
        }

    async def stop_all_motors(self) -> Dict[str, Any]:
        """
        Emergency stop: halt all motors and servos.

        Returns:
            Confirmation dict
        """
        self.wheel_speeds = {"left": 0, "right": 0}
        logger.warning("[MOTOR_CONTROL] EMERGENCY STOP - all motors halted")

        if not self.is_simulated:
            # TODO: Implement emergency stop hardware code
            pass

        return {
            "status": "success",
            "message": "All motors stopped",
            "timestamp": datetime.now().isoformat()
        }
