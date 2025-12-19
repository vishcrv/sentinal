/**
 * Spotify Integration Service
 */
import api from './api';

export interface SpotifyTrack {
  id: string;
  name: string;
  artist: string;
  album?: string;
  preview_url?: string;
  external_url: string;
  image_url?: string;
}

export interface SpotifyRecommendation {
  mood?: string;
  tracks: SpotifyTrack[];
}

class SpotifyService {
  /**
   * Get music recommendations based on mood or search
   */
  async recommend(
    userId: string,
    mode: 'auto' | 'search' = 'auto',
    query?: string
  ): Promise<SpotifyRecommendation> {
    const response = await api.post<SpotifyRecommendation>('/api/spotify/recommend', {
      user_id: userId,
      mode,
      query,
    });
    return response.data;
  }
}

export default new SpotifyService();

