from homeassistant.components.select import SelectEntity

from .const import DOMAIN, MODE_SUMMER, MODE_WINTER


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SolarPriorityModeSelect(hass, entry)])


class SolarPriorityModeSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Vaihetila"
    _attr_options = [MODE_SUMMER, MODE_WINTER]
    _attr_icon = "mdi:solar-power"

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_phase_mode"
        self._attr_current_option = MODE_SUMMER

    async def async_select_option(self, option):
        if option in self._attr_options:
            self._attr_current_option = option
            self.async_write_ha_state()
