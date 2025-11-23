from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, SENSOR_LIST


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the integration from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object (not used directly here).
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None. Stores async_add_entities in hass.data for later use.
    """

    hass.data[DOMAIN + "_add_entities"] = async_add_entities


class PwsDevice:
    """
    Represents a Personal Weather Station (PWS) device.

    Attributes:
        hass: Home Assistant instance.
        device_id: Unique identifier of the device.
        data: Dictionary holding sensor values keyed by sensor type.
        sensors: Dictionary holding sensor objects keyed by sensor type.
    """

    def __init__(self, hass, device_id):
        """
        Initialize the PWS device.

        Args:
            hass: Home Assistant instance.
            device_id: Unique ID of the device.

        Returns:
            None
        """

        # Reference to Home Assistant instance
        self.hass = hass

        # Unique identifier for this device
        self.device_id = device_id

        # Stores sensor data from the device
        self.data = {}

        # Stores sensor objects associated with the device
        self.sensors = {}



class PwsSensor(SensorEntity):
    """
    Represents an individual sensor attached to a PWS device.

    Attributes:
        device: Reference to the parent PwsDevice.
        _key: Sensor key identifier (string).
        _meta: Metadata dictionary from SENSOR_LIST (name, icon, unit, device_class).
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

        # Reference to the parent PwsDevice
        self.device = device

        # Sensor key (e.g., temperature, humidity)
        self._key = key

        # Retrieve metadata for this sensor from SENSOR_LIST, fallback if key is unknown
        self._meta = SENSOR_LIST.get(
            key, {"name": key, "icon": "mdi:help"}
        )

    @property
    def name(self):
        return self._meta.get("name", self._key)

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.device.device_id}_{self._key}".lower()

    @property
    def native_value(self):
        return self.device.data.get(self._key)

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
    def should_poll(self):
        return False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_id)},
            "name": self.device.device_id,
            "manufacturer": "Custom",
            "model": "Personal Weather Station",
        }
