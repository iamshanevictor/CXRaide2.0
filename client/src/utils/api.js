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

    // Handle session expiration (401 errors)
    if (error.response?.status === 401 && error.config.url !== "/login") {
      console.log(
        "[API] Session expired or unauthorized. Redirecting to login."
      );
      localStorage.removeItem("authToken");

      // If not already on login page, redirect
      if (window.location.pathname !== "/login") {
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
