"""Config flow for AuroraTCPBridge."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .const import (
    CONF_ADDRESS,
    CONF_POLL_INTERVAL,
    DEFAULT_ADDRESS,
    DEFAULT_PORT,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)
from .coordinator import AuroraTCPBridgeCoordinator

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_ADDRESS, default=DEFAULT_ADDRESS): vol.Coerce(int),
        vol.Required(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
    }
)


class AuroraTCPBridgeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AuroraTCPBridge."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_ADDRESS]}"
            )
            self._abort_if_unique_id_configured()

            probe = AuroraTCPBridgeCoordinator(
                self.hass,
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                address=user_input[CONF_ADDRESS],
                poll_interval=user_input[CONF_POLL_INTERVAL],
            )
            try:
                connected = await probe.async_test_connection()
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error testing Aurora connection")
                errors["base"] = "unknown"
            else:
                if not connected:
                    errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=f"Aurora ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
