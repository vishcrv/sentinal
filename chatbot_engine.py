"""
Chatbot Engine for Mental Health Support
Handles AI response generation with authentic human conversation
"""

from openai import OpenAI
import random
import re
from typing import Dict, List, Optional
from datetime import datetime
import config
import database as db

# Initialize OpenAI client using config
client = OpenAI(api_key="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")
MODEL = getattr(config, "OPENAI_MODEL", "gpt-4o-mini")

# Crisis keywords detection
CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end it all", "want to die", "better off dead",
    "hurt myself", "self harm", "cut myself", "overdose", "jump off"
]

# Mood detection keywords
MOOD_KEYWORDS = {
    "anxious": ["anxious", "anxiety", "worried", "nervous", "panic", "stressed"],
    "depressed": ["depressed", "depression", "hopeless", "worthless", "empty", "numb"],
    "sad": ["sad", "down", "unhappy", "miserable", "crying", "tears"],
    "angry": ["angry", "mad", "frustrated", "furious", "rage", "pissed"],
    "happy": ["happy", "joy", "good", "great", "wonderful", "amazing"],
    "calm": ["calm", "peaceful", "relaxed", "serene", "content"]
}

# ══════════════════════════════════════════════════════════════
# SYSTEM PROMPT - AUTHENTIC HUMAN FRIEND
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """# """

# ══════════════════════════════════════════════════════════════
# MOOD ANALYSIS PROMPT
# ══════════════════════════════════════════════════════════════

MOOD_ANALYSIS_PROMPT = """Analyze the emotional state from this conversation message.

Return ONLY a JSON object with this exact format (no markdown, no extra text):
{
  "mood": "one of: happy, sad, anxious, depressed, angry, calm, stressed, neutral",
  "intensity": 5,
  "confidence": 0.8,
  "notes": "brief reason for this assessment"
}

Message to analyze: "{message}"

Respond with ONLY the JSON object."""

def detect_crisis(message: str) -> bool:
    """Detect if message contains crisis indicators"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)

def detect_mood(message: str) -> Optional[str]:
    """Detect mood from message using keywords"""
    message_lower = message.lower()
    
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return mood
    
    return None

def analyze_mood_with_llm(message: str) -> Optional[Dict]:
    """Use LLM to analyze mood from message with more nuance"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a mood analysis expert. Return only valid JSON."},
                {"role": "user", "content": MOOD_ANALYSIS_PROMPT.format(message=message)}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        result = response.choices[0].message.content.strip()
        # Clean up any markdown
        result = result.replace("```json", "").replace("```", "").strip()
        
        import json
        mood_data = json.loads(result)
        
        # Validate the response
        if "mood" in mood_data and "intensity" in mood_data:
            return mood_data
        
    except Exception as e:
        print(f"⚠️ Mood analysis error: {e}")
    
    return None

def make_human_like(text: str) -> str:
    """Make text more human and casual - LIGHT touch only"""
    if not text or len(text) < 3:
        return text
    
    # Very light processing - let LLM handle most of it
    
    # Remove trailing periods sometimes (casual texting style)
    if random.random() < 0.7:
        text = text.rstrip('.')
    
    # Only lowercase first letter occasionally
    if random.random() < 0.3 and text[0].isupper() and len(text) > 10:
        text = text[0].lower() + text[1:]
    
    return text.strip()

async def generate_support_response(user_data: Dict, user_message: str, user_id: str) -> Dict:
    """Generate authentic human friend response with continuous mood tracking"""
    
    # Check for crisis
    crisis_detected = detect_crisis(user_message)

    # Analyze mood with LLM for better accuracy
    mood_analysis = analyze_mood_with_llm(user_message)
    mood_detected = None
    intensity = 5
    
    if mood_analysis:
        mood_detected = mood_analysis.get("mood")
        intensity = mood_analysis.get("intensity", 5)
        
        # Skip "neutral" mood unless it's confident
        if mood_detected == "neutral" and mood_analysis.get("confidence", 0) < 0.7:
            mood_detected = None
    
    # Fallback to keyword detection if LLM fails
    if not mood_detected:
        mood_detected = detect_mood(user_message)
        if mood_detected:
            intensity = estimate_intensity(user_message)
    
    # Build context from history
    history = user_data.get("history", [])
    max_msgs = getattr(config, "MAX_HISTORY_MESSAGES", 50)
    recent_history = history[-max_msgs:] if len(history) > max_msgs else history
    
    # Format conversation history
    conversation_context = ""
    if recent_history:
        context_window = recent_history[-10:] if len(recent_history) > 10 else recent_history
        for msg in context_window:
            role = "Them" if msg["role"] == "user" else "You"
            conversation_context += f"{role}: {msg['text']}\n"
    
    # Build user context
    total_messages = len(history)
    context_info = f"You've chatted {total_messages} times before" if total_messages > 5 else "Getting to know them"
    
    # Special handling for crisis
    if crisis_detected:
        guidance = """
🚨 REAL CRISIS - They mentioned suicide/self-harm

You need to be a concerned friend who recognizes this is serious:
- Don't panic but be real: "yo hold up, that sounds really serious"
- Tell them straight up they need professional help: "u should call 988 or go to the ER"
- Be supportive but firm: "bro im worried about u... can u talk to someone who can actually help?"
- Keep it friend-like but serious

Don't ignore it. Don't minimize it. Get them real help."""
    
    elif mood_detected and mood_detected in ["depressed", "anxious"]:
        guidance = f"""
They seem {mood_detected}. Respond like a friend who notices:
- Don't diagnose or therapize
- Just be empathetic naturally: "damn that sucks" or "i feel u"
- Maybe ask what's going on, but casually
- Let them talk, don't push solutions

Keep it real and friendly."""
    
    else:
        guidance = """
Regular conversation with your friend:
- Be natural and casual
- Match their energy
- React authentically to what they say
- Keep responses short like texting
- Be interested in their life

Just chat like you would with any friend."""
    
    # Build prompt
    user_prompt = f"""Context: {context_info}

{guidance}

RECENT CONVERSATION:
{conversation_context if conversation_context else "They just started chatting with you"}

THEM: "{user_message}"

Respond naturally as their friend Alex (super casual, 1-2 sentences typically, authentic human texting style):"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=150
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Minimal cleanup
        reply = reply.strip('"').strip("'")
        reply = re.sub(r'^(Alex|You|Them|Assistant)\s*:\s*', '', reply, flags=re.IGNORECASE)
        
        # Very light human-like touch
        if not crisis_detected:
            reply = make_human_like(reply)
        
        # Generate suggestions ONLY if mood is detected and not crisis
        suggestions = None
        if mood_detected and not crisis_detected and mood_detected in ["anxious", "stressed", "sad"]:
            suggestions = get_subtle_suggestions(mood_detected)

        # Log mood transition if detected
        if mood_detected:
            try:
                db.log_mood_transition(
                    user_id=user_id,
                    mood=mood_detected,
                    intensity=int(intensity),
                    message=user_message,
                    context=mood_analysis.get("notes", "") if mood_analysis else ""
                )
            except Exception as e:
                print(f"⚠️ Failed to log mood transition: {e}")
        
        return {
            "response": reply,
            "mood_detected": mood_detected,
            "mood_intensity": intensity if mood_detected else None,
            "crisis_detected": crisis_detected,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        fallback_responses = [
            "yea im listening, whats up",
            "go on, im here",
            "damn, tell me more",
            "fr? keep going",
            "yea i feel that, what else"
        ]
        return {
            "response": random.choice(fallback_responses),
            "mood_detected": mood_detected,
            "mood_intensity": intensity if mood_detected else None,
            "crisis_detected": crisis_detected,
            "suggestions": None
        }

def get_subtle_suggestions(mood: str) -> List[str]:
    """Get subtle, friend-like suggestions (not clinical)"""
    suggestions_map = {
        "anxious": [
            "maybe take a quick walk to clear ur head?",
            "have u tried just breathing slow for a min?",
            "sometimes music helps me chill out"
        ],
        "depressed": [
            "wanna try calling someone u trust?",
            "maybe do something small u used to like?",
            "talking to someone might help tbh"
        ],
        "sad": [
            "sometimes writing stuff down helps",
            "watch something funny maybe?",
            "its ok to just feel it for a bit"
        ],
        "angry": [
            "maybe hit the gym or go for a run?",
            "write down whats pissing u off?",
            "take some deep breaths bro"
        ],
        "stressed": [
            "make a list of whats stressing u?",
            "take breaks every hour if u can",
            "maybe try that muscle relaxation thing"
        ]
    }
    
    return suggestions_map.get(mood, [])

def estimate_intensity(message: str) -> int:
    """Heuristic to estimate mood intensity from message text (1-10)"""
    if not message:
        return 5

    score = 5
    
    # Exclamation marks = more intense
    exclam = message.count("!")
    if exclam:
        score += min(3, exclam)

    # All caps words = more intense
    caps = sum(1 for w in message.split() if w.isupper() and len(w) > 1)
    score += min(2, caps)

    # Strong emotional words
    intense_words = ["really", "very", "terrible", "horrible", "overwhelmed", "extremely", "fucking", "so much"]
    for w in intense_words:
        if w in message.lower():
            score += 1

    # Clamp between 1-10
    return max(1, min(10, int(score)))