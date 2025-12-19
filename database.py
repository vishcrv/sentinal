"""
Database module for Mental Health Support Chatbot
Handles user data persistence and retrieval
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

# Database file
DB_PATH = "mental_health.db"

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_activity TEXT NOT NULL
        )
    """)
    
    # Mood entries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_entries (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            mood TEXT NOT NULL,
            intensity INTEGER NOT NULL,
            notes TEXT,
            triggers TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Mood transitions table - for continuous mood tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_transitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            mood TEXT NOT NULL,
            intensity INTEGER NOT NULL,
            message TEXT,
            context TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Daily summaries table - NEW
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            summary TEXT NOT NULL,
            message_count INTEGER NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Weekly summaries table - NEW
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            week_key TEXT NOT NULL,
            week_start TEXT NOT NULL,
            summary TEXT NOT NULL,
            days_count INTEGER NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(user_id, week_key),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Monthly summaries table - NEW
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            month_key TEXT NOT NULL,
            summary TEXT NOT NULL,
            weeks_count INTEGER NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(user_id, month_key),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Calendar events table - NEW
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            google_event_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            category TEXT,
            source TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_mood 
        ON mood_entries(user_id, timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_transitions 
        ON mood_transitions(user_id, timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_daily_summaries 
        ON daily_summaries(user_id, date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_weekly_summaries 
        ON weekly_summaries(user_id, week_key)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_monthly_summaries 
        ON monthly_summaries(user_id, month_key)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_calendar_events 
        ON calendar_events(user_id, start_time)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def get_default_user_data() -> Dict:
    """Get default user data structure"""
    return {
        "user_id": "",
        "created_at": str(datetime.now()),
        "last_activity": str(datetime.now()),
        "history": [],
        "mood_entries": [],
        "current_session_moods": [],  # Track moods in current session
        "profile": {
            "name": "",
            "preferences": {
                "communication_style": "supportive",
                "topics_to_avoid": [],
                "preferred_activities": []
            },
            "crisis_contacts": []
        },
        "stats": {
            "total_conversations": 0,
            "total_mood_logs": 0,
            "days_active": 0
        },
        "flags": {
            "needs_crisis_support": False,
            "last_crisis_check": None
        }
    }

def load_user_data(user_id: str) -> Dict:
    """Load user data from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT data FROM users WHERE user_id = ?",
        (user_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = json.loads(row[0])
        return data
    else:
        # Create new user
        data = get_default_user_data()
        data["user_id"] = user_id
        save_user_data(user_id, data)
        return data

def save_user_data(user_id: str, data: Dict):
    """Save user data to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    data["last_activity"] = str(datetime.now())
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, data, created_at, last_activity)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        json.dumps(data),
        data.get("created_at", str(datetime.now())),
        data["last_activity"]
    ))
    
    conn.commit()
    conn.close()

def get_all_users() -> List[str]:
    """Get all user IDs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return users

def save_mood_entry(user_id: str, entry_id: str, mood: str, intensity: int,
                   notes: Optional[str] = None, triggers: Optional[List[str]] = None,
                   timestamp: Optional[datetime] = None):
    """Save a mood entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if timestamp is None:
        timestamp = datetime.now()
    
    cursor.execute("""
        INSERT INTO mood_entries (id, user_id, mood, intensity, notes, triggers, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id,
        user_id,
        mood,
        intensity,
        notes,
        json.dumps(triggers) if triggers else None,
        str(timestamp)
    ))
    
    conn.commit()
    conn.close()

def get_mood_entries(user_id: str, limit: int = 100) -> List[Dict]:
    """Get mood entries for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, mood, intensity, notes, triggers, timestamp
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    
    entries = []
    for row in cursor.fetchall():
        entries.append({
            "id": row[0],
            "mood": row[1],
            "intensity": row[2],
            "notes": row[3],
            "triggers": json.loads(row[4]) if row[4] else None,
            "timestamp": row[5]
        })
    
    conn.close()
    return entries

def get_mood_entries_by_date(user_id: str, date: str) -> List[Dict]:
    """
    Get mood entries for a user on a specific date
    
    Args:
        user_id: User identifier
        date: Date string in YYYY-MM-DD format
    
    Returns:
        List of mood entries for that date
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query for entries on the specified date (any time during that day)
    # Use LIKE to match any timestamp that starts with the date
    date_pattern = f"{date}%"
    
    cursor.execute("""
        SELECT id, mood, intensity, notes, triggers, timestamp
        FROM mood_entries
        WHERE user_id = ? AND timestamp LIKE ?
        ORDER BY timestamp DESC
    """, (user_id, date_pattern))
    
    entries = []
    for row in cursor.fetchall():
        entries.append({
            "id": row[0],
            "mood": row[1],
            "intensity": row[2],
            "notes": row[3],
            "triggers": json.loads(row[4]) if row[4] else None,
            "timestamp": row[5]
        })
    
    conn.close()
    return entries

def get_mood_entries_dates(user_id: str, days: int = 60) -> List[str]:
    """
    Get list of dates that have mood entries (for calendar highlighting)
    
    Args:
        user_id: User identifier
        days: Number of days to look back
    
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    from datetime import timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_str = str(cutoff_date)
    
    # Get all entries and extract dates
    cursor.execute("""
        SELECT timestamp
        FROM mood_entries
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    """, (user_id, cutoff_str))
    
    dates_set = set()
    for row in cursor.fetchall():
        timestamp_str = row[0]
        try:
            # Parse timestamp and extract date part
            if isinstance(timestamp_str, str):
                # Extract YYYY-MM-DD from timestamp string
                date_part = timestamp_str.split()[0] if ' ' in timestamp_str else timestamp_str[:10]
                if len(date_part) >= 10:
                    dates_set.add(date_part[:10])  # Ensure YYYY-MM-DD format
        except Exception:
            continue
    
    dates = sorted(list(dates_set), reverse=True)
    
    conn.close()
    return dates

def log_mood_transition(user_id: str, mood: str, intensity: int, 
                       message: Optional[str] = None, context: Optional[str] = None):
    """Log a mood transition during conversation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO mood_transitions (user_id, mood, intensity, message, context, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        mood,
        intensity,
        message,
        context,
        str(datetime.now())
    ))
    
    conn.commit()
    conn.close()
    print(f"📊 Mood transition logged: {mood} ({intensity}/10) for user {user_id}")

def get_mood_transitions(user_id: str, limit: int = 50) -> List[Dict]:
    """Get mood transitions for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, mood, intensity, message, context, timestamp
        FROM mood_transitions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    
    transitions = []
    for row in cursor.fetchall():
        transitions.append({
            "id": row[0],
            "mood": row[1],
            "intensity": row[2],
            "message": row[3],
            "context": row[4],
            "timestamp": row[5]
        })
    
    conn.close()
    return transitions

def get_session_mood_summary(user_id: str, minutes: int = 60) -> Dict:
    """Get mood summary for recent session (default last 60 minutes)"""
    from datetime import timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    cutoff_str = str(cutoff_time)
    
    cursor.execute("""
        SELECT mood, intensity, timestamp
        FROM mood_transitions
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (user_id, cutoff_str))
    
    transitions = []
    mood_counts = {}
    total_intensity = 0
    count = 0
    
    for row in cursor.fetchall():
        mood = row[0]
        intensity = row[1]
        timestamp = row[2]
        
        transitions.append({
            "mood": mood,
            "intensity": intensity,
            "timestamp": timestamp
        })
        
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        total_intensity += intensity
        count += 1
    
    conn.close()
    
    avg_intensity = round(total_intensity / count, 1) if count > 0 else None
    
    # Get current mood (most recent)
    current_mood = transitions[-1]["mood"] if transitions else None
    current_intensity = transitions[-1]["intensity"] if transitions else None
    
    return {
        "user_id": user_id,
        "session_duration_minutes": minutes,
        "transitions": transitions,
        "mood_distribution": mood_counts,
        "average_intensity": avg_intensity,
        "current_mood": current_mood,
        "current_intensity": current_intensity,
        "total_transitions": count
    }

def clear_old_transitions(user_id: str, hours: int = 24):
    """Clear mood transitions older than specified hours"""
    from datetime import timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = str(cutoff_time)
    
    cursor.execute("""
        DELETE FROM mood_transitions
        WHERE user_id = ? AND timestamp < ?
    """, (user_id, cutoff_str))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"🧹 Cleared {deleted} old mood transitions for user {user_id}")
    return deleted

# ══════════════════════════════════════════════════════════════
# SUMMARY STORAGE FUNCTIONS - NEW
# ══════════════════════════════════════════════════════════════

def save_daily_summary(user_id: str, date: str, summary: str, message_count: int):
    """Save or update a daily summary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO daily_summaries 
        (user_id, date, summary, message_count, generated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        date,
        summary,
        message_count,
        str(datetime.now())
    ))
    
    conn.commit()
    conn.close()
    print(f"📝 Daily summary saved for {user_id} on {date}")

def get_daily_summaries(user_id: str, limit: int = 30) -> Dict[str, Dict]:
    """Get daily summaries for a user (returns dict keyed by date)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, summary, message_count, generated_at
        FROM daily_summaries
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (user_id, limit))
    
    summaries = {}
    for row in cursor.fetchall():
        summaries[row[0]] = {
            "summary": row[1],
            "message_count": row[2],
            "generated_at": row[3]
        }
    
    conn.close()
    return summaries

def save_weekly_summary(user_id: str, week_key: str, week_start: str, 
                       summary: str, days_count: int):
    """Save or update a weekly summary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO weekly_summaries 
        (user_id, week_key, week_start, summary, days_count, generated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        week_key,
        week_start,
        summary,
        days_count,
        str(datetime.now())
    ))
    
    conn.commit()
    conn.close()
    print(f"📅 Weekly summary saved for {user_id} - {week_key}")

def get_weekly_summaries(user_id: str, limit: int = 12) -> Dict[str, Dict]:
    """Get weekly summaries for a user (returns dict keyed by week_key)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT week_key, week_start, summary, days_count, generated_at
        FROM weekly_summaries
        WHERE user_id = ?
        ORDER BY week_key DESC
        LIMIT ?
    """, (user_id, limit))
    
    summaries = {}
    for row in cursor.fetchall():
        summaries[row[0]] = {
            "week_start": row[1],
            "summary": row[2],
            "days_count": row[3],
            "generated_at": row[4]
        }
    
    conn.close()
    return summaries

def save_monthly_summary(user_id: str, month_key: str, summary: str, weeks_count: int):
    """Save or update a monthly summary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO monthly_summaries 
        (user_id, month_key, summary, weeks_count, generated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        month_key,
        summary,
        weeks_count,
        str(datetime.now())
    ))
    
    conn.commit()
    conn.close()
    print(f"📆 Monthly summary saved for {user_id} - {month_key}")

def get_monthly_summaries(user_id: str, limit: int = 12) -> Dict[str, Dict]:
    """Get monthly summaries for a user (returns dict keyed by month_key)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT month_key, summary, weeks_count, generated_at
        FROM monthly_summaries
        WHERE user_id = ?
        ORDER BY month_key DESC
        LIMIT ?
    """, (user_id, limit))
    
    summaries = {}
    for row in cursor.fetchall():
        summaries[row[0]] = {
            "summary": row[1],
            "weeks_count": row[2],
            "generated_at": row[3]
        }
    
    conn.close()
    return summaries

def load_all_summaries(user_id: str) -> Dict:
    """Load all summaries for a user in the hierarchical structure"""
    return {
        "daily": get_daily_summaries(user_id),
        "weekly": get_weekly_summaries(user_id),
        "monthly": get_monthly_summaries(user_id)
    }

def delete_old_summaries(user_id: str, days: int = 90):
    """Delete summaries older than specified days"""
    from datetime import timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Delete old daily summaries
    cursor.execute("""
        DELETE FROM daily_summaries
        WHERE user_id = ? AND date < ?
    """, (user_id, cutoff_date))
    daily_deleted = cursor.rowcount
    
    # Delete old weekly summaries (keep more weeks)
    cutoff_week = (datetime.now() - timedelta(days=days+30)).strftime("%Y-W%W")
    cursor.execute("""
        DELETE FROM weekly_summaries
        WHERE user_id = ? AND week_key < ?
    """, (user_id, cutoff_week))
    weekly_deleted = cursor.rowcount
    
    # Keep all monthly summaries (they're already condensed)
    
    conn.commit()
    conn.close()
    
    print(f"🧹 Deleted {daily_deleted} daily and {weekly_deleted} weekly summaries for {user_id}")
    return {"daily": daily_deleted, "weekly": weekly_deleted}

def delete_user_data(user_id: str):
    """Delete all user data including summaries"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM mood_transitions WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM mood_entries WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM daily_summaries WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM weekly_summaries WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM monthly_summaries WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM calendar_events WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    
    print(f"🗑️ Deleted all data for user {user_id}")

# ══════════════════════════════════════════════════════════════
# CALENDAR EVENTS FUNCTIONS
# ══════════════════════════════════════════════════════════════

def save_calendar_event(user_id: str, event_id: str, google_event_id: Optional[str],
                        title: str, description: Optional[str], start_time: str, 
                        end_time: str, category: Optional[str] = None, 
                        source: Optional[str] = None):
    """Save a calendar event to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO calendar_events 
        (id, user_id, google_event_id, title, description, start_time, end_time, category, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        user_id,
        google_event_id,
        title,
        description,
        start_time,
        end_time,
        category,
        source,
        str(datetime.now())
    ))
    
    conn.commit()
    conn.close()
    print(f"📅 Calendar event saved: {title} for user {user_id}")

def get_calendar_events(user_id: str, limit: int = 50, days_ahead: int = 30) -> List[Dict]:
    """Get calendar events for a user"""
    from datetime import timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get events from now up to days_ahead
    cutoff_time = datetime.now()
    future_time = datetime.now() + timedelta(days=days_ahead)
    
    cursor.execute("""
        SELECT id, google_event_id, title, description, start_time, end_time, category, source, created_at
        FROM calendar_events
        WHERE user_id = ? AND start_time >= ? AND start_time <= ?
        ORDER BY start_time ASC
        LIMIT ?
    """, (user_id, str(cutoff_time), str(future_time), limit))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            "id": row[0],
            "google_event_id": row[1],
            "title": row[2],
            "description": row[3],
            "start_time": row[4],
            "end_time": row[5],
            "category": row[6],
            "source": row[7],
            "created_at": row[8]
        })
    
    conn.close()
    return events

def delete_calendar_event(user_id: str, event_id: str):
    """Delete a calendar event"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM calendar_events
        WHERE user_id = ? AND id = ?
    """, (user_id, event_id))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"🗑️ Deleted calendar event {event_id} for user {user_id}")
    
    return deleted > 0