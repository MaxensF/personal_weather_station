"""The Weather Underground protocol, in its imperial units."""

from datetime import timedelta

import pytest
from homeassistant.util import dt as dt_util

from .conftest import WU_ENDPOINT, state_of

DEVICE_ID = "my_station"


async def test_imperial_payload_is_converted_by_home_assistant(hass, setup_pws):
    """
    Weather Underground is an imperial protocol.

    The integration stores what it receives and lets Home Assistant convert,
    which only works if every key carries the right unit. A metric system, as
    used here, is where a wrong unit would show up.
    """

    _, client = await setup_pws()

    response = await client.get(
        f"{WU_ENDPOINT}?ID={DEVICE_ID}&PASSWORD=&tempf=72&humidity=55"
        "&winddir=180&windspeedmph=4.5&baromin=29.92&dailyrainin=0.1"
    )

    assert response.status == 200

    await hass.async_block_till_done()

    temperature = state_of(hass, DEVICE_ID, "tempf")
    assert temperature.attributes["unit_of_measurement"] == "°C"
    assert float(temperature.state) == pytest.approx(22.2, abs=0.1)

    pressure = state_of(hass, DEVICE_ID, "baromin")
    assert float(pressure.state) == pytest.approx(1013.2, abs=0.5)

    # Percentages and angles are unitless, so they come through untouched.
    assert state_of(hass, DEVICE_ID, "humidity").state == "55"
    assert float(state_of(hass, DEVICE_ID, "winddir").state) == 180


async def test_wslink_metric_payload_is_left_alone(hass, setup_pws):
    """WSLink is metric, so a metric system has nothing to convert."""

    _, client = await setup_pws()

    await client.get(
        f"/data/upload.php?wsid={DEVICE_ID}&t1tem=21.5&rbar=1008.8&t1ws=3.2"
    )
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"
    assert state_of(hass, DEVICE_ID, "t1tem").attributes["unit_of_measurement"] == "°C"
    assert state_of(hass, DEVICE_ID, "rbar").state == "1008.8"

    # Wind speed is the exception: Home Assistant shows km/h in metric, so a
    # correct m/s declaration is what makes this number right.
    wind = state_of(hass, DEVICE_ID, "t1ws")
    assert wind.attributes["unit_of_measurement"] == "km/h"
    assert float(wind.state) == pytest.approx(11.52, abs=0.01)


async def test_dateutc_is_used_as_last_seen(hass, setup_pws):
    """Weather Underground timestamps are UTC and drive the last contact time."""

    _, client = await setup_pws()

    # Relative to now, not a literal date: the integration ignores a station
    # clock more than a day out, so a hardcoded stamp passes on the day it is
    # written and fails every day after.
    moment = (dt_util.utcnow() - timedelta(hours=2)).replace(microsecond=0)
    stamp = moment.strftime("%Y-%m-%d %H:%M:%S")
    await client.get(f"{WU_ENDPOINT}?ID={DEVICE_ID}&tempf=72&dateutc={stamp}")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "last_update").state.startswith(
        moment.strftime("%Y-%m-%dT%H:%M:%S")
    )

    # And it is not mistaken for a sensor.
    assert state_of(hass, DEVICE_ID, "dateutc") is None


async def test_dateutc_now_falls_back_to_server_time(hass, setup_pws):
    """Some stations literally send "now"."""

    _, client = await setup_pws()

    await client.get(f"{WU_ENDPOINT}?ID={DEVICE_ID}&tempf=72&dateutc=now")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "last_update").state not in ("unknown", "")
