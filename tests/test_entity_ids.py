"""Entity ID naming, and the opt-in migration off the pre-1.1 form."""

import json
import pathlib

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.personal_weather_station.const import (
    DOMAIN,
    ISSUE_LEGACY_ENTITY_IDS,
)
from custom_components.personal_weather_station.migration import (
    async_find_legacy_entities,
)
from custom_components.personal_weather_station.repairs import async_create_fix_flow

from .conftest import WU_ENDPOINT, state_of

DEVICE_ID = "my_station"

# unique_id -> entity_id exactly as release 1.0.8 registered them.
LEGACY_PAIRS = json.loads(
    pathlib.Path("tests/legacy_entity_ids_v1_0_8.json").read_text(encoding="utf-8")
)

PAYLOAD = (
    f"?ID={DEVICE_ID}&tempf=72&humidity=55&winddir=180&windgustdir=200"
    "&winddir_avg2m=170&windgustdir_10m=190&baromin=29.9&dailyrainin=0.1"
    "&soilmoisture=30&t1tem=21.5&t1hum=64&t1wdir=237&t1ws=3.2&rbar=1008.8"
    "&intem=20.1&inbat=1&t1bat=1&t1cn=1&t234c1tem=18&t234c1bat=1&t6c1wls=0"
    "&t8pm25=12&t10co2=400&AqPM2.5=11&AqOZONE=30&rtfreq=16&apiver=1.00"
)


def seed_legacy_registry(hass, entry):
    """Recreate what an installation upgrading from 1.0.8 looks like."""

    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, DEVICE_ID)},
        name=DEVICE_ID,
    )
    entity_registry = er.async_get(hass)

    for unique_id, entity_id in LEGACY_PAIRS.items():
        domain, _, object_id = entity_id.partition(".")
        entity_registry.async_get_or_create(
            domain,
            DOMAIN,
            unique_id,
            suggested_object_id=object_id,
            config_entry=entry,
            device_id=device.id,
        )

    return device


async def test_new_station_gets_short_entity_ids(hass, setup_pws):
    """A station seen for the first time has nothing to preserve."""

    _, client = await setup_pws()

    await client.get(f"{WU_ENDPOINT}{PAYLOAD}")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "tempf").entity_id == (
        "sensor.my_station_outdoor_temperature"
    )
    assert state_of(hass, DEVICE_ID, "wind_offset", "number").entity_id == (
        "number.my_station_wind_direction_offset"
    )

    doubled = [
        entity_id
        for entity_id in hass.states.async_entity_ids()
        if "my_station_my_station" in entity_id
    ]
    assert not doubled


async def test_existing_station_keeps_its_entity_ids(hass, setup_pws):
    """
    The whole point: upgrading must not rename anything.

    Every ID release 1.0.8 handed out has to still be there afterwards.
    """

    _, client = await setup_pws(seed=seed_legacy_registry)

    await client.get(f"{WU_ENDPOINT}{PAYLOAD}")
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    for unique_id, entity_id in LEGACY_PAIRS.items():
        found = entity_registry.async_get_entity_id(
            entity_id.partition(".")[0], DOMAIN, unique_id
        )
        assert found == entity_id, f"{unique_id} moved to {found}"


async def test_new_sensor_on_a_legacy_station_stays_legacy(hass, setup_pws):
    """One station must not end up with two naming styles."""

    _, client = await setup_pws(seed=seed_legacy_registry)

    await client.get(f"{WU_ENDPOINT}{PAYLOAD}&dewptf=55")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "dewptf").entity_id == (
        "sensor.my_station_my_station_dew_point"
    )


async def test_repair_only_for_legacy_stations(hass, setup_pws):
    """A fresh installation has nothing to fix."""

    from homeassistant.helpers import issue_registry as ir

    await setup_pws()

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_ENTITY_IDS) is None


async def test_repair_raised_and_migration_applied(hass, setup_pws):
    """The rename happens only when the user goes through the repair."""

    from homeassistant.helpers import issue_registry as ir

    entry, _ = await setup_pws(seed=seed_legacy_registry)

    issue = ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_ENTITY_IDS)
    assert issue is not None
    assert issue.is_fixable
    assert issue.translation_placeholders["count"] == str(len(LEGACY_PAIRS))

    flow = await async_create_fix_flow(
        hass, ISSUE_LEGACY_ENTITY_IDS, {"entry_id": entry.entry_id}
    )
    flow.hass = hass

    form = await flow.async_step_confirm()
    assert form["type"] == "form"
    assert form["description_placeholders"]["count"] == str(len(LEGACY_PAIRS))

    assert (await flow.async_step_confirm({}))["type"] == "create_entry"
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    for unique_id, old_entity_id in LEGACY_PAIRS.items():
        new_entity_id = entity_registry.async_get_entity_id(
            old_entity_id.partition(".")[0], DOMAIN, unique_id
        )
        assert "my_station_my_station" not in new_entity_id
        assert new_entity_id.startswith(f"{old_entity_id.partition('.')[0]}.my_station_")

    assert async_find_legacy_entities(hass, entry) == []
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_LEGACY_ENTITY_IDS) is None


async def test_sensors_added_after_migration_are_short(hass, setup_pws):
    """Once migrated, the station must not fall back to the old naming."""

    entry, client = await setup_pws(seed=seed_legacy_registry)

    flow = await async_create_fix_flow(
        hass, ISSUE_LEGACY_ENTITY_IDS, {"entry_id": entry.entry_id}
    )
    flow.hass = hass
    await flow.async_step_confirm()
    await flow.async_step_confirm({})
    await hass.async_block_till_done()

    await client.get(f"{WU_ENDPOINT}?ID={DEVICE_ID}&dewptf=55")
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "dewptf").entity_id == (
        "sensor.my_station_dew_point"
    )
