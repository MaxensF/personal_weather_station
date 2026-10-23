"""Button platform: wind direction calibration shortcuts."""

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN, KEY_RESET_WIND_OFFSET, KEY_SET_NORTH
from .entity import PwsAlwaysAvailableEntity
from .models import PwsDevice
from .registry import async_rebuild_platform


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the button platform.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None
    """

    runtime = hass.data[DOMAIN]
    runtime.add_entities["button"] = async_add_entities

    restored = async_rebuild_platform(hass, runtime, "button", _restore_button)

    if restored:
        async_add_entities(restored)


def _restore_button(device, key):
    """Build the button matching a unique ID suffix found in the registry."""

    if key in device.entities:
        return None

    button = BUTTONS.get(key)

    return button(device) if button else None


def build_new_entities(device):
    """
    Build the calibration buttons, once the station reports a wind direction.

    Args:
        device: PwsDevice being updated.

    Returns:
        list: Newly created entities.
    """

    if not device.has_wind_direction:
        return []

    return [
        button(device)
        for key, button in BUTTONS.items()
        if key not in device.entities
    ]


class PwsSetNorthButton(PwsAlwaysAvailableEntity, ButtonEntity):
    """
    Take the direction being reported right now as true north.

    Hold the vane pointing at geographic north, press, done.
    """

    _pws_platform = "button"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:compass-rose"
    _attr_translation_key = KEY_SET_NORTH

    def __init__(self, device: PwsDevice):
        super().__init__(device, KEY_SET_NORTH, "Set North From Current")

    async def async_press(self):
        raw = self.device.raw_wind_direction

        if raw is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="no_wind_direction",
                translation_placeholders={"device": self.device.device_id},
            )

        await self.device.async_set_wind_offset(-round(raw))


class PwsResetWindOffsetButton(PwsAlwaysAvailableEntity, ButtonEntity):
    """Drop the calibration and report directions exactly as received."""

    _pws_platform = "button"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:backup-restore"
    _attr_translation_key = KEY_RESET_WIND_OFFSET

    def __init__(self, device: PwsDevice):
        super().__init__(device, KEY_RESET_WIND_OFFSET, "Reset Wind Offset")

    async def async_press(self):
        await self.device.async_set_wind_offset(0)


BUTTONS = {
    KEY_SET_NORTH: PwsSetNorthButton,
    KEY_RESET_WIND_OFFSET: PwsResetWindOffsetButton,
}
