/**
 * User Profile Service
 */
import api from './api';

export interface UserProfile {
  name?: string;
  preferences?: Record<string, any>;
}

export interface UserStats {
  total_messages: number;
  mood_entries: number;
  days_active: number;
}

export interface UserProfileResponse {
  user_id: string;
  profile: UserProfile;
  stats: UserStats;
}

class UserService {
  /**
   * Get user profile
   */
  async getProfile(userId: string): Promise<UserProfileResponse> {
    const response = await api.get<UserProfileResponse>(`/api/user/profile/${userId}`);
    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(
    userId: string,
    profile: UserProfile
  ): Promise<{ success: boolean; profile: UserProfile }> {
    const response = await api.post('/api/user/profile', {
      user_id: userId,
      ...profile,
    });
    return response.data;
  }
}

export default new UserService();

