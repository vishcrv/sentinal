"""
Wellness Recommendations Module
Provides personalized coping strategies and activities
"""

from typing import Dict, List, Optional
import random

# ══════════════════════════════════════════════════════════════
# WELLNESS ACTIVITIES DATABASE
# ══════════════════════════════════════════════════════════════

BREATHING_EXERCISES = [
    {
        "name": "4-7-8 Breathing",
        "description": "Breathe in for 4 seconds, hold for 7, exhale for 8",
        "duration": "5 minutes",
        "difficulty": "easy",
        "benefits": ["reduces anxiety", "promotes calm", "helps sleep"]
    },
    {
        "name": "Box Breathing",
        "description": "Breathe in for 4, hold for 4, out for 4, hold for 4",
        "duration": "5-10 minutes",
        "difficulty": "easy",
        "benefits": ["reduces stress", "improves focus", "calms nervous system"]
    },
    {
        "name": "Belly Breathing",
        "description": "Deep breaths into your belly, not your chest",
        "duration": "5 minutes",
        "difficulty": "easy",
        "benefits": ["reduces tension", "promotes relaxation", "lowers heart rate"]
    }
]

MEDITATION_ACTIVITIES = [
    {
        "name": "Body Scan Meditation",
        "description": "Slowly focus attention on each part of your body",
        "duration": "10-15 minutes",
        "difficulty": "beginner",
        "benefits": ["releases tension", "increases awareness", "promotes relaxation"]
    },
    {
        "name": "Mindful Observation",
        "description": "Focus on one object and observe every detail",
        "duration": "5 minutes",
        "difficulty": "beginner",
        "benefits": ["improves focus", "reduces racing thoughts", "grounds you"]
    },
    {
        "name": "Loving-Kindness Meditation",
        "description": "Send kind wishes to yourself and others",
        "duration": "10 minutes",
        "difficulty": "intermediate",
        "benefits": ["increases compassion", "reduces negative emotions", "improves mood"]
    }
]

PHYSICAL_ACTIVITIES = [
    {
        "name": "Short Walk",
        "description": "Take a 10-minute walk outside or around your space",
        "duration": "10-20 minutes",
        "difficulty": "easy",
        "benefits": ["boosts mood", "increases energy", "clears mind"]
    },
    {
        "name": "Gentle Stretching",
        "description": "Simple stretches to release physical tension",
        "duration": "5-10 minutes",
        "difficulty": "easy",
        "benefits": ["releases tension", "improves circulation", "feels good"]
    },
    {
        "name": "Dancing to Music",
        "description": "Put on your favorite song and move however feels good",
        "duration": "10 minutes",
        "difficulty": "easy",
        "benefits": ["lifts mood", "releases endorphins", "fun!"]
    },
    {
        "name": "Yoga Flow",
        "description": "Follow a simple yoga sequence",
        "duration": "15-30 minutes",
        "difficulty": "moderate",
        "benefits": ["reduces stress", "improves flexibility", "calms mind"]
    }
]

JOURNALING_PROMPTS = [
    {
        "name": "Gratitude Journal",
        "prompt": "Write 3 things you're grateful for today, no matter how small",
        "duration": "5 minutes",
        "difficulty": "easy",
        "benefits": ["shifts perspective", "improves mood", "builds resilience"]
    },
    {
        "name": "Emotion Exploration",
        "prompt": "What am I feeling right now? Where do I feel it in my body? What triggered it?",
        "duration": "10 minutes",
        "difficulty": "moderate",
        "benefits": ["increases awareness", "processes emotions", "identifies patterns"]
    },
    {
        "name": "Future Self Letter",
        "prompt": "Write a letter to your future self about what you're going through",
        "duration": "15 minutes",
        "difficulty": "moderate",
        "benefits": ["gains perspective", "processes thoughts", "provides hope"]
    },
    {
        "name": "Stream of Consciousness",
        "prompt": "Write whatever comes to mind for 5 minutes without stopping",
        "duration": "5 minutes",
        "difficulty": "easy",
        "benefits": ["clears mental clutter", "reduces anxiety", "uncovers thoughts"]
    }
]

GROUNDING_TECHNIQUES = [
    {
        "name": "5-4-3-2-1 Technique",
        "description": "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste",
        "duration": "2-5 minutes",
        "difficulty": "easy",
        "benefits": ["stops panic", "grounds you", "brings you present"]
    },
    {
        "name": "Ice Cube Hold",
        "description": "Hold an ice cube in your hand and focus on the sensation",
        "duration": "1 minute",
        "difficulty": "easy",
        "benefits": ["interrupts spiraling", "strong grounding", "immediate effect"]
    },
    {
        "name": "Cold Water Face Splash",
        "description": "Splash cold water on your face or hold a cold cloth to your face",
        "duration": "30 seconds",
        "difficulty": "easy",
        "benefits": ["calms nervous system", "reduces panic", "quick relief"]
    }
]

SOCIAL_ACTIVITIES = [
    {
        "name": "Text a Friend",
        "description": "Reach out to someone you trust, even just to say hi",
        "duration": "5 minutes",
        "difficulty": "easy",
        "benefits": ["reduces isolation", "builds connection", "boosts mood"]
    },
    {
        "name": "Call Someone",
        "description": "Have a voice conversation with a friend or family member",
        "duration": "15-30 minutes",
        "difficulty": "moderate",
        "benefits": ["deep connection", "reduces loneliness", "feels supported"]
    },
    {
        "name": "Join Online Community",
        "description": "Engage with a supportive online group or forum",
        "duration": "10-20 minutes",
        "difficulty": "easy",
        "benefits": ["reduces isolation", "finds understanding", "shares experiences"]
    }
]

CREATIVE_ACTIVITIES = [
    {
        "name": "Free Drawing",
        "description": "Draw or doodle whatever comes to mind, no judgment",
        "duration": "10-15 minutes",
        "difficulty": "easy",
        "benefits": ["expresses emotions", "relaxes mind", "fun outlet"]
    },
    {
        "name": "Listen to Music",
        "description": "Put on music that matches or shifts your mood",
        "duration": "10-30 minutes",
        "difficulty": "easy",
        "benefits": ["regulates emotions", "provides comfort", "shifts energy"]
    },
    {
        "name": "Write Poetry",
        "description": "Express your feelings through poetry or creative writing",
        "duration": "15 minutes",
        "difficulty": "moderate",
        "benefits": ["processes emotions", "creative outlet", "self-expression"]
    }
]

# Combine all activities
ALL_ACTIVITIES = {
    "breathing": BREATHING_EXERCISES,
    "meditation": MEDITATION_ACTIVITIES,
    "physical": PHYSICAL_ACTIVITIES,
    "journaling": JOURNALING_PROMPTS,
    "grounding": GROUNDING_TECHNIQUES,
    "social": SOCIAL_ACTIVITIES,
    "creative": CREATIVE_ACTIVITIES
}

# ══════════════════════════════════════════════════════════════
# RECOMMENDATION ENGINE
# ══════════════════════════════════════════════════════════════

def get_recommendations(user_data: Dict, category: Optional[str] = None,
                       mood: Optional[str] = None, count: int = 3) -> List[Dict]:
    """
    Get personalized wellness recommendations
    
    Args:
        user_data: User's data including history and preferences
        category: Optional category to filter by
        mood: Optional mood to tailor recommendations
        count: Number of recommendations to return
    
    Returns:
        List of recommended activities
    """
    recommendations = []
    
    # If category specified, get from that category
    if category and category in ALL_ACTIVITIES:
        activities = ALL_ACTIVITIES[category].copy()
        random.shuffle(activities)
        return activities[:count]
    
    # If mood specified, get mood-appropriate activities
    if mood:
        recommendations = get_mood_based_recommendations(mood, count)
        return recommendations
    
    # Otherwise, get a mix of activities
    all_items = []
    for category_items in ALL_ACTIVITIES.values():
        all_items.extend(category_items)
    
    random.shuffle(all_items)
    return all_items[:count]

def get_mood_based_recommendations(mood: str, count: int = 3) -> List[Dict]:
    """Get recommendations based on current mood"""
    
    recommendations = []
    
    if mood == "anxious":
        # Calming activities for anxiety
        recommendations.extend(BREATHING_EXERCISES[:2])
        recommendations.extend(GROUNDING_TECHNIQUES[:2])
        recommendations.append(random.choice(MEDITATION_ACTIVITIES))
    
    elif mood == "depressed":
        # Activating and connecting activities
        recommendations.extend(PHYSICAL_ACTIVITIES[:2])
        recommendations.extend(SOCIAL_ACTIVITIES[:1])
        recommendations.append(random.choice(JOURNALING_PROMPTS))
    
    elif mood == "sad":
        # Comforting and expressive activities
        recommendations.extend(CREATIVE_ACTIVITIES[:2])
        recommendations.extend(JOURNALING_PROMPTS[:2])
        recommendations.append(random.choice(SOCIAL_ACTIVITIES))
    
    elif mood == "angry":
        # Physical release and calming
        recommendations.extend(PHYSICAL_ACTIVITIES[:2])
        recommendations.extend(BREATHING_EXERCISES[:1])
        recommendations.append(random.choice(JOURNALING_PROMPTS))
    
    elif mood == "stressed":
        # Stress-reducing activities
        recommendations.extend(BREATHING_EXERCISES[:2])
        recommendations.append(random.choice(PHYSICAL_ACTIVITIES))
        recommendations.append(random.choice(MEDITATION_ACTIVITIES))
    
    else:
        # General wellbeing activities
        categories = list(ALL_ACTIVITIES.keys())
        for _ in range(count):
            cat = random.choice(categories)
            recommendations.append(random.choice(ALL_ACTIVITIES[cat]))
    
    random.shuffle(recommendations)
    return recommendations[:count]

def get_all_activities() -> Dict[str, List[Dict]]:
    """Get all available activities organized by category"""
    return ALL_ACTIVITIES

def get_activity_by_time(available_minutes: int) -> List[Dict]:
    """Get activities that fit in the available time"""
    suitable = []
    
    for category_items in ALL_ACTIVITIES.values():
        for activity in category_items:
            duration_str = activity["duration"]
            # Parse duration (e.g., "5 minutes", "10-20 minutes")
            max_duration = parse_max_duration(duration_str)
            
            if max_duration <= available_minutes:
                suitable.append(activity)
    
    return suitable

def parse_max_duration(duration_str: str) -> int:
    """Parse duration string to get max minutes"""
    import re
    
    # Extract all numbers from duration string
    numbers = re.findall(r'\d+', duration_str)
    
    if not numbers:
        return 10  # default
    
    # Return the highest number (for ranges like "10-20 minutes")
    return max(int(n) for n in numbers)