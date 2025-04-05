import axios from "axios";

// Determine the API URL from various sources
export const apiUrl =
  window.__ENV__?.VITE_API_URL ||
  import.meta.env?.VITE_API_URL ||
  "https://cxraide-backend.onrender.com";

console.log("[API] Using API URL:", apiUrl);

// Create an axios instance with default configuration
const api = axios.create({
  baseURL: apiUrl,
  timeout: 15000, // Increased timeout for slower connections
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  withCredentials: true,
});

// Track failed requests to prevent redirect loops
let failedRequests = 0;
const MAX_FAILED_REQUESTS = 3;

// Setup reset timer and store it to clear on component unmount if needed
// Using an IIFE to avoid the eslint no-unused-vars error
(function setupFailedRequestsReset() {
  setTimeout(() => {
    if (failedRequests > 0) {
      console.log("[API] Resetting failed requests counter");
      failedRequests = 0;
    }
  }, 30000); // Reset counter after 30 seconds
})();

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
    console.log(
      `[API] ${config.method?.toUpperCase() || "REQUEST"} ${config.url}`
    );
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

    console.log(
      `[API] Response from ${response.config.url}: Status ${response.status}`
    );
    return response;
  },
  (error) => {
    console.error("API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
    });

    // Track failed requests to prevent redirect loops
    failedRequests++;

    // Handle network errors without redirecting immediately
    if (error.code === "ERR_NETWORK") {
      console.warn("[API] Network error detected");
      return Promise.reject(error);
    }

    // Handle session expiration (401 errors)
    if (
      error.response?.status === 401 &&
      error.config.url !== "/login" &&
      failedRequests < MAX_FAILED_REQUESTS
    ) {
      console.log(
        "[API] Session expired or unauthorized. Redirecting to login."
      );
      localStorage.removeItem("authToken");

      // If not already on login page, redirect
      if (
        window.location.pathname !== "/login" &&
        !window.location.pathname.includes("login")
      ) {
        // Use history API for a smoother experience
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const login = (username, password) => {
  console.log("[API] Attempting login for user:", username);
  return api.post("/login", { username, password });
};

export const checkSession = () => {
  console.log("[API] Checking session validity");
  return api.get("/check-session");
};

export const health = () => {
  console.log("[API] Checking API health");
  return api.get("/health");
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
