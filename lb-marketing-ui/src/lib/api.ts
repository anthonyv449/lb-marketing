/**
 * API utility for making requests to the backend
 * Uses VITE_API_URL environment variable in production, or proxy in development
 */

const getApiUrl = (): string => {
  // In production, use the environment variable
  // In development, use relative paths (Vite proxy handles it)
  const apiUrl = import.meta.env.VITE_API_URL;
  
  if (apiUrl) {
    // Remove trailing slash if present
    return apiUrl.replace(/\/$/, '');
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
  
  // Get auth token
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add authorization header if token exists
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
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
  
  authorizeX: () => {
    const apiUrl = getApiUrl();
    const url = apiUrl 
      ? `${apiUrl}/oauth/x/authorize`
      : `/oauth/x/authorize`;
    window.location.href = url;
  },
  
  // Get all platform connection statuses
  getAllPlatformStatus: () =>
    apiFetch('/oauth/status'),
  
  // Get status for a specific platform
  getPlatformStatus: (platform: string) =>
    apiFetch(`/oauth/${platform}/status`),
  
  // Authorize a platform
  authorizePlatform: (platform: string) => {
    const apiUrl = getApiUrl();
    const url = apiUrl 
      ? `${apiUrl}/oauth/${platform}/authorize`
      : `/oauth/${platform}/authorize`;
    window.location.href = url;
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
};

