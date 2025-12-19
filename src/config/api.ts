/**
 * API Configuration
 */
const isDev = process.env.NODE_ENV === 'development' || __DEV__;

export const API_BASE_URL = isDev
  ? 'http://localhost:8000' 
  : 'https://your-production-api.com';

export const WS_BASE_URL = isDev
  ? 'ws://localhost:8000'
  : 'wss://your-production-api.com';

