# Sentinal Frontend

React Native frontend for the Sentinal mental health support chatbot.

## Tech Stack

- **React Native** with **Expo**
- **TypeScript**
- **React Navigation** (Bottom Tabs + Stack)
- **expo-blur** for glassmorphism
- **react-native-reanimated** & **moti** for animations
- **expo-linear-gradient** for gradients
- **axios** for API calls
- **WebSocket** for real-time chat

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint in `src/config/api.ts`:
```typescript
export const API_BASE_URL = 'http://localhost:8000';
export const WS_BASE_URL = 'ws://localhost:8000';
```

3. Start the backend server (from project root):
```bash
python main.py
```

4. Start Expo:
```bash
npm start
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── GlassCard.tsx
│   ├── FloatingOrb.tsx
│   ├── MoodBar.tsx
│   ├── MusicWidget.tsx
│   └── FloatingActionButton.tsx
├── screens/            # Screen components
│   ├── HomeScreen.tsx
│   ├── ChatScreen.tsx
│   ├── JournalScreen.tsx
│   ├── AnalyticsScreen.tsx
│   ├── SettingsScreen.tsx
│   ├── ProfileScreen.tsx
│   └── MoodBarScreen.tsx
├── services/           # API services
│   ├── api.ts
│   ├── ChatService.ts
│   ├── MoodService.ts
│   ├── SpotifyService.ts
│   ├── WellnessService.ts
│   └── UserService.ts
├── context/            # React Context
│   └── UserContext.tsx
├── theme/              # Theme & colors
│   └── colors.ts
├── navigation/         # Navigation setup
│   └── AppNavigator.tsx
└── config/             # Configuration
    └── api.ts
```

## Features

### Navigation
- 5 main tabs: Home, Chat, Analytics, Journal, Settings
- Floating action button for quick chat access
- Stack navigation for Profile and Mood Bar screens

### Screens

1. **Home**: Dashboard with mood calendar and quick stats
2. **Chat**: Real-time WebSocket chat with mood detection
3. **Journal**: Mood logging with notes
4. **Analytics**: Mood insights, transitions, and patterns
5. **Settings**: Profile, integrations, privacy
6. **Profile**: User statistics and reflection
7. **Mood Bar**: Full-screen mood visualization

### UI Design

- **Dark mode only** with glassmorphic cards
- **Mood-driven colors**: Red (low) → Amber (neutral) → Green (stable)
- **Smooth animations** with moti and reanimated
- **Floating orb** animation during AI responses
- **Persistent music widget** for Spotify integration

## API Integration

All API calls are handled through service classes:
- `ChatService`: REST and WebSocket chat
- `MoodService`: Mood tracking and analytics
- `SpotifyService`: Music recommendations
- `WellnessService`: Activity suggestions
- `UserService`: Profile management

## State Management

- **UserContext**: Global user ID and name
- **Local state**: Screen-specific state with React hooks
- **AsyncStorage**: Persistent user ID storage

## Development Notes

- Backend must be running on `http://localhost:8000`
- WebSocket connection auto-reconnects
- All API calls include error handling
- Placeholder data used when backend unavailable

## TODO

- [ ] Implement Spotify OAuth
- [ ] Implement Google Calendar OAuth
- [ ] Add voice input for journal entries
- [ ] Add push notifications
- [ ] Add offline mode support
- [ ] Add data export functionality


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
# Note: this repo uses `requirments.txt` (typo kept for compatibility).
pip install -r requirments.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
# Optional Spotify app credentials for recommendations (Client Credentials flow)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Reference (detailed)

This section documents each endpoint implemented in `main.py`. Use the interactive Swagger UI at `http://localhost:8000/docs` for live testing.

1) POST /api/chat
- Purpose: Primary chat endpoint. Send a user message and receive the bot reply plus mood/crisis signals.
- Request JSON:
  - `user_id` (string) — required
  - `message` (string) — required
  - `session_id` (string) — optional
- Response JSON (ChatResponse):
  - `response` (string)
  - `session_id` (string)
  - `mood_detected` (string|null)
  - `mood_intensity` (int|null)
  - `crisis_detected` (bool)
  - `suggestions` (array|null)

Example request:
```json
{ "user_id": "user123", "message": "I'm feeling anxious today" }
```

2) GET /api/chat/history/{user_id}
- Purpose: Return the user's recent chat history (default limit 50).
- Query param: `limit` (int, optional)
- Response:
```json
{ "user_id": "user123", "history": [ {"role":"user","text":"...","timestamp":"..."}, ... ], "total_messages": 12 }
```

3) DELETE /api/chat/history/{user_id}
- Purpose: Clear a user's chat history and current session moods.
- Response: `{ "success": true, "message": "Chat history cleared" }`

4) WebSocket /ws/chat/{user_id}
- Purpose: Real-time chat. Send JSON `{ "message": "..." }` and receive JSON:
  - `{ "response", "mood_detected", "mood_intensity", "crisis_detected", "suggestions" }`

5) POST /api/mood/log
- Purpose: Manually log a mood entry.
- Request JSON:
  - `user_id` (string)
  - `mood` (string)
  - `intensity` (int, 1-10)
  - `notes` (string, optional)
  - `triggers` (array[string], optional)
- Response JSON:
  - `{ success: true, entry_id: "<uuid>", insights: {...} }`

6) GET /api/mood/history/{user_id}
- Purpose: Return persisted mood entries (default last 30 days).
- Query param: `days` (int)
- Response: `{ user_id, history: [...], insights: {...} }`

7) GET /api/mood/insights/{user_id}
- Purpose: Compute mood insights (most common mood, average intensity, trend, time patterns).
- Response: insights JSON (see `mood_tracker.get_mood_insights`).

8) GET /api/mood/active/{user_id}
- Purpose: Active mood summary for live UI (mood bar): `average_intensity`, `distribution`, `timeline`.
- Query param: `limit` (int)
- Response example:
```json
{ "user_id":"user123","average_intensity":6.2,"distribution":{"anxious":3,"calm":2},"timeline":[ ... ] }
```

9) GET /api/mood/transitions/{user_id}
- Purpose: Return fine-grained mood transitions captured during conversations.
- Response: `{ user_id, transitions:[{id,mood,intensity,message,context,timestamp}], total }`

10) GET /api/mood/session/{user_id}
- Purpose: Session summary for the last N minutes (default 60). Returns transitions and session statistics.
- Query param: `minutes` (int)

11) GET /api/mood/current/{user_id}
- Purpose: Payload for active mood bar UI. Returns current mood, current intensity, average intensity, mood_distribution, recent_transitions, session_transitions_count.

12) POST /api/wellness/recommendations
- Purpose: Get wellness suggestions (breathing, journaling, physical activities).
- Request JSON: `{ user_id: string, category?: string }`
- Response: `{ user_id, recommendations: [...] }`

13) GET /api/wellness/activities
- Purpose: Return available wellness activities.

14) POST /api/user/profile
- Purpose: Create/update user profile and preferences.
- Request JSON: `{ user_id, name?:string, preferences?:{ communication_style?: 'supportive'|'casual'|'playful', ... } }`
- Response: `{ success: true, profile: {...} }`

15) GET /api/user/profile/{user_id}
- Purpose: Return user profile and lightweight stats: total messages, mood entries, days_active.

16) POST /api/spotify/recommend
- Purpose: Provide Spotify track recommendations. Two modes:
  - `mode=auto` (default) — recommend by most recent mood / mood insights.
  - `mode=search` — requires `query` field to search tracks.
- Request JSON: `{ user_id: string, mode?: 'auto'|'search', query?: string }`
- Response (auto): `{ mood: "<mood>", tracks: [ {id,name,artists,preview_url,external_url}, ... ] }`
- Response (search): `{ tracks: [...] }`

Notes:
- Crisis detection is surfaced as `crisis_detected: true` on chat responses when triggered.
- The chat engine uses an LLM with prompts tuned to produce a human, friend-like tone; the stored `profile.preferences.communication_style` may affect tone.


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
├── spotify_integration.py  # Spotify helper: app-token search & mood recommendations
├── database.py             # Database operations
├── mood_tracker.py         # Mood logging and insights
├── wellness.py             # Wellness recommendations
├── config.py               # Configuration settings
├── requirments.txt         # Python dependencies (note filename)
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

Add optional Spotify configuration in `.env` or environment:

- `SPOTIFY_CLIENT_ID` — Spotify application client id
- `SPOTIFY_CLIENT_SECRET` — Spotify application client secret

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

### Spotify recommendations

The backend exposes `/api/spotify/recommend`:

- `mode=auto` (default) — recommends tracks using the most recent detected mood for the user.
- `mode=search` — pass `query` to search tracks.

Example (auto):

```bash
curl -X POST "http://localhost:8000/api/spotify/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test123","mode":"auto"}'
```

Example (search):

```bash
curl -X POST "http://localhost:8000/api/spotify/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test123","mode":"search","query":"lofi chill"}'
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
