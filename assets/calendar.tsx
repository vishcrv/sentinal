import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { MoodEntry, MoodLevel } from "@/types/mood";
import { Button } from "@/components/ui/button";

interface MoodCalendarProps {
  entries: MoodEntry[];
  onDateSelect: (date: string) => void;
  selectedDate?: string;
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const moodBgColors: Record<MoodLevel, string> = {
  low: 'bg-mood-low/40',
  neutral: 'bg-mood-neutral/40',
  positive: 'bg-mood-positive/40',
};

const moodBorderColors: Record<MoodLevel, string> = {
  low: 'border-mood-low/60',
  neutral: 'border-mood-neutral/60',
  positive: 'border-mood-positive/60',
};

export function MoodCalendar({ entries, onDateSelect, selectedDate }: MoodCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month');

  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];

  const getEntryForDate = (dateStr: string): MoodEntry | undefined => {
    return entries.find(e => e.date === dateStr);
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days: (Date | null)[] = [];
    
    // Add empty cells for days before the first of the month
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }

    return days;
  };

  const getWeekDays = (date: Date) => {
    const days: Date[] = [];
    const start = new Date(date);
    start.setDate(start.getDate() - start.getDay());
    
    for (let i = 0; i < 7; i++) {
      const day = new Date(start);
      day.setDate(start.getDate() + i);
      days.push(day);
    }
    
    return days;
  };

  const navigate = (direction: number) => {
    const newDate = new Date(currentDate);
    if (viewMode === 'month') {
      newDate.setMonth(newDate.getMonth() + direction);
    } else {
      newDate.setDate(newDate.getDate() + (direction * 7));
    }
    setCurrentDate(newDate);
  };

  const days = viewMode === 'month' ? getDaysInMonth(currentDate) : getWeekDays(currentDate);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="h-8 w-8 rounded-full"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <h2 className="text-lg font-semibold">
            {MONTHS[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(1)}
            className="h-8 w-8 rounded-full"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* View Toggle */}
        <div className="flex gap-1 p-1 bg-secondary rounded-lg">
          <button
            onClick={() => setViewMode('month')}
            className={cn(
              "px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-300",
              viewMode === 'month' 
                ? "bg-card text-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Month
          </button>
          <button
            onClick={() => setViewMode('week')}
            className={cn(
              "px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-300",
              viewMode === 'week' 
                ? "bg-card text-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Week
          </button>
        </div>
      </div>

      {/* Day Labels */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {DAYS.map(day => (
          <div key={day} className="text-center text-xs text-muted-foreground font-medium py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${currentDate.getMonth()}-${currentDate.getFullYear()}-${viewMode}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className={cn(
            "grid grid-cols-7 gap-1",
            viewMode === 'week' && "gap-2"
          )}
        >
          {days.map((day, index) => {
            if (!day) {
              return <div key={`empty-${index}`} className="aspect-square" />;
            }

            const dateStr = day.toISOString().split('T')[0];
            const entry = getEntryForDate(dateStr);
            const isToday = dateStr === todayStr;
            const isSelected = dateStr === selectedDate;
            const isPast = day < today && !isToday;
            const isFuture = day > today;

            return (
              <motion.button
                key={dateStr}
                onClick={() => !isFuture && onDateSelect(dateStr)}
                disabled={isFuture}
                whileHover={!isFuture ? { scale: 1.05 } : undefined}
                whileTap={!isFuture ? { scale: 0.95 } : undefined}
                className={cn(
                  "relative aspect-square rounded-xl flex flex-col items-center justify-center transition-all duration-300",
                  viewMode === 'week' && "rounded-2xl py-4",
                  entry && moodBgColors[entry.moodLevel],
                  entry && entry.volatility > 0.6 && "ring-2 ring-inset ring-primary/30",
                  isToday && !entry && "border-2 border-primary/50",
                  isSelected && "ring-2 ring-primary",
                  isFuture && "opacity-30 cursor-not-allowed",
                  !entry && !isToday && isPast && "bg-secondary/30",
                  !entry && !isToday && !isPast && !isFuture && "hover:bg-secondary/50"
                )}
              >
                <span className={cn(
                  "text-sm font-medium",
                  isToday && "text-primary",
                  entry && "text-foreground"
                )}>
                  {day.getDate()}
                </span>
                
                {/* High volatility indicator */}
                {entry && entry.volatility > 0.6 && (
                  <motion.div
                    className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-primary"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                )}
              </motion.button>
            );
          })}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
