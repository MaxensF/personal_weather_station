"""Sensor platform for the Personal Weather Station integration."""

from homeassistant.components.sensor import RestoreSensor, SensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    KEY_LAST_UPDATE,
    SENSOR_KEY_MAP,
    SENSOR_LIST,
    SENSOR_TRANSLATION_KEYS,
)
from .entity import PwsAlwaysAvailableEntity, PwsEntity
from .models import PwsDevice
from .normalizer import (
    denormalize_battery,
    normalize_battery,
)
from .registry import async_rebuild_platform


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the sensor platform.

    Recreates the sensors already known to the registries, then keeps a
    reference to async_add_entities so the HTTP handler can add more as new
    payload keys show up.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None
    """

    runtime = hass.data[DOMAIN]
    runtime.add_entities["sensor"] = async_add_entities

    restored = async_rebuild_platform(hass, runtime, "sensor", _restore_sensor)

    if restored:
        async_add_entities(restored)


def _restore_sensor(device, key):
    """
    Build the sensor matching a unique ID suffix found in the registry.

    Args:
        device: PwsDevice the entity belongs to.
        key: Unique ID suffix, lowercase.

    Returns:
        The entity, or None when the suffix is not a sensor we still support.
    """

    if key in device.entities:
        return None

    if key == KEY_LAST_UPDATE:
        return PwsLastUpdateSensor(device)

    canonical = SENSOR_KEY_MAP.get(key)

    if canonical is None:
        return None

    return PwsSensor(device, canonical)


def build_new_entities(device, keys):
    """
    Build the sensors that a freshly received payload calls for.

    Args:
        device: PwsDevice being updated.
        keys: Canonical sensor keys present in the payload.

    Returns:
        list: Newly created entities.
    """

    entities = []

    if KEY_LAST_UPDATE not in device.entities:
        entities.append(PwsLastUpdateSensor(device))

    for key in keys:
        if key in device.entities:
            continue

        # Connection and leak keys belong to the binary_sensor platform now.
        # A device that already exposes them as numbers keeps doing so until
        # the user converts it from Repairs.
        if SENSOR_LIST[key].get("binary") and not device.legacy_status_sensors:
            continue

        entities.append(PwsSensor(device, key))

    return entities


class PwsSensor(PwsEntity, RestoreSensor):
    """
    An individual measurement reported by a PWS device.

    Attributes:
        _meta: Metadata from SENSOR_LIST (name, icon, unit, classes, precision).
    """

    def __init__(self, device: PwsDevice, key: str):
        """
        Initialize the sensor entity.

        Args:
            device: PwsDevice instance the sensor belongs to.
            key: String key identifying the sensor type.

        Returns:
            None
        """

        self._meta = SENSOR_LIST.get(key, {"name": key, "icon": "mdi:help"})
        self._attr_translation_key = SENSOR_TRANSLATION_KEYS.get(key, slugify(key))

        # Readings about the station rather than about the weather belong with
        # the diagnostics, next to the batteries and the last contact time.
        if self._meta.get("diagnostic"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        super().__init__(device, key, self._meta.get("name", key))

    @property
    def native_value(self):
        """Current value, converted when the reading is coded rather than plain."""

        value = self.device.data.get(self._key)

        if (scale := self._meta.get("battery_scale")) is not None:
            return normalize_battery(value, scale)

        if (levels := self._meta.get("options")) is not None:
            # An index the station numbers rather than names. A code outside
            # the documented range becomes unknown rather than a state Home
            # Assistant would reject for not being in `options`.
            try:
                return levels.get(int(value))
            except (TypeError, ValueError):
                return None

        return value

    @property
    def icon(self):
        return self._meta.get("icon")

    @property
    def native_unit_of_measurement(self):
        return self._meta.get("unit")

    @property
    def device_class(self):
        return self._meta.get("device_class")

    @property
    def state_class(self):
        return self._meta.get("state_class")

    @property
    def suggested_display_precision(self):
        return self._meta.get("precision")

    @property
    def options(self):
        """The states an enum sensor may take; `None` for every other sensor."""

        levels = self._meta.get("options")
        return None if levels is None else list(levels.values())

    async def async_added_to_hass(self):
        """Restore the last known value so a restart does not blank the sensor."""

        await super().async_added_to_hass()

        if self.device.data.get(self._key) is not None:
            return

        last_data = await self.async_get_last_sensor_data()

        if last_data is None or last_data.native_value is None:
            return

        value = last_data.native_value

        # The stored state is what was displayed; the device dictionary holds
        # what the station sent. Undo whichever conversion applies.
        if (scale := self._meta.get("battery_scale")) is not None:
            value = denormalize_battery(value, scale)

        self.device.data[self._key] = value


class PwsLastUpdateSensor(PwsAlwaysAvailableEntity, RestoreSensor):
    """When the station last posted a valid payload."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clock-check-outline"
    _attr_translation_key = KEY_LAST_UPDATE

    def __init__(self, device: PwsDevice):
        super().__init__(device, KEY_LAST_UPDATE, "Last Update")

    @property
    def native_value(self):
        return self.device.last_seen

    async def async_added_to_hass(self):
        """
        Restore the last contact time.

        This is what lets availability survive a restart: without it the
        integration would have no idea how long a silent station has been quiet.
        """

        await super().async_added_to_hass()

        if self.device.last_seen is not None:
            return

        last_data = await self.async_get_last_sensor_data()

        if last_data is not None and last_data.native_value is not None:
            self.device.last_seen = last_data.native_value
