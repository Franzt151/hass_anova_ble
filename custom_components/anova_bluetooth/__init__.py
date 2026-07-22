"""Custom integration to integrate anova_bluetooth with Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_integration

from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher

from homeassistant.components import bluetooth

from .const import DOMAIN
from .coordinator import AnovaDataUpdateCoordinator

from anova_ble import AnovaBLEPrecisionCooker

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    address: str = entry.unique_id
    assert address is not None

    hass.data.setdefault(DOMAIN, {})

    # Single source of truth for the version: manifest.json, which the
    # release workflow stamps from the GitHub release tag.
    integration = await async_get_integration(hass, DOMAIN)
    integration_version = (
        str(integration.version) if integration.version else "unknown"
    )

    device = bluetooth.async_ble_device_from_address(hass, address.upper(), connectable=True)

    if not device:
        raise ConfigEntryNotReady(f"Device with address {address} not in range.")

    anova = AnovaBLEPrecisionCooker(ble_device=device)

    @callback
    def _async_update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Update from a ble callback."""
        anova.set_ble_device(service_info.device)

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: address}),
            bluetooth.BluetoothScanningMode.PASSIVE
        )
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator = AnovaDataUpdateCoordinator(
        hass=hass,
        circulator=anova,
        integration_version=integration_version,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
