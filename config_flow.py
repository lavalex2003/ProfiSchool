"""Config flow for ProfiMaktab integration."""
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ProfiMaktabApi, ProfiMaktabApiError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_STUDENT_IDS,
)

_LOGGER = logging.getLogger(__name__)


class ProfiMaktabConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ProfiMaktab."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._username = None
        self._password = None
        self._student_ids = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]
            
            session = async_get_clientsession(self.hass)
            api = ProfiMaktabApi(self._username, self._password, session)
            
            try:
                await api._get_access_token()
                # Токен получен успешно, продолжаем настройку
                return await self.async_step_students()
            except ProfiMaktabApiError:
                errors["base"] = "auth"
            except aiohttp.ClientError:
                errors["base"] = "connection"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error occurred")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_students(self, user_input=None):
        """Configure student IDs."""
        errors = {}

        if user_input is not None:
            raw_student_ids = user_input[CONF_STUDENT_IDS]
            # Разделяем строку с ID студентов и удаляем пробелы
            student_ids = [s.strip() for s in raw_student_ids.split(",")]
            
            # Проверка, что все ID не пустые
            if all(student_ids):
                self._student_ids = student_ids
                
                # Создаем и добавляем запись
                return self.async_create_entry(
                    title=f"ProfiMaktab ({self._username})",
                    data={
                        CONF_USERNAME: self._username,
                        CONF_PASSWORD: self._password,
                        CONF_STUDENT_IDS: self._student_ids,
                    },
                )
            else:
                errors["base"] = "invalid_student_id"

        return self.async_show_form(
            step_id="students",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STUDENT_IDS): str,
                }
            ),
            description_placeholders={
                "instructions": "Введите ID студентов, разделенные запятыми (например: 12345,67890)"
            },
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ProfiMaktabOptionsFlowHandler(config_entry)


class ProfiMaktabOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle ProfiMaktab options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            raw_student_ids = user_input[CONF_STUDENT_IDS]
            student_ids = [s.strip() for s in raw_student_ids.split(",")]
            
            if all(student_ids):
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_STUDENT_IDS: student_ids,
                    },
                )
            else:
                errors["base"] = "invalid_student_id"

        # Загружаем текущие студенческие ID
        student_ids = self.config_entry.data.get(CONF_STUDENT_IDS, [])
        student_ids_str = ", ".join(student_ids)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STUDENT_IDS, default=student_ids_str): str,
                }
            ),
            description_placeholders={
                "instructions": "Измените ID студентов, разделенные запятыми (например: 12345,67890)"
            },
            errors=errors,
        )
