# Sensor Plugins

Sensor plugins that emit readings into the world model.

## Templates

- `_template_sensor.py` - Python template for building sensors
- `_template_sensor.yaml` - YAML configuration template

## Examples

Example sensor configurations for common hardware:

- `example_arduino_servo.yaml` - Arduino servo motor control
- `example_modbus_plc.yaml` - Modbus PLC integration
- `example_philips_hue.yaml` - Philips Hue smart lights

## Creating a Sensor

1. Copy `_template_sensor.py` and `_template_sensor.yaml`
2. Follow the EVENT-DRIVEN ARCHITECTURE section in the Python template
3. Register in your agent's plugin loader
4. Sensor will emit readings as world model events (not polling)

## Key Pattern

```python
async def emit_reading_event():
    reading = get_sensor_reading()
    await world_model.record(
        type="sensor_reading",
        sensor_id=self.id,
        value=reading,
        timestamp=time.time()
    )
```

See [EVENT_DRIVEN_ARCHITECTURE.md](../../docs/EVENT_DRIVEN_ARCHITECTURE.md) for how state and events flow.
