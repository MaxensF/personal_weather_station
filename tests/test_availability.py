"""Marking a silent station unavailable."""

from datetime import timedelta

from homeassistant.const import STATE_UNAVAILABLE
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.personal_weather_station.const import (
    CONF_AVAILABILITY_TIMEOUT,
)

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"


async def test_silent_station_becomes_unavailable(hass, setup_pws, freezer):
    """
    A dead station used to keep showing its last reading forever.

    That is the kind of thing an automation quietly trusts.
    """

    _, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 15})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"

    freezer.tick(timedelta(minutes=20))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == STATE_UNAVAILABLE

    # The diagnostic stays readable: it is exactly when a station goes quiet
    # that you want to know for how long.
    assert state_of(hass, DEVICE_ID, "last_update").state != STATE_UNAVAILABLE


async def test_station_recovers_on_the_next_payload(hass, setup_pws, freezer):
    _, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 15})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    freezer.tick(timedelta(minutes=20))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == STATE_UNAVAILABLE

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=19.5")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "19.5"


async def test_timeout_zero_disables_the_check(hass, setup_pws, freezer):
    """Some stations report rarely on purpose."""

    _, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 0})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    freezer.tick(timedelta(days=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"


async def test_calibration_entities_stay_available(hass, setup_pws, freezer):
    """Resetting a calibration has to stay possible on an offline station."""

    _, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 15})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237")
    await hass.async_block_till_done()

    freezer.tick(timedelta(minutes=20))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert (
        state_of(hass, DEVICE_ID, "wind_offset", "number").state != STATE_UNAVAILABLE
    )
    assert (
        state_of(hass, DEVICE_ID, "set_north", "button").state != STATE_UNAVAILABLE
    )
