"""Runtime objects shared between the HTTP handler and the entity platforms."""

import time
from collections import deque
from datetime import timedelta

from homeassistant.core import callback
from homeassistant.util import dt as dt_util

from .const import (
    CONF_AVAILABILITY_TIMEOUT,
    CONF_WIND_OFFSETS,
    DEFAULT_AVAILABILITY_TIMEOUT,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    WIND_DIR_PRIMARY_KEYS,
    WIND_OFFSET_KEYS,
)


class PwsDevice:
    """
    Represents a Personal Weather Station (PWS) device.

    Attributes:
        hass: Home Assistant instance.
        entry: Config entry owning the device.
        device_id: Unique identifier of the device, as announced by the station.
        data: Raw sensor values keyed by sensor type, exactly as received.
        entities: Every entity attached to the device, keyed by entity key.
        unknown_keys: Parameters this station sent that we do not recognise.
        legacy_entity_ids: Whether this device already carries the entity IDs
            released up to 1.0.8, which repeat the station name twice.
        legacy_status_sensors: Whether its connection and leak keys are still
            numeric sensors rather than binary sensors.
        last_seen: When the station last posted a valid payload.
        was_available: Availability at the last periodic check.
    """

    def __init__(self, hass, entry, device_id):
        """
        Initialize the PWS device.

        Args:
            hass: Home Assistant instance.
            entry: Config entry owning the device.
            device_id: Unique ID of the device.

        Returns:
            None
        """

        self.hass = hass
        self.entry = entry
        self.device_id = device_id

        # Values are stored exactly as received. The wind calibration offset is
        # applied when reading, never here: correcting in place would make a
        # second calibration compound the error instead of replacing it.
        self.data = {}

        self.entities = {}
        self.unknown_keys = set()

        self.last_seen = None
        self.was_available = True

        # Arrival times of the recent requests, for the rate limit. Bounded by
        # the limit itself, so it cannot grow however hard a station tries.
        self._requests = deque(maxlen=RATE_LIMIT_REQUESTS)

        # Devices seen for the first time get the shorter, modern entity IDs.
        # Existing ones keep theirs so nothing an automation or a dashboard
        # points at ever moves on its own.
        self.legacy_entity_ids = False
        self.legacy_status_sensors = False

    def register_request(self):
        """
        Record an incoming request and say whether it is within the rate limit.

        Uses the monotonic clock rather than the wall clock: a station
        correcting its time, or the host adjusting for daylight saving, must
        not open or close the window by an hour.

        Returns:
            bool: False when the station is posting faster than the API allows,
                in which case the request should be answered 404 and dropped.
        """

        now = time.monotonic()

        # A full deque means the oldest of the last RATE_LIMIT_REQUESTS is
        # still in the window, so this one is over the limit.
        if len(self._requests) == RATE_LIMIT_REQUESTS and (
            now - self._requests[0] < RATE_LIMIT_WINDOW
        ):
            return False

        self._requests.append(now)

        return True

    @property
    def availability_timeout(self):
        """Grace period before the station is considered offline, or None."""

        try:
            minutes = int(
                self.entry.options.get(
                    CONF_AVAILABILITY_TIMEOUT, DEFAULT_AVAILABILITY_TIMEOUT
                )
            )
        except (TypeError, ValueError):
            minutes = DEFAULT_AVAILABILITY_TIMEOUT

        return timedelta(minutes=minutes) if minutes > 0 else None

    @property
    def available(self):
        """
        Whether the station is still considered alive.

        A device that has never reported is treated as available: this happens
        right after a restart, before the first payload comes in, and marking
        every restored entity unavailable at that point would be noise.
        """

        timeout = self.availability_timeout

        if timeout is None or self.last_seen is None:
            return True

        return dt_util.utcnow() - self.last_seen <= timeout

    @property
    def wind_offset(self):
        """Calibration offset in degrees applied to the wind directions."""

        offsets = self.entry.options.get(CONF_WIND_OFFSETS) or {}

        try:
            return int(offsets.get(self.device_id, 0) or 0) % 360
        except (TypeError, ValueError):
            return 0

    async def async_set_wind_offset(self, offset):
        """
        Persist the calibration offset in the config entry options.

        Deliberately not stored as a restored entity state: an offset is
        configuration, and losing it to a recorder purge would silently put
        every wind direction back off course.

        Args:
            offset: Offset in degrees. 0 removes the calibration.

        Returns:
            None
        """

        offset = int(offset) % 360
        offsets = dict(self.entry.options.get(CONF_WIND_OFFSETS) or {})

        if offset:
            offsets[self.device_id] = offset
        else:
            offsets.pop(self.device_id, None)

        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, CONF_WIND_OFFSETS: offsets},
        )

    @property
    def raw_wind_direction(self):
        """Uncorrected direction used as the reference when calibrating."""

        for key in WIND_DIR_PRIMARY_KEYS:
            value = self.data.get(key)
            if isinstance(value, (int, float)):
                return value

        return None

    @property
    def has_wind_direction(self):
        """Whether the station ever reported a wind direction."""

        return any(
            key in self.data or key in self.entities for key in WIND_OFFSET_KEYS
        )

    @callback
    def async_write_keys(self, keys):
        """
        Rewrite the state of the entities matching the given keys.

        Args:
            keys: Iterable of entity keys. Unknown keys are ignored.

        Returns:
            None
        """

        for key in keys:
            entity = self.entities.get(key)
            if entity is not None:
                entity.update_state()

    @callback
    def async_write_states(self):
        """Rewrite the state of every entity attached to this device."""

        for entity in list(self.entities.values()):
            entity.update_state()


class PwsRuntime:
    """
    Holds everything the HTTP handler needs, for the single config entry.

    The integration only ever has one config entry (see "single_config_entry" in
    the manifest): one HTTP server, one station key, any number of stations
    posting to it.
    """

    def __init__(self, hass, entry):
        """
        Initialize the runtime.

        Args:
            hass: Home Assistant instance.
            entry: Config entry being set up.

        Returns:
            None
        """

        self.hass = hass
        self.entry = entry

        self.devices = {}

        # Filled in by each platform as it is set up.
        self.add_entities = {}

        self.last_request = None
        self.cancel_availability = None

    def get_device(self, device_id):
        """
        Return the device for this ID, creating it on first sight.

        Args:
            device_id: Identifier announced by the station.

        Returns:
            tuple: (PwsDevice, bool) where the bool says whether it is new.
        """

        if device_id in self.devices:
            return self.devices[device_id], False

        device = PwsDevice(self.hass, self.entry, device_id)
        self.devices[device_id] = device

        return device, True

    def async_add_entities(self, platform, entities):
        """
        Register new entities with the matching platform.

        Args:
            platform: Platform name, e.g. "sensor".
            entities: Entities to add. Ignored when empty.

        Returns:
            bool: True when the entities were handed over to Home Assistant.
        """

        if not entities:
            return True

        add_entities = self.add_entities.get(platform)

        if add_entities is None:
            return False

        add_entities(entities)
        return True
