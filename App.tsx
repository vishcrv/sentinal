/**
 * Main App Entry Point
 */
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { UserProvider } from './src/context/UserContext';
import { AppNavigator } from './src/navigation/AppNavigator';
import { ErrorBoundary } from './src/components/ErrorBoundary';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from './src/theme/colors';

export default function App() {
  // Add basic error catching
  try {
    return (
      <ErrorBoundary>
        <GestureHandlerRootView style={{ flex: 1 }}>
          <SafeAreaProvider>
            <UserProvider>
              <StatusBar style="light" />
              <AppNavigator />
            </UserProvider>
          </SafeAreaProvider>
        </GestureHandlerRootView>
      </ErrorBoundary>
    );
  } catch (error) {
    console.error('App initialization error:', error);
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>App failed to load</Text>
        <Text style={styles.errorDetail}>{String(error)}</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: colors.crisis,
    fontSize: 18,
    marginBottom: 10,
  },
  errorDetail: {
    color: colors.textSecondary,
    fontSize: 12,
  },
});

