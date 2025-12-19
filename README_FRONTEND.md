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

