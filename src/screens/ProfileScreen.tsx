/**
 * Profile Screen - User stats and information
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { useUser } from '../context/UserContext';
import UserService from '../services/UserService';
import { GlassCard } from '../components/GlassCard';
import { colors } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';

const ProfileScreen: React.FC = () => {
  const { userId, userName } = useUser();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    try {
      const data = await UserService.getProfile(userId);
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <AnimatedView
        from={{ opacity: 0, translateY: -20 }}
        animate={{ opacity: 1, translateY: 0 }}
      >
        <GlassCard style={styles.headerCard}>
          <Text style={styles.greeting}>
            {userName ? `hi, ${userName.toLowerCase()}` : 'hi there'}
          </Text>
          <Text style={styles.subtitle}>Your journey so far</Text>
        </GlassCard>
      </AnimatedView>

      {/* Stats */}
      {profile?.stats && (
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 200 }}
        >
          <GlassCard style={styles.card}>
            <Text style={styles.sectionTitle}>Statistics</Text>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.stats.total_messages || 0}</Text>
                <Text style={styles.statLabel}>Chats</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.stats.mood_entries || 0}</Text>
                <Text style={styles.statLabel}>Mood Entries</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{profile.stats.days_active || 0}</Text>
                <Text style={styles.statLabel}>Days Active</Text>
              </View>
            </View>
          </GlassCard>
        </AnimatedView>
      )}

      {/* Reflection */}
      <AnimatedView
        from={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 400 }}
      >
        <GlassCard style={styles.card}>
          <Text style={styles.sectionTitle}>Reflection</Text>
          <Text style={styles.reflectionText}>
            Every entry you make, every conversation you have, is a step forward.
            Your feelings are valid, and tracking them helps you understand yourself better.
          </Text>
          <Text style={styles.reflectionText}>
            Keep going. You're doing great.
          </Text>
        </GlassCard>
      </AnimatedView>
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
  headerCard: {
    marginBottom: 20,
    padding: 24,
  },
  greeting: {
    fontSize: 36,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  card: {
    marginBottom: 20,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 20,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 40,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  reflectionText: {
    fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 24,
    marginBottom: 12,
  },
});

export default ProfileScreen;

