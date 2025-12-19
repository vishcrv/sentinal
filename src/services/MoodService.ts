/**
 * Mood Tracking Service
 */
import api from './api';

export interface MoodEntry {
  user_id: string;
  mood: string;
  intensity: number;
  notes?: string;
  triggers?: string[];
}

export interface MoodResponse {
  success: boolean;
  entry_id: string;
  insights?: any;
}

export interface MoodHistory {
  user_id: string;
  history: Array<{
    id: string;
    mood: string;
    intensity: number;
    timestamp: string;
    notes?: string;
  }>;
  insights: any;
}

export interface MoodInsights {
  most_common_mood?: { mood: string; count: number };
  average_intensity?: number;
  trends?: any;
  patterns?: any;
}

export interface MoodTransition {
  from_mood: string;
  to_mood: string;
  timestamp: string;
  intensity_change: number;
}

export interface CurrentMood {
  user_id: string;
  current_mood?: string;
  current_intensity?: number;
  average_intensity?: number;
  mood_distribution?: Record<string, number>;
  recent_transitions?: MoodTransition[];
  session_transitions_count?: number;
}

class MoodService {
  /**
   * Log a mood entry
   */
  async logMood(entry: MoodEntry): Promise<MoodResponse> {
    const response = await api.post<MoodResponse>('/api/mood/log', entry);
    return response.data;
  }

  /**
   * Get mood history
   */
  async getHistory(userId: string, days: number = 30): Promise<MoodHistory> {
    const response = await api.get<MoodHistory>(`/api/mood/history/${userId}`, {
      params: { days },
    });
    return response.data;
  }

  /**
   * Get mood insights
   */
  async getInsights(userId: string): Promise<MoodInsights> {
    const response = await api.get<MoodInsights>(`/api/mood/insights/${userId}`);
    return response.data;
  }

  /**
   * Get active mood (recent timeline)
   */
  async getActiveMood(userId: string, limit: number = 20): Promise<any> {
    const response = await api.get(`/api/mood/active/${userId}`, {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Get mood transitions
   */
  async getTransitions(userId: string, limit: number = 50): Promise<{
    user_id: string;
    transitions: MoodTransition[];
    total: number;
  }> {
    const response = await api.get(`/api/mood/transitions/${userId}`, {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Get current mood bar data
   */
  async getCurrentMood(userId: string): Promise<CurrentMood> {
    const response = await api.get<CurrentMood>(`/api/mood/current/${userId}`);
    return response.data;
  }

  /**
   * Get session mood summary
   */
  async getSessionMood(userId: string, minutes: number = 60): Promise<any> {
    const response = await api.get(`/api/mood/session/${userId}`, {
      params: { minutes },
    });
    return response.data;
  }
}

export default new MoodService();

