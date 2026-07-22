"""Number platform for anova_bluetooth."""
from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AnovaDataUpdateCoordinator
from .entity import AnovaBluetoothEntity

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="timer_minutes",
        name="Timer Minutes",
        icon="mdi:timer-cog-outline",
        native_min_value=0,
        # Protocol limit: "set timer {:d}", [0, 6000] minutes.
        native_max_value=6000,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        AnovaBluetoothNumber(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AnovaBluetoothNumber(AnovaBluetoothEntity, NumberEntity):
    """Sets the Anova timer duration in minutes."""

    def __init__(
        self,
        coordinator: AnovaDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.coordinator = coordinator

    @property
    def native_value(self) -> float | None:
        """Return the timer value currently on the device."""
        if state := self.coordinator.circulator.state:
            return state.timer[0]
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Write a new timer duration to the device."""
        await self.coordinator.circulator.set_timer(int(value))
        await self.coordinator.async_request_refresh()
