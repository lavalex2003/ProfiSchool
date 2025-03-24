"""Constants for the ProfiMaktab integration."""
from datetime import timedelta
import datetime

DOMAIN = "profimaktab"
PLATFORMS = ["sensor"]
SCAN_INTERVAL = timedelta(minutes=30)

# Config flow
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_STUDENT_IDS = "student_ids"

# API
BASE_URL = "https://api.profimaktab.uz/api"
TOKEN_URL = f"{BASE_URL}/token/"
PROFILE_URL = f"{BASE_URL}/profile/"
SCHEDULE_URL = f"{BASE_URL}/lessons/"
DAIRY_URL = f"{BASE_URL}/dairy/"

# API Params
SCHEDULE_PARAMS = {
    "schedule_view": "1",
    "page": "1",
    "page_size": "100"
}

# Получение текущей даты
def get_current_date():
    """Get current date in YYYY-MM-DD format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Attributes
ATTR_LAST_UPDATE = "last_update"
ATTR_STUDENT_NAME = "student_name"
ATTR_STUDENT_CLASS = "student_class"
ATTR_STUDENT_ID = "student_id"
ATTR_DAILY_AVERAGE = "daily_average"
ATTR_LESSON_PREFIX = "lesson_"
ATTR_MAX_LESSONS = 9

# Sensor
SENSOR_NAME = "student_{}"
