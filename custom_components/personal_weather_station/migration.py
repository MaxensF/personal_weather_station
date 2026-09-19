"""Renaming the entity IDs released up to 1.0.8.

Those IDs repeat the station name twice, because the integration suggested an
object ID that Home Assistant then prefixed with the device name again. New
stations get the shorter form; existing ones are only ever renamed when the user
asks for it from Repairs.
"""

import logging

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import (
    BINARY_KEYS,
    DOMAIN,
    FIXED_ENTITY_NAMES,
    SENSOR_KEY_MAP,
    SENSOR_LIST,
)
from .entity import build_object_id

_LOGGER = logging.getLogger(__name__)


def english_name(platform, key):
    """
    English name of an entity, from its platform and key.

    Args:
        platform: "sensor", "number" or "button".
        key: Entity key, lowercase.

    Returns:
        str or None when the key is not one we still support.
    """

    fixed = FIXED_ENTITY_NAMES.get(platform, {}).get(key)

    if fixed is not None:
        return fixed

    canonical = SENSOR_KEY_MAP.get(key)

    return SENSOR_LIST[canonical]["name"] if canonical else None


def async_find_legacy_entities(hass, entry):
    """
    List the entities whose ID still repeats the station name.

    Args:
        hass: Home Assistant instance.
        entry: Config entry owning the devices.

    An entity counts as legacy when its object ID still starts with the station
    name twice *and* the shorter form would actually differ. The second check
    matters for a station whose own name opens the sensor name, such as a
    station called "wind" owning "wind_wind_direction".

    Returns:
        list: (old_entity_id, suggested_new_entity_id) pairs, sorted. The
            suggestion is indicative: collisions are resolved at rename time.
    """

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    renames = []

    for device_entry in dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    ):
        device_id = next(
            (
                identifier[1]
                for identifier in device_entry.identifiers
                if identifier[0] == DOMAIN
            ),
            None,
        )

        if device_id is None:
            continue

        prefix = f"{DOMAIN}_{device_id}_".lower()
        doubled = f"{slugify(device_id)}_{slugify(device_id)}_"

        for registry_entry in er.async_entries_for_device(
            entity_registry, device_entry.id, include_disabled_entities=True
        ):
            if registry_entry.platform != DOMAIN:
                continue

            if not registry_entry.entity_id.partition(".")[2].startswith(doubled):
                continue

            unique_id = registry_entry.unique_id.lower()

            if not unique_id.startswith(prefix):
                continue

            name = english_name(registry_entry.domain, unique_id[len(prefix) :])

            if name is None:
                continue

            new_entity_id = (
                f"{registry_entry.domain}.{build_object_id(device_id, name)}"
            )

            if new_entity_id != registry_entry.entity_id:
                renames.append((registry_entry.entity_id, new_entity_id))

    return sorted(renames)


def async_migrate_entity_ids(hass, entry):
    """
    Rename the legacy entity IDs to their shorter form.

    History and long term statistics follow a rename: the recorder listens for
    it and updates both. Automations, scripts and dashboards do not, which is
    why this is never done without the user asking.

    Args:
        hass: Home Assistant instance.
        entry: Config entry owning the devices.

    Returns:
        list: (old_entity_id, new_entity_id) pairs actually renamed.
    """

    entity_registry = er.async_get(hass)
    renamed = []

    for old_entity_id, suggested in async_find_legacy_entities(hass, entry):
        domain, _, object_id = suggested.partition(".")

        # Two payload keys can share an English name, "tempf" and "t1tem" both
        # being an outdoor temperature. Letting the registry pick a free ID
        # gives the same "_2" suffix a fresh installation would have produced.
        new_entity_id = entity_registry.async_generate_entity_id(domain, object_id)

        try:
            entity_registry.async_update_entity(
                old_entity_id, new_entity_id=new_entity_id
            )
        except ValueError:
            _LOGGER.warning(
                "Could not rename %s to %s", old_entity_id, new_entity_id
            )
            continue

        renamed.append((old_entity_id, new_entity_id))

    runtime = hass.data.get(DOMAIN)

    if runtime is not None:
        for device in runtime.devices.values():
            device.legacy_entity_ids = False

    return renamed


def async_find_status_sensors(hass, entry):
    """
    List connection and leak keys still registered as numeric sensors.

    Args:
        hass: Home Assistant instance.
        entry: Config entry owning the devices.

    Returns:
        list: entity IDs, sorted.
    """

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    found = []

    for device_entry in dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    ):
        device_id = next(
            (
                identifier[1]
                for identifier in device_entry.identifiers
                if identifier[0] == DOMAIN
            ),
            None,
        )

        if device_id is None:
            continue

        prefix = f"{DOMAIN}_{device_id}_".lower()

        for registry_entry in er.async_entries_for_device(
            entity_registry, device_entry.id, include_disabled_entities=True
        ):
            if registry_entry.platform != DOMAIN or registry_entry.domain != "sensor":
                continue

            unique_id = registry_entry.unique_id.lower()

            if not unique_id.startswith(prefix):
                continue

            if SENSOR_KEY_MAP.get(unique_id[len(prefix) :]) in BINARY_KEYS:
                found.append(registry_entry.entity_id)

    return sorted(found)


def async_migrate_status_sensors(hass, entry):
    """
    Drop the numeric connection and leak sensors.

    A platform change cannot be a rename, so the entities are removed and the
    binary sensors are built from scratch. These keys carry no state class, so
    no long term statistics are lost, only the raw recorder history.

    Args:
        hass: Home Assistant instance.
        entry: Config entry owning the devices.

    Returns:
        list: entity IDs that were removed.
    """

    entity_registry = er.async_get(hass)
    removed = async_find_status_sensors(hass, entry)

    for entity_id in removed:
        entity_registry.async_remove(entity_id)

    runtime = hass.data.get(DOMAIN)

    if runtime is not None:
        for device in runtime.devices.values():
            device.legacy_status_sensors = False

    return removed
