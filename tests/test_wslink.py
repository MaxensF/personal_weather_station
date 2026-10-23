"""The WSLink protocol, driven by the payload from the official API document."""

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"
STATION_KEY = "a123456789"


async def test_official_example_payload(hass, setup_pws, wslink_payload):
    """
    Replay the vendor's own upload example.

    It carries 111 parameters, two of which are sent with an empty value
    (t1feels and t1heat). Those used to raise inside the update loop, which
    aborted the request and lost every parameter that came after them.
    """

    _, client = await setup_pws(password=STATION_KEY)

    response = await client.get(f"{WSLINK_ENDPOINT}{wslink_payload}")

    assert response.status == 200

    body = await response.json()
    assert body["status"] == "ok"
    assert body["device"] == DEVICE_ID
    assert body["errors"] == 0

    await hass.async_block_till_done()

    # The empty ones exist but hold no value.
    assert state_of(hass, DEVICE_ID, "t1feels").state == STATE_UNKNOWN
    assert state_of(hass, DEVICE_ID, "t1heat").state == STATE_UNKNOWN

    # Everything sent after them still made it through.
    assert state_of(hass, DEVICE_ID, "t1dew").state == "33.9"
    assert state_of(hass, DEVICE_ID, "t1wbgt").state == "42.1"
    assert state_of(hass, DEVICE_ID, "t10co2").state == "400"
    assert state_of(hass, DEVICE_ID, "apiver").state == "1.0"

    # And the values from before them too.
    assert state_of(hass, DEVICE_ID, "t1tem").state == "38"
    assert state_of(hass, DEVICE_ID, "rbar").state == "1008.8"


async def test_battery_scales(hass, setup_pws, wslink_payload):
    """Binary batteries and 0-5 batteries both end up as a percentage."""

    _, client = await setup_pws(password=STATION_KEY)
    await client.get(f"{WSLINK_ENDPOINT}{wslink_payload}")
    await hass.async_block_till_done()

    # "Normal=1, Low battery=0", as a plain on/off: on means the battery is fine.
    assert state_of(hass, DEVICE_ID, "t1bat", "binary_sensor").state == "on"
    assert state_of(hass, DEVICE_ID, "t6c1bat", "binary_sensor").state == "off"

    # The document's example sends 2 here, outside its own documented range.
    # Only 1 counts as normal.
    assert state_of(hass, DEVICE_ID, "t234c2bat", "binary_sensor").state == "off"

    # "0~5, remark: 5 is full" — reported as the middle of the band each level
    # stands for, so the lowest one does not claim the battery is flat.
    assert state_of(hass, DEVICE_ID, "t11bat").state == "95"
    assert state_of(hass, DEVICE_ID, "t8bat").state == "5"


async def test_unknown_parameters_are_ignored(hass, setup_pws):
    """An unsupported key is skipped without failing the request."""

    _, client = await setup_pws()

    response = await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5&notasensor=42"
    )

    assert response.status == 200
    assert (await response.json())["updated"] == 1

    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"
    assert state_of(hass, DEVICE_ID, "notasensor") is None


async def test_partial_payloads_add_entities_over_time(hass, setup_pws):
    """Entities appear as new keys turn up, request after request."""

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1hum") is None

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=22&t1hum=64")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "22"
    assert state_of(hass, DEVICE_ID, "t1hum").state == "64"


async def test_case_insensitive_keys(hass, setup_pws):
    """Stations are not consistent about the case of their parameters."""

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?WSID={DEVICE_ID}&T1TEM=21.5")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"


async def test_last_update_sensor_is_created(hass, setup_pws):
    """Every station gets a diagnostic telling when it last reported."""

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    last_update = state_of(hass, DEVICE_ID, "last_update")

    assert last_update is not None
    assert last_update.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)


async def test_stale_station_clock_falls_back_to_server_time(
    hass, setup_pws, wslink_payload
):
    """
    The vendor example is dated 2000-01-01.

    A station clock that far off would immediately mark everything offline, so
    it is ignored in favour of the server time.
    """

    _, client = await setup_pws(password=STATION_KEY)
    await client.get(f"{WSLINK_ENDPOINT}{wslink_payload}")
    await hass.async_block_till_done()

    assert not state_of(hass, DEVICE_ID, "last_update").state.startswith("2000")
    assert state_of(hass, DEVICE_ID, "t1tem").state == "38"


async def test_several_stations_share_one_config_entry(hass, setup_pws):
    """
    Nothing limits how many stations post to the integration.

    A single config entry is deliberate — there is one HTTP endpoint and one
    station key — but every station that posts gets its own device and its own
    sensors under it.
    """

    entry, client = await setup_pws(password=STATION_KEY)

    for station, temperature in (("jardin", 12.4), ("serre", 27.1), ("cave", 9.8)):
        response = await client.get(
            f"{WSLINK_ENDPOINT}?wsid={station}&wspw={STATION_KEY}"
            f"&t1tem={temperature}&t1hum=60"
        )
        assert response.status == 200

    await hass.async_block_till_done()

    from homeassistant.helpers import device_registry as dr

    from custom_components.personal_weather_station.const import DOMAIN

    devices = {
        identifier[1]
        for device in dr.async_entries_for_config_entry(
            dr.async_get(hass), entry.entry_id
        )
        for identifier in device.identifiers
        if identifier[0] == DOMAIN
    }
    assert devices == {"jardin", "serre", "cave"}

    # Each keeps its own readings.
    assert state_of(hass, "jardin", "t1tem").state == "12.4"
    assert state_of(hass, "serre", "t1tem").state == "27.1"
    assert state_of(hass, "cave", "t1tem").state == "9.8"

    # And its own north calibration, stored per station.
    await client.get(f"{WSLINK_ENDPOINT}?wsid=jardin&wspw={STATION_KEY}&t1wdir=237")
    await client.get(f"{WSLINK_ENDPOINT}?wsid=serre&wspw={STATION_KEY}&t1wdir=90")
    await hass.async_block_till_done()

    assert state_of(hass, "jardin", "wind_offset", "number") is not None
    assert state_of(hass, "serre", "wind_offset", "number") is not None


async def test_unknown_parameters_are_reported(hass, setup_pws):
    """
    Dropping a reading in silence is how issue #29 upstream went unsolved.

    A Bresser with more extra sensors than Weather Underground has slots loses
    the surplus without a word. Naming the parameters makes it reportable.
    """

    from homeassistant.helpers import issue_registry as ir

    from custom_components.personal_weather_station.const import (
        DOMAIN,
        ISSUE_UNKNOWN_PARAMETERS,
    )

    _, client = await setup_pws()

    await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5&soilmoisture5=30&temp6f=68"
    )
    await hass.async_block_till_done()

    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"{ISSUE_UNKNOWN_PARAMETERS}_{DEVICE_ID}"
    )
    assert issue is not None
    assert issue.translation_placeholders["count"] == "2"
    assert issue.translation_placeholders["parameters"] == "`soilmoisture5`, `temp6f`"
    assert issue.translation_placeholders["station"] == DEVICE_ID

    # The known reading still went through.
    assert state_of(hass, DEVICE_ID, "t1tem").state == "21.5"


async def test_unknown_parameters_reported_once(hass, setup_pws):
    """The station repeats them every minute; the repair must not churn."""

    from homeassistant.helpers import issue_registry as ir

    from custom_components.personal_weather_station.const import (
        DOMAIN,
        ISSUE_UNKNOWN_PARAMETERS,
    )

    _, client = await setup_pws()

    for _ in range(3):
        await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5&nope=1")
    await hass.async_block_till_done()

    issues = [i for (d, _), i in ir.async_get(hass).issues.items() if d == DOMAIN]
    unknown = [i for i in issues if i.translation_key == ISSUE_UNKNOWN_PARAMETERS]
    assert len(unknown) == 1
    assert unknown[0].translation_placeholders["count"] == "1"
