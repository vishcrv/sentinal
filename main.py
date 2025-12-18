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

# Initialize FastAPI
app = FastAPI(title="Mental Health Support API", version="1.0.0")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
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
    crisis_detected: bool = False
    suggestions: Optional[List[str]] = None
    mood_stats: Optional[Dict] = None

class MoodEntry(BaseModel):
    user_id: str
    mood: str  # happy, sad, anxious, stressed, angry, calm, etc.
    intensity: int  # 1-10
    notes: Optional[str] = None
    triggers: Optional[List[str]] = None

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
    category: Optional[str] = None  # breathing, meditation, activity, journaling

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
        
        # Generate response (this also analyzes and logs mood automatically)
        # Note: user_data is modified in-place to track conversation_moods
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
        
        # Update last activity
        user_data["last_activity"] = str(datetime.now())
        
        # Save user data
        db.save_user_data(request.user_id, user_data)
        
        # Get conversation mood stats for active mood bar
        mood_stats = chat.get_conversation_mood_stats(user_data)
        
        # Return response with mood stats
        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            mood_detected=response_data.get("mood_detected"),
            crisis_detected=response_data.get("crisis_detected", False),
            suggestions=response_data.get("suggestions"),
            mood_stats=mood_stats
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
        
        # Return last N messages
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
        db.save_user_data(user_id, user_data)
        
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/mood-bar/{user_id}")
async def get_active_mood_bar(user_id: str):
    """
    Get active mood bar data - current mood and conversation mood statistics
    """
    try:
        user_data = db.load_user_data(user_id)
        mood_stats = chat.get_conversation_mood_stats(user_data)
        
        return {
            "user_id": user_id,
            "mood_stats": mood_stats,
            "timestamp": str(datetime.now())
        }
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
            triggers=entry.triggers
        )
        
        # Get insights if user has enough data
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
# WEBSOCKET FOR REAL-TIME CHAT (OPTIONAL)
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
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            # Load user data
            user_data = db.load_user_data(user_id)
            
            # Add user message
            user_data["history"].append({
                "role": "user",
                "text": message,
                "timestamp": str(datetime.now())
            })
            
            # Generate response (this also analyzes and logs mood automatically)
            # Note: user_data is modified in-place to track conversation_moods
            response_data = await chat.generate_support_response(
                user_data=user_data,
                user_message=message,
                user_id=user_id
            )
            
            # Add bot response
            user_data["history"].append({
                "role": "assistant",
                "text": response_data["response"],
                "timestamp": str(datetime.now())
            })
            
            # Save
            db.save_user_data(user_id, user_data)
            
            # Get conversation mood stats
            mood_stats = chat.get_conversation_mood_stats(user_data)
            
            # Send response
            await websocket.send_json({
                "response": response_data["response"],
                "mood_detected": response_data.get("mood_detected"),
                "crisis_detected": response_data.get("crisis_detected", False),
                "suggestions": response_data.get("suggestions"),
                "mood_stats": mood_stats
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
        reload=True  # Auto-reload on code changes
    )