"""Connection and water leak readings as binary sensors."""


from datetime import timedelta

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.personal_weather_station.const import (
    BINARY_KEYS,
    CONF_AVAILABILITY_TIMEOUT,
    DOMAIN,
    ISSUE_LEGACY_STATUS_SENSORS,
    KEY_STATION_ONLINE,
    SENSOR_LIST,
)
from custom_components.personal_weather_station.migration import (
    async_find_status_sensors,
)
from custom_components.personal_weather_station.repairs import async_create_fix_flow

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"
PAYLOAD = f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1cn=1&t6c1wls=0&t1bat=1&t1tem=21.5"

# The numeric sensors an installation upgrading from 1.0.8 already has.
LEGACY_STATUS = {
    f"{DOMAIN}_{DEVICE_ID}_t1cn": "sensor.legacy_outdoor_sensor_connection_status",
    f"{DOMAIN}_{DEVICE_ID}_t6c1wls": "sensor.legacy_ch1_water_leak_status",
}


def seed_numeric_status(hass, entry):
    """Recreate the numeric connection and leak sensors of an older release."""

    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, DEVICE_ID)},
        name=DEVICE_ID,
    )
    entity_registry = er.async_get(hass)

    for unique_id, entity_id in LEGACY_STATUS.items():
        entity_registry.async_get_or_create(
            "sensor",
            DOMAIN,
            unique_id,
            suggested_object_id=entity_id.partition(".")[2],
            config_entry=entry,
            device_id=device.id,
        )


def test_which_keys_are_binary():
    """
    Connection, leak, and the Normal/Low batteries.

    The 0~5 batteries stay numeric: they carry six levels, which a percentage
    can express and an on/off cannot.
    """

    assert len(BINARY_KEYS) == 44

    for key in BINARY_KEYS:
        assert key.endswith(("cn", "wls", "bat")), key

    graded = [
        key for key, meta in SENSOR_LIST.items() if meta.get("battery_scale") == 5
    ]
    assert sorted(graded) == ["t10bat", "t11bat", "t8bat", "t9bat"]

    for key in graded:
        assert not SENSOR_LIST[key].get("binary"), key


async def test_new_station_gets_binary_sensors(hass, setup_pws):
    """A leak detector has to read Wet/Dry, not 1/0."""

    _, client = await setup_pws()

    await client.get(PAYLOAD)
    await hass.async_block_till_done()

    leak = state_of(hass, DEVICE_ID, "t6c1wls", "binary_sensor")
    assert leak.state == STATE_OFF
    assert leak.attributes["device_class"] == "moisture"

    connection = state_of(hass, DEVICE_ID, "t1cn", "binary_sensor")
    assert connection.state == STATE_ON
    assert connection.attributes["device_class"] == "connectivity"

    # And they are no longer numbers.
    assert state_of(hass, DEVICE_ID, "t6c1wls") is None
    assert state_of(hass, DEVICE_ID, "t1cn") is None


async def test_a_battery_reads_on_when_it_is_fine(hass, setup_pws):
    """
    The station reports Normal=1, Low=0, and the sensor follows that directly.

    Deliberately no battery device class: that one renders as Normal / Low,
    which says nothing useful about a console sitting on mains power. Plain
    on/off, with on meaning the battery is fine.
    """

    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1bat=1&t234c1bat=0")
    await hass.async_block_till_done()

    healthy = state_of(hass, DEVICE_ID, "t1bat", "binary_sensor")
    assert healthy.state == STATE_ON
    assert "device_class" not in healthy.attributes

    assert state_of(hass, DEVICE_ID, "t234c1bat", "binary_sensor").state == STATE_OFF

    # No numeric leftover alongside it.
    assert state_of(hass, DEVICE_ID, "t1bat") is None


async def test_a_leak_turns_the_sensor_on(hass, setup_pws):
    _, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t6c1wls=1")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t6c1wls", "binary_sensor").state == STATE_ON


async def test_existing_station_keeps_its_numeric_sensors(hass, setup_pws):
    """Upgrading must not silently drop entities someone points at."""

    _, client = await setup_pws(seed=seed_numeric_status)

    await client.get(PAYLOAD)
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t6c1wls").state == "0"
    assert state_of(hass, DEVICE_ID, "t1cn").state == "1"
    assert state_of(hass, DEVICE_ID, "t6c1wls", "binary_sensor") is None


async def test_new_status_key_on_a_legacy_station_stays_numeric(hass, setup_pws):
    """One station must not mix both representations."""

    _, client = await setup_pws(seed=seed_numeric_status)

    await client.get(f"{PAYLOAD}&t5lscn=1")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t5lscn").state == "1"
    assert state_of(hass, DEVICE_ID, "t5lscn", "binary_sensor") is None


async def test_no_repair_for_a_fresh_install(hass, setup_pws):
    _, client = await setup_pws()

    await client.get(PAYLOAD)
    await hass.async_block_till_done()

    assert (
        ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_STATUS_SENSORS) is None
    )


async def test_repair_converts_on_confirmation(hass, setup_pws):
    """The conversion happens only when the user asks for it."""

    entry, client = await setup_pws(seed=seed_numeric_status)

    issue = ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_STATUS_SENSORS)
    assert issue is not None
    assert issue.is_fixable
    assert issue.translation_placeholders["count"] == "2"

    flow = await async_create_fix_flow(
        hass, ISSUE_LEGACY_STATUS_SENSORS, {"entry_id": entry.entry_id}
    )
    flow.hass = hass

    form = await flow.async_step_confirm()
    assert form["type"] == "form"
    assert form["description_placeholders"]["count"] == "2"

    assert (await flow.async_step_confirm({}))["type"] == "create_entry"
    await hass.async_block_till_done()

    # The numeric sensors are gone.
    entity_registry = er.async_get(hass)
    for unique_id in LEGACY_STATUS:
        assert entity_registry.async_get_entity_id("sensor", DOMAIN, unique_id) is None

    assert async_find_status_sensors(hass, entry) == []
    assert (
        ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_STATUS_SENSORS) is None
    )

    # And the binary sensors appear on the next upload.
    await client.get(PAYLOAD)
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t6c1wls", "binary_sensor").state == STATE_OFF
    assert state_of(hass, DEVICE_ID, "t1cn", "binary_sensor").state == STATE_ON


async def test_the_station_reports_its_own_silence(hass, setup_pws, freezer):
    """
    Every other connection status comes from the station itself.

    None of them covers the console, because the console is what does the
    posting: when it stops, nobody is left to say so. This one is derived from
    the availability timeout instead.
    """

    _, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 15})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    online = state_of(hass, DEVICE_ID, KEY_STATION_ONLINE, "binary_sensor")
    assert online.state == STATE_ON

    freezer.tick(timedelta(minutes=20))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    online = state_of(hass, DEVICE_ID, KEY_STATION_ONLINE, "binary_sensor")

    # Available, and saying the station is not: an entity that went unavailable
    # itself could not report the outage.
    assert online.state == STATE_OFF

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=22.0")
    await hass.async_block_till_done()

    assert (
        state_of(hass, DEVICE_ID, KEY_STATION_ONLINE, "binary_sensor").state
        == STATE_ON
    )
