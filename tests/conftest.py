"""Shared fixtures for the Personal Weather Station tests."""

import pathlib

import pytest
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.personal_weather_station.const import DOMAIN

WU_ENDPOINT = "/weatherstation/updateweatherstation.php"
WSLINK_ENDPOINT = "/data/upload.php"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let Home Assistant load the integration from custom_components."""

    yield


@pytest.fixture
def wslink_payload():
    """The upload example straight out of the WSLink API document."""

    return (
        pathlib.Path(__file__)
        .parent.joinpath("wslink_example_payload.txt")
        .read_text(encoding="utf-8")
        .strip()
    )


@pytest.fixture
async def setup_pws(hass, hass_client_no_auth):
    """Set up the integration and return the config entry and an HTTP client."""

    async def _setup(password=None, options=None, seed=None):
        assert await async_setup_component(hass, "http", {})

        entry = MockConfigEntry(
            domain=DOMAIN,
            title="Personal Weather Station",
            data={CONF_PASSWORD: password} if password else {},
            options=options or {},
        )
        entry.add_to_hass(hass)

        if seed is not None:
            # Populate the registries before setup, the way an upgrade from an
            # earlier release would have left them.
            seed(hass, entry)

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        return entry, await hass_client_no_auth()

    return _setup


def entity_id_for(hass, device_id, key, platform="sensor"):
    """Resolve an entity ID from the unique ID the integration builds."""

    return er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{DOMAIN}_{device_id}_{key}".lower()
    )


def device_for(hass, entry, device_id):
    """
    Look a station's device up by the identifier it announced.

    Goes through async_entries_for_config_entry rather than a registry lookup:
    async_get_device(identifiers=...) is deprecated and
    async_get_device_by_identifier only exists from 2026.9, so either one ties
    the suite to a narrow band of Home Assistant versions.
    """

    entries = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)

    for device in entries:
        if (DOMAIN, device_id) in device.identifiers:
            return device

    return None


def state_of(hass, device_id, key, platform="sensor"):
    """Return the state object of one entity, or None when it does not exist."""

    entity_id = entity_id_for(hass, device_id, key, platform)

    return hass.states.get(entity_id) if entity_id else None
