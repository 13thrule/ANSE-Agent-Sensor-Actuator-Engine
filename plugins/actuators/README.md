# Actuator Plugins

Actuator plugins that take actions in the physical world.

## Current Plugins

### Motor Control
- `motor_control/` - General motor control interface
  - Handles speed control, angle positioning, torque limits
  - Integrates with reflex system for fast reactions
  - Supports hardware-agnostic abstraction

## Creating an Actuator

1. Create a new folder for your actuator type
2. Implement the actuator interface (see `motor_control/` as reference)
3. Expose a tool that agents can call
4. Register in your agent's tool registry

## Key Pattern

Actuators should respond to:
- **Direct tool calls** from agents (for complex maneuvers)
- **Reflex triggers** from the reflex system (for fast reactions)
- **World model updates** streamed as events

Example:
```python
async def execute_move(target_position, speed=100):
    # Set motor parameters
    await motor.set_speed(speed)
    await motor.move_to(target_position)
    
    # Emit result event
    await world_model.record(
        type="tool_result",
        tool_name="move_motor",
        result={"position": target_position, "success": True}
    )
```

See [EVENT_DRIVEN_ARCHITECTURE.md](../../docs/EVENT_DRIVEN_ARCHITECTURE.md) for the nervous system model.
