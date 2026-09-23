"""Repairs flows: the two opt-in migrations."""

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.helpers import issue_registry as ir

from .const import (
    DOMAIN,
    ISSUE_LEGACY_ENTITY_IDS,
    ISSUE_LEGACY_STATUS_SENSORS,
)
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


FLOWS = {
    ISSUE_LEGACY_ENTITY_IDS: LegacyEntityIdsRepairFlow,
    ISSUE_LEGACY_STATUS_SENSORS: LegacyStatusSensorsRepairFlow,
}


async def async_create_fix_flow(hass, issue_id, data):
    """Build the flow behind a repair."""

    entry = hass.config_entries.async_get_entry((data or {}).get("entry_id"))

    return FLOWS[issue_id](entry)
