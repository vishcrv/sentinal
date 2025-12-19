/**
 * Color System - Mood-driven dark theme
 */

// Base Colors
export const colors = {
  background: '#0a0a0a',
  backgroundSecondary: '#141414',
  glass: 'rgba(30, 30, 30, 0.6)',
  glassLight: 'rgba(40, 40, 40, 0.4)',
  text: '#e8e8e8',
  textSecondary: '#b0b0b0',
  border: 'rgba(255, 255, 255, 0.1)',
  
  // Mood Colors (low saturation, calming)
  moodRed: {
    light: '#8b4d5a',
    base: '#6b2d3a',
    dark: '#4a1d2a',
  },
  moodAmber: {
    light: '#9a7a5a',
    base: '#7a5a3a',
    dark: '#5a3a2a',
  },
  moodGreen: {
    light: '#5a8b7a',
    base: '#3a6b5a',
    dark: '#2a4a3a',
  },
  
  // Status
  crisis: '#8b2d2d',
  success: '#3a6b5a',
  warning: '#8b6b2d',
};

/**
 * Get mood color based on mood string
 */
export const getMoodColor = (mood?: string): string => {
  if (!mood) return colors.moodAmber.base;
  
  const moodLower = mood.toLowerCase();
  
  if (moodLower.includes('sad') || moodLower.includes('depressed') || moodLower.includes('low')) {
    return colors.moodRed.base;
  }
  if (moodLower.includes('happy') || moodLower.includes('good') || moodLower.includes('calm') || moodLower.includes('stable')) {
    return colors.moodGreen.base;
  }
  if (moodLower.includes('anxious') || moodLower.includes('stressed') || moodLower.includes('worried')) {
    return colors.moodAmber.base;
  }
  
  return colors.moodAmber.base;
};

/**
 * Get mood gradient colors
 */
export const getMoodGradient = (mood?: string): [string, string] => {
  if (!mood) return [colors.moodAmber.dark, colors.moodAmber.light];
  
  const moodLower = mood.toLowerCase();
  
  if (moodLower.includes('sad') || moodLower.includes('depressed') || moodLower.includes('low')) {
    return [colors.moodRed.dark, colors.moodRed.light];
  }
  if (moodLower.includes('happy') || moodLower.includes('good') || moodLower.includes('calm') || moodLower.includes('stable')) {
    return [colors.moodGreen.dark, colors.moodGreen.light];
  }
  
  return [colors.moodAmber.dark, colors.moodAmber.light];
};

