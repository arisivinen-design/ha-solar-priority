import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_GRID_POWER,
    CONF_WALLBOX_CURRENT,
    CONF_WALLBOX_PAUSE,
    CONF_WATER_SWITCH,
    CONF_NORD_POOL,
    CONF_MIN_CURRENT,
    CONF_MAX_CURRENT,
    CONF_CHEAP_PRICE,
    CONF_SURPLUS_MARGIN,
    CONF_GRID_LIMIT,
    CONF_WATER_POWER,
    DEFAULT_MIN_CURRENT,
    DEFAULT_MAX_CURRENT,
    DEFAULT_CHEAP_PRICE,
    DEFAULT_SURPLUS_MARGIN,
    DEFAULT_GRID_LIMIT,
    DEFAULT_WATER_POWER,
    DOMAIN,
)


class SolarPriorityConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Aurinko-ohjaus",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GRID_POWER,
                    default="sensor.shellypro3em_c8f09e82ede4_teho",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor"
                    )
                ),
                vol.Required(
                    CONF_WALLBOX_CURRENT,
                    default="number.wallbox_pulsarplus_sn_244017_suurin_latausvirta",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="number"
                    )
                ),
                vol.Required(
                    CONF_WALLBOX_PAUSE,
                    default="switch.wallbox_pulsarplus_sn_244017_keskeyta_jatka",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="switch"
                    )
                ),
                vol.Required(
                    CONF_WATER_SWITCH,
                    default="switch.shellypro3_ec6260882ad0_output_0",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="switch"
                    )
                ),
                vol.Required(
                    CONF_NORD_POOL,
                    default="sensor.nord_pool_fi_current_price",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor"
                    )
                ),
                vol.Optional(
                    CONF_MIN_CURRENT,
                    default=DEFAULT_MIN_CURRENT,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_MAX_CURRENT,
                    default=DEFAULT_MAX_CURRENT,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_CHEAP_PRICE,
                    default=DEFAULT_CHEAP_PRICE,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_SURPLUS_MARGIN,
                    default=DEFAULT_SURPLUS_MARGIN,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_GRID_LIMIT,
                    default=DEFAULT_GRID_LIMIT,
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_WATER_POWER,
                    default=DEFAULT_WATER_POWER,
                ): vol.Coerce(float),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
