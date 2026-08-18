"""Sensor platform for AuroraTCPBridge."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DESCRIPTIONS, AuroraSensorEntityDescription
from .coordinator import AuroraTCPBridgeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AuroraTCPBridge sensors from a config entry."""
    coordinator: AuroraTCPBridgeCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AuroraSensor(coordinator, entry, description) for description in SENSOR_DESCRIPTIONS
    )


class AuroraSensor(CoordinatorEntity[AuroraTCPBridgeCoordinator], SensorEntity):
    """Representation of an AuroraTCPBridge sensor."""

    entity_description: AuroraSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AuroraTCPBridgeCoordinator,
        entry: ConfigEntry,
        description: AuroraSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aurora / ABB / Power-One",
            model="Aurora TCP",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)
