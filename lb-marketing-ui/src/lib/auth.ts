/**
 * Authentication utilities for managing user sessions
 */

const TOKEN_KEY = "auth_token";
const USER_KEY = "user_data";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Store authentication token
 */
export const setAuthToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Get authentication token
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Store user data
 */
export const setUser = (user: User): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * Get user data
 */
export const getUser = (): User | null => {
  const userData = localStorage.getItem(USER_KEY);
  if (!userData) return null;
  try {
    return JSON.parse(userData);
  } catch {
    return null;
  }
};

/**
 * Clear authentication data
 */
export const clearAuth = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return getAuthToken() !== null;
};

