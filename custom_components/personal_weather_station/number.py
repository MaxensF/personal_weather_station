"""Number platform: wind direction calibration offset."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import DEGREE, EntityCategory

from .const import DOMAIN, KEY_WIND_OFFSET
from .entity import PwsAlwaysAvailableEntity
from .models import PwsDevice
from .registry import async_rebuild_platform


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the number platform.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None
    """

    runtime = hass.data[DOMAIN]
    runtime.add_entities["number"] = async_add_entities

    restored = async_rebuild_platform(hass, runtime, "number", _restore_number)

    if restored:
        async_add_entities(restored)


def _restore_number(device, key):
    """Build the number matching a unique ID suffix found in the registry."""

    if key in device.entities or key != KEY_WIND_OFFSET:
        return None

    return PwsWindOffsetNumber(device)


def build_new_entities(device):
    """
    Build the calibration number, once the station reports a wind direction.

    Args:
        device: PwsDevice being updated.

    Returns:
        list: Newly created entities.
    """

    if not device.has_wind_direction or KEY_WIND_OFFSET in device.entities:
        return []

    return [PwsWindOffsetNumber(device)]


class PwsWindOffsetNumber(PwsAlwaysAvailableEntity, NumberEntity):
    """
    Rotation applied to every wind direction reported by the station.

    A weather station has to be oriented when it is installed. When that could
    not be done precisely, this recovers true north without touching the
    hardware.
    """

    _pws_platform = "number"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 359
    _attr_native_step = 1
    _attr_native_unit_of_measurement = DEGREE
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:compass-rose"
    _attr_translation_key = KEY_WIND_OFFSET

    def __init__(self, device: PwsDevice):
        super().__init__(device, KEY_WIND_OFFSET, "Wind Direction Offset")

    @property
    def native_value(self):
        return self.device.wind_offset

    async def async_set_native_value(self, value):
        """
        Store a new offset.

        The affected sensors are rewritten by the config entry update listener,
        which keeps a single code path whether the offset is changed here, from
        a button, or from the options.
        """

        await self.device.async_set_wind_offset(value)
