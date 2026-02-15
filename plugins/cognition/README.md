# Cognition Plugins

Higher-level cognitive functions: memory, embodiment, learning, and reward.

## Current Plugins

### Body Schema
- `body_schema/` - Spatial representation of the agent's body
  - Tracks limb positions and orientations
  - Manages proprioception (sense of self in space)
  - Updates from sensor fusion

### Long-Term Memory
- `long_term_memory/` - Persistent storage of experiences
  - Records important events and patterns
  - Provides retrieval interface for agents
  - Supports memory consolidation

### Reward System
- `reward_system/` - Reinforcement learning integration
  - Evaluates outcomes against goals
  - Generates reward signals
  - Tracks learning progress

## Design Pattern

Cognition plugins receive world model events and produce:
- **Computed values**: derived facts (e.g., "body at position X")
- **Evaluations**: assessments of situation (e.g., "goal achieved?")
- **Predictions**: forecasts based on memory (e.g., "this will fail")

Example:
```python
async def process_world_model_update(event):
    if event.type == "sensor_reading":
        # Update internal model
        await self.update_position(event.data)
        
        # Emit result
        await world_model.record(
            type="cognition_update",
            plugin="body_schema",
            derived_fact={"position": self.position}
        )
```

See [EVENT_DRIVEN_ARCHITECTURE.md](../../docs/EVENT_DRIVEN_ARCHITECTURE.md) for how state and events flow.
