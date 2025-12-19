/**
 * Settings Screen
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  TextInput,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import UserService from '../services/UserService';
import { GlassCard } from '../components/GlassCard';
import { colors } from '../theme/colors';

const SettingsScreen: React.FC = () => {
  const { userId, userName, setUserName } = useUser();
  const navigation = useNavigation();
  const [spotifyConnected, setSpotifyConnected] = useState(false);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [nameInput, setNameInput] = useState(userName);

  const handleSaveName = async () => {
    try {
      await UserService.updateProfile(userId, { name: nameInput });
      setUserName(nameInput);
      Alert.alert('Saved', 'Profile updated successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile');
    }
  };

  const handleConnectSpotify = () => {
    // TODO: Implement Spotify OAuth
    Alert.alert('Spotify', 'OAuth integration coming soon');
    setSpotifyConnected(true);
  };

  const handleConnectCalendar = () => {
    // TODO: Implement Google Calendar OAuth
    Alert.alert('Calendar', 'OAuth integration coming soon');
    setCalendarConnected(true);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Profile Section */}
      <GlassCard style={styles.card}>
        <Text style={styles.sectionTitle}>Profile</Text>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Name</Text>
          <TextInput
            style={styles.input}
            value={nameInput}
            onChangeText={setNameInput}
            placeholder="Your name"
            placeholderTextColor={colors.textSecondary}
          />
          <TouchableOpacity
            style={styles.saveButton}
            onPress={handleSaveName}
          >
            <Text style={styles.saveButtonText}>Save</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity
          style={styles.profileButton}
          onPress={() => navigation.navigate('Profile' as never)}
        >
          <Text style={styles.profileButtonText}>View Full Profile</Text>
        </TouchableOpacity>
      </GlassCard>

      {/* Integrations */}
      <GlassCard style={styles.card}>
        <Text style={styles.sectionTitle}>Integrations</Text>
        
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Spotify</Text>
            <Text style={styles.settingDescription}>
              Music recommendations based on mood
            </Text>
          </View>
          <TouchableOpacity
            style={[
              styles.connectButton,
              spotifyConnected && styles.connectButtonConnected,
            ]}
            onPress={handleConnectSpotify}
          >
            <Text style={styles.connectButtonText}>
              {spotifyConnected ? 'Connected' : 'Connect'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Google Calendar</Text>
            <Text style={styles.settingDescription}>
              Sync wellness activities
            </Text>
          </View>
          <TouchableOpacity
            style={[
              styles.connectButton,
              calendarConnected && styles.connectButtonConnected,
            ]}
            onPress={handleConnectCalendar}
          >
            <Text style={styles.connectButtonText}>
              {calendarConnected ? 'Connected' : 'Connect'}
            </Text>
          </TouchableOpacity>
        </View>
      </GlassCard>

      {/* Privacy & Safety */}
      <GlassCard style={styles.card}>
        <Text style={styles.sectionTitle}>Privacy & Safety</Text>
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            This app is not a substitute for professional mental health care.
            If you're experiencing a crisis, please contact:
          </Text>
          <Text style={styles.crisisNumber}>
            National Suicide Prevention Lifeline:{'\n'}
            988
          </Text>
          <Text style={styles.disclaimerText}>
            All your data is stored locally and encrypted. We respect your privacy.
          </Text>
        </View>
      </GlassCard>

      {/* App Info */}
      <GlassCard style={styles.card}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.aboutText}>Sentinal v1.0.0</Text>
        <Text style={styles.aboutText}>
          Emotional support chatbot with mood tracking
        </Text>
      </GlassCard>
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
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  input: {
    backgroundColor: colors.glass,
    borderRadius: 12,
    padding: 12,
    color: colors.text,
    fontSize: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  saveButton: {
    backgroundColor: colors.moodGreen.base,
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
  profileButton: {
    padding: 12,
    alignItems: 'center',
  },
  profileButtonText: {
    color: colors.moodGreen.light,
    fontSize: 14,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    color: colors.text,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  connectButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.border,
  },
  connectButtonConnected: {
    backgroundColor: colors.moodGreen.base + '40',
    borderColor: colors.moodGreen.light,
  },
  connectButtonText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
  disclaimer: {
    gap: 12,
  },
  disclaimerText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  crisisNumber: {
    fontSize: 18,
    color: colors.crisis,
    fontWeight: '500',
    textAlign: 'center',
    marginVertical: 8,
  },
  aboutText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
});

export default SettingsScreen;

