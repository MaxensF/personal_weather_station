"""Binary sensor platform: connection and water leak status.

The WSLink API documents these as 1/0 readings. Exposing them as numbers made
them unusable with Home Assistant's standard leak cards and alerts.
"""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    KEY_STATION_ONLINE,
    SENSOR_KEY_MAP,
    SENSOR_LIST,
    SENSOR_TRANSLATION_KEYS,
)
from .entity import PwsAlwaysAvailableEntity, PwsEntity
from .models import PwsDevice
from .registry import async_rebuild_platform

PLATFORM = "binary_sensor"


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the binary sensor platform.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None
    """

    runtime = hass.data[DOMAIN]
    runtime.add_entities[PLATFORM] = async_add_entities

    restored = async_rebuild_platform(hass, runtime, PLATFORM, _restore_binary_sensor)

    if restored:
        async_add_entities(restored)


def _restore_binary_sensor(device, key):
    """Build the binary sensor matching a unique ID suffix in the registry."""

    if key in device.entities:
        return None

    if key == KEY_STATION_ONLINE:
        return PwsStationOnlineBinarySensor(device)

    canonical = SENSOR_KEY_MAP.get(key)

    if canonical is None or not SENSOR_LIST[canonical].get("binary"):
        return None

    return PwsBinarySensor(device, canonical)


def build_new_entities(device, keys):
    """
    Build the binary sensors a freshly received payload calls for.

    Devices that already expose these keys as numeric sensors are left alone
    until the user asks for the conversion from Repairs.

    Args:
        device: PwsDevice being updated.
        keys: Canonical sensor keys present in the payload.

    Returns:
        list: Newly created entities.
    """

    entities = []

    # Not subject to the legacy conversion: this one has never existed as a
    # numeric sensor, so there is nothing of the user's to preserve.
    if KEY_STATION_ONLINE not in device.entities:
        entities.append(PwsStationOnlineBinarySensor(device))

    if device.legacy_status_sensors:
        return entities

    entities.extend(
        PwsBinarySensor(device, key)
        for key in keys
        if key not in device.entities and SENSOR_LIST[key].get("binary")
    )

    return entities


class PwsBinarySensor(PwsEntity, BinarySensorEntity):
    """A connection or water leak status reported by a PWS device."""

    _pws_platform = PLATFORM

    def __init__(self, device: PwsDevice, key: str):
        """
        Initialize the binary sensor.

        Args:
            device: PwsDevice instance the sensor belongs to.
            key: String key identifying the sensor type.

        Returns:
            None
        """

        self._meta = SENSOR_LIST[key]
        self._attr_translation_key = SENSOR_TRANSLATION_KEYS.get(key, slugify(key))
        binary = self._meta["binary"]

        # A string names a Home Assistant device class; True just means "this
        # is a binary reading". The batteries take that second form on purpose:
        # the battery class renders as Normal / Low, and a console sitting on
        # mains power has no battery level to be normal about.
        self._attr_device_class = (
            BinarySensorDeviceClass(binary) if isinstance(binary, str) else None
        )

        if (
            self._attr_device_class is BinarySensorDeviceClass.CONNECTIVITY
            or self._meta.get("diagnostic")
        ):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        super().__init__(device, key, self._meta["name"])

    @property
    def is_on(self):
        """
        Both protocols use 1 for the active state.

        Connected=1 for a connection status, Leak=1 for a water leak sensor,
        Normal=1 for a battery — which reads as on when the battery is fine.
        """

        value = self.device.data.get(self._key)

        if value is None:
            return None

        return value == 1


class PwsStationOnlineBinarySensor(PwsAlwaysAvailableEntity, BinarySensorEntity):
    """
    Whether the station is still posting.

    Every other connection status comes from the station itself, which says
    nothing about the console: the console is the thing doing the posting, so
    when it stops there is nobody left to report it. This one is derived from
    the availability timeout instead, and stays available precisely when the
    station is not — an entity that went unavailable could not say it was off.
    """

    _pws_platform = PLATFORM

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = KEY_STATION_ONLINE

    def __init__(self, device: PwsDevice):
        super().__init__(device, KEY_STATION_ONLINE, "Station Online")

    @property
    def is_on(self):
        return self.device.available
