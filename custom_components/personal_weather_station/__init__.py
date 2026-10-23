"""The Personal Weather Station integration.

Home Assistant acts as the server here: stations push their readings over HTTP
and devices and entities are created from whatever keys turn up in the query
string. Nothing is configured up front on the Home Assistant side.
"""

import hmac
import itertools
import logging
import time
from datetime import timedelta

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from . import binary_sensor, button, number, sensor
from .const import (
    AUTH_PARAMS,
    CONF_DEBUG,
    CONF_WIND_OFFSETS,
    DATA_ONBOARDING,
    DATA_VIEWS_REGISTERED,
    DOMAIN,
    ENDPOINTS,
    ID_PARAMS,
    ISSUE_LEGACY_ENTITY_IDS,
    ISSUE_LEGACY_STATUS_SENSORS,
    ISSUE_NO_STATION_YET,
    ISSUE_TRACKER_URL,
    ISSUE_UNKNOWN_PARAMETERS,
    KEY_LAST_UPDATE,
    KEY_STATION_ONLINE,
    KEY_WIND_DIR_RAW,
    PLATFORMS,
    RATE_LIMIT_REQUESTS,
    RESERVED_PARAMS,
    SENSOR_KEY_MAP,
    SENSOR_LIST,
    TIMESTAMP_PARAMS,
)
from .instructions import async_ensure_images, async_placeholders_for_entry
from .migration import async_find_legacy_entities, async_find_status_sensors
from .models import PwsRuntime
from .normalizer import parse_value

_LOGGER = logging.getLogger(__name__)

# There is no YAML configuration: everything is set up from the config entry.
# Declaring it silences hassfest, which asks any integration defining async_setup
# to say what it accepts.
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

REQUEST_COUNTER = itertools.count(1)

# The integration is purely passive, so nothing else would ever notice that a
# station went quiet. This tick is what flips entities to unavailable.
AVAILABILITY_SCAN_INTERVAL = timedelta(minutes=1)

# A station clock this far off is not trustworthy; fall back to server time.
MAX_CLOCK_DRIFT = timedelta(days=1)


async def async_setup(hass: HomeAssistant, config):
    """
    Register the HTTP endpoints, once per Home Assistant run.

    Home Assistant offers no way to unregister a view, so this deliberately
    happens here rather than in async_setup_entry: doing it per entry stacked a
    new route on every reload, and aiohttp resolves on the first one registered.

    Args:
        hass: Home Assistant instance.
        config: YAML configuration, unused.

    Returns:
        bool: True.
    """

    async_ensure_views(hass)
    await async_ensure_images(hass)

    return True


@callback
def async_ensure_views(hass):
    """
    Register the upload endpoints, once per Home Assistant run.

    Also called from the setup wizard, which needs the endpoints live before any
    config entry exists so it can wait for the station's first upload with the
    user. Guarded because Home Assistant offers no way to unregister a view.

    Args:
        hass: Home Assistant instance.

    Returns:
        None
    """

    if hass.data.get(DATA_VIEWS_REGISTERED):
        return

    hass.data[DATA_VIEWS_REGISTERED] = True

    for url in ENDPOINTS:
        hass.http.register_view(PwsView(hass, url))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """
    Set up the integration from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        bool: True if setup was successful.
    """

    runtime = PwsRuntime(hass, entry)
    hass.data[DOMAIN] = runtime

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _async_check_legacy_entity_ids(hass, entry)
    _async_check_legacy_status_sensors(hass, entry)
    _async_check_no_station_yet(hass, entry, runtime)

    entry.async_on_unload(
        async_track_time_interval(
            hass,
            _make_availability_check(hass),
            AVAILABILITY_SCAN_INTERVAL,
        )
    )

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

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        hass.data.pop(DOMAIN, None)

    return unloaded


async def async_remove_config_entry_device(hass, entry, device_entry):
    """
    Allow a station to be deleted from the device page.

    Devices appear on their own, so a typo in the station ID creates one that
    would otherwise stay forever.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        device_entry: Device registry entry being removed.

    Returns:
        bool: True, the device may always be removed.
    """

    device_id = next(
        (
            identifier[1]
            for identifier in device_entry.identifiers
            if identifier[0] == DOMAIN
        ),
        None,
    )

    if device_id is None:
        return True

    runtime = hass.data.get(DOMAIN)

    if runtime is not None:
        runtime.devices.pop(device_id, None)

    offsets = dict(entry.options.get(CONF_WIND_OFFSETS) or {})

    if offsets.pop(device_id, None) is not None:
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_WIND_OFFSETS: offsets}
        )

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """
    Handle an options update.

    Every option is read live from the config entry, so there is nothing to
    reload: rewriting the states is enough, and it keeps the wind offset
    responsive when it is nudged from the number entity.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        None
    """

    runtime = hass.data.get(DOMAIN)

    if runtime is None:
        return

    for device in runtime.devices.values():
        device.was_available = device.available
        device.async_write_states()


@callback
def _async_check_legacy_entity_ids(hass: HomeAssistant, entry: ConfigEntry):
    """
    Offer to shorten the entity IDs released up to 1.0.8.

    Never done automatically: an automation or a dashboard pointing at the old
    ID would break, and only the user knows whether anything does.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        None
    """

    renames = async_find_legacy_entities(hass, entry)

    if not renames:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_LEGACY_ENTITY_IDS)
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_LEGACY_ENTITY_IDS,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_LEGACY_ENTITY_IDS,
        translation_placeholders={"count": str(len(renames))},
        data={"entry_id": entry.entry_id},
    )


@callback
def _async_report_unknown_parameters(hass, device, unknown_keys):
    """
    Surface parameters this integration silently drops.

    A station that reports more than the protocol can express — a Bresser with
    five extra sensors uploading over Weather Underground, for instance — loses
    the surplus without a word. Naming the parameters turns a mystery into
    something reportable.

    Args:
        hass: Home Assistant instance.
        device: PwsDevice the payload came from.
        unknown_keys: Parameter names seen in this payload and not recognised.

    Returns:
        None
    """

    new_keys = unknown_keys - device.unknown_keys

    if not new_keys:
        return

    device.unknown_keys |= new_keys

    ir.async_create_issue(
        hass,
        DOMAIN,
        f"{ISSUE_UNKNOWN_PARAMETERS}_{slugify(device.device_id)}",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_UNKNOWN_PARAMETERS,
        translation_placeholders={
            "station": device.device_id,
            "count": str(len(device.unknown_keys)),
            "parameters": ", ".join(f"`{key}`" for key in sorted(device.unknown_keys)),
            "issue_tracker": ISSUE_TRACKER_URL,
        },
        learn_more_url=ISSUE_TRACKER_URL,
    )


@callback
def _async_check_no_station_yet(hass: HomeAssistant, entry: ConfigEntry, runtime):
    """
    Say what to do while no station has ever posted.

    There is no "add device" button here, so an empty integration page is all a
    user gets otherwise. The issue clears itself on the first payload.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        runtime: PwsRuntime, holding the devices rebuilt from the registries.

    Returns:
        None
    """

    if runtime.devices:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_NO_STATION_YET)
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_NO_STATION_YET,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_NO_STATION_YET,
        translation_placeholders=async_placeholders_for_entry(hass, entry),
        data={"entry_id": entry.entry_id},
    )


@callback
def _async_check_legacy_status_sensors(hass: HomeAssistant, entry: ConfigEntry):
    """
    Offer to turn the connection and leak readings into binary sensors.

    Crossing platforms cannot be a rename, so the old entities are dropped and
    rebuilt. Only the user knows whether something points at them.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.

    Returns:
        None
    """

    found = async_find_status_sensors(hass, entry)

    if not found:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_LEGACY_STATUS_SENSORS)
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_LEGACY_STATUS_SENSORS,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_LEGACY_STATUS_SENSORS,
        translation_placeholders={"count": str(len(found))},
        data={"entry_id": entry.entry_id},
    )


def _make_availability_check(hass: HomeAssistant):
    """Build the periodic callback that marks silent stations unavailable."""

    @callback
    def _async_check_availability(now):
        runtime = hass.data.get(DOMAIN)

        if runtime is None:
            return

        for device in runtime.devices.values():
            available = device.available

            if available != device.was_available:
                device.was_available = available
                device.async_write_states()

    return _async_check_availability


def _get_param(params, names):
    """
    Look a parameter up, ignoring case.

    Args:
        params: Query string mapping.
        names: Lowercase parameter names to accept.

    Returns:
        The first matching value, or None.
    """

    for key, value in params.items():
        if key.lower() in names:
            return value

    return None


def _parse_timestamp(params):
    """
    Read the moment the payload was produced, if the station sent one.

    WSLink sends "datetime" in station local time, Weather Underground sends
    "dateutc" in UTC. Both are ignored when the clock looks obviously wrong.

    Args:
        params: Query string mapping.

    Returns:
        An aware datetime in UTC, or None.
    """

    for name in TIMESTAMP_PARAMS:
        raw = _get_param(params, (name,))

        if not raw or not raw.strip() or raw.strip().lower() == "now":
            continue

        parsed = dt_util.parse_datetime(raw.strip())

        if parsed is None:
            continue

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=dt_util.UTC
                if name == "dateutc"
                else dt_util.DEFAULT_TIME_ZONE
            )

        parsed = dt_util.as_utc(parsed)

        if abs(parsed - dt_util.utcnow()) > MAX_CLOCK_DRIFT:
            return None

        return parsed

    return None


@callback
def _async_report_rejection(hass, kind, issue_key, placeholders):
    """
    Surface a rejected request in Repairs, where it is actually visible.

    Args:
        hass: Home Assistant instance.
        kind: Issue translation key.
        issue_key: What identifies the offending station. The station ID is
            preferred over the address: behind a proxy such as the WSLink
            add-on, every station shares one address, and one of them getting
            through would clear a warning raised for another.
        placeholders: Translation placeholders.

    Returns:
        None
    """

    ir.async_create_issue(
        hass,
        DOMAIN,
        f"{kind}_{slugify(issue_key)}",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=kind,
        translation_placeholders=placeholders,
    )


@callback
def _async_clear_rejections(hass, remote, device_id):
    """
    Drop the Repairs issues for a station that is now getting through.

    Both keyings are cleared: a station rejected before it announced an ID was
    filed under its address.

    Args:
        hass: Home Assistant instance.
        remote: Address the request came from.
        device_id: Identifier the station announced.

    Returns:
        None
    """

    for issue_id in (
        f"invalid_station_key_{slugify(device_id)}",
        f"invalid_station_key_{slugify(remote)}",
        f"missing_device_id_{slugify(remote)}",
    ):
        ir.async_delete_issue(hass, DOMAIN, issue_id)


@callback
def _async_handle_without_entry(hass, request, request_id, remote):
    """
    Answer an upload that arrived before the integration is set up.

    Normally that means the entry is unloaded and there is nothing to do. While
    the setup wizard is waiting, though, this is the whole point: the station
    has just been pointed at Home Assistant and its first upload is what the
    user is waiting to see. The sighting is recorded for the flow, and the
    station is answered 200 so it does not decide the server is broken.

    Args:
        hass: Home Assistant instance.
        request: The incoming aiohttp request.
        request_id: Counter value used in the logs.
        remote: Source address, for the logs.

    Returns:
        web.Response
    """

    onboarding = hass.data.get(DATA_ONBOARDING)

    if onboarding is None:
        _LOGGER.debug(
            "[#%d] Request from %s while the integration is not loaded",
            request_id,
            remote,
        )
        return web.json_response(
            {"status": "error", "detail": "Integration not loaded"},
            status=503,
        )

    params = request.rel_url.query
    device_id = _get_param(params, ID_PARAMS)
    expected = onboarding.get("key")

    if expected:
        offered = _get_param(params, AUTH_PARAMS) or ""

        if not hmac.compare_digest(str(offered), str(expected)):
            # Recorded rather than answered 401: the wizard can tell the user
            # their station reached Home Assistant but the key does not match,
            # which is far more useful than a silent timeout.
            onboarding["key_mismatch"] = True

            _LOGGER.warning(
                "[#%d] A station at %s reached the wizard with a wrong key",
                request_id,
                remote,
            )
            return web.json_response(
                {"status": "error", "detail": "Invalid password"}, status=401
            )

    onboarding["station"] = str(device_id) if device_id else remote

    _LOGGER.info(
        "[#%d] The setup wizard saw station '%s' at %s",
        request_id,
        onboarding["station"],
        remote,
    )

    return web.json_response({"status": "ok", "detail": "Setup in progress"})


class PwsView(HomeAssistantView):
    """HTTP endpoint receiving weather station updates."""

    requires_auth = False

    def __init__(self, hass: HomeAssistant, url: str):
        """
        Initialize the HTTP view.

        Args:
            hass: Home Assistant instance.
            url: URL path to register the view on.

        Returns:
            None
        """

        super().__init__()

        self.hass = hass
        self.url = url
        self.name = f"api:{DOMAIN}:{slugify(url)}"

    async def get(self, request):
        return await self._async_handle(request)

    async def _async_handle(self, request):
        """
        Handle one station update.

        Args:
            request: aiohttp.web.Request carrying the readings as query
                string parameters.

        Returns:
            web.Response: JSON summary, or an error following the codes
                documented by the WSLink API (200, 400, 401, 404, 405).
        """

        hass = self.hass
        start = time.monotonic()
        request_id = next(REQUEST_COUNTER)
        remote = request.remote or "unknown"

        runtime = hass.data.get(DOMAIN)

        if runtime is None:
            return _async_handle_without_entry(hass, request, request_id, remote)

        entry = runtime.entry
        debug = entry.options.get(CONF_DEBUG, False)

        def debug_log(message, *args):
            if debug:
                _LOGGER.info(message, *args)

        params = request.rel_url.query

        debug_log("[#%d] %s request from %s", request_id, request.method, remote)
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
            remote,
            request.raw_path,
            request.version,
            dict(request.headers),
            dict(params),
        )

        # Check the station key, from the options first, then the initial data.
        password = entry.options.get(CONF_PASSWORD)

        if password is None:
            password = entry.data.get(CONF_PASSWORD)

        if password:
            request_password = _get_param(params, AUTH_PARAMS) or ""

            if not hmac.compare_digest(str(request_password), str(password)):
                _LOGGER.warning(
                    "[#%d] Rejected a station at %s: wrong station key",
                    request_id,
                    remote,
                )
                announced_id = _get_param(params, ID_PARAMS)

                _async_report_rejection(
                    hass,
                    "invalid_station_key",
                    announced_id or remote,
                    {"ip": remote, "station_id": str(announced_id or "?")},
                )
                return web.json_response(
                    {"status": "error", "detail": "Invalid password"}, status=401
                )

        device_id = _get_param(params, ID_PARAMS)

        if not device_id:
            _LOGGER.warning(
                "[#%d] Rejected a station at %s: no device identifier",
                request_id,
                remote,
            )
            _async_report_rejection(
                hass, "missing_device_id", remote, {"ip": remote}
            )
            return web.json_response(
                {
                    "status": "error",
                    "detail": "Missing device identifier (ID or wsid)",
                },
                status=400,
            )

        _async_clear_rejections(hass, remote, device_id)

        runtime.last_request = dt_util.utcnow()

        device, is_new = runtime.get_device(device_id)

        if not device.register_request():
            # Answered before anything is recorded: a station stuck in a loop
            # is not reporting, and its readings should not reach the recorder
            # sixty times a minute.
            _LOGGER.warning(
                "[#%d] Station '%s' at %s is posting more than %d times a "
                "minute; answering 404 as the API prescribes",
                request_id,
                device_id,
                remote,
                RATE_LIMIT_REQUESTS,
            )
            return web.json_response(
                {"status": "error", "detail": "Too many requests"},
                status=404,
            )

        if is_new:
            debug_log("[#%d] New device detected: %s", request_id, device_id)
            ir.async_delete_issue(hass, DOMAIN, ISSUE_NO_STATION_YET)

        device.last_seen = _parse_timestamp(params) or dt_util.utcnow()
        device.was_available = True

        updated_keys = []
        unknown_keys = set()
        errors = 0

        for key, value in params.items():
            if key.lower() in RESERVED_PARAMS:
                continue

            try:
                canonical = SENSOR_KEY_MAP.get(key.lower())

                if canonical is None:
                    debug_log(
                        "[#%d] Ignoring unknown parameter '%s'='%s'",
                        request_id,
                        key,
                        value,
                    )
                    unknown_keys.add(key)
                    continue

                # Stored exactly as received, like every other reading: a
                # battery level is turned into a percentage when read, so the
                # binary sensors can still see the 1 or 0 the station sent.
                device.data[canonical] = parse_value(value)
                updated_keys.append(canonical)

            except Exception:
                errors += 1
                _LOGGER.exception(
                    "[#%d] Could not process '%s'='%s' from %s",
                    request_id,
                    key,
                    value,
                    remote,
                )

        if errors and not updated_keys:
            # Every recognised parameter failed and none produced a reading.
            # Unknown parameters do not count: a station speaking a newer API
            # version is not malformed, and telling it so would be wrong.
            _LOGGER.warning(
                "[#%d] Station '%s' at %s sent %d parameters and not one "
                "could be read; answering 405",
                request_id,
                device_id,
                remote,
                errors,
            )
            return web.json_response(
                {"status": "error", "detail": "Incorrect data format"},
                status=405,
            )

        _async_report_unknown_parameters(hass, device, unknown_keys)

        created = self._async_add_new_entities(runtime, device, updated_keys)

        # Only rewrite what this payload actually touched: a station posting
        # every minute would otherwise fill the recorder with unchanged states.
        # KEY_STATION_ONLINE has to be rewritten here rather than left to the
        # availability tick: accepting this payload already set was_available,
        # so the tick sees no change and would leave the entity saying the
        # station is offline for as long as it keeps posting.
        write_keys = [*updated_keys, KEY_LAST_UPDATE, KEY_STATION_ONLINE]

        if any(SENSOR_LIST[key].get("wind_offset") for key in updated_keys):
            write_keys.append(KEY_WIND_DIR_RAW)

        device.async_write_keys(write_keys)

        elapsed = time.monotonic() - start

        debug_log(
            "[#%d] Returning HTTP 200 (device=%s created=%d updated=%d "
            "errors=%d time=%.3fs)",
            request_id,
            device_id,
            created,
            len(updated_keys),
            errors,
            elapsed,
        )

        return web.json_response(
            {
                "status": "ok",
                "device": device_id,
                "created": created,
                "updated": len(updated_keys),
                "errors": errors,
            }
        )

    @staticmethod
    def _async_add_new_entities(runtime, device, updated_keys):
        """
        Create the entities this payload calls for, across every platform.

        Args:
            runtime: PwsRuntime for the config entry.
            device: PwsDevice being updated.
            updated_keys: Canonical keys present in the payload.

        Returns:
            int: Number of entities handed over to Home Assistant.
        """

        created = 0

        for platform, module, takes_keys in (
            ("sensor", sensor, True),
            ("binary_sensor", binary_sensor, True),
            ("number", number, False),
            ("button", button, False),
        ):
            entities = (
                module.build_new_entities(device, updated_keys)
                if takes_keys
                else module.build_new_entities(device)
            )

            if not entities:
                continue

            if runtime.async_add_entities(platform, entities):
                created += len(entities)
            else:
                # The platform is not ready yet. Drop the entities so the next
                # payload builds them again instead of leaving orphans behind.
                for entity in entities:
                    device.entities.pop(entity.entity_key, None)

        return created
