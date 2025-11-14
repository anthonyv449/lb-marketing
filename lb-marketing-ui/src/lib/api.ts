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
 */
export const apiFetch = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const apiUrl = getApiUrl();
  const url = apiUrl ? `${apiUrl}${endpoint}` : endpoint;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
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
  
  // OAuth
  checkXStatus: (businessId: number = 1) => 
    apiFetch(`/oauth/x/status?business_id=${businessId}`),
  
  authorizeX: (businessId: number = 1) => {
    const apiUrl = getApiUrl();
    const url = apiUrl 
      ? `${apiUrl}/oauth/x/authorize?business_id=${businessId}`
      : `/oauth/x/authorize?business_id=${businessId}`;
    window.location.href = url;
  },
  
  // Social Profiles
  listSocialProfiles: () => apiFetch('/social-profiles'),
  
  createSocialProfile: (data: any) => apiFetch('/social-profiles', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

