/**
 * User Context - Global user state
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface UserContextType {
  userId: string;
  userName: string;
  setUserId: (id: string) => void;
  setUserName: (name: string) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize with default userId immediately to prevent empty string issues
  const [userId, setUserIdState] = useState<string>(`user_${Date.now()}`);
  const [userName, setUserNameState] = useState<string>('');

  // Load user from storage on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUserId = await AsyncStorage.getItem('userId');
        const storedUserName = await AsyncStorage.getItem('userName');
        
        if (storedUserId) {
          setUserIdState(storedUserId);
        } else {
          // Generate default user ID
          const newUserId = `user_${Date.now()}`;
          await AsyncStorage.setItem('userId', newUserId);
          setUserIdState(newUserId);
        }
        
        if (storedUserName) {
          setUserNameState(storedUserName);
        }
      } catch (error) {
        console.error('Failed to load user from storage:', error);
        // Keep default userId if storage fails
      }
    };
    
    loadUser();
  }, []);

  const setUserId = async (id: string) => {
    setUserIdState(id);
    await AsyncStorage.setItem('userId', id);
  };

  const setUserName = async (name: string) => {
    setUserNameState(name);
    await AsyncStorage.setItem('userName', name);
  };

  return (
    <UserContext.Provider value={{ userId, userName, setUserId, setUserName }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
};

