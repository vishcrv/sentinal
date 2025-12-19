/**
 * Home Screen - Dashboard with Calendar
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useUser } from '../context/UserContext';
import MoodService from '../services/MoodService';
import { GlassCard } from '../components/GlassCard';
import { FloatingActionButton } from '../components/FloatingActionButton';
import { colors, getMoodColor } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';

const { width } = Dimensions.get('window');
const CALENDAR_ITEM_SIZE = (width - 64) / 7;

const HomeScreen: React.FC = () => {
  const { userId, userName } = useUser();
  const navigation = useNavigation();
  const [moodHistory, setMoodHistory] = useState<any[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  useEffect(() => {
    loadMoodHistory();
  }, [userId]);

  const loadMoodHistory = async () => {
    try {
      const history = await MoodService.getHistory(userId, 30);
      setMoodHistory(history.history || []);
    } catch (error) {
      console.error('Failed to load mood history:', error);
    }
  };

  const getMoodForDate = (date: Date): string | null => {
    const dateStr = date.toISOString().split('T')[0];
    const entry = moodHistory.find((e) => 
      e.timestamp?.startsWith(dateStr)
    );
    return entry?.mood || null;
  };

  const navigateMonth = (direction: number) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const renderCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    return (
      <View>
        {/* Calendar Header with Navigation */}
        <View style={styles.calendarHeaderRow}>
          <TouchableOpacity onPress={() => navigateMonth(-1)} style={styles.navButton}>
            <Text style={styles.navButtonText}>‹</Text>
          </TouchableOpacity>
          <Text style={styles.monthYearText}>
            {monthNames[month]} {year}
          </Text>
          <TouchableOpacity onPress={() => navigateMonth(1)} style={styles.navButton}>
            <Text style={styles.navButtonText}>›</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.calendarGrid}>
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <View key={day} style={styles.calendarHeader}>
              <Text style={styles.calendarHeaderText}>{day}</Text>
            </View>
          ))}
          {days.map((date, index) => {
            if (!date) {
              return <View key={`empty-${index}`} style={styles.calendarDay} />;
            }
            
            const mood = getMoodForDate(date);
            const isToday = date.toDateString() === new Date().toDateString();
            const isSelected = selectedDate?.toDateString() === date.toDateString();
            const isFuture = date > new Date();
            
            return (
              <TouchableOpacity
                key={date.toISOString()}
                style={styles.calendarDay}
                onPress={() => {
                  if (!isFuture) {
                    const dateStr = date.toISOString().split('T')[0];
                    navigation.navigate('DateDetail' as never, { date: dateStr } as never);
                  }
                }}
                disabled={isFuture}
              >
                <AnimatedView
                  animate={{
                    scale: isSelected ? 1.1 : 1,
                    opacity: mood ? 1 : isFuture ? 0.3 : 0.5,
                  }}
                  style={[
                    styles.calendarDate,
                    mood && { backgroundColor: getMoodColor(mood) + '40' },
                    isToday && styles.todayDate,
                    isSelected && styles.selectedDate,
                    isFuture && styles.futureDate,
                  ]}
                >
                  <Text style={[
                    styles.calendarDateText,
                    isFuture && styles.futureDateText,
                  ]}>
                    {date.getDate()}
                  </Text>
                </AnimatedView>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  const greeting = userName 
    ? `hi, ${userName.toLowerCase()}`
    : 'hi there';

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Greeting */}
        <AnimatedView
          from={{ opacity: 0, translateY: -20 }}
          animate={{ opacity: 1, translateY: 0 }}
          transition={{ type: 'timing', duration: 500 }}
        >
          <GlassCard style={styles.greetingCard}>
            <Text style={styles.greeting}>{greeting}</Text>
            <Text style={styles.subtitle}>How are you feeling today?</Text>
          </GlassCard>
        </AnimatedView>

        {/* Calendar */}
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ type: 'timing', duration: 500, delay: 200 }}
        >
          <GlassCard style={styles.calendarCard}>
            <Text style={styles.sectionTitle}>Mood Calendar</Text>
            {renderCalendar()}
          </GlassCard>
        </AnimatedView>

        {/* Quick Stats */}
        <AnimatedView
          from={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ type: 'timing', duration: 500, delay: 400 }}
        >
          <GlassCard style={styles.statsCard}>
            <Text style={styles.sectionTitle}>This Week</Text>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{moodHistory.length}</Text>
                <Text style={styles.statLabel}>Entries</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>
                  {moodHistory.length > 0 
                    ? Math.round(moodHistory.reduce((sum, e) => sum + (e.intensity || 0), 0) / moodHistory.length)
                    : '—'}
                </Text>
                <Text style={styles.statLabel}>Avg Intensity</Text>
              </View>
            </View>
          </GlassCard>
        </AnimatedView>
      </ScrollView>

      {/* Floating Action Button */}
      <FloatingActionButton
        onPress={() => navigation.navigate('Chat' as never)}
      />

    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 100,
  },
  greetingCard: {
    marginBottom: 20,
  },
  greeting: {
    fontSize: 32,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  calendarCard: {
    marginBottom: 20,
  },
  calendarHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  navButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.glass,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navButtonText: {
    fontSize: 24,
    color: colors.text,
    fontWeight: '300',
  },
  monthYearText: {
    fontSize: 18,
    fontWeight: '500',
    color: colors.text,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 16,
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  calendarHeader: {
    width: CALENDAR_ITEM_SIZE,
    height: 30,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  calendarHeaderText: {
    fontSize: 12,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  calendarDay: {
    width: CALENDAR_ITEM_SIZE,
    height: CALENDAR_ITEM_SIZE,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  calendarDate: {
    width: CALENDAR_ITEM_SIZE - 8,
    height: CALENDAR_ITEM_SIZE - 8,
    borderRadius: (CALENDAR_ITEM_SIZE - 8) / 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  todayDate: {
    borderWidth: 2,
    borderColor: colors.moodGreen.light,
  },
  selectedDate: {
    borderWidth: 2,
    borderColor: colors.text,
  },
  futureDate: {
    opacity: 0.3,
  },
  calendarDateText: {
    fontSize: 14,
    color: colors.text,
    fontWeight: '500',
  },
  futureDateText: {
    opacity: 0.5,
  },
  statsCard: {
    marginBottom: 20,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: '300',
    color: colors.text,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
});

export default HomeScreen;

