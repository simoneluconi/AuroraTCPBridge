"""Binary sensor platform for AuroraTCPBridge."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_info import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_RESPONDING, DOMAIN
from .coordinator import AuroraTCPBridgeCoordinator

RESPONDING_DESCRIPTION = BinarySensorEntityDescription(
    key=ATTR_RESPONDING,
    translation_key="responding",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AuroraTCPBridge responding binary sensor from a config entry."""
    coordinator: AuroraTCPBridgeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AuroraRespondingBinarySensor(coordinator, entry)])


class AuroraRespondingBinarySensor(CoordinatorEntity[AuroraTCPBridgeCoordinator], BinarySensorEntity):
    """Whether the inverter is currently responding to polls."""

    entity_description = RESPONDING_DESCRIPTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: AuroraTCPBridgeCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ATTR_RESPONDING}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Aurora / ABB / Power-One",
            model="Aurora TCP",
        )

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(ATTR_RESPONDING, False))
