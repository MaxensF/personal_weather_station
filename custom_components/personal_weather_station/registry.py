"""Rebuild entities from the registries so they survive a restart.

Entities are normally born when a payload mentions them. Without this, every
entity stays unavailable after a restart until the station posts again, which
can take minutes depending on the configured upload interval.
"""

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .const import BINARY_KEYS, DOMAIN, SENSOR_KEY_MAP


def uses_legacy_status_sensors(device_id, registry_entries):
    """
    Detect connection and leak keys still registered on the sensor platform.

    Args:
        device_id: Identifier announced by the station.
        registry_entries: Entity registry entries of that device.

    Returns:
        bool: True when at least one of them is still a numeric sensor.
    """

    prefix = f"{DOMAIN}_{device_id}_".lower()

    for entry in registry_entries:
        if entry.domain != "sensor":
            continue

        unique_id = entry.unique_id.lower()

        if not unique_id.startswith(prefix):
            continue

        if SENSOR_KEY_MAP.get(unique_id[len(prefix) :]) in BINARY_KEYS:
            return True

    return False


def uses_legacy_entity_ids(device_id, registry_entries):
    """
    Detect the entity IDs released up to 1.0.8, which repeat the station name.

    Args:
        device_id: Identifier announced by the station.
        registry_entries: Entity registry entries of that device.

    Returns:
        bool: True when at least one entity still carries the doubled prefix.
    """

    doubled = f"{slugify(device_id)}_{slugify(device_id)}_"

    return any(
        entry.entity_id.partition(".")[2].startswith(doubled)
        for entry in registry_entries
    )


def async_rebuild_platform(hass, runtime, platform, factory):
    """
    Recreate the known entities of one platform from the registries.

    The device ID is read straight from the device registry identifiers, so it
    is recovered exactly. The entity key is then the remainder of the unique ID
    once the known device prefix is stripped, which stays unambiguous even when
    the device ID itself contains underscores.

    Args:
        hass: Home Assistant instance.
        runtime: PwsRuntime for the config entry.
        platform: Platform being set up, e.g. "sensor".
        factory: Callable (device, key) returning an entity or None.

    Returns:
        list: Entities to hand over to async_add_entities.
    """

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    entities = []

    for device_entry in dr.async_entries_for_config_entry(
        device_registry, runtime.entry.entry_id
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

        device, _ = runtime.get_device(device_id)
        prefix = f"{DOMAIN}_{device_id}_".lower()

        ours = [
            entry
            for entry in er.async_entries_for_device(
                entity_registry, device_entry.id, include_disabled_entities=True
            )
            if entry.platform == DOMAIN
        ]

        # Decided once per device, before any entity is built: a device that
        # already has the old IDs keeps them, including for sensors that show up
        # later, so one station never ends up with two naming styles.
        device.legacy_entity_ids = device.legacy_entity_ids or uses_legacy_entity_ids(
            device_id, ours
        )
        device.legacy_status_sensors = (
            device.legacy_status_sensors
            or uses_legacy_status_sensors(device_id, ours)
        )

        for registry_entry in ours:
            if registry_entry.domain != platform:
                continue

            unique_id = registry_entry.unique_id.lower()

            if not unique_id.startswith(prefix):
                continue

            entity = factory(device, unique_id[len(prefix) :])

            if entity is not None:
                entities.append(entity)

    return entities
