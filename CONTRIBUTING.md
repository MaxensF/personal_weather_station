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
- If the sensor is a wind direction, add `"wind_offset": True` so the north calibration applies to it.

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

## Documentation

The readme exists in two languages, linked to each other by the flag index at the
top: [`readme.md`](readme.md) in English and
[`docs/readme.fr.md`](docs/readme.fr.md) in French. **A change to one belongs in
the other**, or the flag stops meaning what it says. English is the reference.

## Translations

Every user-visible string lives in `custom_components/personal_weather_station/strings.json`,
which is the single source of truth. **Never edit `translations/*.json` by hand:**
they are generated.

- Sensor names come from `SENSOR_LIST`. After adding a sensor, run:

  ```bash
  python scripts/build_translations.py strings
  ```

  This regenerates the English names in `strings.json` and `translations/en.json`.

- Other languages are expanded from a phrase book in `scripts/phrasebooks/<lang>.json`,
  which holds only the distinct phrases: the seven channels of a multi-channel
  sensor share the same wording, so it is translated once. To improve or add a
  language, edit its phrase book, then run:

  ```bash
  python scripts/build_translations.py build
  python scripts/build_translations.py check
  ```

- `check` verifies that every language has exactly the keys of the English source
  and that no `{placeholder}` was lost. It runs in CI, together with the tests.

To start a new language, use the template printed by
`python scripts/build_translations.py phrases`.

### Which languages have been reviewed

Every phrase book carries a `quality` field. **Only these have been written and
reviewed with care:**

`de`, `en-GB`, `es`, `fr`, `it`, `nl`, `pt-BR`, `pt`

All other languages are complete — every string, the setup wizard and the repairs
included — but were written in one pass and are marked `"quality": "seeded"`:
nobody has proofread them. **If you
speak one of them, corrections are very welcome** — fix the phrase book, set
`"quality": "reviewed"`, run `build`, and open a pull request. `build` prints
which languages are still waiting for a review.

## Tests

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```

The suite drives a real Home Assistant instance. Two tests matter more than the
others when changing entities:

- `test_wslink.py::test_official_example_payload` replays the upload example from
  the vendor's own API document, empty values included.
- `test_translations.py::test_entity_ids_match_release_1_0_8` makes sure an
  upgrade never renames an entity someone already put on a dashboard.

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
