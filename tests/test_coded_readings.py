"""Readings the station sends as a code or on a scale of its own.

A number with no unit is a number nobody can read. A battery at 0 could be
empty or fine; a VOC level of 3 says neither how far the scale goes nor which
end of it is the bad one. These are the sensors where the value alone is not
the whole reading.
"""

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import PERCENTAGE

from custom_components.personal_weather_station.const import SENSOR_LIST, VOC_LEVELS

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"


def test_every_battery_declares_a_percentage():
    """
    Home Assistant requires `%` for `device_class: battery`, and without it a
    battery renders as a bare number and the core logs a warning. The readings
    are already normalised to 0-100 by `normalize_battery`, so the unit is
    what was missing, not the value.
    """

    batteries = [
        key
        for key, meta in SENSOR_LIST.items()
        if meta.get("device_class") is SensorDeviceClass.BATTERY
    ]

    assert batteries, "expected the battery sensors to still exist"

    for key in batteries:
        assert SENSOR_LIST[key]["unit"] == PERCENTAGE, key


def test_aqi_uses_the_home_assistant_device_class():
    """AQI is a standard index; it does not need a scale spelled out."""

    for key in ("t8pm25ai", "t8pm10ai"):
        assert SENSOR_LIST[key]["device_class"] is SensorDeviceClass.AQI


async def test_battery_reads_as_a_percentage(hass, setup_pws):
    """A 0~5 battery at 2 is 40%, and says so."""

    _, client = await setup_pws()

    # t8bat is one of the 0~5 batteries; t1bat one of the Normal/Low pair.
    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t8bat=2&t1bat=0")
    await hass.async_block_till_done()

    state = state_of(hass, DEVICE_ID, "t8bat")
    assert state.state == "40"
    assert state.attributes["unit_of_measurement"] == PERCENTAGE

    # The Normal/Low one is a binary sensor: 0 is a low battery, so it is off.
    assert state_of(hass, DEVICE_ID, "t1bat") is None
    assert state_of(hass, DEVICE_ID, "t1bat", "binary_sensor").state == "off"


async def test_voc_level_reads_as_a_named_state(hass, setup_pws):
    """
    The API numbers this one `1~5` with **1 the highest** VOC concentration.
    A bare 3 is unreadable and "3 / 5" reads backwards, so the states are
    named — and the naming has to follow the API's direction, not the
    intuition that a bigger number is worse.
    """

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t9voclv=1")
    await hass.async_block_till_done()
    assert state_of(hass, DEVICE_ID, "t9voclv").state == "very_high"

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t9voclv=5")
    await hass.async_block_till_done()
    state = state_of(hass, DEVICE_ID, "t9voclv")
    assert state.state == "very_low"
    assert state.attributes["device_class"] == SensorDeviceClass.ENUM
    assert set(state.attributes["options"]) == set(VOC_LEVELS.values())


async def test_an_undocumented_voc_code_is_not_invented(hass, setup_pws):
    """
    A code outside `1~5` becomes unknown. Home Assistant rejects an enum state
    that is not in `options`, and guessing one would be worse than admitting
    the reading means nothing to us.
    """

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t9voclv=9")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t9voclv").state == "unknown"
