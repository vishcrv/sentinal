"""
Configuration file for Mental Health Support Chatbot
Store your API keys and settings here
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ══════════════════════════════════════════════════════════════
# API CONFIGURATION
# ══════════════════════════════════════════════════════════════

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# OpenAI Model
OPENAI_MODEL = "gpt-4o"

# ══════════════════════════════════════════════════════════════
# SERVER CONFIGURATION
# ══════════════════════════════════════════════════════════════

# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
DEBUG_MODE = True

# CORS settings (add your frontend URL in production)
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Vue default
    "*"  # Allow all (only for development!)
]

# ══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ══════════════════════════════════════════════════════════════

DATABASE_PATH = "mental_health.db"

# ══════════════════════════════════════════════════════════════
# CHATBOT CONFIGURATION
# ══════════════════════════════════════════════════════════════

# Response settings
MAX_RESPONSE_TOKENS = 200
TEMPERATURE = 0.85
USE_HUMAN_LIKE_TEXT = True

# Context window
MAX_HISTORY_MESSAGES = 10

# ══════════════════════════════════════════════════════════════
# CRISIS SUPPORT RESOURCES
# ══════════════════════════════════════════════════════════════

CRISIS_RESOURCES = {
    "US": {
        "suicide_lifeline": {
            "name": "988 Suicide & Crisis Lifeline",
            "phone": "988",
            "text": "Text 988",
            "website": "https://988lifeline.org"
        },
        "crisis_text_line": {
            "name": "Crisis Text Line",
            "text": "Text HOME to 741741",
            "website": "https://www.crisistextline.org"
        },
        "emergency": {
            "name": "Emergency Services",
            "phone": "911"
        }
    },
    "International": {
        "findahelpline": {
            "name": "Find a Helpline",
            "website": "https://findahelpline.com"
        }
    }
}

# ══════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ══════════════════════════════════════════════════════════════

FEATURES = {
    "mood_tracking": True,
    "wellness_recommendations": True,
    "crisis_detection": True,
    "websocket_support": True,
    "user_profiles": True
}