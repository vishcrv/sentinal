/**
 * Wellness Recommendations Service
 */
import api from './api';

export interface WellnessRecommendation {
  category: string;
  title: string;
  description: string;
  duration?: string;
  difficulty?: string;
}

class WellnessService {
  /**
   * Get wellness recommendations
   */
  async getRecommendations(
    userId: string,
    category?: string
  ): Promise<{ user_id: string; recommendations: WellnessRecommendation[] }> {
    const response = await api.post('/api/wellness/recommendations', {
      user_id: userId,
      category,
    });
    return response.data;
  }

  /**
   * Get all available wellness activities
   */
  async getActivities(): Promise<{ activities: any[] }> {
    const response = await api.get('/api/wellness/activities');
    return response.data;
  }
}

export default new WellnessService();

