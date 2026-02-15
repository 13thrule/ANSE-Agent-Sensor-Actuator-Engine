# What ANSE Actually Is

ANSE is a control scaffold — not a brain, not an AI system, not a world model.

It's an event relay and state manager for autonomous agents.

## What ANSE Does

**It connects three things:**
1. Sensors (read hardware state)
2. Agents (make decisions via WebSocket)
3. Actuators (execute commands)

**It enforces constraints.**
Safety rules block unsafe commands before they reach actuators.

**It logs everything.**
Every sensor reading, every command, every decision. Immutable audit trail with checksums.

## What ANSE Is NOT

- A Vision-Language-Action (VLA) model
- A robotics brain or motion planner
- A learned predictive model
- An embodiment framework
- An AGI or AI research project

The "state store" is not a "world model". It's a timestamped JSON dictionary of sensor readings and actuator states. No learning, no prediction, fully auditable.

## What ANSE Actually Provides

1. **Sensor integration** — Plugins for standard sensors; custom ones are easy to add
2. **Event-driven loop** — Sensors → state → rules → actuators (fully logged)
3. **Safety rules** — YAML-based, execute instantly, block unsafe commands
4. **Actuator control** — Motor commands, state transitions, constrained operations
5. **State store** — Current sensor readings and actuator states, queryable
6. **Rate limiting** — Per-tool, per-agent quotas
7. **Permission scopes** — Agents access only authorized sensors/actuators
8. **Audit trail** — Immutable JSONL log, SHA256 checksums
9. **WebSocket API** — External agents read state and send commands
10. **Simulation mode** — Swap real sensors for deterministic tests

## Example: Home Automation

A concrete, real example ANSE supports today:

```
Setup:
  - Temperature sensor (connected to Raspberry Pi)
  - Motion sensor (PIR detector)
  - Smart plug controlling a fan/heater
  - Local LLM (Llama 2, Mistral, Claude API, etc.)

Reflex rules defined in YAML:
  - IF temperature > 28°C AND motion_detected == true → ALLOW_FAN
  - IF motion_detected == false → FORCE_FAN_OFF
  - IF temperature > 35°C → FORCE_FAN_ON (override motion rule)

LLM decision loop:
  1. Connect to ws://localhost:8001
  2. Receive sensor events: {type: "sensor", sensor: "temperature", value: 27.3}
  3. Observe world state: {temperature_c: 27.3, motion_detected: false, fan_state: "off"}
  4. Decide: "user is away, good time to cool the house"
  5. Send command: {type: "actuator_action", actuator: "fan", state: "on"}
  6. ANSE checks reflexes:
     - Reflex "FORCE_FAN_OFF" fires because motion == false
     - Reflex wins; fan stays OFF
     - Log: "actuator_override: fan command denied, reflex_priority=100"
  7. LLM observes the rejection in the event log, adjusts reasoning
  8. Next cycle, LLM waits for motion detected before retrying

Result:
  - User's safety rules are enforced (ANSE reflexes always win)
  - LLM plans at a high level; ANSE handles constraints
  - Every decision is logged and auditable
  - No surprises; no silent failures
```

The key principle: **ANSE enforces constraints, not intelligence.**

---

## Architecture

```
External Agent (LLM / Script / Controller)
        ↕ WebSocket JSON
        
    ANSE Control Scaffold
    ├─ Sensor Plugins
    │  └─ Read hardware (camera, microphone, temperature, network, etc.)
    ├─ State Store
    │  └─ Timestamped JSON of current state
    ├─ Rule Engine
    │  └─ Validate commands against safety rules
    ├─ Actuator Plugins
    │  └─ Write to hardware (motors, relays, LEDs, etc.)
    ├─ Permission Layer
    │  └─ Rate limits, access scopes
    └─ Audit Logger
       └─ Immutable event trail (SHA256 checksums)
```

Events flow through the pipeline. Everything is logged. Agents observe state, issue commands, and adapt based on approvals/rejections.

---

## Why ANSE Exists

You have hardware. You want an external agent to use it safely.

Without ANSE:
- Manual wiring of sensor drivers, safety logic, actuator handlers
- No audit trail
- Agent logic mixed with hardware logic (hard to test, hard to debug)
- Race conditions between sensors and commands
- No clear separation: what agent wants vs. what's safe

---

## Use ANSE For

- Home automation with safety constraints
- IoT systems with permission enforcement
- Robotics with hardcoded safety limits
- Research with reproducible agent-environment interaction
- Systems requiring audit trails

## Don't Use ANSE For

- Vision-language models (use Claude Vision, OpenAI Vision)
- Motion planning (use MoveIt, ROS Navigation)
- Perception systems (use dedicated ML models)
- Real-time robotics in dynamic environments (use ROS middleware)
- Anything requiring a learned world model

---

## Bottom Line

ANSE is a boring, purpose-built control scaffold. It decouples agent logic from hardware constraints and keeps an immutable audit trail. Use it when you need safe, decoupled agent-hardware interaction with clear accountability.
