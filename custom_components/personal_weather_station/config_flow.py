"""Config flow for the Personal Weather Station integration."""

import asyncio
import time

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback

from .const import (
    CONF_AVAILABILITY_TIMEOUT,
    CONF_DEBUG,
    DATA_ONBOARDING,
    DEFAULT_AVAILABILITY_TIMEOUT,
    DOMAIN,
    STATION_WAIT_TIMEOUT,
)
from .instructions import (
    async_ensure_images,
    async_placeholders,
    async_placeholders_for_entry,
    image,
)

AVAILABILITY_TIMEOUT_SELECTOR = vol.All(vol.Coerce(int), vol.Range(min=0, max=1440))

# One screen per screen of the station's app, in the order they appear there.
WALKTHROUGH = {
    "station": "wslink-1-your-device.jpeg",
    "settings": "wslink-2-settings.jpeg",
    "server": "wslink-3-weather-server.jpeg",
    "form": "wslink-4-other-server.jpeg",
    "confirm": "wslink-5-confirm-and-exit.jpeg",
}


class Walkthrough:
    """
    The five screens of the station's app, walked one at a time.

    Shared by both flows: someone adding a second station needs exactly the
    same guidance as someone adding the first, and keeping one copy means the
    screens cannot drift apart or be translated twice.
    """

    # Where the last screen leads. Setting up waits for the first upload;
    # adding another station has nothing to wait for, the endpoints are already
    # listening and the device turns up on its own.
    _after_confirm = "wait"

    def _walkthrough_placeholders(self):
        """The addresses and key hint, worked out for this flow."""

        raise NotImplementedError

    async def _async_walk(self, step, next_step, user_input):
        if user_input is not None:
            return await getattr(self, f"async_step_{next_step}")()

        return self.async_show_form(
            step_id=step,
            data_schema=vol.Schema({}),
            description_placeholders={
                "image": image(WALKTHROUGH[step]),
                **self._walkthrough_placeholders(),
            },
        )

    async def async_step_station(self, user_input=None):
        return await self._async_walk("station", "settings", user_input)

    async def async_step_settings(self, user_input=None):
        return await self._async_walk("settings", "server", user_input)

    async def async_step_server(self, user_input=None):
        return await self._async_walk("server", "form", user_input)

    async def async_step_form(self, user_input=None):
        return await self._async_walk("form", "confirm", user_input)

    async def async_step_confirm(self, user_input=None):
        return await self._async_walk("confirm", self._after_confirm, user_input)


class ConfigFlow(Walkthrough, config_entries.ConfigFlow, domain=DOMAIN):
    """Walk the user through the station app, then wait for its first upload."""

    def __init__(self):
        self._data = {}
        self._task = None
        self._station = None

        # Whether the closing screen has been shown. Home Assistant carries the
        # user_input that submitted the previous step into the step that a
        # finished progress task lands on, so "did the user submit?" cannot be
        # read from user_input here: it would skip the screen entirely for the
        # common case of a station that already posted.
        self._closed = False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    @callback
    def async_remove(self):
        """Stop accepting uploads on behalf of a flow that is going away."""

        self.hass.data.pop(DATA_ONBOARDING, None)

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Optional(CONF_PASSWORD): str}),
            )

        self._data = user_input

        # The screenshots and the endpoints both have to be live before the
        # entry exists: Home Assistant only calls async_setup once one does.
        await async_ensure_images(self.hass)

        # Registered from here, not from the wait step. A station configured
        # while the user is still reading is then already recorded when the
        # wait begins, and its upload is not thrown away.
        from . import async_ensure_views

        async_ensure_views(self.hass)

        self.hass.data[DATA_ONBOARDING] = {
            "key": self._data.get(CONF_PASSWORD),
            "station": None,
            "key_mismatch": False,
        }

        return await self.async_step_station()

    def _walkthrough_placeholders(self):
        return async_placeholders(self.hass, self._data.get(CONF_PASSWORD))

    async def async_step_wait(self, user_input=None):
        """Watch for the first upload while the user is still looking."""

        if self._task is None:
            self._task = self.hass.async_create_task(
                _async_wait_for_upload(self.hass, STATION_WAIT_TIMEOUT)
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
        if self._closed:
            return self._async_finish()

        self._closed = True

        return self.async_show_form(
            step_id="received",
            data_schema=vol.Schema({}),
            description_placeholders={"station": self._station},
        )

    async def async_step_timeout(self, user_input=None):
        """
        Nothing arrived in time.

        The entry is still created: the endpoints only start listening for real
        once it exists, and a repair picks the user back up from here. Throwing
        the configuration away would mean typing it all again.
        """

        if self._closed:
            return self._async_finish()

        self._closed = True

        onboarding = self.hass.data.get(DATA_ONBOARDING) or {}

        return self.async_show_form(
            step_id="timeout",
            data_schema=vol.Schema({}),
            description_placeholders={
                "minutes": str(STATION_WAIT_TIMEOUT // 60),
                "key_hint_extra": (
                    "\n\n> ⚠️ A station did reach Home Assistant, but the station "
                    "key it sent does not match the one you entered. Correct it "
                    "in the station app, or leave the key blank here."
                    if onboarding.get("key_mismatch")
                    else ""
                ),
                **async_placeholders(self.hass, self._data.get(CONF_PASSWORD)),
            },
        )

    def _async_finish(self):
        self.hass.data.pop(DATA_ONBOARDING, None)

        return self.async_create_entry(
            title="Personal Weather Station", data=self._data
        )


async def _async_wait_for_upload(hass, timeout):
    """
    Wait until a station posts, or give up.

    Polls rather than holding an event: the flow can be abandoned at any point,
    and a task waiting on something nobody will ever set would outlive it.

    Args:
        hass: Home Assistant instance.
        timeout: Seconds to wait.

    Returns:
        str or None: the identifier the station announced.
    """

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        onboarding = hass.data.get(DATA_ONBOARDING)

        if onboarding is None:
            return None

        if onboarding.get("station"):
            return onboarding["station"]

        await asyncio.sleep(1)

    return None


class OptionsFlowHandler(Walkthrough, config_entries.OptionsFlow):
    """Handle the options, and walk a second station through the same screens."""

    _after_confirm = "done"

    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _walkthrough_placeholders(self):
        return async_placeholders_for_entry(self.hass, self._config_entry)

    async def async_step_init(self, user_input=None):
        """
        Offer the settings, or the instructions for setting up a station.

        The onboarding repair goes away once a station has posted, so this is
        where the address to point a second one at stays reachable.
        """

        return self.async_show_menu(
            step_id="init", menu_options=["options", "instructions"]
        )

    async def async_step_instructions(self, user_input=None):
        """Menu entry point: hand straight over to the walkthrough."""

        return await self.async_step_station()

    async def async_step_done(self, user_input=None):
        """Close the dialog, leaving the options exactly as they were."""

        return self.async_create_entry(title="", data=dict(self._config_entry.options))

    async def async_step_options(self, user_input=None):
        if user_input is not None:
            # Merge rather than replace: the per station wind calibration lives
            # in the options too and is not part of this form.
            return self.async_create_entry(
                title="", data={**self._config_entry.options, **user_input}
            )

        options = self._config_entry.options

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PASSWORD,
                        default=options.get(
                            CONF_PASSWORD,
                            self._config_entry.data.get(CONF_PASSWORD, ""),
                        ),
                    ): str,
                    vol.Optional(
                        CONF_AVAILABILITY_TIMEOUT,
                        default=options.get(
                            CONF_AVAILABILITY_TIMEOUT, DEFAULT_AVAILABILITY_TIMEOUT
                        ),
                    ): AVAILABILITY_TIMEOUT_SELECTOR,
                    vol.Optional(
                        CONF_DEBUG, default=options.get(CONF_DEBUG, False)
                    ): bool,
                }
            ),
        )
