"""AnovaBluetoothEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, MODEL
from .coordinator import AnovaDataUpdateCoordinator


class AnovaBluetoothEntity(CoordinatorEntity):
    """AnovaBluetoothEntity class."""

    def __init__(self, coordinator: AnovaDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            # The blueprint template put VERSION here, which is why the
            # device card showed "0.0.1" where the model should be.
            model=MODEL,
            sw_version=coordinator.integration_version,
            manufacturer="Anova Applied Electronics, Inc",
            connections={
                ("bluetooth", coordinator.config_entry.unique_id)
            },
        )
