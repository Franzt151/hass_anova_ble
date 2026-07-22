"""DataUpdateCoordinator for anova_bluetooth."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, LOGGER
import asyncio

from anova_ble import AnovaBLEPrecisionCooker

# BLE connection setup (via bleak_retry_connector) routinely takes longer
# than a few seconds on a weak link, and update_state() issues five
# separate command round-trips. The original 5s budget aborted mid-connect.
UPDATE_TIMEOUT = 25
UPDATE_INTERVAL = timedelta(seconds=30)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AnovaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        circulator: AnovaBLEPrecisionCooker,
    ) -> None:
        """Initialize."""
        self.circulator = circulator
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with asyncio.timeout(UPDATE_TIMEOUT):
                await self.circulator.connect()
                await self.circulator.update_state()
                LOGGER.debug("Updated state: %s", self.circulator.state)
                return
        except asyncio.TimeoutError as exception:
            raise UpdateFailed(
                f"Timed out after {UPDATE_TIMEOUT}s talking to the cooker "
                f"(connect + read). Usually weak signal."
            ) from exception
        except Exception as exception:
            # Include the exception type, since some library exceptions are
            # raised with no message at all and would otherwise log blank.
            raise UpdateFailed(
                f"{type(exception).__name__}: {exception}"
            ) from exception
