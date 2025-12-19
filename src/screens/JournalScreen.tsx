/**
 * Journal Screen - Mood logging and entry
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import MoodService from '../services/MoodService';
import { GlassCard } from '../components/GlassCard';
import { colors } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';

const MOOD_OPTIONS = [
  { label: 'Great', value: 'happy', intensity: 80 },
  { label: 'Good', value: 'calm', intensity: 60 },
  { label: 'Okay', value: 'neutral', intensity: 50 },
  { label: 'Low', value: 'sad', intensity: 30 },
  { label: 'Struggling', value: 'depressed', intensity: 20 },
];

const JournalScreen: React.FC = () => {
  const { userId } = useUser();
  const navigation = useNavigation();
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [intensity, setIntensity] = useState(50);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!selectedMood) {
      Alert.alert('Select a mood', 'Please select how you\'re feeling');
      return;
    }

    setIsSubmitting(true);

    try {
      await MoodService.logMood({
        user_id: userId,
        mood: selectedMood,
        intensity,
        notes: notes.trim() || undefined,
      });

      Alert.alert(
        'Entry saved',
        'Your mood has been logged.',
        [
          {
            text: 'Talk about this',
            onPress: () => {
              // Navigate to chat with journal context
              navigation.navigate('Chat' as never, { 
                journalContext: notes,
                mood: selectedMood,
              } as never);
            },
          },
          { text: 'OK', style: 'cancel' },
        ]
      );

      // Reset form
      setSelectedMood(null);
      setIntensity(50);
      setNotes('');
    } catch (error) {
      console.error('Failed to log mood:', error);
      Alert.alert('Error', 'Failed to save entry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <GlassCard style={styles.card}>
        <Text style={styles.title}>How are you feeling?</Text>
        <Text style={styles.subtitle}>Select your current mood</Text>

        {/* Mood Options */}
        <View style={styles.moodOptions}>
          {MOOD_OPTIONS.map((option) => (
            <TouchableOpacity
              key={option.value}
              onPress={() => {
                setSelectedMood(option.value);
                setIntensity(option.intensity);
              }}
              style={[
                styles.moodOption,
                selectedMood === option.value && styles.moodOptionSelected,
              ]}
            >
              <AnimatedView
                animate={{
                  scale: selectedMood === option.value ? 1.1 : 1,
                }}
              >
                <Text style={styles.moodLabel}>{option.label}</Text>
              </AnimatedView>
            </TouchableOpacity>
          ))}
        </View>

        {/* Intensity Slider */}
        {selectedMood && (
          <AnimatedView
            from={{ opacity: 0, translateY: 10 }}
            animate={{ opacity: 1, translateY: 0 }}
            style={styles.intensityContainer}
          >
            <Text style={styles.intensityLabel}>
              Intensity: {intensity}%
            </Text>
            <View style={styles.sliderContainer}>
              <View style={styles.sliderTrack}>
                <View
                  style={[
                    styles.sliderFill,
                    { width: `${intensity}%` },
                    intensity < 40 && { backgroundColor: colors.moodRed.base },
                    intensity >= 40 && intensity < 60 && { backgroundColor: colors.moodAmber.base },
                    intensity >= 60 && { backgroundColor: colors.moodGreen.base },
                  ]}
                />
              </View>
              <View style={styles.sliderButtons}>
                {[0, 25, 50, 75, 100].map((value) => (
                  <TouchableOpacity
                    key={value}
                    onPress={() => setIntensity(value)}
                    style={[
                      styles.sliderButton,
                      Math.abs(intensity - value) < 5 && styles.sliderButtonActive,
                    ]}
                  />
                ))}
              </View>
            </View>
          </AnimatedView>
        )}

        {/* Notes Input */}
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 200 }}
          style={styles.notesContainer}
        >
          <Text style={styles.notesLabel}>Notes (optional)</Text>
          <TextInput
            style={styles.notesInput}
            value={notes}
            onChangeText={setNotes}
            placeholder="What's on your mind?"
            placeholderTextColor={colors.textSecondary}
            multiline
            numberOfLines={4}
          />
        </AnimatedView>

        {/* Submit Button */}
        <TouchableOpacity
          onPress={handleSubmit}
          disabled={!selectedMood || isSubmitting}
          style={[
            styles.submitButton,
            (!selectedMood || isSubmitting) && styles.submitButtonDisabled,
          ]}
        >
          <Text style={styles.submitButtonText}>
            {isSubmitting ? 'Saving...' : 'Save Entry'}
          </Text>
        </TouchableOpacity>
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
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    marginBottom: 24,
  },
  moodOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 32,
  },
  moodOption: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    borderRadius: 16,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  moodOptionSelected: {
    borderColor: colors.moodGreen.light,
    backgroundColor: colors.moodGreen.base + '20',
  },
  moodLabel: {
    fontSize: 16,
    color: colors.text,
    fontWeight: '500',
  },
  intensityContainer: {
    marginBottom: 32,
  },
  intensityLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 12,
  },
  sliderContainer: {
    marginBottom: 8,
  },
  sliderTrack: {
    height: 8,
    backgroundColor: colors.glass,
    borderRadius: 4,
    overflow: 'hidden',
  },
  sliderFill: {
    height: '100%',
    borderRadius: 4,
  },
  sliderButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  sliderButton: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.textSecondary,
  },
  sliderButtonActive: {
    backgroundColor: colors.text,
    width: 16,
    height: 16,
    borderRadius: 8,
  },
  notesContainer: {
    marginBottom: 24,
  },
  notesLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  notesInput: {
    backgroundColor: colors.glass,
    borderRadius: 12,
    padding: 16,
    color: colors.text,
    fontSize: 15,
    minHeight: 100,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: colors.border,
  },
  submitButton: {
    backgroundColor: colors.moodGreen.base,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '500',
  },
});

export default JournalScreen;

