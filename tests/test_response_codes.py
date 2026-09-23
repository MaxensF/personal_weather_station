"""
The two response codes the API defines beyond success and authentication.

404 "Too many request" and 405 "Incorrect data format" are part of the vendor
specification. Neither should ever be seen by a healthy station, which is
exactly why they need tests: nothing in normal use would reveal a threshold set
wrong or a condition that fires too eagerly.
"""

import pytest

import custom_components.personal_weather_station as pws
from custom_components.personal_weather_station.const import RATE_LIMIT_REQUESTS

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"


async def test_a_normal_station_is_never_rate_limited(hass, setup_pws):
    """The limit has to sit far above anything a real station does."""

    _, client = await setup_pws()

    # The shortest upload interval these stations offer is 8 seconds, so a
    # station posting for a full minute sends at most 8 requests.
    for index in range(8):
        response = await client.get(
            f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem={20 + index}"
        )
        assert response.status == 200

    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "27"


async def test_a_looping_station_gets_404(hass, setup_pws):
    """Past the limit the request is dropped rather than recorded."""

    _, client = await setup_pws()

    for _ in range(RATE_LIMIT_REQUESTS):
        assert (
            await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=20")
        ).status == 200

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=99")

    assert response.status == 404
    assert (await response.json())["detail"] == "Too many requests"

    await hass.async_block_till_done()

    # The rejected payload left no trace.
    assert state_of(hass, DEVICE_ID, "t1tem").state == "20"


async def test_the_limit_is_per_station(hass, setup_pws):
    """One misbehaving station must not silence the others."""

    _, client = await setup_pws()

    for _ in range(RATE_LIMIT_REQUESTS + 1):
        await client.get(f"{WSLINK_ENDPOINT}?wsid=loud&t1tem=20")

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid=quiet&t1tem=21")

    assert response.status == 200


async def test_unreadable_payload_gets_405(hass, setup_pws, monkeypatch):
    """
    Recognised parameters that all fail to parse are a format problem.

    parse_value is deliberately total, so this condition is unreachable without
    forcing it. That is the point of the test: to pin the behaviour down now,
    for whatever future change makes it reachable again.
    """

    _, client = await setup_pws()

    def explode(_raw):
        raise ValueError("unreadable")

    monkeypatch.setattr(pws, "parse_value", explode)

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=20")

    assert response.status == 405
    assert (await response.json())["detail"] == "Incorrect data format"


async def test_a_partly_unreadable_payload_still_succeeds(
    hass, setup_pws, monkeypatch
):
    """One bad parameter must never cost the others their reading."""

    _, client = await setup_pws()

    original = pws.parse_value

    def explode_on_humidity(raw):
        if raw == "55":
            raise ValueError("unreadable")
        return original(raw)

    monkeypatch.setattr(pws, "parse_value", explode_on_humidity)

    response = await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1hum=55&t1tem=20"
    )

    assert response.status == 200

    body = await response.json()
    assert body["errors"] == 1
    assert body["updated"] == 1

    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "20"


@pytest.mark.parametrize("payload", ["apiver=8&futuresensor=42", "onlyunknown=1"])
async def test_unknown_parameters_are_not_a_format_error(hass, setup_pws, payload):
    """
    A station speaking a newer API version is not malformed.

    The document transcribed in the repository is version 0.6, and firmware in
    the field already announces a higher apiver. Answering 405 to a station
    whose only crime is being newer than our table would be wrong, and would
    make it look as though Home Assistant had rejected it.
    """

    _, client = await setup_pws()

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&{payload}")

    assert response.status == 200
