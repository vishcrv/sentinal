/**
 * Floating Orb Animation for Chatbot - Enhanced with slushy movement
 */
import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Text, Platform, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, getMoodGradient } from '../theme/colors';
import { AnimatedView } from './AnimatedView';

interface FloatingOrbProps {
  isActive: boolean;
  mood?: string;
  caption?: string;
  size?: number;
}

export const FloatingOrb: React.FC<FloatingOrbProps> = ({
  isActive,
  mood,
  caption,
  size = 80,
}) => {
  const gradient = getMoodGradient(mood);
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const translateXAnim = useRef(new Animated.Value(0)).current;
  const translateYAnim = useRef(new Animated.Value(0)).current;
  const rotationAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (isActive && Platform.OS !== 'web') {
      // Continuous slushy movement
      const createSlushyAnimation = () => {
        // Scale pulsing (breathing effect)
        Animated.loop(
          Animated.sequence([
            Animated.timing(scaleAnim, {
              toValue: 1.15,
              duration: 2000,
              useNativeDriver: true,
            }),
            Animated.timing(scaleAnim, {
              toValue: 1,
              duration: 2000,
              useNativeDriver: true,
            }),
          ])
        ).start();

        // Horizontal drift (slushy movement)
        Animated.loop(
          Animated.sequence([
            Animated.timing(translateXAnim, {
              toValue: 8,
              duration: 3000,
              useNativeDriver: true,
            }),
            Animated.timing(translateXAnim, {
              toValue: -8,
              duration: 3000,
              useNativeDriver: true,
            }),
            Animated.timing(translateXAnim, {
              toValue: 0,
              duration: 2000,
              useNativeDriver: true,
            }),
          ])
        ).start();

        // Vertical float
        Animated.loop(
          Animated.sequence([
            Animated.timing(translateYAnim, {
              toValue: -6,
              duration: 2500,
              useNativeDriver: true,
            }),
            Animated.timing(translateYAnim, {
              toValue: 6,
              duration: 2500,
              useNativeDriver: true,
            }),
            Animated.timing(translateYAnim, {
              toValue: 0,
              duration: 1500,
              useNativeDriver: true,
            }),
          ])
        ).start();

        // Slow rotation
        Animated.loop(
          Animated.timing(rotationAnim, {
            toValue: 1,
            duration: 8000,
            useNativeDriver: true,
          })
        ).start();
      };

      createSlushyAnimation();
    } else {
      // Reset animations when not active
      scaleAnim.setValue(1);
      translateXAnim.setValue(0);
      translateYAnim.setValue(0);
      rotationAnim.setValue(0);
    }
  }, [isActive]);

  if (!isActive) return null;

  const spin = rotationAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  // Web-safe animation
  if (Platform.OS === 'web') {
    return (
      <View style={styles.container}>
        <View style={[styles.orb, { width: size, height: size, borderRadius: size / 2 }]}>
          <LinearGradient
            colors={gradient}
            style={[styles.gradient, { borderRadius: size / 2 }]}
          >
            <View style={styles.innerGlow} />
          </LinearGradient>
        </View>
        {caption && (
          <View style={styles.captionContainer}>
            <View style={styles.caption}>
              <Text style={styles.captionText}>{caption}</Text>
            </View>
          </View>
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.orb,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
            transform: [
              { scale: scaleAnim },
              { translateX: translateXAnim },
              { translateY: translateYAnim },
              { rotate: spin },
            ],
          },
        ]}
      >
        <LinearGradient
          colors={gradient}
          style={[styles.gradient, { borderRadius: size / 2 }]}
        >
          <View style={styles.innerGlow} />
        </LinearGradient>
      </Animated.View>
      
      {caption && (
        <AnimatedView
          from={{ opacity: 0, translateY: 10 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: 'timing', duration: 500 }}
          style={styles.captionContainer}
        >
          <View style={styles.caption}>
            <Text style={styles.captionText}>{caption}</Text>
          </View>
        </AnimatedView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  orb: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  gradient: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  innerGlow: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    borderRadius: 999,
  },
  captionContainer: {
    marginTop: 16,
    maxWidth: 200,
  },
  caption: {
    backgroundColor: colors.glass,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  captionText: {
    color: colors.textSecondary,
    fontSize: 12,
    textAlign: 'center',
  },
});
