"""API client for ProfiMaktab."""
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

from .const import (
    TOKEN_URL, 
    PROFILE_URL, 
    SCHEDULE_URL, 
    DAIRY_URL,
    SCHEDULE_PARAMS,
    get_current_date
)

_LOGGER = logging.getLogger(__name__)

class ProfiMaktabApiError(Exception):
    """Exception to indicate an error from the API."""
    pass

class ProfiMaktabApi:
    """API Client for ProfiMaktab."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession):
        """Initialize the API client."""
        self._username = username
        self._password = password
        self._session = session
        self._access_token = None
        self._token_expires = None

    async def _get_access_token(self) -> str:
        """Get access token for API."""
        if self._access_token and self._token_expires and self._token_expires > datetime.now():
            return self._access_token

        try:
            response = await self._session.post(
                TOKEN_URL,
                json={"username": self._username, "password": self._password}
            )
            
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error(f"Failed to authenticate: {error_text}")
                raise ProfiMaktabApiError(f"Authentication failed: {response.status}")
                
            data = await response.json()
            
            if "access" not in data:
                raise ProfiMaktabApiError("No access token in login response")
                
            self._access_token = data["access"]
            # Токен действителен 24 часа (предположение, можно настроить под API)
            self._token_expires = datetime.now() + timedelta(hours=23)
            
            return self._access_token
            
        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error connecting to ProfiMaktab API: {error}")
            raise ProfiMaktabApiError(f"Connection error: {error}")

    async def _api_call(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make an API call."""
        headers = {"Authorization": f"Bearer {await self._get_access_token()}"}
        
        try:
            response = await self._session.get(url, headers=headers, params=params)
            
            if response.status != 200:
                error_text = await response.text()
                _LOGGER.error(f"API call failed: {url}, status: {response.status}, response: {error_text}")
                raise ProfiMaktabApiError(f"API call failed: {response.status}")
                
            return await response.json()
            
        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error connecting to ProfiMaktab API: {error}")
            raise ProfiMaktabApiError(f"Connection error: {error}")

    async def get_profile(self) -> Dict:
        """Get user profile."""
        try:
            return await self._api_call(PROFILE_URL)
        except Exception as e:
            _LOGGER.error(f"Error getting profile: {e}")
            raise ProfiMaktabApiError(f"Error getting profile: {e}")

    async def get_schedule(self) -> Dict:
        """Get schedule using predefined parameters."""
        try:
            return await self._api_call(SCHEDULE_URL, SCHEDULE_PARAMS)
        except Exception as e:
            _LOGGER.error(f"Error getting schedule: {e}")
            raise ProfiMaktabApiError(f"Error getting schedule: {e}")

    async def get_dairy(self, student_id: str, date: Optional[str] = None) -> Dict:
        """Get dairy (grades, lessons, homework) for student.
        
        Args:
            student_id: The student ID
            date: Date in format YYYY-MM-DD, defaults to current date
        """
        if date is None:
            date = get_current_date()
            
        params = {
            "for_date": date,
            "student": student_id
        }
            
        try:
            return await self._api_call(DAIRY_URL, params)
        except Exception as e:
            _LOGGER.error(f"Error getting dairy for student {student_id}: {e}")
            raise ProfiMaktabApiError(f"Error getting dairy: {e}")
    
    async def fetch_student_data(self, student_id: str) -> Dict[str, Any]:
        """Fetch daily dairy data for a student.
        
        This collects the daily performance information including
        lessons, grades, homework, etc.
        """
        try:
            # Get dairy data for current day
            dairy_data = await self.get_dairy(student_id)
            
            # Calculate average score if available
            average_score = 0.0
            score_count = 0
            
            lessons_data = {}
            
            # Parse lessons data and calculate average score
            if "results" in dairy_data and dairy_data["results"]:
                for idx, lesson in enumerate(dairy_data["results"], 1):
                    if idx > 9:  # We only support up to 9 lessons
                        break
                        
                    lesson_data = {
                        "name": lesson.get("lesson_name", "Неизвестный урок"),
                        "topic": lesson.get("theme", ""),
                        "grade": lesson.get("balls", ""),
                        "homework": lesson.get("tasks", "")
                    }
                    
                    lessons_data[f"lesson_{idx}"] = lesson_data
                    
                    # Add to average if there's a grade
                    if lesson.get("balls") and isinstance(lesson.get("balls"), (int, float)):
                        average_score += float(lesson.get("balls"))
                        score_count += 1
            
            # Calculate average if we have scores
            if score_count > 0:
                average_score = round(average_score / score_count, 1)
            else:
                average_score = 0.0
            
            return {
                "student_id": student_id,
                "daily_average": average_score,
                "lessons": lessons_data,
                "date": get_current_date()
            }
        except Exception as e:
            _LOGGER.error(f"Error fetching dairy data for student {student_id}: {e}")
            raise ProfiMaktabApiError(f"Error fetching dairy data: {e}")
