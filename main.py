"""
Mental Health Support Chatbot - FastAPI Backend
Main server file with REST API endpoints
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime
import uuid
import database as db
import chatbot_engine as chat
import mood_tracker as mood
import wellness as well
import spotify_integration as sp
import calendar_integration as cal
import asyncio

# Initialize FastAPI
app = FastAPI(title="Mental Health Support API", version="1.0.0")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db.init_db()

# ══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    mood_detected: Optional[str] = None
    mood_intensity: Optional[int] = None
    crisis_detected: bool = False
    suggestions: Optional[List[str]] = None

class MoodEntry(BaseModel):
    user_id: str
    mood: str
    intensity: int
    notes: Optional[str] = None
    triggers: Optional[List[str]] = None
    date: Optional[str] = None  # Date in YYYY-MM-DD format

class MoodResponse(BaseModel):
    success: bool
    entry_id: str
    insights: Optional[Dict] = None

class UserProfileRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    preferences: Optional[Dict] = None

class WellnessRequest(BaseModel):
    user_id: str
    category: Optional[str] = None

# ══════════════════════════════════════════════════════════════
# CHAT ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - send message, get response
    """
    try:
        # Load user data
        user_data = db.load_user_data(request.user_id)
        
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Add user message to history
        user_data["history"].append({
            "role": "user",
            "text": request.message,
            "timestamp": str(datetime.now())
        })
        
        # Generate response with mood tracking
        response_data = await chat.generate_support_response(
            user_data=user_data,
            user_message=request.message,
            user_id=request.user_id
        )
        
        # Add bot response to history
        user_data["history"].append({
            "role": "assistant",
            "text": response_data["response"],
            "timestamp": str(datetime.now())
        })
        
        # Track mood in session if detected
        if response_data.get("mood_detected"):
            user_data.setdefault("current_session_moods", []).append({
                "mood": response_data.get("mood_detected"),
                "intensity": response_data.get("mood_intensity"),
                "timestamp": str(datetime.now())
            })
        
        # Update last activity
        user_data["last_activity"] = str(datetime.now())
        
        # Save user data
        db.save_user_data(request.user_id, user_data)
        
        # Return response
        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            mood_detected=response_data.get("mood_detected"),
            mood_intensity=response_data.get("mood_intensity"),
            crisis_detected=response_data.get("crisis_detected", False),
            suggestions=response_data.get("suggestions")
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Get user's chat history
    """
    try:
        user_data = db.load_user_data(user_id)
        history = user_data.get("history", [])
        
        return {
            "user_id": user_id,
            "history": history[-limit:] if len(history) > limit else history,
            "total_messages": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear user's chat history
    """
    try:
        user_data = db.load_user_data(user_id)
        user_data["history"] = []
        user_data["current_session_moods"] = []
        db.save_user_data(user_id, user_data)
        
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════
# MOOD TRACKING ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.post("/api/mood/log", response_model=MoodResponse)
async def log_mood(entry: MoodEntry):
    """
    Log a mood entry
    """
    try:
        entry_id = mood.log_mood_entry(
            user_id=entry.user_id,
            mood=entry.mood,
            intensity=entry.intensity,
            notes=entry.notes,
            triggers=entry.triggers,
            entry_date=entry.date
        )
        
        insights = mood.get_mood_insights(entry.user_id)
        
        return MoodResponse(
            success=True,
            entry_id=entry_id,
            insights=insights
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/history/{user_id}")
async def get_mood_history(user_id: str, days: int = 30):
    """
    Get mood history for a user
    """
    try:
        history = mood.get_mood_history(user_id, days=days)
        insights = mood.get_mood_insights(user_id)
        
        return {
            "user_id": user_id,
            "history": history,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/date/{user_id}/{date}")
async def get_mood_by_date(user_id: str, date: str):
    """
    Get mood entries for a specific date (YYYY-MM-DD format)
    """
    try:
        entries = db.get_mood_entries_by_date(user_id, date)
        return {
            "user_id": user_id,
            "date": date,
            "entries": entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/dates/{user_id}")
async def get_mood_dates(user_id: str, days: int = 60):
    """
    Get list of dates that have mood entries (for calendar highlighting)
    """
    try:
        dates = db.get_mood_entries_dates(user_id, days=days)
        return {
            "user_id": user_id,
            "dates": dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/insights/{user_id}")
async def get_insights(user_id: str):
    """
    Get mood insights and patterns
    """
    try:
        insights = mood.get_mood_insights(user_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/active/{user_id}")
async def get_active_mood(user_id: str, limit: int = 20):
    """Return recent mood timeline and an active mood bar summary"""
    try:
        entries = db.get_mood_entries(user_id, limit=limit)

        if not entries:
            return {
                "user_id": user_id,
                "average_intensity": None,
                "distribution": {},
                "timeline": []
            }

        avg_intensity = round(sum(e.get("intensity", 0) for e in entries) / max(1, len(entries)), 1)
        dist = {}
        for e in entries:
            dist[e["mood"]] = dist.get(e["mood"], 0) + 1

        return {
            "user_id": user_id,
            "average_intensity": avg_intensity,
            "distribution": dist,
            "timeline": entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS FOR MOOD TRANSITIONS

@app.get("/api/mood/transitions/{user_id}")
async def get_mood_transitions(user_id: str, limit: int = 50):
    """
    Get mood transitions during conversations
    """
    try:
        transitions = db.get_mood_transitions(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "transitions": transitions,
            "total": len(transitions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/session/{user_id}")
async def get_session_mood(user_id: str, minutes: int = 60):
    """
    Get current session mood summary (last N minutes)
    """
    try:
        summary = db.get_session_mood_summary(user_id, minutes=minutes)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/current/{user_id}")
async def get_current_mood_bar(user_id: str):
    """
    Get data for active mood bar visualization
    Returns: current mood, intensity, recent transitions
    """
    try:
        # Get session summary (last hour)
        summary = db.get_session_mood_summary(user_id, minutes=60)
        
        # Get last 10 transitions for visualization
        recent_transitions = db.get_mood_transitions(user_id, limit=10)
        
        return {
            "user_id": user_id,
            "current_mood": summary.get("current_mood"),
            "current_intensity": summary.get("current_intensity"),
            "average_intensity": summary.get("average_intensity"),
            "mood_distribution": summary.get("mood_distribution", {}),
            "recent_transitions": recent_transitions[::-1],  # Chronological order
            "session_transitions_count": summary.get("total_transitions", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SpotifyRequest(BaseModel):
    user_id: str
    mode: Optional[str] = "auto"
    query: Optional[str] = None

@app.post("/api/spotify/recommend")
async def spotify_recommend(req: SpotifyRequest):
    """Recommend songs via Spotify based on current mood or search query"""
    try:
        user_data = db.load_user_data(req.user_id)

        if req.mode == "search" and req.query:
            tracks = await sp.search_tracks(req.query)
            return {"tracks": tracks}

        # Get most recent mood
        transitions = db.get_mood_transitions(req.user_id, limit=1)
        mood_val = transitions[0]["mood"] if transitions else None

        if not mood_val:
            entries = db.get_mood_entries(req.user_id, limit=20)
            mood_val = entries[0].get("mood") if entries else None

        if not mood_val:
            insights = mood.get_mood_insights(req.user_id)
            mood_val = insights.get("most_common_mood", {}).get("mood") if isinstance(insights, dict) else None

        if not mood_val:
            mood_val = "calm"

        tracks = await sp.recommend_for_mood(mood_val)
        return {"mood": mood_val, "tracks": tracks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════
# WELLNESS RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════

@app.post("/api/wellness/recommendations")
async def get_wellness_recommendations(request: WellnessRequest):
    """
    Get personalized wellness recommendations
    """
    try:
        user_data = db.load_user_data(request.user_id)
        recommendations = well.get_recommendations(
            user_data=user_data,
            category=request.category
        )
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wellness/activities")
async def get_wellness_activities():
    """
    Get all available wellness activities
    """
    try:
        activities = well.get_all_activities()
        return {"activities": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════
# CALENDAR EVENTS
# ══════════════════════════════════════════════════════════════

class CalendarEventRequest(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: str  # ISO format datetime string
    duration_minutes: int = 30
    category: Optional[str] = None
    source: Optional[str] = None  # "suggestion" or "wellness"

@app.post("/api/calendar/create")
async def create_calendar_event(request: CalendarEventRequest):
    """
    Create a calendar event from suggestion or wellness activity
    """
    try:
        from datetime import timedelta
        import uuid
        
        # Parse start time
        start_dt = datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))
        end_dt = start_dt + timedelta(minutes=request.duration_minutes)
        
        # Determine event type from title/category
        event_type = request.category or cal.extract_event_type(request.title)
        
        # Create event in Google Calendar using the provided title
        # We'll use create_event directly to have more control
        from tools.calendar_tools import create_event as create_google_event
        
        end_dt = start_dt + timedelta(minutes=request.duration_minutes)
        
        google_result = create_google_event(
            summary=request.title,
            start_time=start_dt.isoformat(),
            end_time=end_dt.isoformat(),
            description=request.description or request.title,
            calendar_id="primary",
            reminders=[{"method": "popup", "minutes": 15}],
            use_default_reminders=False,
        )
        
        # Parse result to try to get event ID (though it's not in the JSON response)
        import json
        google_event_id = None
        try:
            result_data = json.loads(google_result) if isinstance(google_result, str) else google_result
            # The create_event doesn't return event ID, but we can try to extract from message
        except:
            pass
        
        result = {"success": True, "result": google_result, "google_event_id": google_event_id}
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create calendar event"))
        
        # Extract Google event ID from result
        google_event_id = result.get("google_event_id")
        
        # Generate local event ID
        event_id = str(uuid.uuid4())
        
        # Save to database
        db.save_calendar_event(
            user_id=request.user_id,
            event_id=event_id,
            google_event_id=google_event_id,
            title=request.title,
            description=request.description,
            start_time=start_dt.isoformat(),
            end_time=end_dt.isoformat(),
            category=request.category or event_type,
            source=request.source or "wellness"
        )
        
        return {
            "success": True,
            "event_id": event_id,
            "title": request.title,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "message": result.get("result", "")
        }
        
    except Exception as e:
        print(f"❌ Calendar event creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/events/{user_id}")
async def get_calendar_events(user_id: str, days_ahead: int = 30):
    """
    Get calendar events for a user
    """
    try:
        events = db.get_calendar_events(user_id, days_ahead=days_ahead)
        return {
            "user_id": user_id,
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/calendar/events/{user_id}/{event_id}")
async def delete_calendar_event(user_id: str, event_id: str):
    """
    Delete a calendar event
    """
    try:
        # Get event to find Google event ID
        events = db.get_calendar_events(user_id, limit=1000)
        event = next((e for e in events if e["id"] == event_id), None)
        
        if event and event.get("google_event_id"):
            # Delete from Google Calendar
            # Note: calendar_integration uses calendar_tools internally
            # We'll handle deletion through the calendar integration if needed
            pass
        
        # Delete from database
        success = db.delete_calendar_event(user_id, event_id)
        
        return {
            "success": success,
            "message": "Event deleted" if success else "Event not found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════════════════════════

@app.post("/api/user/profile")
async def update_user_profile(request: UserProfileRequest):
    """
    Update user profile and preferences
    """
    try:
        user_data = db.load_user_data(request.user_id)
        
        if request.name:
            user_data["profile"]["name"] = request.name
        
        if request.preferences:
            user_data["profile"]["preferences"].update(request.preferences)
        
        db.save_user_data(request.user_id, user_data)
        
        return {
            "success": True,
            "profile": user_data["profile"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user profile
    """
    try:
        user_data = db.load_user_data(user_id)
        return {
            "user_id": user_id,
            "profile": user_data.get("profile", {}),
            "stats": {
                "total_messages": len(user_data.get("history", [])),
                "mood_entries": len(user_data.get("mood_entries", [])),
                "days_active": user_data.get("days_active", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════════
# WEBSOCKET FOR REAL-TIME CHAT
# ══════════════════════════════════════════════════════════════

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    print(f"🔌 WebSocket connected: {user_id}")
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            user_data = db.load_user_data(user_id)
            
            user_data["history"].append({
                "role": "user",
                "text": message,
                "timestamp": str(datetime.now())
            })
            
            response_data = await chat.generate_support_response(
                user_data=user_data,
                user_message=message,
                user_id=user_id
            )
            
            user_data["history"].append({
                "role": "assistant",
                "text": response_data["response"],
                "timestamp": str(datetime.now())
            })
            
            db.save_user_data(user_id, user_data)
            
            await websocket.send_json({
                "response": response_data["response"],
                "mood_detected": response_data.get("mood_detected"),
                "mood_intensity": response_data.get("mood_intensity"),
                "crisis_detected": response_data.get("crisis_detected", False),
                "suggestions": response_data.get("suggestions")
            })
            
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: {user_id}")

# ══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Mental Health Support API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(datetime.now())}

# ══════════════════════════════════════════════════════════════
# RUN SERVER
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 MENTAL HEALTH SUPPORT CHATBOT API")
    print("="*60)
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )