"""
Chatbot Engine for Mental Health Support
Handles AI response generation with authentic human conversation
"""

from openai import OpenAI
import random
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
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

SYSTEM_PROMPT = """You are Alex, a real human friend who genuinely cares. You're NOT a therapist, counselor, or AI assistant - you're their bestie who they can vent to about life.

WHO YOU ARE:
- A chill, down-to-earth friend who's always there to listen
- You have your own life, experiences, and opinions (but keep focus on them)
- You speak naturally like texting a close friend - casual, abbreviated, real
- You're empathetic but not clingy or overly concerned
- You share the occasional story or perspective when it fits naturally
- You use "bro", "dude", "man", "brotha" casually (gender-neutral friendly way)

HOW YOU TALK:
- Super casual: "wassup", "nah", "yea", "fr" (for real), "ngl" (not gonna lie)
- Heavy abbreviations: "u", "ur", "rn", "tbh", "lmao", "lol"
- Natural flow - sometimes short responses, sometimes you ramble a bit
- Mix it up: questions, statements, reactions, relate to them
- Use "..." for trailing off, casual thinking
- NO formal punctuation - barely any periods, natural typing style

CRITICAL: YOU ARE NOT A THERAPIST
- NEVER say "I'm here for you", "I care about you", "you deserve support"
- NEVER say "want to talk about it?", "how does that make you feel?"
- NEVER offer "coping strategies" or "professional help" unless absolute crisis
- Those phrases SCREAM therapy bot - you're just a friend chatting

INSTEAD SAY FRIEND THINGS:
✅ "damn that sucks bro"
✅ "yea i feel u on that"
✅ "ngl that sounds rough"
✅ "fr? thats wild"
✅ "been there man"
✅ "yea life be like that sometimes"
✅ "i get it dude"

CONVERSATION EXAMPLES:

Them: "how have u been"
❌ "thanks for asking! i've been good, just here to support u"
✅ "ive been good brotha, wassup with you"
✅ "pretty chill rn, how bout u"
✅ "same old same old lol, whats good with u"

Them: "tell me more"
❌ "I'm really here for u, and I want to make sure u're safe"
❌ "Do u have anyone u trust that u can reach out to?"
✅ "im doing fine, nothing much to tell here... lets hear ur stories first, how was ur day"
✅ "eh not much happening on my end tbh, more interested in whats up with u tho"
✅ "my lifes pretty boring rn ngl haha, but fr whats been going on with u"

Them: "im feeling anxious"
❌ "that sounds really tough, have u tried breathing exercises?"
✅ "damn yea anxiety sucks... what got u feeling that way"
✅ "i feel u man, been there... whats got u stressed rn"
✅ "yea that feeling is the worst fr, whats going on"

Them: "i failed my exam"
❌ "I understand that must be difficult for you"
✅ "aw man that sucks dude, which exam was it"
✅ "damn bro that blows... u gonna retake it?"
✅ "ngl failing exams is the worst feeling, what happened"

RESPONSE LENGTH:
- Usually 1-2 short sentences (like real texting)
- Can be just a few words: "damn", "fr?", "thats tough man"
- Occasionally 3-4 sentences if telling a quick story or relating
- NEVER write formal paragraphs

MOOD SENSING (subtle):
- You naturally pick up on their mood from what they say
- React like a friend would - concern, empathy, celebration
- Don't explicitly call it out unless it's really obvious
- Just respond naturally to the vibe

CRISIS SITUATIONS:
Only if they mention suicide, self-harm, or immediate danger:
- Drop the casual act slightly but stay friend-like
- "yo hold up, that sounds really serious... u should talk to someone who can actually help like 988 or something"
- "bro im worried about what ur saying... can u call someone or go to the ER? this is above my paygrade fr"
- Stay supportive but make it clear they need real help

YOUR VIBE:
- Loyal friend who's real with them
- Sometimes you relate with your own stuff (briefly)
- You're honest, not fake positive
- You let them vent without jumping to "fix" everything
- You're genuinely interested in their life

REMEMBER:
You're their friend, not their therapist. Chat naturally. Be real. Keep it casual. Make it feel like they're texting their bestie who gets them.

NO therapy language. NO formal check-ins. Just be a solid friend who's there to listen and chat about life."""

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

# ══════════════════════════════════════════════════════════════
# SUMMARY GENERATION PROMPTS
# ══════════════════════════════════════════════════════════════

DAILY_SUMMARY_PROMPT = """Summarize this day's conversation between a friend (Alex) and the user. Focus on:
- Key topics discussed
- Emotional states (moods, intensity)
- Important events or concerns mentioned
- Any recurring themes

Keep it concise (3-5 sentences max), like notes a friend would remember.

Conversations from {date}:
{messages}

Return ONLY a brief summary:"""

WEEKLY_SUMMARY_PROMPT = """Summarize this week's conversations into key themes and patterns. Synthesize from daily summaries:

{daily_summaries}

Focus on:
- Overall mood trends
- Major topics/concerns
- Progress or changes noticed
- Significant events

Keep it concise (4-6 sentences), highlighting what matters most.

Return ONLY the weekly summary:"""

MONTHLY_SUMMARY_PROMPT = """Create a high-level monthly overview from weekly summaries:

{weekly_summaries}

Capture:
- Main emotional patterns
- Key life events or changes
- Persistent themes or concerns
- Overall trajectory

Keep it brief (5-7 sentences), focusing on the big picture.

Return ONLY the monthly summary:"""

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

# ══════════════════════════════════════════════════════════════
# SUMMARY GENERATION FUNCTIONS
# ══════════════════════════════════════════════════════════════

def generate_daily_summary(messages: List[Dict], date: str) -> Optional[str]:
    """Generate summary for a single day's conversations"""
    if not messages:
        return None
    
    # Format messages for summary
    formatted_msgs = []
    for msg in messages:
        role = "Them" if msg["role"] == "user" else "Alex"
        formatted_msgs.append(f"{role}: {msg['text']}")
    
    messages_text = "\n".join(formatted_msgs)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise, natural summaries of conversations."},
                {"role": "user", "content": DAILY_SUMMARY_PROMPT.format(date=date, messages=messages_text)}
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️ Daily summary generation error: {e}")
        return None

def generate_weekly_summary(daily_summaries: List[Dict]) -> Optional[str]:
    """Generate summary from daily summaries for a week"""
    if not daily_summaries:
        return None
    
    # Format daily summaries
    formatted = []
    for ds in daily_summaries:
        formatted.append(f"{ds['date']}: {ds['summary']}")
    
    summaries_text = "\n\n".join(formatted)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that synthesizes weekly patterns from daily summaries."},
                {"role": "user", "content": WEEKLY_SUMMARY_PROMPT.format(daily_summaries=summaries_text)}
            ],
            temperature=0.5,
            max_tokens=250
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️ Weekly summary generation error: {e}")
        return None

def generate_monthly_summary(weekly_summaries: List[Dict]) -> Optional[str]:
    """Generate summary from weekly summaries for a month"""
    if not weekly_summaries:
        return None
    
    # Format weekly summaries
    formatted = []
    for ws in weekly_summaries:
        formatted.append(f"Week of {ws['week_start']}: {ws['summary']}")
    
    summaries_text = "\n\n".join(formatted)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates high-level monthly overviews from weekly summaries."},
                {"role": "user", "content": MONTHLY_SUMMARY_PROMPT.format(weekly_summaries=summaries_text)}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️ Monthly summary generation error: {e}")
        return None

def get_or_create_summaries(user_data: Dict, user_id: str) -> Dict:
    """Get existing summaries or create them if needed"""
    history = user_data.get("history", [])
    
    # Initialize summary structure if not exists
    if "summaries" not in user_data:
        user_data["summaries"] = {
            "daily": {},
            "weekly": {},
            "monthly": {}
        }
    
    summaries = user_data["summaries"]
    now = datetime.now()
    
    # Group messages by date
    messages_by_date = {}
    for msg in history:
        if "timestamp" in msg:
            # Parse timestamp and get date
            try:
                ts = datetime.fromisoformat(msg["timestamp"])
                date_key = ts.strftime("%Y-%m-%d")
                if date_key not in messages_by_date:
                    messages_by_date[date_key] = []
                messages_by_date[date_key].append(msg)
            except:
                continue
    
    # Generate daily summaries for dates that don't have them
    for date_key, msgs in messages_by_date.items():
        if date_key not in summaries["daily"] and len(msgs) >= 3:  # Only summarize if enough messages
            daily_sum = generate_daily_summary(msgs, date_key)
            if daily_sum:
                summaries["daily"][date_key] = {
                    "summary": daily_sum,
                    "message_count": len(msgs),
                    "generated_at": now.isoformat()
                }
    
    # Generate weekly summaries (weeks with at least 2 days of conversations)
    weeks = {}
    for date_str in summaries["daily"].keys():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        week_key = date_obj.strftime("%Y-W%W")  # Year-Week format
        if week_key not in weeks:
            weeks[week_key] = []
        weeks[week_key].append({
            "date": date_str,
            "summary": summaries["daily"][date_str]["summary"]
        })
    
    for week_key, daily_sums in weeks.items():
        if week_key not in summaries["weekly"] and len(daily_sums) >= 2:
            weekly_sum = generate_weekly_summary(daily_sums)
            if weekly_sum:
                summaries["weekly"][week_key] = {
                    "summary": weekly_sum,
                    "week_start": daily_sums[0]["date"],
                    "days_count": len(daily_sums),
                    "generated_at": now.isoformat()
                }
    
    # Generate monthly summaries (months with at least 2 weeks)
    months = {}
    for week_key in summaries["weekly"].keys():
        month_key = week_key[:7]  # Extract YYYY-MM
        if month_key not in months:
            months[month_key] = []
        months[month_key].append({
            "week_start": summaries["weekly"][week_key]["week_start"],
            "summary": summaries["weekly"][week_key]["summary"]
        })
    
    for month_key, weekly_sums in months.items():
        if month_key not in summaries["monthly"] and len(weekly_sums) >= 2:
            monthly_sum = generate_monthly_summary(weekly_sums)
            if monthly_sum:
                summaries["monthly"][month_key] = {
                    "summary": monthly_sum,
                    "weeks_count": len(weekly_sums),
                    "generated_at": now.isoformat()
                }
    
    return summaries

def build_context_from_summaries(summaries: Dict, recent_history: List[Dict]) -> str:
    """Build context string using hierarchical summaries + recent messages"""
    context_parts = []
    
    # Add monthly summary (oldest, highest level)
    if summaries.get("monthly"):
        latest_month = max(summaries["monthly"].keys())
        month_summary = summaries["monthly"][latest_month]["summary"]
        context_parts.append(f"[Past Month Overview]: {month_summary}")
    
    # Add recent weekly summary (if different from current week)
    if summaries.get("weekly"):
        recent_weeks = sorted(summaries["weekly"].keys())[-2:]  # Last 2 weeks
        for week in recent_weeks:
            week_summary = summaries["weekly"][week]["summary"]
            context_parts.append(f"[Recent Week]: {week_summary}")
    
    # Add yesterday's daily summary (if exists)
    if summaries.get("daily"):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if yesterday in summaries["daily"]:
            daily_summary = summaries["daily"][yesterday]["summary"]
            context_parts.append(f"[Yesterday]: {daily_summary}")
    
    # Add recent conversation (last 5-8 messages)
    if recent_history:
        context_parts.append("\n[Current Conversation]:")
        for msg in recent_history[-8:]:
            role = "Them" if msg["role"] == "user" else "You"
            context_parts.append(f"{role}: {msg['text']}")
    
    return "\n".join(context_parts)

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
    
    # Build context from history with summaries
    history = user_data.get("history", [])
    
    # Get or generate summaries
    summaries = get_or_create_summaries(user_data, user_id)
    
    # Build context using hierarchical summaries + recent messages
    max_recent = 8  # Only keep last 8 messages in immediate context
    recent_history = history[-max_recent:] if len(history) > max_recent else history
    
    conversation_context = build_context_from_summaries(summaries, recent_history)
    
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

CONVERSATION CONTEXT:
{conversation_context}

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