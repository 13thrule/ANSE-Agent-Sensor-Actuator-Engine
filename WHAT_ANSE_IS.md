# What ANSE Actually Is

## The Clarity Section

**ANSE is the body, not the brain.**

ANSE is a deterministic runtime that implements a nervous system for autonomous systems. It connects sensors, enforces safety rules, manages state, and controls actuators through a WebSocket API that external agents (LLMs, scripts, controllers) can interface with.

Think of it this way:

- **ANSE is the body**: sensors, reflexes, actuators, state storage, safety enforcement, audit logging
- **Your agent is the brain**: LLM, controller, decision logic, planning

The agent makes decisions by observing the world through ANSE's WebSocket API. ANSE enforces constraints, logs everything, and keeps the system safe.

---

## What ANSE Is NOT

ANSE is **not**:

- A Vision-Language-Action (VLA) model or multimodal AI system
- A robotics brain or motion planner
- A predictive or learned world model (no neural networks, no learning)
- An embodiment framework for LLMs
- A system that translates natural language into perfect motion
- An AGI or general-purpose AI research project

The "world model" in ANSE is not a research concept. **It is a simple, structured state store**: a timestamped JSON-based record updated by sensor readings and reflex triggers. It is deterministic and auditable.

---

## What ANSE Actually Does

ANSE provides:

1. **Sensor integration**: Plugins for cameras, microphones, temperature sensors, network tools, custom hardware
2. **Event-driven loop**: Sensor → World State Update → Reflex Check → Actuator Execution (all async, all logged)
3. **Reflex rules**: Hardcoded safety logic that executes instantly (no agent latency)
4. **Actuator control**: Motor commands, state transitions, constrained operations
5. **World state**: A deterministic, queryable record of all sensor readings, actuator states, and reflex triggers
6. **Rate limiting**: Per-tool, per-agent quotas to prevent resource exhaustion
7. **Permission scopes**: Agents can only access sensors/actuators they're authorized for
8. **Audit trail**: Immutable JSONL log with SHA256 hashes for non-repudiation
9. **WebSocket API**: External agents subscribe to events and send constrained commands
10. **Simulation mode**: Swap real sensors for deterministic test tools; agent code unchanged

---

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

The key insight: **ANSE is not smart about what to do. ANSE is strict about HOW TO DO IT SAFELY.**

---

## Architecture in 100 Words

```
External Agent (LLM / Script / Controller)
        ↕ WebSocket JSON
        
    ANSE Runtime
    ├─ Sensor Plugins
    │  └─ Emit events (camera, microphone, temperature, network, etc.)
    ├─ World Model
    │  └─ Timestamped JSONL event store (deterministic state)
    ├─ Reflex Engine
    │  └─ Fast, synchronous rule evaluation (no agent latency)
    ├─ Actuator Plugins
    │  └─ Motor commands, state transitions (safety-gated)
    ├─ Safety Layer
    │  └─ Rate limits, permission scopes, approval gates
    └─ Audit Logger
       └─ Immutable trail (SHA256 signed)
```

Events flow asynchronously through the pipeline. Everything is logged. Agents react to observing state, not driving it directly.

---

## Why ANSE Exists

Problem it solves:

**You have hardware (sensors, actuators). You want an external agent (LLM, controller, script) to use it safely.**

Without ANSE, you end up:
- Wiring sensor drivers, actuator handlers, and safety logic manually
- No consistent audit trail
- Mixing agent logic with hardware logic (hard to test, hard to debug)
- Racing conditions between agent commands and sensor events
- No separation between "what the agent wants" and "what is actually safe"

ANSE fixes this by providing:
- A **deterministic, auditable event loop** (agent-independent)
- **Pluggable sensors and actuators** (no hand-wiring)
- **Hardcoded safety rules** that execute before agents influence outcomes
- **Clear separation**: agent decides what to do; ANSE enforces how it's done
- **Replayable history**: every sensor reading, every decision, every outcome logged
- **Same API for testing and production**: swap real sensors for simulated ones

This is especially useful for:
- Home automation (safety rules for thermostats, locks, appliances)
- Robotics (reflexes for collision detection, force limits, estop)
- IoT systems (rate limiting, permission enforcement)
- Research (reproducible agent-environment interaction)
- Regulated systems (audit trail for compliance)

---

## When NOT to Use ANSE

ANSE is not the right tool if you need:

- Vision-language grounding (use OpenAI Vision, Claude Vision, etc.)
- Motion planning (use MoveIt, ROS Navigation, etc.)
- Learned world models (use neural networks, diffusion models, etc.)
- Real-time perception and control in dynamic environments (use a robotics middleware like ROS)
- A complete embodied AI stack (ANSE is one piece; you need a brain)

ANSE is one piece. It assumes you have:
- Sensor drivers (whether physical or simulated)
- An external agent (brain) that makes decisions
- Safety policies you can articulate as rules
- A local, deterministic environment (no cloud dependencies, no real-time guarantees)

---

## Bottom Line

**ANSE is boring on purpose.** It is a deterministic, auditable runtime that keeps your hardware and agent decoupled. It does one job well: enforce safety and keep a trail of what happened.

If you need to build a system where an external agent controls hardware safely, ANSE removes the boilerplate and lets you focus on the logic that matters.
