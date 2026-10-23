"""Recalibrating true north on a station that was not oriented precisely."""

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.personal_weather_station.const import (
    CONF_WIND_OFFSETS,
    WIND_OFFSET_KEYS,
)

from .conftest import WSLINK_ENDPOINT, entity_id_for, state_of

DEVICE_ID = "wsabcde123"


async def press(hass, key):
    """Press one of the calibration buttons."""

    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": entity_id_for(hass, DEVICE_ID, key, "button")},
        blocking=True,
    )
    await hass.async_block_till_done()


async def test_calibration_entities_appear_with_a_wind_direction(hass, setup_pws):
    """Stations without an anemometer must not get calibration controls."""

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "wind_offset", "number") is None
    assert state_of(hass, DEVICE_ID, "wind_direction_raw") is None

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "wind_offset", "number") is not None
    assert state_of(hass, DEVICE_ID, "set_north", "button") is not None
    assert state_of(hass, DEVICE_ID, "reset_wind_offset", "button") is not None


async def test_set_north_from_current(hass, setup_pws):
    """Hold the vane at north, press, and that direction becomes zero."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()

    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 237
    assert float(state_of(hass, DEVICE_ID, "wind_offset", "number").state) == 0

    await press(hass, "set_north")

    assert entry.options[CONF_WIND_OFFSETS] == {DEVICE_ID: 123}
    assert float(state_of(hass, DEVICE_ID, "wind_offset", "number").state) == 123
    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 0

    # The raw reading is untouched, which is what makes a second calibration
    # replace the first instead of stacking on top of it.
    assert float(state_of(hass, DEVICE_ID, "wind_direction_raw").state) == 237


async def test_offset_applies_to_later_payloads(hass, setup_pws):
    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=257")
    await hass.async_block_till_done()

    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 20
    assert float(state_of(hass, DEVICE_ID, "wind_direction_raw").state) == 257


async def test_calibrating_twice_replaces_the_offset(hass, setup_pws):
    """The second calibration must not compound the first."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=100")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    assert entry.options[CONF_WIND_OFFSETS] == {DEVICE_ID: 260}
    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 0


async def test_reset_button(hass, setup_pws):
    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    await press(hass, "reset_wind_offset")

    assert entry.options.get(CONF_WIND_OFFSETS) == {}
    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 237


async def test_offset_applies_to_every_direction_key_only(hass, setup_pws):
    """All five direction keys rotate, and nothing else does."""

    _, client = await setup_pws()

    await client.get(
        f"/weatherstation/updateweatherstation.php?ID={DEVICE_ID}"
        "&winddir=100&windgustdir=100&winddir_avg2m=100&windgustdir_10m=100"
        "&windspeedmph=10&tempf=72"
    )
    await hass.async_block_till_done()

    await hass.services.async_call(
        "number",
        "set_value",
        {
            "entity_id": entity_id_for(hass, DEVICE_ID, "wind_offset", "number"),
            "value": 90,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    rotated = [key for key in WIND_OFFSET_KEYS if key.startswith("wind")]
    assert len(rotated) == 4

    for key in rotated:
        assert float(state_of(hass, DEVICE_ID, key).state) == 190, key

    # Speed and temperature are untouched (values shown converted to metric).
    assert float(state_of(hass, DEVICE_ID, "windspeedmph").state) == pytest.approx(
        16.09, abs=0.01
    )
    assert float(state_of(hass, DEVICE_ID, "tempf").state) == pytest.approx(
        22.2, abs=0.1
    )


async def test_set_north_without_a_reading_explains_itself(hass, setup_pws):
    """
    The button can only exist once a direction was received.

    Should the reading go away, pressing has to say why rather than silently
    calibrating against nothing.
    """

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()

    runtime = hass.data["personal_weather_station"]
    runtime.devices[DEVICE_ID].data.pop("t1wdir")

    with pytest.raises(ServiceValidationError) as err:
        await press(hass, "set_north")

    assert err.value.translation_key == "no_wind_direction"


async def test_offset_survives_a_reload(hass, setup_pws):
    """A calibration is configuration, not a restored state."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert float(state_of(hass, DEVICE_ID, "wind_offset", "number").state) == 123

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()

    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 0


async def test_options_flow_keeps_the_calibration(hass, setup_pws):
    """Saving the options form must not wipe the per station offsets."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()
    await press(hass, "set_north")

    result = await hass.config_entries.options.async_init(entry.entry_id)

    # The options open on a menu now: settings, or how to point a station here.
    assert result["type"] == "menu"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "options"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"password": "newkey", "availability_timeout": 30, "debug": False},
    )
    await hass.async_block_till_done()

    assert entry.options[CONF_WIND_OFFSETS] == {DEVICE_ID: 123}
    assert entry.options["password"] == "newkey"
    assert float(state_of(hass, DEVICE_ID, "t1wdir").state) == 0
