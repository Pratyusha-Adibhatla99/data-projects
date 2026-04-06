/**
 * Authentication Hook
 * Manages user authentication state
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../Services/api';
import type { User, LoginCredentials, RegisterData } from '../Types';

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already logged in (on mount)
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await api.getCurrentUser();
        if (response.success && response.user) {
          setUser(response.user);
        }
      } catch (err) {
        // User not authenticated - this is normal
        console.log('User not authenticated');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setError(null);
    setIsLoading(true);
    
    try {
      const response = await api.login(credentials);
      
      if (response.success && response.user) {
        setUser(response.user);
      } else {
        throw new Error(response.error || 'Login failed');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    setError(null);
    setIsLoading(true);
    
    try {
      const response = await api.register(data);
      
      if (response.success && response.user) {
        setUser(response.user);
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Registration failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await api.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    error,
  };
};