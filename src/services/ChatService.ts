/**
 * Chat Service - REST API and WebSocket
 */
import api from './api';
import { API_BASE_URL, WS_BASE_URL } from '../config/api';

export interface ChatRequest {
  user_id: string;
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  mood_detected?: string;
  mood_intensity?: number;
  crisis_detected: boolean;
  suggestions?: string[];
}

export interface ChatHistory {
  user_id: string;
  history: Array<{
    role: 'user' | 'assistant';
    text: string;
    timestamp: string;
  }>;
  total_messages: number;
}

class ChatService {
  /**
   * Send chat message via REST API
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/api/chat', request);
    return response.data;
  }

  /**
   * Get chat history
   */
  async getHistory(userId: string, limit: number = 50): Promise<ChatHistory> {
    const response = await api.get<ChatHistory>(`/api/chat/history/${userId}`, {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Clear chat history
   */
  async clearHistory(userId: string): Promise<void> {
    await api.delete(`/api/chat/history/${userId}`);
  }

  /**
   * Create WebSocket connection for real-time chat
   */
  createWebSocket(userId: string): WebSocket {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/chat/${userId}`);
    return ws;
  }
}

export default new ChatService();

