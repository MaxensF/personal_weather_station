"""Base entity shared by the sensor, number and button platforms."""

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .const import DOMAIN


def build_object_id(device_id, english_name):
    """
    Build the object ID of an entity, prefixed with the station.

    Args:
        device_id: Identifier announced by the station.
        english_name: English name of the entity.

    Returns:
        str: e.g. "my_station_outdoor_temperature".
    """

    return f"{slugify(device_id)}_{slugify(english_name)}"


class PwsEntity(Entity):
    """
    Common plumbing for every entity attached to a PwsDevice.

    Attributes:
        device: Parent PwsDevice.
        _key: Suffix identifying the entity within the device.
        _added: Whether Home Assistant finished adding the entity.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    # Platform this entity belongs to, needed to build its entity ID.
    _pws_platform = "sensor"

    def __init__(self, device, key, english_name):
        """
        Initialize the entity.

        Args:
            device: PwsDevice the entity belongs to.
            key: Suffix identifying the entity within the device.
            english_name: Name used to derive a stable, language independent
                entity ID.

        Returns:
            None
        """

        self.device = device
        self._key = key
        self._english_name = english_name
        self._added = False

        object_id = build_object_id(device.device_id, english_name)

        if device.legacy_entity_ids:
            # Home Assistant treats a suggested object ID as a base and prefixes
            # the device name to it, which is where the station name appearing
            # twice in released entity IDs comes from.
            self._legacy_object_id = object_id
        else:
            # Setting the entity ID outright skips that prefixing. It also keeps
            # the ID in English whatever the user's language, so a dashboard
            # still works when shared.
            self._legacy_object_id = None
            self.entity_id = f"{self._pws_platform}.{object_id}"

        device.entities[key] = self

    @property
    def entity_key(self):
        """Key identifying this entity inside its device."""

        return self._key

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.device.device_id}_{self._key}".lower()

    @property
    def suggested_object_id(self):
        """Only used by devices kept on the pre-1.1 naming."""

        return self._legacy_object_id

    @property
    def available(self):
        return self.device.available

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_id)},
            "name": self.device.device_id,
            "manufacturer": "Custom",
            "model": "Personal Weather Station",
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._added = True

    async def async_will_remove_from_hass(self):
        self._added = False
        self.device.entities.pop(self._key, None)
        await super().async_will_remove_from_hass()

    @callback
    def update_state(self):
        """
        Write the current state, if Home Assistant is ready for it.

        Entities are handed to async_add_entities and attached asynchronously.
        A payload arriving in that window would otherwise raise, and the
        exception would abort the rest of the request.
        """

        if self._added and self.hass is not None:
            self.async_write_ha_state()


class PwsAlwaysAvailableEntity(PwsEntity):
    """
    An entity that stays available when the station goes quiet.

    Used for diagnostics and configuration: knowing how long a station has been
    silent, or resetting its calibration, has to stay possible precisely when it
    stopped reporting.
    """

    @property
    def available(self):
        return True
