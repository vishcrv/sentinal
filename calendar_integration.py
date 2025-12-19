"""
Lightweight Calendar integration helpers for scheduling wellness activities.
Simple pattern matching spotify_integration.py structure.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

from tools.calendar_tools import create_event, get_events, modify_event, delete_event
import config

logger = logging.getLogger(__name__)

# Simple keyword detection
CALENDAR_KEYWORDS = [
    "schedule",
    "appointment",
    "meeting",
    "reminder",
    "calendar",
    "book",
    "plan",
    "set up",
    "arrange",
    "therapy",
    "meditation",
]

TIME_KEYWORDS = [
    "tomorrow",
    "today",
    "next week",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "at",
    "pm",
    "am",
]


def detect_calendar_intent(message: str) -> bool:
    """Check if message contains calendar-related intent."""
    message_lower = message.lower()
    has_keyword = any(kw in message_lower for kw in CALENDAR_KEYWORDS)
    has_time = any(kw in message_lower for kw in TIME_KEYWORDS)
    return has_keyword or has_time


def extract_event_type(message: str) -> str:
    """Determine event type from message."""
    message_lower = message.lower()

    if any(w in message_lower for w in ["therapy", "counseling", "psychologist"]):
        return "therapy"
    elif any(w in message_lower for w in ["meditation", "mindfulness"]):
        return "meditation"
    elif any(w in message_lower for w in ["exercise", "workout", "gym"]):
        return "exercise"
    elif any(w in message_lower for w in ["doctor", "appointment"]):
        return "medical"
    elif any(w in message_lower for w in ["journal", "write"]):
        return "journaling"

    return "wellness"


async def create_wellness_event(
    event_type: str,
    start_time: str,
    duration_minutes: int = 30,
    notes: Optional[str] = None,
) -> Dict:
    """
    Create a wellness calendar event.
    Similar to recommend_for_mood() but for calendar events.

    Args:
        event_type: Type of wellness activity (therapy, meditation, etc.)
        start_time: ISO format datetime string
        duration_minutes: Event duration
        notes: Optional event description

    Returns:
        Dict with success status and event details
    """
    try:
        # Map event types to emoji and descriptions
        event_templates = {
            "therapy": {
                "emoji": "🧠",
                "title": "Therapy Session",
                "description": "Mental health counseling session",
            },
            "meditation": {
                "emoji": "🧘",
                "title": "Meditation",
                "description": "Mindfulness and relaxation practice",
            },
            "exercise": {
                "emoji": "💪",
                "title": "Exercise",
                "description": "Physical wellness activity",
            },
            "medical": {
                "emoji": "🏥",
                "title": "Medical Appointment",
                "description": "Healthcare appointment",
            },
            "journaling": {
                "emoji": "📝",
                "title": "Journaling",
                "description": "Reflective writing time",
            },
            "wellness": {
                "emoji": "🌿",
                "title": "Wellness Activity",
                "description": "Self-care time",
            },
        }

        template = event_templates.get(event_type, event_templates["wellness"])

        # Calculate end time
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        # Create the event
        summary = f"{template['emoji']} {template['title']}"
        description = notes or template["description"]

        result = create_event(
            summary=summary,
            start_time=start_dt.isoformat(),
            end_time=end_dt.isoformat(),
            description=description,
            calendar_id="primary",
            reminders=[{"method": "popup", "minutes": 15}],
            use_default_reminders=False,
        )

        logger.info(f"Created {event_type} event: {summary}")

        return {
            "success": True,
            "event_type": event_type,
            "title": summary,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_minutes": duration_minutes,
            "description": description,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}", exc_info=True)
        return {"success": False, "error": str(e), "event_type": event_type}


async def get_upcoming_events(days_ahead: int = 7, max_results: int = 10) -> List[Dict]:
    """
    Get upcoming wellness events from calendar.
    Similar to search_tracks() pattern.

    Args:
        days_ahead: Number of days to look ahead
        max_results: Maximum number of events to return

    Returns:
        List of event dictionaries
    """
    try:
        # Calculate time range
        time_min = datetime.now().isoformat() + "Z"
        time_max = (datetime.now() + timedelta(days=days_ahead)).isoformat() + "Z"

        # Get events from calendar
        events_json = get_events(
            calendar_id="primary",
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
            detailed=True,
        )

        import json

        events_data = json.loads(events_json)

        events = []
        for event in events_data.get("events", []):
            events.append(
                {
                    "id": event.get("id"),
                    "title": event.get("summary"),
                    "start": event.get("start", {}).get(
                        "dateTime", event.get("start", {}).get("date")
                    ),
                    "end": event.get("end", {}).get(
                        "dateTime", event.get("end", {}).get("date")
                    ),
                    "description": event.get("description"),
                    "location": event.get("location"),
                }
            )

        return events

    except Exception as e:
        logger.error(f"Failed to get upcoming events: {e}", exc_info=True)
        return []


async def suggest_wellness_activities(mood: str) -> List[Dict]:
    """
    Suggest wellness activities based on mood.
    Matches the recommend_for_mood() pattern exactly.

    Args:
        mood: User's current mood (happy, anxious, sad, etc.)

    Returns:
        List of suggested activity dictionaries
    """
    # Map moods to wellness activities (simple heuristics)
    mood_activities = {
        "anxious": [
            {"type": "meditation", "title": "🧘 Breathing Exercise", "duration": 15},
            {"type": "exercise", "title": "🚶 Calming Walk", "duration": 30},
            {"type": "journaling", "title": "📝 Anxiety Journal", "duration": 20},
        ],
        "sad": [
            {"type": "exercise", "title": "☀️ Outdoor Activity", "duration": 30},
            {"type": "meditation", "title": "🎵 Music Meditation", "duration": 20},
            {"type": "wellness", "title": "🤝 Social Connection", "duration": 45},
        ],
        "stressed": [
            {
                "type": "meditation",
                "title": "🧘 Stress Relief Meditation",
                "duration": 20,
            },
            {"type": "exercise", "title": "💪 Workout Session", "duration": 45},
            {"type": "wellness", "title": "🛀 Relaxation Time", "duration": 30},
        ],
        "happy": [
            {"type": "exercise", "title": "🏃 Energizing Workout", "duration": 45},
            {"type": "wellness", "title": "🎨 Creative Activity", "duration": 60},
            {"type": "journaling", "title": "📔 Gratitude Journal", "duration": 15},
        ],
        "calm": [
            {"type": "meditation", "title": "🌅 Morning Meditation", "duration": 20},
            {"type": "journaling", "title": "✍️ Reflective Writing", "duration": 30},
            {"type": "wellness", "title": "📚 Reading Time", "duration": 45},
        ],
    }

    # Return activities for mood, or default calm activities
    activities = mood_activities.get(mood.lower(), mood_activities["calm"])

    return activities[:6]  # Limit to 6 like Spotify


async def schedule_from_message(message: str, user_id: str) -> Dict:
    """
    Parse message and create calendar event.
    High-level helper similar to how Spotify integration works.

    Args:
        message: User's natural language message
        user_id: User identifier

    Returns:
        Dict with scheduling result
    """
    try:
        # Detect event type
        event_type = extract_event_type(message)

        # Simple time parsing (you can enhance this)
        message_lower = message.lower()

        # Determine start time
        if "tomorrow" in message_lower:
            start_time = datetime.now() + timedelta(days=1)
            start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
        elif "today" in message_lower:
            start_time = datetime.now() + timedelta(hours=2)
        elif "next week" in message_lower:
            start_time = datetime.now() + timedelta(weeks=1)
            start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            # Default to tomorrow at 10am
            start_time = datetime.now() + timedelta(days=1)
            start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)

        # Extract time from message (basic regex)
        time_match = re.search(r"(\d{1,2})\s*(am|pm)", message_lower)
        if time_match:
            hour = int(time_match.group(1))
            meridiem = time_match.group(2)
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            start_time = start_time.replace(hour=hour, minute=0)

        # Create the event
        result = await create_wellness_event(
            event_type=event_type,
            start_time=start_time.isoformat(),
            duration_minutes=30,
            notes=f"Scheduled via chat by {user_id}",
        )

        if result.get("success"):
            return {
                "success": True,
                "message": f"✅ Scheduled {result['title']} for {start_time.strftime('%B %d at %I:%M %p')}",
                "event": result,
            }
        else:
            return {
                "success": False,
                "message": "❌ Could not schedule the event. Please try again with more details.",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error scheduling from message: {e}", exc_info=True)
        return {
            "success": False,
            "message": "❌ Failed to schedule. Please provide date and time details.",
            "error": str(e),
        }
