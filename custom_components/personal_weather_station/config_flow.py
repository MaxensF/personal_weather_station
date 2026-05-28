"""Config flow for Personal Weather Station integration."""
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        if user_input is None:
            data_schema = vol.Schema({
                vol.Optional(CONF_PASSWORD): str,
            })
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema
            )

        return self.async_create_entry(title="Personal Weather Station", data=user_input)

class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_PASSWORD,
                    default=self._config_entry.options.get(
                        CONF_PASSWORD,
                        self._config_entry.data.get(CONF_PASSWORD, "")
                    )
                ): str
            })
        )
