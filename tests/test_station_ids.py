"""Station identifiers users actually type.

Issue #7 upstream reported a station ID containing a hyphen failing to produce
an entity. These are the shapes a station app will happily let someone enter.
"""
import pytest
from homeassistant.core import valid_entity_id
from homeassistant.helpers import entity_registry as er

from custom_components.personal_weather_station.const import DOMAIN

from .conftest import WSLINK_ENDPOINT

CASES = ["my-station", "Ma Station", "station.1", "ÉTÉ", "123", "a",
         "my--station", "-lead", "trail-", "_under", "wsabcde123"]

@pytest.mark.parametrize("station", CASES)
async def test_awkward_station_id(hass, setup_pws, station):
    _, client = await setup_pws()
    resp = await client.get(f"{WSLINK_ENDPOINT}?wsid={station}&t1tem=21.5")
    assert resp.status == 200, await resp.text()
    await hass.async_block_till_done()

    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_{station}_t1tem".lower())
    assert eid is not None, f"aucune entité pour {station!r}"
    assert valid_entity_id(eid), f"entity_id invalide : {eid}"
    assert hass.states.get(eid).state == "21.5"
