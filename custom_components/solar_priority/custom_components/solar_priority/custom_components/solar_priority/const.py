from homeassistant.const import Platform

DOMAIN = "solar_priority"

CONF_GRID_POWER = "grid_power"
CONF_WALLBOX_CURRENT = "wallbox_current"
CONF_WALLBOX_PAUSE = "wallbox_pause"
CONF_WATER_SWITCH = "water_switch"
CONF_NORD_POOL = "nord_pool"

CONF_MIN_CURRENT = "min_current"
CONF_MAX_CURRENT = "max_current"
CONF_CHEAP_PRICE = "cheap_price"
CONF_SURPLUS_MARGIN = "surplus_margin"
CONF_GRID_LIMIT = "grid_limit"
CONF_WATER_POWER = "water_power"

DEFAULT_MIN_CURRENT = 6.0
DEFAULT_MAX_CURRENT = 16.0
DEFAULT_CHEAP_PRICE = 0.08
DEFAULT_SURPLUS_MARGIN = 300.0
DEFAULT_GRID_LIMIT = 10000.0
DEFAULT_WATER_POWER = 3000.0

MODE_SUMMER = "Kesä (1-vaihe)"
MODE_WINTER = "Talvi (3-vaihe)"

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
]
