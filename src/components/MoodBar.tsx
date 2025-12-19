/**
 * Vertical Mood Bar Component
 */
import React from 'react';
import { View, StyleSheet, Text, Dimensions, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, getMoodGradient } from '../theme/colors';
import { AnimatedView } from './AnimatedView';

interface MoodBarProps {
  currentMood?: string;
  intensity?: number; // 0-100
  height?: number;
}

const { height: SCREEN_HEIGHT } = Dimensions.get('window');

export const MoodBar: React.FC<MoodBarProps> = ({ 
  currentMood, 
  intensity = 50,
  height = SCREEN_HEIGHT * 0.6 
}) => {
  const [redGradient, amberGradient, greenGradient] = [
    [colors.moodRed.dark, colors.moodRed.light],
    [colors.moodAmber.dark, colors.moodAmber.light],
    [colors.moodGreen.dark, colors.moodGreen.light],
  ];

  // Calculate position based on intensity (0 = bottom/red, 100 = top/green)
  const barPosition = (intensity / 100) * height;

  return (
    <View style={[styles.container, { height }]}>
      <LinearGradient
        colors={[...redGradient, ...amberGradient, ...greenGradient]}
        start={{ x: 0, y: 1 }}
        end={{ x: 0, y: 0 }}
        style={styles.gradient}
      >
        {/* Current mood indicator */}
        <AnimatedView
          from={{ translateY: 0 }}
          animate={{ translateY: height - barPosition - 10 }}
          transition={{ type: 'timing', duration: 800 }}
          style={[styles.indicator, Platform.OS === 'web' && { transform: [{ translateY: height - barPosition - 10 }] }]}
        >
          <View style={styles.indicatorDot} />
          <View style={styles.indicatorGlow} />
        </AnimatedView>
      </LinearGradient>
      
      {/* Segments */}
      <View style={styles.segments}>
        <View style={[styles.segment, styles.segmentLow]} />
        <View style={[styles.segment, styles.segmentMid]} />
        <View style={[styles.segment, styles.segmentHigh]} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: 60,
    borderRadius: 30,
    overflow: 'hidden',
    position: 'relative',
  },
  gradient: {
    flex: 1,
    width: '100%',
  },
  indicator: {
    position: 'absolute',
    width: '100%',
    alignItems: 'center',
  },
  indicatorDot: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.text,
    borderWidth: 2,
    borderColor: colors.background,
  },
  indicatorGlow: {
    position: 'absolute',
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    top: -5,
    left: -5,
  },
  segments: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    justifyContent: 'space-between',
    paddingVertical: 10,
  },
  segment: {
    width: '100%',
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  segmentLow: {
    marginTop: '33%',
  },
  segmentMid: {
    marginTop: '33%',
  },
  segmentHigh: {
    marginTop: '33%',
  },
});

