# Contributing

First of all, thank you for considering contributing to **Personal Weather Station**!

Whether you want to report a bug, add support for a new weather station, improve the documentation, or submit code, your help is greatly appreciated.

## Reporting issues

Before opening an issue:

- Search existing issues to avoid duplicates.
- Use the appropriate issue template.
- Include as much information as possible:
  - Home Assistant version
  - Integration version
  - Weather station model
  - Firmware version (if known)
  - Example HTTP request or WSLink payload
  - Debug logs (if applicable)

## Adding support for new sensors

Most sensors are defined in:

```
custom_components/personal_weather_station/const.py
```

When adding a new sensor:

- Use the appropriate Home Assistant `device_class` and `state_class`.
- Use the correct unit of measurement.
- Follow the existing naming conventions.
- If the sensor represents a battery level, add a `battery_scale` when the raw value is not already expressed as a percentage.
- If the reading is an on/off status reported as `1` / `0`, add `"binary": "<device class>"` (for example `connectivity` or `moisture`) and it is served by the `binary_sensor` platform instead. Battery levels are an exception and stay percentages.

Example:

```python
"t8bat": {
    "name": "PM Sensor Battery Level",
    "icon": "mdi:battery",
    "device_class": SensorDeviceClass.BATTERY,
    "state_class": SensorStateClass.MEASUREMENT,
    "precision": 0,
    "battery_scale": 5,
}
```

## Tests

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```

The suite drives a real Home Assistant instance. Two tests matter more than the
others when changing entities:

- `test_wslink.py::test_official_example_payload` replays the upload example from
  the vendor's own API document, empty values included.
- `test_entity_ids.py::test_existing_station_keeps_its_entity_ids` replays the
  entity IDs of release 1.0.8 so an upgrade never renames an entity someone
  already put on a dashboard.

## Code style

Please try to keep the code consistent with the rest of the project:

- Follow PEP 8.
- Keep functions small and readable.
- Add comments only when they improve understanding.
- Prefer configuration-driven logic over hardcoded special cases.
- Keep backward compatibility whenever possible.

## Pull requests

Before submitting a pull request:

- Make sure the integration still loads correctly.
- Test with a real weather station whenever possible.
- Update the documentation if new features or sensors are added.
- Keep pull requests focused on a single feature or fix.

## New weather station models

If you successfully tested the integration with a new weather station, feel free to submit a pull request updating the README.

Please include:

- Manufacturer
- Model number
- Firmware version (if available)
- Whether it uses Weather Underground or WSLink mode

## Questions

If you're unsure about an implementation or want to discuss a feature before coding it, feel free to open a GitHub Discussion or Issue first.

Thank you for helping improve this integration!
