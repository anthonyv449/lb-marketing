/**
 * API utility for making requests to the backend
 * Uses VITE_API_URL environment variable in production, or proxy in development
 */

import { getAuthToken } from "./auth";

const getApiUrl = (): string => {
  // In production, use the environment variable
  // In development, use relative paths (Vite proxy handles it)
  const apiUrl = import.meta.env.VITE_API_URL;

  if (apiUrl) {
    // Remove trailing slash if present
    let baseUrl = apiUrl.replace(/\/$/, "");
    // Ensure /api is included in the base URL for Azure Functions
    if (!baseUrl.endsWith("/api")) {
      baseUrl = baseUrl.endsWith("/") ? `${baseUrl}api` : `${baseUrl}/api`;
    }
    return baseUrl;
  }

  // In development, return empty string to use relative paths (proxy)
  return "";
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

  const defaultHeaders: HeadersInit = {};

  // Set default Content-Type to application/json only if not already specified
  // This allows callers to override it (e.g., for PDF downloads)
  if (!options.headers || !("Content-Type" in options.headers)) {
    defaultHeaders["Content-Type"] = "application/json";
  }

  // Add authorization header if token exists
  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token.toString()}`;
  } else {
    console.warn("DEBUG: apiFetch - No token found for request to", endpoint);
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
  createPost: (data: any) =>
    apiFetch("/posts", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listPosts: () => apiFetch("/posts"),

  getPost: (id: number) => apiFetch(`/posts/${id}`),

  // Media Assets
  uploadMedia: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const apiUrl = getApiUrl();
    const url = apiUrl ? `${apiUrl}/assets/upload` : "/assets/upload";

    const headers: HeadersInit = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token.toString()}`;
    }
    // Don't set Content-Type - browser will set it with boundary for FormData

    return fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });
  },

  publishPost: (id: number) =>
    apiFetch(`/posts/${id}/publish`, {
      method: "POST",
    }),

  publishAllPosts: () =>
    apiFetch("/posts/publish", {
      method: "POST",
    }),

  // OAuth (legacy - kept for backwards compatibility)
  checkXStatus: () => apiFetch("/oauth/x/status"),

  authorizeX: async () => {
    // Fetch the authorization URL with authentication
    const token = getAuthToken();
    if (!token) {
      throw new Error("Not authenticated. Please log in first.");
    }

    const response = await apiFetch("/oauth/x/authorize?return_url=true");

    if (!response.ok) {
      const errorText = await response.text();
      console.error("DEBUG: Authorization failed:", response.status, errorText);
      if (response.status === 401) {
        throw new Error("Authentication failed. Please log in again.");
      }
      throw new Error(`Failed to get authorization URL: ${errorText}`);
    }

    const data = await response.json();
    window.location.href = data.authorization_url;
  },

  // Get all platform connection statuses
  getAllPlatformStatus: () => apiFetch("/oauth/status"),

  // Get status for a specific platform
  getPlatformStatus: (platform: string) =>
    apiFetch(`/oauth/${platform}/status`),

  // Authorize a platform
  authorizePlatform: async (platform: string) => {
    // Fetch the authorization URL with authentication
    const response = await apiFetch(
      `/oauth/${platform}/authorize?return_url=true`
    );
    if (!response.ok) {
      throw new Error("Failed to get authorization URL");
    }
    const data = await response.json();
    window.location.href = data.authorization_url;
  },

  // Disconnect a platform
  disconnectPlatform: (platform: string) =>
    apiFetch(`/oauth/${platform}/disconnect`, {
      method: "POST",
    }),

  // Social Profiles
  listSocialProfiles: () => apiFetch("/social-profiles"),

  createSocialProfile: (data: any) =>
    apiFetch("/social-profiles", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Authentication
  register: (data: { email: string; password: string; full_name?: string }) =>
    apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    return apiFetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });
  },

  getCurrentUser: () => apiFetch("/auth/me"),

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_data");
    }
  },

  // Admin endpoints
  runMigrations: () =>
    apiFetch("/admin/migrate", {
      method: "POST",
    }),

  // PDF downloads
  downloadBusinessPlan: async () => {
    // Using response.blob() handles binary data (equivalent to responseType: 'blob' in axios)
    const response = await apiFetch("/pdfs/download/business", {
      headers: {
        "Content-Type": "application/pdf",
      },
    });
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = "Failed to download PDF";
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    const blob = await response.blob();
    console.log({ blob });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "30-day-plan-boost-engagement-business.pdf";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  downloadAffiliatePlan: async () => {
    // Using response.blob() handles binary data (equivalent to responseType: 'blob' in axios)
    const response = await apiFetch("/pdfs/download/affiliate", {
      headers: {
        Accept: "application/pdf", // Indicate that we expect a PDF response
      },
    });
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = "Failed to download PDF";
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "30-day-plan-boost-engagement-affiliate.pdf";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  // AI Text Generation
  generateText: (prompt: string, tone?: string) =>
    apiFetch("/ai/generate", {
      method: "POST",
      body: JSON.stringify({ text: prompt, tone }),
    }),
};
