import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .view import MirdomProxyView

DOMAIN = "mirdom_proxy"
CONF_SECRET = "secret"
CONF_AGENT_URL = "agent_url"
DEFAULT_AGENT_URL = "http://localhost:8088"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SECRET): cv.string,
                vol.Optional(CONF_AGENT_URL, default=DEFAULT_AGENT_URL): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    conf = config[DOMAIN]
    hass.http.register_view(
        MirdomProxyView(hass, conf[CONF_SECRET], conf.get(CONF_AGENT_URL, DEFAULT_AGENT_URL))
    )
    return True
