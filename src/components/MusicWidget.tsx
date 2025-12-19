/**
 * Persistent Music Widget
 */
import React, { useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { GlassCard } from './GlassCard';
import { colors } from '../theme/colors';

interface MusicWidgetProps {
  track?: {
    name: string;
    artist: string;
  };
  onPlay: () => void;
  onPause: () => void;
  onSkip: () => void;
}

export const MusicWidget: React.FC<MusicWidgetProps> = ({
  track,
  onPlay,
  onPause,
  onSkip,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  const handleToggle = () => {
    setIsPlaying(!isPlaying);
    if (isPlaying) {
      onPause();
    } else {
      onPlay();
    }
  };

  if (!track) return null;

  return (
    <View style={styles.container}>
      <GlassCard style={styles.card}>
        <View style={styles.content}>
          <View style={styles.info}>
            <Text style={styles.trackName} numberOfLines={1}>
              {track.name}
            </Text>
            <Text style={styles.artistName} numberOfLines={1}>
              {track.artist}
            </Text>
          </View>
          
          <View style={styles.controls}>
            <TouchableOpacity onPress={handleToggle} style={styles.button}>
              <Text style={styles.buttonText}>{isPlaying ? '⏸' : '▶'}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={onSkip} style={styles.button}>
              <Text style={styles.buttonText}>⏭</Text>
            </TouchableOpacity>
          </View>
        </View>
      </GlassCard>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 100,
    right: 16,
    width: 200,
    zIndex: 1000,
  },
  card: {
    padding: 12,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  info: {
    flex: 1,
    marginRight: 8,
  },
  trackName: {
    color: colors.text,
    fontSize: 12,
    fontWeight: '500',
  },
  artistName: {
    color: colors.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  controls: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.glassLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: colors.text,
    fontSize: 14,
  },
});

