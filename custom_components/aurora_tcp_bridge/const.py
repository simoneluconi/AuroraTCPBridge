"""Constants for the AuroraTCPBridge integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)

DOMAIN = "aurora_tcp_bridge"

CONF_ADDRESS = "address"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = 2
DEFAULT_POLL_INTERVAL = 10

# After this many consecutive polls with no response, the coordinator closes
# the socket and reconnects from scratch instead of continuing to reuse a
# stale connection. Ports the fix already applied to the original add-on,
# where a wedged socket only recovered after a manual restart.
FAILURE_THRESHOLD = 3
# Reconnect attempts back off exponentially (capped) so a long inverter-silent
# period (e.g. overnight, no PV output) doesn't hammer the TCP gateway with
# constant reconnects. Backoff resets to poll_interval on the first successful
# response.
MAX_BACKOFF = 300  # 5 minutes

# Cumulative counters must hold their last known value across a failed poll
# instead of going unknown - they don't change while the inverter is asleep,
# and losing them mid-stream is what breaks the Energy Dashboard's
# total_increasing statistic for energy_total.
HOLD_LAST_VALUE_KEYS = (
    "daily_energy",
    "energy_week",
    "energy_month",
    "year_energy",
    "energy_total",
    "inverter_temperature",
)
# Instantaneous readings default to 0 when the inverter isn't responding
# (e.g. overnight with no PV production) rather than going unknown, which
# otherwise breaks history graphs and templates that expect a number.
ZERO_ON_NO_RESPONSE_KEYS = (
    "output_power",
    "input_voltage",
    "input1_current",
    "input2_current",
)

STATUS_RESPONDING = "responding"
STATUS_NO_RESPONSE = "no_response"
STATUS_UNREACHABLE = "unreachable"

ATTR_RESPONDING = "inverter_responding"
ATTR_STATUS = "inverter_status"
ATTR_LAST_RESPONSE = "inverter_last_response"


@dataclass(frozen=True, kw_only=True)
class AuroraSensorEntityDescription(SensorEntityDescription):
    """Describes an AuroraTCPBridge sensor."""


SENSOR_DESCRIPTIONS: tuple[AuroraSensorEntityDescription, ...] = (
    AuroraSensorEntityDescription(
        key="output_power",
        translation_key="output_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AuroraSensorEntityDescription(
        key="input_voltage",
        translation_key="input_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    AuroraSensorEntityDescription(
        key="input1_current",
        translation_key="input1_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    AuroraSensorEntityDescription(
        key="input2_current",
        translation_key="input2_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    AuroraSensorEntityDescription(
        key="daily_energy",
        translation_key="daily_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AuroraSensorEntityDescription(
        key="energy_week",
        translation_key="energy_week",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AuroraSensorEntityDescription(
        key="energy_month",
        translation_key="energy_month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AuroraSensorEntityDescription(
        key="year_energy",
        translation_key="year_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AuroraSensorEntityDescription(
        key="energy_total",
        translation_key="energy_total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AuroraSensorEntityDescription(
        key="inverter_temperature",
        translation_key="inverter_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    AuroraSensorEntityDescription(
        key=ATTR_STATUS,
        translation_key="status",
        icon="mdi:information-outline",
    ),
    AuroraSensorEntityDescription(
        key=ATTR_LAST_RESPONSE,
        translation_key="last_response",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
    ),
)
