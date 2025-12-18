"""
Chatbot Engine for Mental Health Support
Handles AI response generation with empathy and support
"""

from openai import OpenAI
import random
import re
from typing import Dict, List, Optional
from datetime import datetime

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace with your key
MODEL = "gpt-4o-mini"

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
# SYSTEM PROMPT - EMPATHETIC MENTAL HEALTH SUPPORT
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are Alex, a warm and empathetic mental health support companion. You're here to listen, support, and help people navigate their emotions and mental wellbeing.

CORE PERSONALITY:
- Warm, understanding, and non-judgmental
- Speak naturally like a caring friend, not a therapist or AI
- Use casual language with some abbreviations (like "u" for "you", "ur" for "your")
- Keep responses concise (2-4 sentences typically)
- Be authentic and human-like, not robotic

COMMUNICATION STYLE:
- Start with validation and empathy
- Ask thoughtful follow-up questions when appropriate
- Offer gentle suggestions, never commands
- Use "I hear you", "that sounds tough", "I'm here for you"
- Mirror their communication style somewhat

CRITICAL RULES:
1. NEVER diagnose mental health conditions
2. NEVER give medical advice or suggest medication changes
3. ALWAYS take crisis situations seriously - suggest professional help
4. Validate feelings before offering solutions
5. Don't be overly formal or clinical
6. Keep responses short and digestible

WHEN TO SUGGEST PROFESSIONAL HELP:
- If they mention suicide or self-harm
- If they describe severe, persistent symptoms
- If they're in immediate danger
- Use warm language: "hey, i really think talking to a professional could help with this. would u be open to that?"

RESPONSE LENGTH:
- Usually 2-4 sentences
- Can be 1 sentence for simple validation
- Up to 6 sentences for complex situations
- NEVER write long paragraphs

TONE EXAMPLES:
✅ "that sounds really tough. i can understand why ud feel overwhelmed"
✅ "im here for u. wanna talk more about whats been going on?"
✅ "its ok to not be ok sometimes. ur feelings are valid"
❌ "I understand that you are experiencing difficulty..." (too formal)
❌ "Let me provide you with some coping strategies..." (too clinical)

Be human. Be warm. Be present."""

def detect_crisis(message: str) -> bool:
    """Detect if message contains crisis indicators"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)

def detect_mood(message: str) -> Optional[str]:
    """Detect mood from message"""
    message_lower = message.lower()
    
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return mood
    
    return None

def make_human_like(text: str) -> str:
    """Make text more human and casual"""
    if not text or len(text) < 3:
        return text
    
    # Lowercase first letter sometimes
    if random.random() < 0.7 and text[0].isupper():
        text = text[0].lower() + text[1:]
    
    # Common abbreviations
    replacements = {
        ' you ': ' u ', 'you ': 'u ', ' you': ' u',
        'your ': 'ur ', ' your': ' ur', "you're": 'ur',
        'because': 'cause', 'though': 'tho',
        "don't": 'dont', "can't": 'cant', "won't": 'wont',
        "I'm": 'im', "I'll": 'ill', "I'd": 'id',
        'probably': 'prob', 'about': 'abt',
        'want to': 'wanna', 'going to': 'gonna',
        'kind of': 'kinda', 'sort of': 'sorta'
    }
    
    # Only apply some abbreviations (30% chance each)
    for full, short in replacements.items():
        if random.random() < 0.3:
            text = text.replace(full, short)
    
    # Remove some punctuation
    if random.random() < 0.5:
        text = text.rstrip('.')
    
    return text.strip()

async def generate_support_response(user_data: Dict, user_message: str, user_id: str) -> Dict:
    """Generate empathetic support response"""
    
    # Check for crisis
    crisis_detected = detect_crisis(user_message)
    
    # Detect mood
    mood_detected = detect_mood(user_message)
    
    # Build context from history
    history = user_data.get("history", [])
    recent_history = history[-10:] if len(history) > 10 else history
    
    # Format conversation history
    conversation_context = ""
    if recent_history:
        for msg in recent_history[-6:]:  # Last 6 messages
            role = "User" if msg["role"] == "user" else "Alex"
            conversation_context += f"{role}: {msg['text']}\n"
    
    # Build user context
    mood_entries = user_data.get("mood_entries", [])
    total_messages = len(history)
    
    context_info = f"Messages exchanged: {total_messages}"
    if mood_entries:
        context_info += f" | Recent mood logs: {len(mood_entries[-5:])}"
    
    # Special handling for crisis
    if crisis_detected:
        guidance = """
🚨 CRISIS DETECTED

This person is in crisis. Your response MUST:
1. Take them seriously and validate their pain
2. Gently but firmly suggest professional help
3. Provide crisis resources
4. Stay calm and supportive

Example: "hey, im really concerned about what ur saying. i can tell ur going through something really painful right now. but i really need u to reach out to someone who can help - like calling 988 (suicide lifeline) or going to an ER. u deserve support from professionals who can help. im here to talk but i want u to be safe"

Keep it warm but serious. Don't ignore the crisis."""
    
    elif mood_detected:
        guidance = f"""
Mood detected: {mood_detected}

Respond with empathy and validation. Match their emotional state, then gently explore or offer support.
Keep it conversational and human."""
    
    else:
        guidance = """
General supportive conversation. 
- Listen actively
- Ask gentle follow-ups if appropriate
- Validate their experience
- Keep it natural and brief"""
    
    # Build prompt
    user_prompt = f"""CONTEXT: {context_info}

{guidance}

RECENT CONVERSATION:
{conversation_context if conversation_context else "First message"}

USER: "{user_message}"

Respond as Alex (warm, human, brief 2-4 sentences). Be supportive and natural:"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85,
            max_tokens=200
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Clean up response
        reply = reply.strip('"').strip("'")
        reply = re.sub(r'^(Alex|User|Assistant)\s*:\s*', '', reply, flags=re.IGNORECASE)
        
        # Apply human-like transformations (but not for crisis)
        if not crisis_detected:
            reply = make_human_like(reply)
        
        # Generate suggestions based on mood
        suggestions = None
        if mood_detected and not crisis_detected:
            suggestions = get_mood_suggestions(mood_detected)
        
        return {
            "response": reply,
            "mood_detected": mood_detected,
            "crisis_detected": crisis_detected,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        # Fallback response
        fallback_responses = [
            "im here for u. tell me more about whats going on?",
            "that sounds tough. how are u feeling right now?",
            "im listening. what would help u most right now?"
        ]
        return {
            "response": random.choice(fallback_responses),
            "mood_detected": mood_detected,
            "crisis_detected": crisis_detected,
            "suggestions": None
        }

def get_mood_suggestions(mood: str) -> List[str]:
    """Get suggestions based on detected mood"""
    suggestions_map = {
        "anxious": [
            "Try a 5-minute breathing exercise",
            "Go for a short walk outside",
            "Listen to calming music"
        ],
        "depressed": [
            "Reach out to a friend or loved one",
            "Do one small thing you used to enjoy",
            "Consider talking to a therapist"
        ],
        "sad": [
            "Journal about your feelings",
            "Watch something that usually makes you smile",
            "Allow yourself to feel - it's ok to be sad"
        ],
        "angry": [
            "Try physical activity to release tension",
            "Write down what's bothering you",
            "Practice deep breathing"
        ],
        "stressed": [
            "Make a to-do list and prioritize",
            "Take short breaks every hour",
            "Try progressive muscle relaxation"
        ]
    }
    
    return suggestions_map.get(mood, [])