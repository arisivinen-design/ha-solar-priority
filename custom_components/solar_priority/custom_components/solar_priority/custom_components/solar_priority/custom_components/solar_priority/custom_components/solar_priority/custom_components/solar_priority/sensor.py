from datetime import timedelta
import asyncio
import math

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *


SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    controller = SolarPriorityController(hass, entry)
    hass.data[DOMAIN][entry.entry_id]["controller"] = controller

    async_add_entities(
        [
            SolarSurplus(controller),
            SolarState(controller),
            SolarPrice(controller),
        ]
    )

    await controller.update()

    entry.async_on_unload(
        async_track_time_interval(
            hass,
            controller.update,
            SCAN_INTERVAL,
        )
    )


class SolarPriorityController:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.data = entry.data

        self.surplus = 0.0
        self.price = None
        self.state_text = "Käynnistyy"

        self.last_current = None
        self.last_paused = None
        self.last_water = None

    def number(self, entity_id, default=0.0):
        state = self.hass.states.get(entity_id)

        if not state or state.state in ("unknown", "unavailable"):
            return default

        try:
            return float(state.state)
        except (TypeError, ValueError):
            return default

    async def update(self, _now=None):
        grid = self.number(self.data[CONF_GRID_POWER])
        raw_price = self.number(
            self.data[CONF_NORD_POOL],
            math.nan,
        )

        self.price = (
            None if math.isnan(raw_price) else raw_price
        )

        # Shelly:
        # negative = electricity exported to grid
        self.surplus = max(0.0, -grid)

        min_a = float(self.data[CONF_MIN_CURRENT])
        max_a = float(self.data[CONF_MAX_CURRENT])
        margin = float(self.data[CONF_SURPLUS_MARGIN])
        water_power = float(self.data[CONF_WATER_POWER])
        cheap_limit = float(self.data[CONF_CHEAP_PRICE])
        grid_limit = float(self.data[CONF_GRID_LIMIT])

        cheap = (
            self.price is not None
            and self.price <= cheap_limit
        )

        mode = hass_mode = self.hass.data[DOMAIN][
            self.entry.entry_id
        ]["mode"]

        three_phase = mode == MODE_WINTER

        watts_per_amp = (
            230.0 * math.sqrt(3)
            if three_phase
            else 230.0
        )

        # -----------------------------------------
        # 1. SOLAR SURPLUS -> EV FIRST
        # -----------------------------------------

        minimum_ev_power = min_a * watts_per_amp

        if self.surplus >= minimum_ev_power + margin:

            available_amps = (
                (self.surplus - margin)
                / watts_per_amp
            )

            amps = min(
                max_a,
                max(
                    min_a,
                    math.floor(
                        available_amps * 2
                    ) / 2,
                ),
            )

            await self.set_wallbox(
                amps,
                paused=False,
            )

            ev_power = amps * watts_per_amp

            water_on = (
                self.surplus
                >= ev_power + water_power + margin
            )

            await self.set_water(water_on)

            self.state_text = (
                f"Aurinko: auto {amps:.1f} A"
                + (
                    ", vesi ON"
                    if water_on
                    else ""
                )
            )

            return

        # -----------------------------------------
        # 2. CHEAP NORD POOL PRICE
        # -----------------------------------------

        if cheap:
            await self.set_wallbox(
                max_a,
                paused=False,
            )

            # Allow water heater only if grid import
            # stays below configured limit.
            import_power = max(0.0, grid)

            water_on = (
                import_power + water_power
                <= grid_limit
            )

            await self.set_water(water_on)

            self.state_text = (
                f"Halpa tunti: auto {max_a:.0f} A"
                + (
                    ", vesi ON"
                    if water_on
                    else ""
                )
            )

            return

        # -----------------------------------------
        # 3. NO SURPLUS / NO CHEAP PRICE
        # -----------------------------------------

        await self.set_water(False)

        await self.set_wallbox(
            min_a,
            paused=True,
        )

        self.state_text = (
            "Odotus: ei ylijäämää "
            "eikä halpaa tuntia"
        )

    async def set_wallbox(
        self,
        amps: float,
        paused: bool,
    ):
        current_id = self.data[
            CONF_WALLBOX_CURRENT
        ]

        pause_id = self.data[
            CONF_WALLBOX_PAUSE
        ]

        # Never set Wallbox current to 0 A.
        # The Wallbox minimum is normally 6 A.

        if self.last_current != amps:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {
                    "entity_id": current_id,
                    "value": float(amps),
                },
                blocking=True,
            )

            self.last_current = amps

        # For the Wallbox "Keskeytä/jatka" switch:
        # ON = pause
        # OFF = resume.

        if self.last_paused != paused:
            await self.hass.services.async_call(
                "switch",
                "turn_on" if paused else "turn_off",
                {
                    "entity_id": pause_id,
                },
                blocking=True,
            )

            self.last_paused = paused

    async def set_water(self, on: bool):
        if self.last_water == on:
            return

        await self.hass.services.async_call(
            "switch",
            "turn_on" if on else "turn_off",
            {
                "entity_id": self.data[
                    CONF_WATER_SWITCH
                ],
            },
            blocking=True,
        )

        self.last_water = on


class Base(SensorEntity):

    def __init__(self, controller):
        self.controller = controller
        self._attr_should_poll = False

    @property
    def available(self):
        return True


class SolarSurplus(Base):

    _attr_name = "Aurinko-ohjaus ylijäämä"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:solar-power"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = (
            f"{controller.entry.entry_id}_surplus"
        )

    @property
    def native_value(self):
        return round(
            self.controller.surplus,
            0,
        )


class SolarState(Base):

    _attr_name = "Aurinko-ohjaus tila"
    _attr_icon = "mdi:state-machine"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = (
            f"{controller.entry.entry_id}_state"
        )

    @property
    def native_value(self):
        return self.controller.state_text


class SolarPrice(Base):

    _attr_name = "Aurinko-ohjaus Nord Pool hinta"
    _attr_native_unit_of_measurement = "EUR/kWh"
    _attr_icon = "mdi:currency-eur"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = (
            f"{controller.entry.entry_id}_price"
        )

    @property
    def native_value(self):
        return self.controller.price
