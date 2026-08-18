"""DataUpdateCoordinator for AuroraTCPBridge.

Polls the Aurora/ABB inverter over TCP via aurorapy. Ports the reconnection
fix already applied to the original aurora_mqtt.py add-on: after
FAILURE_THRESHOLD consecutive polls with no response, the socket is closed
and reconnected from scratch, with exponential backoff (capped at
MAX_BACKOFF) between reconnect attempts. The backoff resets to the base poll
interval as soon as a poll gets a valid response. Without this, a wedged
socket previously required a manual restart to recover.
"""
from __future__ import annotations

import logging
import time
from datetime import timedelta

from aurorapy.client import AuroraTCPClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_LAST_RESPONSE,
    ATTR_RESPONDING,
    ATTR_STATUS,
    DOMAIN,
    FAILURE_THRESHOLD,
    MAX_BACKOFF,
    STATUS_NO_RESPONSE,
    STATUS_RESPONDING,
    STATUS_UNREACHABLE,
)

_LOGGER = logging.getLogger(__name__)


class AuroraTCPBridgeCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Aurora inverter and manages reconnection."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        address: int,
        poll_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.host = host
        self.port = port
        self.address = address
        self.poll_interval = poll_interval

        self._client: AuroraTCPClient | None = None
        self._consecutive_failures = 0
        self._reconnect_backoff = float(poll_interval)
        self._last_attempt_time = 0.0
        self._last_response_ts = None

    def _connect(self) -> bool:
        try:
            self._client = AuroraTCPClient(ip=self.host, port=self.port, address=self.address)
            self._client.connect()
            _LOGGER.info("Connected to Aurora inverter at %s:%s", self.host, self.port)
            return True
        except Exception as err:  # noqa: BLE001 - mirrors the add-on's tolerant connect
            _LOGGER.warning("Aurora TCP connect failed: %s", err)
            self._client = None
            return False

    def _close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass
        self._client = None

    def _poll(self) -> dict:
        """Blocking poll of the inverter. Runs in the executor."""
        result: dict = {}
        responding = False
        status = STATUS_UNREACHABLE
        now = time.time()

        if self._client is None:
            connected = False
            if now - self._last_attempt_time >= self._reconnect_backoff:
                self._last_attempt_time = now
                connected = self._connect()
                if connected:
                    self._reconnect_backoff = float(self.poll_interval)
                else:
                    self._reconnect_backoff = min(self._reconnect_backoff * 2, MAX_BACKOFF)
        else:
            connected = True

        if not connected:
            status = STATUS_UNREACHABLE
            _LOGGER.debug(
                "Aurora unreachable (TCP). Next reconnect attempt in %.0fs.",
                self._reconnect_backoff,
            )
        else:
            status = STATUS_NO_RESPONSE
            client = self._client

            def read(key: str, fn) -> None:
                nonlocal responding
                try:
                    result[key] = fn()
                    responding = True
                except Exception as err:  # noqa: BLE001 - one bad register shouldn't block the rest
                    _LOGGER.debug("%s read failed: %s", key, err)

            read("output_power", lambda: round(client.measure(3)))
            read("input_voltage", lambda: client.measure(23))
            read("input1_current", lambda: client.measure(25))
            read("input2_current", lambda: client.measure(27))
            read("daily_energy", lambda: client.cumulated_energy(period=0) / 1000.0)
            read("energy_week", lambda: client.cumulated_energy(period=1) / 1000.0)
            read("energy_month", lambda: client.cumulated_energy(period=3) / 1000.0)
            read("year_energy", lambda: client.cumulated_energy(period=4) / 1000.0)
            read("energy_total", lambda: client.cumulated_energy(period=5) / 1000.0)
            read("inverter_temperature", lambda: client.measure(21))

            status = STATUS_RESPONDING if responding else STATUS_NO_RESPONSE

        if responding:
            self._last_response_ts = dt_util.utcnow()
            self._consecutive_failures = 0
            self._reconnect_backoff = float(self.poll_interval)
        elif connected:
            self._consecutive_failures += 1
            if self._consecutive_failures >= FAILURE_THRESHOLD:
                _LOGGER.warning(
                    "No response from inverter for %d consecutive polls; forcing reconnect (next attempt in %.0fs)",
                    self._consecutive_failures,
                    self._reconnect_backoff,
                )
                self._close()
                self._consecutive_failures = 0
                self._last_attempt_time = time.time()
                self._reconnect_backoff = min(self._reconnect_backoff * 2, MAX_BACKOFF)

        result[ATTR_RESPONDING] = responding
        result[ATTR_STATUS] = status
        result[ATTR_LAST_RESPONSE] = self._last_response_ts
        return result

    async def _async_update_data(self) -> dict:
        return await self.hass.async_add_executor_job(self._poll)

    async def async_test_connection(self) -> bool:
        """Used by the config flow to validate host/port/address before setup."""
        return await self.hass.async_add_executor_job(self._test_connection)

    def _test_connection(self) -> bool:
        try:
            client = AuroraTCPClient(ip=self.host, port=self.port, address=self.address)
            client.connect()
            try:
                client.measure(3)
            finally:
                client.close()
            return True
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Connection test failed: %s", err)
            return False
