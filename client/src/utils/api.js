import axios from "axios";

// Determine the API URL from various sources
export const apiUrl =
  window.__ENV__?.VITE_API_URL ||
  import.meta.env?.VITE_API_URL ||
  "http://localhost:5000";

console.log("[API] Using API URL:", apiUrl);

// Create an axios instance with default configuration
const api = axios.create({
  baseURL: apiUrl,
  timeout: 30000, // Increased timeout for slower connections
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  withCredentials: true,
});

// Track failed requests to prevent redirect loops
let failedRequests = 0;
const MAX_FAILED_REQUESTS = 3;

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      // Add Bearer prefix if not already present
      config.headers.Authorization = token.startsWith("Bearer ")
        ? token
        : `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error("[API] Request error:", error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Reset failed requests counter on successful response
    failedRequests = 0;
    return response;
  },
  (error) => {
    // Track failed requests to prevent redirect loops
    failedRequests++;

    // Handle network errors without redirecting immediately
    if (error.code === "ERR_NETWORK" || error.code === "ECONNABORTED") {
      console.warn("[API] Network error detected:", error.message);
      return Promise.reject(error);
    }

    // Handle session expiration (401 errors)
    if (
      error.response?.status === 401 &&
      error.config.url !== "/login" &&
      failedRequests < MAX_FAILED_REQUESTS
    ) {
      localStorage.removeItem("authToken");
      // If not already on login page, redirect
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// Reset the failed requests counter periodically
setInterval(() => {
  if (failedRequests > 0) {
    console.log("[API] Resetting failed requests counter");
    failedRequests = 0;
  }
}, 30000);

// API endpoints
export const login = (username, password) => {
  console.log("[API] Attempting login for user:", username);
  return api.post("/login", { username, password })
    .catch(error => {
      console.error("[API] Login failed:", error.message);
      throw error;
    });
};

export const checkSession = () => {
  console.log("[API] Checking session validity");
  return api.get("/check-session")
    .catch(error => {
      console.error("[API] Session check failed:", error.message);
      throw error;
    });
};

export const health = () => {
  console.log("[API] Checking API health");
  return api.get("/health")
    .catch(error => {
      console.error("[API] Health check failed:", error.message);
      throw error;
    });
};

export const logout = () => {
  console.log("[API] Logging out user");
  localStorage.removeItem("authToken");
  // Reset the failed requests counter on logout
  failedRequests = 0;

  return api.post("/logout").catch((err) => {
    console.log("[API] Logout API error (ignoring):", err.message);
    return Promise.resolve(); // Don't fail on logout errors
  });
};

// Helper function to manually check token expiration
export const isTokenExpired = () => {
  const token = localStorage.getItem("authToken");
  if (!token) return true;

  try {
    // JWT tokens are in format: header.payload.signature
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload));

    // Check if token is expired
    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  } catch (e) {
    console.error("[API] Error parsing token:", e);
    return true; // Assume expired on error
  }
};

export default api;
