from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
import itertools
import time
import logging

from .const import DOMAIN, SENSOR_LIST, CONF_DEBUG
from .sensor import PwsSensor, PwsDevice

_LOGGER = logging.getLogger(__name__)
REQUEST_COUNTER = itertools.count(1)



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

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def handle_request(request):
        """
        Handle HTTP requests from the weather station.

        Args:
            request: aiohttp.web.Request object containing query parameters.

        Returns:
            web.Response: JSON response indicating success, created/updated sensors, or error.
        """

        start = time.monotonic()
        request_id = next(REQUEST_COUNTER)

        debug = entry.options.get(CONF_DEBUG, False)

        def debug_log(message, *args):
            if debug:
                _LOGGER.info(message, *args)

        try:         
            
            debug_log("[#%d] %s request from %s", request_id, request.method, request.remote )

            # Extract all query parameters from the URL
            params = request.rel_url.query

            debug_log(
                    "\n"
                    "========== Weather Station Request ==========\n"
                    "Method     : %s\n"
                    "Remote IP  : %s\n"
                    "URL        : %s\n"
                    "HTTP       : %s\n"
                    "Headers    : %s\n"
                    "Parameters : %s\n"
                    "=============================================",
                    request.method,
                    request.remote,
                    request.raw_path,
                    request.version,
                    dict(request.headers),
                    dict(params),
                )

            # Check for password
            # Check options first, then data
            password = entry.options.get(CONF_PASSWORD)
            if password is None:
                password = entry.data.get(CONF_PASSWORD)

            if password:
                request_password = params.get("PASSWORD") or params.get("wspw")
                if request_password != password:
                    debug_log("[#%d] Returning HTTP 401", request_id)
                    return web.json_response({"status": "error", "detail": "Invalid password"}, status=401)

            # Get the devices dictionary from hass.data.
            # During reload there is a brief window where unload removed the key.
            devices = hass.data.setdefault(DOMAIN + "_devices", {})

            # Get the reference to the function that adds new entities
            add_entities = hass.data.get(DOMAIN + "_add_entities")

            # If the sensor platform is not ready, return an error JSON response
            if not add_entities:
                debug_log("[#%d] Returning HTTP 503 (sensor platform not ready)", request_id)
                return web.json_response(
                    {"status": "error", "detail": "Sensor platform not ready"},
                    status=503,
                )

            # Get the device ID from supported query parameters.
            # Keep backward compatibility with "ID" and support WSLink's "wsid".
            device_id = params.get("ID") or params.get("wsid")

            # If no device identifier is provided, return an error JSON response
            if not device_id:
                debug_log("[#%d] Returning HTTP 400 (missing device ID)", request_id)
                return web.json_response({"status": "error", "detail": "Missing device identifier (ID or wsid)"})

            # If this device ID does not exist yet, create a new PwsDevice instance
            if device_id not in devices:
                debug_log("[#%d] New device detected: %s", request_id, device_id)
                devices[device_id] = PwsDevice(hass, device_id)

            # Retrieve the device object
            device = devices[device_id]

            # Initialize a list to store any new sensors to add to Home Assistant
            new_entities = []

            # Initialize a counter for updated sensors
            updated = 0

            # Create a map for case-insensitive lookup
            SENSOR_MAP = {k.lower(): k for k in SENSOR_LIST}

            processed_params = sum(
                1 for key in params
                if key not in ("ID", "wsid", "PASSWORD", "wspw")
            )

            debug_log("[#%d] Processing %d sensor parameters", request_id, processed_params)

            # Loop through all query parameters
            for key, value in params.items():

                # Skip identifier/auth parameters as they are not sensors.
                if key in ("ID", "wsid", "PASSWORD", "wspw"):
                    continue

                # Check if key exists (case insensitive)
                normalized_key = SENSOR_MAP.get(key.lower())

                # Skip any key that is not in the predefined SENSOR_LIST
                if not normalized_key:
                    debug_log("[#%d] Ignoring unknown parameter '%s'='%s'", request_id, key, value)
                    continue

                # Use the normalized key
                key = normalized_key

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

                    debug_log("[#%d] Creating sensor '%s'", request_id, key )

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
            
            elapsed = time.monotonic() - start
                
            debug_log("[#%d] Returning HTTP 200 (device=%s created=%d updated=%d time=%.3fs)", request_id, device_id, len(new_entities), updated, elapsed)

            # Return a JSON response summarizing the operation
            return web.json_response({
                "status": "ok",
                "device": device_id,
                "created": len(new_entities),
                "updated": updated
            })
                
        except Exception:
            _LOGGER.exception(
                "[#%d] Unhandled exception while processing %s from %s",
                request_id,
                request.raw_path,
                request.remote,
            )
            raise

    # Register the HTTP view to listen on the specified URL
    hass.http.register_view(
        PwsView("/weatherstation/updateweatherstation.php", handle_request)
    )
    hass.http.register_view(
        PwsView("/data/upload.php", handle_request)
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


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """
    Handle options update.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
    """
    await hass.config_entries.async_reload(entry.entry_id)


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
