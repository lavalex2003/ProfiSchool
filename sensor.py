"""Sensor platform for ProfiMaktab integration."""
import logging
from typing import Any, Callable, Dict, List, Optional
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    ATTR_LAST_UPDATE,
    ATTR_STUDENT_ID,
    ATTR_DAILY_AVERAGE,
    ATTR_LESSON_PREFIX,
    ATTR_MAX_LESSONS,
    SENSOR_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ProfiMaktab sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    student_ids = hass.data[DOMAIN][entry.entry_id]["student_ids"]

    sensors = []
    for student_id in student_ids:
        sensors.append(ProfiMaktabStudentSensor(coordinator, student_id))

    async_add_entities(sensors, True)


class ProfiMaktabStudentSensor(CoordinatorEntity, SensorEntity):
    """Representation of a ProfiMaktab student sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, student_id: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._student_id = student_id
        self._attr_name = SENSOR_NAME.format(student_id)
        self._attr_unique_id = f"{DOMAIN}_{student_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self) -> Optional[str]:
        """Return the state of the sensor."""
        if self.coordinator.data and self._student_id in self.coordinator.data:
            student_data = self.coordinator.data[self._student_id]
            if "daily_average" in student_data:
                return f"{student_data['daily_average']}"
        return "0"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:school"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            ATTR_STUDENT_ID: self._student_id,
            ATTR_LAST_UPDATE: self.coordinator.last_update_success_time.isoformat() 
                if self.coordinator.last_update_success_time else None,
            ATTR_DAILY_AVERAGE: 0
        }

        if self.coordinator.data and self._student_id in self.coordinator.data:
            student_data = self.coordinator.data[self._student_id]
            
            # Добавляем среднюю оценку за день
            if "daily_average" in student_data:
                attrs[ATTR_DAILY_AVERAGE] = student_data["daily_average"]
            
            # Добавляем информацию об уроках
            if "lessons" in student_data:
                lessons = student_data["lessons"]
                
                # Добавляем данные о каждом уроке (максимум 9)
                for i in range(1, ATTR_MAX_LESSONS + 1):
                    lesson_key = f"{ATTR_LESSON_PREFIX}{i}"
                    
                    # Если урок существует, добавляем его данные
                    if lesson_key in lessons:
                        lesson_data = lessons[lesson_key]
                        # Преобразуем данные урока в JSON
                        attrs[lesson_key] = json.dumps(lesson_data, ensure_ascii=False)
                    else:
                        # Если урока нет, добавляем пустые данные
                        attrs[lesson_key] = json.dumps({
                            "name": "",
                            "topic": "",
                            "grade": "",
                            "homework": ""
                        }, ensure_ascii=False)

        return attrs
