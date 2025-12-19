"""
Mood Tracking Module
Handles mood logging, analysis, and insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
from collections import Counter
import database as db

def log_mood_entry(user_id: str, mood: str, intensity: int,
                   notes: Optional[str] = None,
                   triggers: Optional[List[str]] = None,
                   entry_date: Optional[str] = None) -> str:
    """
    Log a mood entry for a user
    
    Args:
        user_id: User identifier
        mood: Mood type (happy, sad, anxious, stressed, angry, calm, etc.)
        intensity: Mood intensity from 1-10
        notes: Optional notes about the mood
        triggers: Optional list of triggers
        entry_date: Optional date string (YYYY-MM-DD format). If not provided, uses current date/time
    
    Returns:
        entry_id: Unique identifier for the mood entry
    """
    entry_id = str(uuid.uuid4())
    
    # Parse entry_date if provided, otherwise use current datetime
    if entry_date:
        try:
            # Parse date string and create datetime at noon
            date_obj = datetime.strptime(entry_date, "%Y-%m-%d")
            entry_timestamp = date_obj.replace(hour=12, minute=0, second=0, microsecond=0)
        except ValueError:
            # If parsing fails, use current datetime
            entry_timestamp = datetime.now()
    else:
        entry_timestamp = datetime.now()
    
    # Save to database
    db.save_mood_entry(
        user_id=user_id,
        entry_id=entry_id,
        mood=mood,
        intensity=intensity,
        notes=notes,
        triggers=triggers,
        timestamp=entry_timestamp
    )
    
    # Update user data
    user_data = db.load_user_data(user_id)
    user_data["mood_entries"].append({
        "id": entry_id,
        "mood": mood,
        "intensity": intensity,
        "timestamp": str(entry_timestamp)
    })
    user_data["stats"]["total_mood_logs"] = len(user_data["mood_entries"])
    db.save_user_data(user_id, user_data)
    
    print(f"📊 Mood logged: {mood} ({intensity}/10) for user {user_id} on {entry_timestamp.strftime('%Y-%m-%d')}")
    return entry_id

def get_mood_history(user_id: str, days: int = 30) -> List[Dict]:
    """
    Get mood history for a user
    
    Args:
        user_id: User identifier
        days: Number of days to look back
    
    Returns:
        List of mood entries
    """
    entries = db.get_mood_entries(user_id, limit=1000)
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_entries = []
    
    for entry in entries:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            entry_date = datetime.fromisoformat(ts)
        except Exception:
            # Skip entries with invalid timestamp formats
            continue
        if entry_date >= cutoff_date:
            filtered_entries.append(entry)
    
    return filtered_entries

def get_mood_insights(user_id: str) -> Dict:
    """
    Generate insights from mood data
    
    Returns:
        Dictionary with mood insights and patterns
    """
    entries = get_mood_history(user_id, days=30)
    
    if not entries:
        return {
            "message": "Not enough data yet. Log a few moods to see insights!",
            "entries_count": 0
        }
    
    # Calculate statistics
    moods = [e["mood"] for e in entries]
    intensities = [e["intensity"] for e in entries]
    
    mood_counts = Counter(moods)
    most_common_mood = mood_counts.most_common(1)[0] if mood_counts else ("", 0)
    
    avg_intensity = sum(intensities) / len(intensities) if intensities else 0
    
    # Detect trends (last 7 days vs previous 7 days)
    last_7_days = entries[:7] if len(entries) >= 7 else entries
    prev_7_days = entries[7:14] if len(entries) >= 14 else []
    
    trend = None
    if last_7_days and prev_7_days:
        last_7_avg = sum(e["intensity"] for e in last_7_days) / len(last_7_days)
        prev_7_avg = sum(e["intensity"] for e in prev_7_days) / len(prev_7_days)
        
        if last_7_avg > prev_7_avg + 1:
            trend = "improving"
        elif last_7_avg < prev_7_avg - 1:
            trend = "declining"
        else:
            trend = "stable"
    
    # Find common triggers
    all_triggers = []
    for entry in entries:
        if entry.get("triggers"):
            all_triggers.extend(entry["triggers"])
    
    common_triggers = Counter(all_triggers).most_common(3) if all_triggers else []
    
    # Time of day analysis (if we have timestamps)
    time_patterns = analyze_time_patterns(entries)
    
    insights = {
        "entries_count": len(entries),
        "most_common_mood": {
            "mood": most_common_mood[0],
            "count": most_common_mood[1]
        },
        "average_intensity": round(avg_intensity, 1),
        "trend": trend,
        "common_triggers": [{"trigger": t[0], "count": t[1]} for t in common_triggers],
        "time_patterns": time_patterns,
        "mood_distribution": dict(mood_counts)
    }
    
    # Generate personalized message
    insights["message"] = generate_insight_message(insights)
    
    return insights

def analyze_time_patterns(entries: List[Dict]) -> Dict:
    """Analyze when moods tend to occur"""
    if not entries:
        return {}
    
    morning = []  # 6am-12pm
    afternoon = []  # 12pm-6pm
    evening = []  # 6pm-12am
    night = []  # 12am-6am
    
    for entry in entries:
        try:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            hour = timestamp.hour
            intensity = entry["intensity"]
            
            if 6 <= hour < 12:
                morning.append(intensity)
            elif 12 <= hour < 18:
                afternoon.append(intensity)
            elif 18 <= hour < 24:
                evening.append(intensity)
            else:
                night.append(intensity)
        except:
            continue
    
    patterns = {}
    
    if morning:
        patterns["morning"] = round(sum(morning) / len(morning), 1)
    if afternoon:
        patterns["afternoon"] = round(sum(afternoon) / len(afternoon), 1)
    if evening:
        patterns["evening"] = round(sum(evening) / len(evening), 1)
    if night:
        patterns["night"] = round(sum(night) / len(night), 1)
    
    return patterns

def generate_insight_message(insights: Dict) -> str:
    """Generate a human-readable insight message"""
    count = insights["entries_count"]
    most_common = insights["most_common_mood"]["mood"]
    avg_intensity = insights["average_intensity"]
    trend = insights["trend"]
    
    messages = []
    
    # Entry count message
    if count < 5:
        messages.append(f"You've logged {count} moods so far. Keep going to see better insights!")
    else:
        messages.append(f"You've logged {count} moods in the last 30 days.")
    
    # Most common mood
    if most_common:
        messages.append(f"You've been feeling {most_common} most often.")
    
    # Trend
    if trend == "improving":
        messages.append("Great news - your mood seems to be improving lately! 📈")
    elif trend == "declining":
        messages.append("I notice your mood has been lower recently. Want to talk about it? 💙")
    elif trend == "stable":
        messages.append("Your mood has been pretty stable.")
    
    # Average intensity
    if avg_intensity >= 7:
        messages.append("Overall, you're doing pretty well!")
    elif avg_intensity >= 5:
        messages.append("You're hanging in there.")
    else:
        messages.append("It's been a tough time. Remember, it's ok to reach out for support.")
    
    return " ".join(messages)

def get_weekly_summary(user_id: str) -> Dict:
    """Get a summary of the past week"""
    entries = get_mood_history(user_id, days=7)
    
    if not entries:
        return {"message": "No mood entries this week"}
    
    moods = [e["mood"] for e in entries]
    intensities = [e["intensity"] for e in entries]
    
    return {
        "total_logs": len(entries),
        "moods": dict(Counter(moods)),
        "average_intensity": round(sum(intensities) / len(intensities), 1),
        "best_day": max(entries, key=lambda x: x["intensity"]) if entries else None,
        "worst_day": min(entries, key=lambda x: x["intensity"]) if entries else None
    }