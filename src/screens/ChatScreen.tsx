/**
 * Chat Screen - Core chatbot interface
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useUser } from '../context/UserContext';
import { useRoute } from '@react-navigation/native';
import ChatService from '../services/ChatService';
import { GlassCard } from '../components/GlassCard';
import { FloatingOrb } from '../components/FloatingOrb';
import { colors, getMoodColor } from '../theme/colors';
import { AnimatedView } from '../components/AnimatedView';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
  mood_detected?: string;
  mood_intensity?: number;
  crisis_detected?: boolean;
}

const ChatScreen: React.FC = () => {
  const { userId } = useUser();
  const route = useRoute();
  const routeParams = route.params as { journalContext?: string; mood?: string; date?: string } | undefined;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentMood, setCurrentMood] = useState<string>(routeParams?.mood);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);

  // Load chat history on mount
  useEffect(() => {
    if (userId) {
      loadHistory();
      connectWebSocket();
      
      // If journal context provided, send it as initial message
      if (routeParams?.journalContext) {
        setTimeout(() => {
          const contextMessage = `I logged my journal for ${routeParams.date || 'today'}. ${routeParams.journalContext}`;
          setInputText(contextMessage);
          // Auto-send after a brief delay
          setTimeout(() => {
            sendMessageWithText(contextMessage);
          }, 500);
        }, 1000);
      }
    }
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [userId, routeParams]);
  
  const sendMessageWithText = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      text: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ message: text }));
      } else {
        // Fallback to REST API
        const response = await ChatService.sendMessage({
          user_id: userId,
          message: text,
        });
        
        const assistantMessage: Message = {
          role: 'assistant',
          text: response.response,
          timestamp: new Date().toISOString(),
          mood_detected: response.mood_detected,
          mood_intensity: response.mood_intensity,
          crisis_detected: response.crisis_detected,
        };
        
        setMessages((prev) => [...prev, assistantMessage]);
        setCurrentMood(response.mood_detected);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const history = await ChatService.getHistory(userId);
      setMessages(history.history || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const connectWebSocket = () => {
    try {
      const websocket = ChatService.createWebSocket(userId);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setWs(websocket);
      };
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const newMessage: Message = {
            role: 'assistant',
            text: data.response,
            timestamp: new Date().toISOString(),
            mood_detected: data.mood_detected,
            mood_intensity: data.mood_intensity,
            crisis_detected: data.crisis_detected,
          };
          
          setMessages((prev) => [...prev, newMessage]);
          setCurrentMood(data.mood_detected);
          setIsLoading(false);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
          setIsLoading(false);
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsLoading(false);
        // WebSocket will fall back to REST API
      };
      
      websocket.onclose = () => {
        console.log('WebSocket closed');
        setWs(null);
      };
      
      setWs(websocket);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      // Will fall back to REST API
    }
  };

  const sendMessage = async () => {
    await sendMessageWithText(inputText);
  };

  useEffect(() => {
    if (messages.length > 0) {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }
  }, [messages]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}
    >
      <View style={styles.content}>
        {/* Chat messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
        >
          {messages.length === 0 && (
            <View style={styles.emptyState}>
              <FloatingOrb isActive={false} />
              <Text style={styles.emptyText}>
                Start a conversation...{'\n'}I'm here to listen.
              </Text>
            </View>
          )}
          
          {messages.map((msg, index) => (
            <AnimatedView
              key={index}
              from={{ opacity: 0, translateY: 10 }}
              animate={{ opacity: 1, translateY: 0 }}
              transition={{ type: 'timing', duration: 300 }}
              style={[
                styles.messageWrapper,
                msg.role === 'user' ? styles.userMessage : styles.assistantMessage,
              ]}
            >
              <GlassCard style={styles.messageCard}>
                <Text style={styles.messageText}>{msg.text}</Text>
                {msg.crisis_detected && (
                  <View style={styles.crisisBanner}>
                    <Text style={styles.crisisText}>
                      ⚠️ Crisis support available
                    </Text>
                  </View>
                )}
              </GlassCard>
            </AnimatedView>
          ))}
          
          {isLoading && (
            <View style={styles.loadingContainer}>
              <FloatingOrb isActive={true} mood={currentMood} caption="Thinking..." />
            </View>
          )}
        </ScrollView>

        {/* Input area */}
        <View style={styles.inputContainer}>
          <GlassCard style={styles.inputCard}>
            <TextInput
              style={styles.input}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Type a message..."
              placeholderTextColor={colors.textSecondary}
              multiline
              editable={!isLoading}
            />
            <TouchableOpacity
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
              style={[
                styles.sendButton,
                (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
              ]}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </GlassCard>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 100,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 400,
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: 16,
    textAlign: 'center',
    marginTop: 20,
  },
  messageWrapper: {
    marginBottom: 12,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  assistantMessage: {
    alignItems: 'flex-start',
  },
  messageCard: {
    maxWidth: '80%',
    padding: 12,
  },
  messageText: {
    color: colors.text,
    fontSize: 15,
    lineHeight: 22,
  },
  crisisBanner: {
    marginTop: 8,
    padding: 8,
    backgroundColor: colors.crisis + '40',
    borderRadius: 8,
  },
  crisisText: {
    color: colors.crisis,
    fontSize: 12,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  inputContainer: {
    padding: 16,
    paddingBottom: 32,
  },
  inputCard: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 8,
  },
  input: {
    flex: 1,
    color: colors.text,
    fontSize: 15,
    maxHeight: 100,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  sendButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: colors.moodGreen.base,
    borderRadius: 20,
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonText: {
    color: colors.text,
    fontWeight: '500',
  },
});

export default ChatScreen;

