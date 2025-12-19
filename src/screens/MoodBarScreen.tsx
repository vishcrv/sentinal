/**
 * Mood Bar Screen - Full screen mood visualization
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useUser } from '../context/UserContext';
import MoodService from '../services/MoodService';
import { MoodBar } from '../components/MoodBar';
import { GlassCard } from '../components/GlassCard';
import { colors } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';

const MoodBarScreen: React.FC = () => {
  const { userId } = useUser();
  const [currentMood, setCurrentMood] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMoodData();
    const interval = setInterval(loadMoodData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [userId]);

  const loadMoodData = async () => {
    try {
      const data = await MoodService.getCurrentMood(userId);
      setCurrentMood(data);
    } catch (error) {
      console.error('Failed to load mood data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading mood data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.moodBarContainer}>
        <MoodBar
          currentMood={currentMood?.current_mood}
          intensity={currentMood?.current_intensity || currentMood?.average_intensity || 50}
        />
      </View>

      <View style={styles.infoContainer}>
        <GlassCard style={styles.infoCard}>
          <Text style={styles.moodLabel}>Current Mood</Text>
          <Text style={styles.moodValue}>
            {currentMood?.current_mood || 'Neutral'}
          </Text>
          <Text style={styles.intensityLabel}>Intensity</Text>
          <Text style={styles.intensityValue}>
            {currentMood?.current_intensity || currentMood?.average_intensity || '—'}%
          </Text>
        </GlassCard>

        {currentMood?.recent_transitions && currentMood.recent_transitions.length > 0 && (
          <GlassCard style={styles.infoCard}>
            <Text style={styles.transitionsTitle}>Recent Changes</Text>
            {currentMood.recent_transitions.slice(0, 3).map((transition: any, index: number) => (
              <View key={index} style={styles.transitionItem}>
                <Text style={styles.transitionText}>
                  {transition.from_mood} → {transition.to_mood}
                </Text>
              </View>
            ))}
          </GlassCard>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  loadingText: {
    color: colors.textSecondary,
    fontSize: 16,
  },
  moodBarContainer: {
    marginBottom: 40,
  },
  infoContainer: {
    width: '100%',
    maxWidth: 400,
  },
  infoCard: {
    marginBottom: 20,
    padding: 24,
    alignItems: 'center',
  },
  moodLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  moodValue: {
    fontSize: 32,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 20,
    textTransform: 'capitalize',
  },
  intensityLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  intensityValue: {
    fontSize: 24,
    fontWeight: '300',
    color: colors.text,
  },
  transitionsTitle: {
    fontSize: 16,
    color: colors.text,
    marginBottom: 12,
  },
  transitionItem: {
    padding: 8,
    marginBottom: 8,
  },
  transitionText: {
    fontSize: 14,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
});

export default MoodBarScreen;

