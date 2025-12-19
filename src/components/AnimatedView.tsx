/**
 * Web-safe animated view wrapper
 * Uses MotiView on native, regular View on web
 */
import React from 'react';
import { View, Platform, ViewStyle } from 'react-native';

// Only import MotiView on native platforms
let MotiView: any = null;
if (Platform.OS !== 'web') {
  try {
    MotiView = require('moti').MotiView;
  } catch (e) {
    console.warn('MotiView not available:', e);
  }
}

interface AnimatedViewProps {
  children: React.ReactNode;
  from?: any;
  animate?: any;
  transition?: any;
  style?: ViewStyle | ViewStyle[];
  [key: string]: any;
}

export const AnimatedView: React.FC<AnimatedViewProps> = ({
  children,
  from,
  animate,
  transition,
  style,
  ...props
}) => {
  // On web, use regular View (no animations)
  if (Platform.OS === 'web' || !MotiView) {
    return (
      <View style={style} {...props}>
        {children}
      </View>
    );
  }

  // On native, use MotiView
  return (
    <MotiView
      from={from}
      animate={animate}
      transition={transition}
      style={style}
      {...props}
    >
      {children}
    </MotiView>
  );
};

