/**
 * Glassmorphic Card Component
 */
import React from 'react';
import { View, StyleSheet, ViewStyle, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { colors } from '../theme/colors';

interface GlassCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  intensity?: number;
}

export const GlassCard: React.FC<GlassCardProps> = ({ 
  children, 
  style, 
  intensity = 20 
}) => {
  // BlurView doesn't work on web, use fallback
  if (Platform.OS === 'web') {
    return (
      <View style={[styles.container, styles.webFallback, style]}>
        {children}
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      <BlurView intensity={intensity} style={styles.blur} tint="dark">
        {children}
      </BlurView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 24,
    overflow: 'hidden',
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.border,
  },
  webFallback: {
    backgroundColor: colors.glass,
    opacity: 0.9,
  },
  blur: {
    flex: 1,
  },
});

