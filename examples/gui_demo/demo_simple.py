#!/usr/bin/env python3
"""Simple demo showing ANSE nervous system in action.

This script demonstrates:
1. Distance sensor emitting readings
2. Proximity reflex triggering
3. Movement actuator responding
4. All events recorded to world model

Run with: python demo_simple.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from anse.engine_core import EngineCore
from anse.world_model import WorldModel


class SimpleNervousSystemDemo:
    """Demonstrate ANSE nervous system with one sensor, one reflex, one actuator."""
    
    def __init__(self):
        self.engine = None
        self.world_model = None
        self.distance = 50  # cm
        self.movement_state = "IDLE"
        self.events_recorded = 0
    
    async def initialize(self):
        """Initialize ANSE engine."""
        print("[INIT] Initializing ANSE Engine...")
        self.engine = EngineCore(simulate=True)
        self.world_model = self.engine.world
        print("[INIT] Engine ready\n")
    
    async def record_event(self, event_type: str, data: dict):
        """Record event to world model."""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        self.world_model.append_event(event)
        self.events_recorded += 1
    
    async def sensor_reading(self, iteration: int):
        """Emit sensor reading."""
        # Gradually approach (0-7: 50 > 5cm), then recede (8-18: 5 > 50cm)
        if iteration < 8:
            self.distance = max(5, 50 - (iteration * 5.5))
        else:
            self.distance = min(50, 5 + ((iteration - 8) * 5.5))
        
        await self.record_event("sensor_reading", {
            "sensor": "distance_01",
            "distance_cm": round(self.distance, 1),
            "safe": self.distance > 10
        })
        
        print(f"  [{iteration}] Distance: {self.distance:5.1f}cm ", end="")
    
    async def check_reflex(self):
        """Check and trigger reflexes based on sensor readings."""
        old_state = self.movement_state
        
        # Reflex: If too close, stop
        if self.distance < 10 and self.movement_state != "STOPPED":
            await self.record_event("reflex_triggered", {
                "reflex": "proximity_safeguard",
                "condition": "distance < 10cm",
                "action": "STOP"
            })
            self.movement_state = "STOPPED"
            print("-> REFLEX TRIGGERED (too close!) -> STOP")
        
        # Reflex: If safe and stopped, can move again
        elif self.distance > 15 and self.movement_state == "STOPPED":
            await self.record_event("reflex_triggered", {
                "reflex": "clear_to_move",
                "condition": "distance > 15cm",
                "action": "RESUME"
            })
            self.movement_state = "MOVING"
            print("-> REFLEX CLEARED (safe now) -> RESUME")
        
        else:
            print(f"(state: {self.movement_state})")
        
        # Record any state change as actuator action
        if old_state != self.movement_state:
            await self.record_event("actuator_action", {
                "actuator": "movement_01",
                "old_state": old_state,
                "new_state": self.movement_state
            })
    
    async def run(self):
        """Run the nervous system demo."""
        print("\n" + "="*70)
        print(" ANSE NERVOUS SYSTEM DEMO - Real Event-Driven Architecture")
        print("="*70)
        print()
        print("Showing three nervous system phases:")
        print("  1. SENSOR PHASE: Distance sensor emits readings")
        print("  2. REFLEX PHASE: Proximity detector triggers when distance < 10cm")
        print("  3. ACTUATOR PHASE: Movement control responds (MOVING vs STOPPED)")
        print()
        print("All events recorded to ANSE world model and broadcast to GUI")
        print()
        print("-" * 70)
        
        await self.initialize()
        
        # Run 20 iterations of the nervous system
        print("\n[RUNNING] Nervous system simulation:\n")
        for iteration in range(20):
            # Phase 1: Sensor reads distance
            await self.sensor_reading(iteration)
            
            # Phase 2 & 3: Reflex checks condition and actuator responds
            await self.check_reflex()
            
            await asyncio.sleep(0.8)
        
        print("\n" + "-" * 70)
        print(f"\n[COMPLETE] Simulation finished")
        print(f"[STATS] Total events recorded: {self.events_recorded}")
        
        # Show some of the events recorded
        recent_events = self.world_model.get_recent(15)
        print(f"\n[WORLD MODEL] Last 15 events:")
        for i, event in enumerate(recent_events[-15:], 1):
            evt_type = event.get("type", "unknown")
            if evt_type == "sensor_reading":
                dist = event.get("distance_cm", "?")
                print(f"  {i:2}. Sensor reading: {dist}cm")
            elif evt_type == "reflex_triggered":
                reflex = event.get("reflex", "?")
                print(f"  {i:2}. Reflex triggered: {reflex}")
            elif evt_type == "actuator_action":
                new_state = event.get("new_state", "?")
                print(f"  {i:2}. Actuator action: state={new_state}")
        
        print("\n" + "="*70)
        print("SUCCESS: Nervous system works! Now open GUI to see real-time events.")
        print("="*70 + "\n")


async def main():
    demo = SimpleNervousSystemDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted")
        sys.exit(0)
