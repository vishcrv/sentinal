# Sentinal Frontend Setup Guide

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Expo CLI: `npm install -g expo-cli`
- Python 3.8+ (for backend)
- Backend server running on port 8000

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Start the backend server** (in project root):
```bash
python main.py
```

3. **Start Expo development server:**
```bash
npm start
```

4. **Run on device/simulator:**
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on physical device

## Configuration

### API Endpoint
Edit `src/config/api.ts` to change the backend URL:
```typescript
export const API_BASE_URL = 'http://your-backend-url:8000';
export const WS_BASE_URL = 'ws://your-backend-url:8000';
```

### User ID
The app automatically generates a user ID on first launch and stores it in AsyncStorage. To reset:
- Clear app data, or
- Delete AsyncStorage entry manually

## Project Structure

```
├── App.tsx                 # Main entry point
├── src/
│   ├── components/         # Reusable UI components
│   ├── screens/           # Screen components
│   ├── services/          # API service layer
│   ├── context/           # React Context providers
│   ├── theme/             # Colors and styling
│   ├── navigation/        # Navigation setup
│   └── config/            # Configuration files
├── package.json
└── tsconfig.json
```

## Features Overview

### Navigation
- **Bottom Tabs**: Home, Chat, Analytics, Journal, Settings
- **Stack Navigation**: Profile, Mood Bar
- **Floating Action Button**: Quick chat access from any screen

### Key Screens

1. **Home Screen**
   - Personalized greeting
   - Mood calendar (color-coded by mood)
   - Weekly statistics
   - Quick access to chat

2. **Chat Screen**
   - Real-time WebSocket chat
   - Floating orb animation during AI responses
   - Mood detection display
   - Crisis detection alerts

3. **Journal Screen**
   - Mood selection (5 options)
   - Intensity slider
   - Optional notes
   - "Talk about this" button to start chat

4. **Analytics Screen**
   - Current mood summary
   - Mood distribution charts
   - Mood transitions timeline
   - AI-generated insights

5. **Settings Screen**
   - Profile management
   - OAuth integrations (Spotify, Calendar)
   - Privacy & safety information

6. **Profile Screen**
   - User statistics
   - Reflection section
   - Personal journey overview

## API Integration

All API calls are abstracted through service classes:

- **ChatService**: `/api/chat`, WebSocket `/ws/chat/{user_id}`
- **MoodService**: `/api/mood/*` endpoints
- **SpotifyService**: `/api/spotify/recommend`
- **WellnessService**: `/api/wellness/*`
- **UserService**: `/api/user/profile/*`

## UI Design Principles

- **Dark mode only** with glassmorphic cards
- **Mood-driven colors**: Red (low) → Amber (neutral) → Green (stable)
- **Smooth animations** using moti and react-native-reanimated
- **Minimal, calm aesthetic** with soft gradients
- **Emotionally sensitive** design language

## Development Tips

1. **Hot Reload**: Changes auto-reload in Expo
2. **Debugging**: Use React Native Debugger or Chrome DevTools
3. **WebSocket**: Auto-reconnects on connection loss
4. **Error Handling**: All API calls include try-catch blocks
5. **TypeScript**: Strict mode enabled for type safety

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in `src/config/api.ts`

### WebSocket Connection Fails
- Falls back to REST API automatically
- Check network connectivity
- Verify WS_BASE_URL configuration

### Build Errors
- Clear cache: `expo start -c`
- Delete node_modules and reinstall
- Check TypeScript errors: `npx tsc --noEmit`

## Next Steps

- [ ] Add voice input for journal entries
- [ ] Implement Spotify OAuth
- [ ] Add push notifications
- [ ] Create data export feature
- [ ] Add offline mode support

## Support

For issues or questions, check:
- Backend logs in terminal
- Expo DevTools console
- React Native Debugger network tab

