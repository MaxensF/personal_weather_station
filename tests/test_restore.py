"""Entities and values surviving a restart."""

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"


async def test_entities_come_back_after_a_reload(hass, setup_pws):
    """
    Without this, every entity sits unavailable until the station posts again.

    Depending on the configured upload interval that can be several minutes of
    a dashboard full of holes after each restart.
    """

    entry, client = await setup_pws()

    await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5&t1hum=64&t1wdir=237"
    )
    await hass.async_block_till_done()

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    for key, expected in (("t1tem", "21.5"), ("t1hum", "64")):
        state = state_of(hass, DEVICE_ID, key)
        assert state is not None, f"{key} was not recreated"
        assert state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
        assert state.state == expected

    # The calibration entities come back too.
    assert state_of(hass, DEVICE_ID, "wind_offset", "number") is not None
    assert state_of(hass, DEVICE_ID, "set_north", "button") is not None
    assert state_of(hass, DEVICE_ID, "last_update").state != STATE_UNKNOWN


async def test_reload_does_not_duplicate_entities(hass, setup_pws):
    """Rebuilding from the registry must not create a second set."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5&t1wdir=237")
    await hass.async_block_till_done()

    before = len(hass.states.async_entity_ids())

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=22&t1wdir=240")
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids()) == before
    assert state_of(hass, DEVICE_ID, "t1tem").state == "22"


async def test_payload_after_reload_still_works(hass, setup_pws):
    """The endpoint keeps serving across a reload, with the current options."""

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=23.5")

    assert response.status == 200

    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "23.5"
