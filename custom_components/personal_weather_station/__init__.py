from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, SENSOR_LIST
from .sensor import PwsSensor, PwsDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """
    Set up the integration from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        bool: True if setup was successful.
    """

    # Store devices by ID
    hass.data.setdefault(DOMAIN + "_devices", {})

    #  Reference to the function that adds entities
    hass.data.setdefault(DOMAIN + "_add_entities", None)

    async def handle_request(request):
        """
        Handle HTTP requests from the weather station.

        Args:
            request: aiohttp.web.Request object containing query parameters.

        Returns:
            web.Response: JSON response indicating success, created/updated sensors, or error.
        """

        # Extract all query parameters from the URL
        params = request.rel_url.query

        # Get the devices dictionary from hass.data
        devices = hass.data[DOMAIN + "_devices"]

        # Get the reference to the function that adds new entities
        add_entities = hass.data.get(DOMAIN + "_add_entities")

        # If the sensor platform is not ready, return an error JSON response
        if not add_entities:
            return web.json_response({"status": "error", "detail": "Sensor platform not ready"})

        # Get the device ID from the query parameters
        device_id = params.get("ID")

        # If no ID is provided, return an error JSON response
        if not device_id:
            return web.json_response({"status": "error", "detail": "Missing ID"})

        # If this device ID does not exist yet, create a new PwsDevice instance
        if device_id not in devices:
            devices[device_id] = PwsDevice(hass, device_id)

        # Retrieve the device object
        device = devices[device_id]

        # Initialize a list to store any new sensors to add to Home Assistant
        new_entities = []

        # Initialize a counter for updated sensors
        updated = 0

        # Loop through all query parameters
        for key, value in params.items():

            # Skip the "ID" parameter as it is not a sensor
            if key == "ID":
                continue

            # Skip any key that is not in the predefined SENSOR_LIST
            if key not in SENSOR_LIST:
                continue

            # Attempt to convert the value to a number (int or float)
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except(ValueError, TypeError):

                # Leave value as string if conversion fails
                pass

            # Update the sensor value in the device's data dictionary
            device.data[key] = value

            # If this sensor does not exist yet, create it
            if key not in device.sensors:

                # Instantiate a new PwsSensor
                sensor = PwsSensor(device, key)

                # Store the sensor in the device's sensors dictionary
                device.sensors[key] = sensor

                # Add it to the list of new entities to register
                new_entities.append(sensor)

            else:

                # If the sensor already exists, update its state in Home Assistant
                device.sensors[key].async_write_ha_state()

                # Increment the updated counter
                updated += 1

        # If there are any new sensors, add them to Home Assistant
        if new_entities:
            add_entities(new_entities)

        # Return a JSON response summarizing the operation
        return web.json_response({
            "status": "ok",
            "device": device_id,
            "created": len(new_entities),
            "updated": updated
        })

    # Register the HTTP view to listen on the specified URL
    hass.http.register_view(
        PwsView("/weatherstation/updateweatherstation.php", handle_request)
    )

    # Forward the setup of the config entry to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """
    Unload a config entry and clean up resources.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        bool: True if unload was successful.
    """

    # Unload the sensor platform associated with this config entry
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    # Remove the devices dictionary from hass.data
    hass.data.pop(DOMAIN + "_devices", None)

    # Remove the reference to the add_entities function
    hass.data.pop(DOMAIN + "_add_entities", None)

    return True


class PwsView(HomeAssistantView):
    """
    Custom HTTP view for receiving weather station updates.
    """

    requires_auth = False

    def __init__(self, url, handler):
        """
        Initialize the HTTP view.

        Args:
            url: URL path to register the view.
            handler: Async function to handle incoming GET requests.
        """

        super().__init__()
        self.url = url
        self.name = "Personal_weather_station_server_view"
        self._handler = handler

    async def get(self, request):
        return await self._handler(request)
