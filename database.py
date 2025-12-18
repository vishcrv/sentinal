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
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_mood 
        ON mood_entries(user_id, timestamp)
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
        "conversation_moods": [],  # Track moods detected during conversation
        "profile": {
            "name": "",
            "preferences": {
                "communication_style": "supportive",  # supportive, casual, professional
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
                   notes: Optional[str] = None, triggers: Optional[List[str]] = None):
    """Save a mood entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
        str(datetime.now())
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

def delete_user_data(user_id: str):
    """Delete all user data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM mood_entries WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    
    print(f"🗑️ Deleted all data for user {user_id}")