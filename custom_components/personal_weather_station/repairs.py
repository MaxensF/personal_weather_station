"""Repairs flows: onboarding a first station, and the two opt-in migrations."""

import asyncio
import time

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.helpers import issue_registry as ir

from .const import (
    DOMAIN,
    ISSUE_LEGACY_ENTITY_IDS,
    ISSUE_LEGACY_STATUS_SENSORS,
    ISSUE_NO_STATION_YET,
    STATION_WAIT_TIMEOUT,
)
from .instructions import async_placeholders_for_entry
from .migration import (
    async_find_legacy_entities,
    async_find_status_sensors,
    async_migrate_entity_ids,
    async_migrate_status_sensors,
)


class LegacyEntityIdsRepairFlow(RepairsFlow):
    """Ask before renaming anything the user may already point at."""

    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        renames = async_find_legacy_entities(self.hass, self._entry)

        if user_input is not None:
            async_migrate_entity_ids(self.hass, self._entry)
            ir.async_delete_issue(self.hass, DOMAIN, ISSUE_LEGACY_ENTITY_IDS)
            return self.async_create_entry(title="", data={})

        example_old, example_new = renames[0] if renames else ("", "")

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={
                "count": str(len(renames)),
                "example_old": example_old,
                "example_new": example_new,
            },
        )


class LegacyStatusSensorsRepairFlow(RepairsFlow):
    """Ask before dropping entities the user may already point at."""

    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        found = async_find_status_sensors(self.hass, self._entry)

        if user_input is not None:
            async_migrate_status_sensors(self.hass, self._entry)
            ir.async_delete_issue(self.hass, DOMAIN, ISSUE_LEGACY_STATUS_SENSORS)

            # Rebuild from a clean slate: the binary sensors then appear on the
            # station's next upload.
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry.entry_id)
            )

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={
                "count": str(len(found)),
                "example": found[0] if found else "",
            },
        )


async def _async_wait_for_station(hass, timeout):
    """
    Wait until a station posts, or give up.

    Polls the runtime rather than holding an event, so a reload in the middle
    of the wait does not leave the flow waiting on something that no longer
    exists.

    Args:
        hass: Home Assistant instance.
        timeout: Seconds to wait.

    Returns:
        str or None: the identifier of the station that showed up.
    """

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        runtime = hass.data.get(DOMAIN)

        if runtime is not None and runtime.devices:
            return next(iter(runtime.devices))

        await asyncio.sleep(1)

    return None


class NoStationYetRepairFlow(RepairsFlow):
    """Show what to type into the station, then watch for its first upload."""

    def __init__(self, entry):
        self._entry = entry
        self._task = None
        self._station = None

    async def async_step_init(self, user_input=None):
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            return await self.async_step_wait()

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders=async_placeholders_for_entry(
                self.hass, self._entry
            ),
        )

    async def async_step_wait(self, user_input=None):
        """Watch for the first upload while the user is still looking."""

        if self._task is None:
            self._task = self.hass.async_create_task(
                _async_wait_for_station(self.hass, STATION_WAIT_TIMEOUT)
            )

        if not self._task.done():
            return self.async_show_progress(
                step_id="wait",
                progress_action="waiting_for_station",
                progress_task=self._task,
            )

        self._station = self._task.result()
        self._task = None

        return self.async_show_progress_done(
            next_step_id="received" if self._station else "timeout"
        )

    async def async_step_received(self, user_input=None):
        if user_input is not None:
            # Home Assistant deletes the issue for any ending that is not an
            # abort, so there is nothing to clear here.
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="received",
            data_schema=vol.Schema({}),
            description_placeholders={"station": self._station},
        )

    async def async_step_timeout(self, user_input=None):
        """Nothing arrived. The repair stays so the user can come back."""

        if user_input is not None:
            # Aborting is the only ending that leaves the issue in place:
            # RepairsFlowManager.async_finish_flow deletes it for every other
            # result type, which would mark a failed wait as resolved.
            return self.async_abort(reason="not_received")

        return self.async_show_form(
            step_id="timeout",
            data_schema=vol.Schema({}),
            description_placeholders={
                "minutes": str(STATION_WAIT_TIMEOUT // 60),
                **async_placeholders_for_entry(self.hass, self._entry),
            },
        )


FLOWS = {
    ISSUE_LEGACY_ENTITY_IDS: LegacyEntityIdsRepairFlow,
    ISSUE_LEGACY_STATUS_SENSORS: LegacyStatusSensorsRepairFlow,
    ISSUE_NO_STATION_YET: NoStationYetRepairFlow,
}


async def async_create_fix_flow(hass, issue_id, data):
    """Build the flow behind a repair."""

    entry = hass.config_entries.async_get_entry((data or {}).get("entry_id"))

    return FLOWS[issue_id](entry)
