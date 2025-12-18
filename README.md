# Mental Health Support Chatbot Backend 🧠💙

A compassionate AI-powered mental health support chatbot with mood tracking, wellness recommendations, and crisis detection.

## Features

- **Empathetic Chat Support**: Natural, human-like conversations with emotional support
- **Context Retention**: Remembers conversation history for personalized responses
- **Mood Tracking**: Log and analyze mood patterns over time
- **Wellness Recommendations**: Personalized coping strategies and activities
- **Crisis Detection**: Identifies crisis situations and provides appropriate resources
- **RESTful API**: Easy integration with any frontend
- **WebSocket Support**: Real-time chat capabilities

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Chat Endpoints

#### POST `/api/chat`
Send a message and get a response.

**Request:**
```json
{
  "user_id": "user123",
  "message": "I'm feeling anxious today",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "im sorry ur feeling anxious. wanna talk about whats making u feel that way?",
  "session_id": "abc-123",
  "mood_detected": "anxious",
  "crisis_detected": false,
  "suggestions": [
    "Try a 5-minute breathing exercise",
    "Go for a short walk outside"
  ]
}
```

#### GET `/api/chat/history/{user_id}`
Get chat history for a user.

#### DELETE `/api/chat/history/{user_id}`
Clear chat history.

### Mood Tracking Endpoints

#### POST `/api/mood/log`
Log a mood entry.

**Request:**
```json
{
  "user_id": "user123",
  "mood": "anxious",
  "intensity": 7,
  "notes": "Work deadline stress",
  "triggers": ["work", "deadline"]
}
```

#### GET `/api/mood/history/{user_id}`
Get mood history (default: last 30 days).

#### GET `/api/mood/insights/{user_id}`
Get mood insights and patterns.

### Wellness Endpoints

#### POST `/api/wellness/recommendations`
Get personalized wellness recommendations.

**Request:**
```json
{
  "user_id": "user123",
  "category": "breathing"
}
```

Categories: `breathing`, `meditation`, `physical`, `journaling`, `grounding`, `social`, `creative`

#### GET `/api/wellness/activities`
Get all available wellness activities.

### User Profile Endpoints

#### POST `/api/user/profile`
Update user profile and preferences.

#### GET `/api/user/profile/{user_id}`
Get user profile and statistics.

### WebSocket

#### WS `/ws/chat/{user_id}`
Real-time chat via WebSocket.

**Send:**
```json
{
  "message": "I need someone to talk to"
}
```

**Receive:**
```json
{
  "response": "im here for u. whats going on?",
  "mood_detected": null,
  "crisis_detected": false,
  "suggestions": null
}
```

## Example Frontend Integration

### JavaScript/React Example

```javascript
// Send a chat message
async function sendMessage(userId, message) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message: message
    })
  });
  
  const data = await response.json();
  console.log('Bot response:', data.response);
  
  if (data.crisis_detected) {
    alert('Crisis detected - showing resources');
  }
  
  return data;
}

// Log a mood
async function logMood(userId, mood, intensity) {
  const response = await fetch('http://localhost:8000/api/mood/log', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      mood: mood,
      intensity: intensity
    })
  });
  
  return await response.json();
}

// Get recommendations
async function getRecommendations(userId, category) {
  const response = await fetch('http://localhost:8000/api/wellness/recommendations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      category: category
    })
  });
  
  return await response.json();
}
```

### WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/user123');

ws.onopen = () => {
  console.log('Connected to chat');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Bot:', data.response);
};

// Send message
ws.send(JSON.stringify({
  message: "I'm feeling stressed"
}));
```

## File Structure

```
mental-health-chatbot/
├── main.py                 # FastAPI server and endpoints
├── chatbot_engine.py       # AI chat logic and response generation
├── database.py             # Database operations
├── mood_tracker.py         # Mood logging and insights
├── wellness.py             # Wellness recommendations
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # This file
└── mental_health.db       # SQLite database (auto-created)
```

## Configuration

Edit `config.py` to customize:

- OpenAI model and settings
- Server host/port
- CORS origins
- Crisis resources
- Feature flags

## Crisis Support Resources

The bot includes crisis detection and will provide appropriate resources:

- **988 Suicide & Crisis Lifeline**: Call or text 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911

## Privacy & Security

- All data is stored locally in SQLite
- No data is sent to third parties (except OpenAI for AI responses)
- User IDs should be anonymized/hashed in production
- Add authentication for production use
- Use HTTPS in production

## Development

### Running in Development Mode

```bash
# With auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

### Testing Endpoints

Use the interactive docs at `http://localhost:8000/docs` or tools like:
- Postman
- curl
- Thunder Client (VS Code extension)

### Example curl Commands

```bash
# Send a chat message
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "message": "I feel anxious"}'

# Log a mood
curl -X POST "http://localhost:8000/api/mood/log" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "mood": "anxious", "intensity": 7}'

# Get recommendations
curl -X POST "http://localhost:8000/api/wellness/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "category": "breathing"}'
```

## Customization

### Adjust Bot Personality

Edit `SYSTEM_PROMPT` in `chatbot_engine.py` to change the bot's personality, tone, and communication style.

### Add Custom Wellness Activities

Edit activity lists in `wellness.py` to add your own recommendations.

### Modify Crisis Detection

Update `CRISIS_KEYWORDS` in `chatbot_engine.py` to adjust crisis detection sensitivity.

## Production Deployment

For production use:

1. Set `DEBUG_MODE = False` in `config.py`
2. Use a production-grade database (PostgreSQL)
3. Add authentication/authorization
4. Use HTTPS
5. Set specific CORS origins
6. Add rate limiting
7. Implement proper logging
8. Add monitoring and error tracking
9. Use environment-specific configs

## Contributing

This is a starting template. Feel free to extend it with:
- User authentication
- Multiple language support
- Voice chat integration
- Mobile app backend
- Professional therapist matching
- Group support features
- Progress tracking dashboards

## License

This is a template for educational and development purposes. Ensure you comply with healthcare regulations (HIPAA, etc.) if deploying for real users.

## Disclaimer

⚠️ **Important**: This chatbot is for emotional support and information only. It is NOT a substitute for professional mental health care. If you're in crisis or experiencing severe symptoms, please contact a mental health professional or emergency services immediately.

## Support

For questions or issues, please refer to the documentation or create an issue in your repository.

---

**Remember**: Mental health is important. This tool aims to provide accessible support, but professional help should always be sought when needed. 💙