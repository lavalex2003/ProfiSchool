"""The ProfiMaktab integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed

from .api import ProfiMaktabApi, ProfiMaktabApiError
from .const import (
    DOMAIN,
    PLATFORMS,
    SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_STUDENT_IDS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the ProfiMaktab integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up ProfiMaktab from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    student_ids = entry.data[CONF_STUDENT_IDS]

    session = async_get_clientsession(hass)
    api = ProfiMaktabApi(username, password, session)

    # Проверим соединение с API, получив доступ к токену
    try:
        await api._get_access_token()
    except ProfiMaktabApiError as err:
        _LOGGER.error("Error authenticating with ProfiMaktab API: %s", err)
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}")
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.error("Error connecting to ProfiMaktab API: %s", err)
        raise ConfigEntryNotReady(f"Connection error: {err}")

    # Создаем координатор для обновления данных
    async def async_update_data():
        """Fetch data from API."""
        try:
            data = {}
            for student_id in student_ids:
                student_data = await api.fetch_student_data(student_id)
                data[student_id] = student_data
            return data
        except ProfiMaktabApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    # Первоначальное обновление данных
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "student_ids": student_ids,
    }

    # Настраиваем платформы
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
