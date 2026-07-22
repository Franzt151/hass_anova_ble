"""Climate platform for anova_bluetooth."""
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PRECISION_TENTHS, UnitOfTemperature

from .const import DOMAIN
from .coordinator import AnovaDataUpdateCoordinator
from .entity import AnovaBluetoothEntity

from anova_ble import AnovaStatus

async def async_setup_entry(hass, entry: ConfigEntry, async_add_devices):
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([
        AnovaBluetoothClimate(
            coordinator=coordinator,
            entity_description=ClimateEntityDescription(
                key="water_bath",
                name="Sous Vide"
            )
        )
    ])


class AnovaBluetoothClimate(AnovaBluetoothEntity, ClimateEntity):
    """Anova Bluetooth Climate class."""

    def __init__(
        self,
        coordinator: AnovaDataUpdateCoordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.coordinator = coordinator

        self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )

        self._attr_max_temp = 211.8
        self._attr_min_temp = 41
        # Display current/target temperature to one decimal place.
        self._attr_precision = PRECISION_TENTHS
        self._attr_target_temperature_step = 0.1
        

    @property
    def target_temperature(self):
        if state := self.coordinator.circulator.state:
            return state.target_temp
        return None

    @property
    def current_temperature(self):
        if state := self.coordinator.circulator.state:
            return state.current_temp
        return None

    @property
    def hvac_mode(self):
        if state := self.coordinator.circulator.state:
            if state.status == AnovaStatus.Running:
                return HVACMode.HEAT
            else:
                return HVACMode.OFF
        else:
            return None

    async def async_set_temperature(self, **kwargs):
        await self.coordinator.circulator.set_temp(kwargs["temperature"])
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.HEAT:
            await self.coordinator.circulator.start()
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.circulator.stop()

        await self.coordinator.async_request_refresh()
