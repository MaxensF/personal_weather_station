"""
Keep the transcribed API document and the sensor table in step.

"WSLink API.md" is a transcription of the vendor specification, and a
transcription rots: a parameter gets added to const.py and never written down,
or worse, one is written down and never implemented. Parsing the document's own
tables here means the two cannot drift apart without the build saying so.
"""

import re
from pathlib import Path

from custom_components.personal_weather_station.const import SENSOR_LIST

DOCUMENT = Path(__file__).parent.parent / "WSLink API.md"

# Carried in the query string but never a reading: the credentials, and the
# timestamp, which feeds the station's last-seen rather than an entity.
NOT_SENSORS = {"wsid", "wspw", "datetime"}

# The unit column of the document, mapped to the fragment that has to appear in
# the Home Assistant unit constant for that key.
UNIT_HINTS = {
    "hPa": "hPa",
    "°C": "°C",
    "%": "%",
    "deg": "°",
    "m/s": "m/s",
    "mm/h": "mm/h",
    "mm": "mm",
    "W/m²": "W/m²",
    "km": "km",
    # Home Assistant spells this with the Greek mu (U+03BC), not the micro
    # sign (U+00B5). They render identically and compare unequal.
    "ug/m³": "μg/m³",
    "ppb": "ppb",
    "ppm": "ppm",
}

ROW = re.compile(r"^\| `&([a-z0-9]+)=` \| (.+?) \| (\w+) \| (.*?) \|$", re.MULTILINE)


def documented_parameters():
    """Every parameter row of the document, as (key, description, type, unit)."""

    return ROW.findall(DOCUMENT.read_text(encoding="utf-8"))


def test_document_parses():
    """A tableless or reformatted document must not silently pass everything."""

    rows = documented_parameters()

    assert len(rows) == 111, "the vendor document lists 111 parameters"


def test_every_documented_parameter_is_implemented():
    """Nothing the station can send may be dropped on the floor."""

    missing = [
        key
        for key, _, _, _ in documented_parameters()
        if key not in NOT_SENSORS and key not in SENSOR_LIST
    ]

    assert not missing, f"documented but not in SENSOR_LIST: {missing}"


def test_units_match_the_document():
    """A wrong unit is worse than none: it converts, and quietly lies."""

    wrong = []

    for key, _, _, unit in documented_parameters():
        if key in NOT_SENSORS or not unit:
            continue

        declared = SENSOR_LIST[key].get("unit")
        expected = UNIT_HINTS[unit]

        if declared is None or expected not in str(declared):
            wrong.append(f"{key}: document says {unit!r}, code says {declared!r}")

    assert not wrong, wrong


def test_battery_scales_match_the_document():
    """
    The two battery scales are easy to confuse and impossible to see.

    A "Normal=1, Low battery=0" reading scaled as if it ran to 5 reports a full
    battery as 20%, which looks like a flat one.
    """

    wrong = []

    for key, description, _, _ in documented_parameters():
        if not key.endswith("bat") or key in NOT_SENSORS:
            continue

        expected = 5 if "0~5" in description else 1
        declared = SENSOR_LIST[key].get("battery_scale")

        if declared != expected:
            wrong.append(f"{key}: document implies {expected}, code says {declared}")

    assert not wrong, wrong
