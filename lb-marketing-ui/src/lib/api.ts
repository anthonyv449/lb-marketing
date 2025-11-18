/**
 * API utility for making requests to the backend
 * Uses VITE_API_URL environment variable in production, or proxy in development
 */

import { getAuthToken } from './auth';

const getApiUrl = (): string => {
  // In production, use the environment variable
  // In development, use relative paths (Vite proxy handles it)
  const apiUrl = import.meta.env.VITE_API_URL;
  
  if (apiUrl) {
    // Remove trailing slash if present
    let baseUrl = apiUrl.replace(/\/$/, '');
    // Ensure /api is included in the base URL for Azure Functions
    if (!baseUrl.endsWith('/api')) {
      baseUrl = baseUrl.endsWith('/') ? `${baseUrl}api` : `${baseUrl}/api`;
    }
    return baseUrl;
  }
  
  // In development, return empty string to use relative paths (proxy)
  return '';
};

/**
 * Makes a fetch request to the API
 * Automatically handles API URL prefix in production
 * Includes authentication token if available
 */
export const apiFetch = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const apiUrl = getApiUrl();
  const url = apiUrl ? `${apiUrl}${endpoint}` : endpoint;
  
  // Get auth token using auth utility
  const token = getAuthToken();
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add authorization header if token exists
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token.toString()}`;
    // Debug logging (remove in production)
    if (endpoint.includes('/oauth')) {
      console.log('DEBUG: apiFetch - Adding Authorization header for', endpoint);
    }
  } else {
    console.warn('DEBUG: apiFetch - No token found for request to', endpoint);
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  console.log({url, config});
  return fetch(url, config);
};

/**
 * API endpoints
 */
export const api = {
  // Posts
  createPost: (data: any) => apiFetch('/posts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  listPosts: () => apiFetch('/posts'),
  
  getPost: (id: number) => apiFetch(`/posts/${id}`),
  
  publishPost: (id: number) => apiFetch(`/posts/${id}/publish`, {
    method: 'POST',
  }),
  
  publishAllPosts: () => apiFetch('/posts/publish', {
    method: 'POST',
  }),
  
  // OAuth (legacy - kept for backwards compatibility)
  checkXStatus: () => 
    apiFetch('/oauth/x/status'),
  
  authorizeX: async () => {
    // Fetch the authorization URL with authentication
    const token = getAuthToken();
    if (!token) {
      throw new Error('Not authenticated. Please log in first.');
    }
    
    console.log('DEBUG: Attempting to authorize X, token exists:', !!token);
    const response = await apiFetch('/oauth/x/authorize?return_url=true');
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('DEBUG: Authorization failed:', response.status, errorText);
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      throw new Error(`Failed to get authorization URL: ${errorText}`);
    }
    
    const data = await response.json();
    window.location.href = data.authorization_url;
  },
  
  // Get all platform connection statuses
  getAllPlatformStatus: () =>
    apiFetch('/oauth/status'),
  
  // Get status for a specific platform
  getPlatformStatus: (platform: string) =>
    apiFetch(`/oauth/${platform}/status`),
  
  // Authorize a platform
  authorizePlatform: async (platform: string) => {

    // Fetch the authorization URL with authentication
    const response = await apiFetch(`/oauth/${platform}/authorize?return_url=true`);
    if (!response.ok) {
      throw new Error('Failed to get authorization URL');
    }
    const data = await response.json();
    window.location.href = data.authorization_url;
  },
  
  // Disconnect a platform
  disconnectPlatform: (platform: string) =>
    apiFetch(`/oauth/${platform}/disconnect`, {
      method: 'POST',
    }),
  
  // Social Profiles
  listSocialProfiles: () => apiFetch('/social-profiles'),
  
  createSocialProfile: (data: any) => apiFetch('/social-profiles', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // Authentication
  register: (data: { email: string; password: string; full_name?: string }) =>
    apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  login: (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    return apiFetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
  },
  
  getCurrentUser: () => apiFetch('/auth/me'),
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  },
  
  // Admin endpoints
  runMigrations: () => apiFetch('/admin/migrate', {
    method: 'POST',
  }),
};

