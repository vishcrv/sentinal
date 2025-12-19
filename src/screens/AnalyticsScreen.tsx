/**
 * Analytics Screen - Mood insights and patterns
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import MoodService from '../services/MoodService';
import { GlassCard } from '../components/GlassCard';
import { colors, getMoodColor } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

const AnalyticsScreen: React.FC = () => {
  const { userId } = useUser();
  const navigation = useNavigation();
  const [insights, setInsights] = useState<any>(null);
  const [transitions, setTransitions] = useState<any[]>([]);
  const [currentMood, setCurrentMood] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [userId]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [insightsData, transitionsData, currentMoodData] = await Promise.all([
        MoodService.getInsights(userId),
        MoodService.getTransitions(userId, 20),
        MoodService.getCurrentMood(userId),
      ]);
      
      setInsights(insightsData);
      setTransitions(transitionsData.transitions || []);
      setCurrentMood(currentMoodData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMoodDistribution = () => {
    if (!currentMood?.mood_distribution) return null;

    const distribution = currentMood.mood_distribution;
    const total = Object.values(distribution).reduce((sum: number, val: any) => sum + val, 0);
    const maxValue = Math.max(...Object.values(distribution) as number[]);

    return (
      <View style={styles.distributionContainer}>
        {Object.entries(distribution).map(([mood, count]: [string, any]) => {
          const percentage = (count / total) * 100;
          const barWidth = (count / maxValue) * 100;
          
          return (
            <View key={mood} style={styles.distributionItem}>
              <View style={styles.distributionLabelRow}>
                <Text style={styles.distributionLabel}>{mood}</Text>
                <Text style={styles.distributionValue}>{count}</Text>
              </View>
              <View style={styles.distributionBarContainer}>
                <LinearGradient
                  colors={[getMoodColor(mood), getMoodColor(mood) + '80']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={[styles.distributionBar, { width: `${barWidth}%` }]}
                />
              </View>
            </View>
          );
        })}
      </View>
    );
  };

  const renderTransitions = () => {
    if (transitions.length === 0) return null;

    return (
      <View style={styles.transitionsContainer}>
        <Text style={styles.sectionTitle}>Recent Transitions</Text>
        {transitions.slice(0, 10).map((transition, index) => (
          <AnimatedView
            key={index}
            from={{ opacity: 0, translateX: -20 }}
            animate={{ opacity: 1, translateX: 0 }}
            transition={{ delay: index * 50 }}
            style={styles.transitionItem}
          >
            <View style={styles.transitionMoods}>
              <View
                style={[
                  styles.transitionMood,
                  { backgroundColor: getMoodColor(transition.from_mood) + '40' },
                ]}
              >
                <Text style={styles.transitionMoodText}>{transition.from_mood}</Text>
              </View>
              <Text style={styles.transitionArrow}>→</Text>
              <View
                style={[
                  styles.transitionMood,
                  { backgroundColor: getMoodColor(transition.to_mood) + '40' },
                ]}
              >
                <Text style={styles.transitionMoodText}>{transition.to_mood}</Text>
              </View>
            </View>
            <Text style={styles.transitionTime}>
              {new Date(transition.timestamp).toLocaleDateString()}
            </Text>
          </AnimatedView>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading insights...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Current Mood Summary */}
      {currentMood && (
        <AnimatedView
          from={{ opacity: 0, translateY: 20 }}
          animate={{ opacity: 1, translateY: 0 }}
        >
          <GlassCard style={styles.card}>
            <Text style={styles.title}>Current Mood</Text>
            <View style={styles.currentMoodRow}>
              <View
                style={[
                  styles.currentMoodBadge,
                  { backgroundColor: getMoodColor(currentMood.current_mood) + '40' },
                ]}
              >
                <Text style={styles.currentMoodText}>
                  {currentMood.current_mood || 'Neutral'}
                </Text>
              </View>
              <View>
                <Text style={styles.intensityLabel}>Intensity</Text>
                <Text style={styles.intensityValue}>
                  {currentMood.current_intensity || currentMood.average_intensity || '—'}
                </Text>
              </View>
            </View>
          </GlassCard>
        </AnimatedView>
      )}

      {/* Mood Distribution */}
      {currentMood?.mood_distribution && (
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 200 }}
        >
          <GlassCard style={styles.card}>
            <Text style={styles.sectionTitle}>Mood Distribution</Text>
            {renderMoodDistribution()}
          </GlassCard>
        </AnimatedView>
      )}

      {/* Insights */}
      {insights && (
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 400 }}
        >
          <GlassCard style={styles.card}>
            <Text style={styles.sectionTitle}>Insights</Text>
            {insights.most_common_mood && (
              <View style={styles.insightItem}>
                <Text style={styles.insightLabel}>Most Common Mood</Text>
                <Text style={styles.insightValue}>
                  {insights.most_common_mood.mood} ({insights.most_common_mood.count} times)
                </Text>
              </View>
            )}
            {insights.average_intensity && (
              <View style={styles.insightItem}>
                <Text style={styles.insightLabel}>Average Intensity</Text>
                <Text style={styles.insightValue}>
                  {Math.round(insights.average_intensity)}%
                </Text>
              </View>
            )}
          </GlassCard>
        </AnimatedView>
      )}

      {/* Transitions */}
      {renderTransitions() && (
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 600 }}
        >
          <GlassCard style={styles.card}>
            {renderTransitions()}
          </GlassCard>
        </AnimatedView>
      )}

      {/* Action Button */}
      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => navigation.navigate('Chat' as never)}
      >
        <Text style={styles.actionButtonText}>Suggest Events</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 16,
    paddingBottom: 100,
  },
  loadingText: {
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 40,
  },
  card: {
    marginBottom: 20,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 16,
  },
  currentMoodRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  currentMoodBadge: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
  },
  currentMoodText: {
    fontSize: 18,
    color: colors.text,
    fontWeight: '500',
  },
  intensityLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  intensityValue: {
    fontSize: 24,
    color: colors.text,
    fontWeight: '300',
  },
  distributionContainer: {
    gap: 12,
  },
  distributionItem: {
    marginBottom: 12,
  },
  distributionLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  distributionLabel: {
    fontSize: 14,
    color: colors.text,
    textTransform: 'capitalize',
  },
  distributionValue: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  distributionBarContainer: {
    height: 8,
    backgroundColor: colors.glass,
    borderRadius: 4,
    overflow: 'hidden',
  },
  distributionBar: {
    height: '100%',
    borderRadius: 4,
  },
  transitionsContainer: {
    gap: 12,
  },
  transitionItem: {
    padding: 12,
    backgroundColor: colors.glass,
    borderRadius: 12,
    marginBottom: 8,
  },
  transitionMoods: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 4,
  },
  transitionMood: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  transitionMoodText: {
    fontSize: 12,
    color: colors.text,
    textTransform: 'capitalize',
  },
  transitionArrow: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  transitionTime: {
    fontSize: 11,
    color: colors.textSecondary,
  },
  insightItem: {
    marginBottom: 16,
  },
  insightLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  insightValue: {
    fontSize: 18,
    color: colors.text,
    fontWeight: '500',
  },
  actionButton: {
    backgroundColor: colors.moodGreen.base,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  actionButtonText: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '500',
  },
});

export default AnalyticsScreen;

