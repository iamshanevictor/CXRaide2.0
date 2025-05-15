import { createRouter, createWebHistory } from "vue-router";
import { checkSession } from "../utils/api";
import modelService from "../services/modelService";

const routes = [
  {
    path: "/",
    redirect: "/login", // Direct initial redirect to login
  },
  {
    path: "/home",
    name: "home",
    component: () => import(/* webpackChunkName: "home" */ "../views/HomeView.vue"), // Dynamic import
    meta: { requiresAuth: true },
  },
  {
    path: "/annotate",
    name: "annotate",
    component: () => import(/* webpackChunkName: "annotate" */ "../views/AnnotateView.vue"), // Dynamic import
    meta: { 
      requiresAuth: true,
      // Add a leave guard to ensure component cleanup
      leaveGuard: true 
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import(/* webpackChunkName: "login" */ "../views/LoginView.vue"), // Dynamic import
  },
  {
    path: "/upload-cxr",
    name: "upload-cxr",
    component: () => import(/* webpackChunkName: "upload" */ "../views/UploadCXRView.vue"), // Dynamic import
    meta: { requiresAuth: true },
  },
  // Add a catch-all 404 route
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

// Get the base URL from environment variables or use a default value
const baseUrl =
  window.__ENV__?.VITE_BASE_URL || import.meta.env?.VITE_BASE_URL || "/";

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes,
});

// Navigation guard to check authentication
router.beforeEach(async (to, from, next) => {
  console.log("[Router] Navigation to:", to.path);
  
  // Cancel any pending API requests
  modelService.cancelRequests();

  // Special handling for leaving AnnotateView page
  if (from.name === 'annotate') {
    console.log("[Router] Leaving Annotation page - cleanup resources");
    // Perform basic cleanup
    const canvasElements = document.querySelectorAll('canvas');
    canvasElements.forEach(canvas => {
      try {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
      } catch (e) {
        console.warn("[Router] Error cleaning canvas:", e.message);
      }
    });
  }

  // Bypass auth check for login page
  if (to.path === "/login") {
    const token = localStorage.getItem("authToken");
    if (token) {
      return next("/home");
    }
    return next();
  }

  const token = localStorage.getItem("authToken");

  // No token - redirect to login
  if (!token) {
    return next("/login");
  }

  // Check if token is an offline token
  if (isOfflineToken(token)) {
    console.log("[Router] Using offline mode");
    return next(); // Allow navigation with offline token
  }

  try {
    const response = await checkSession();
    if (response?.data?.valid) {
      return next();
    } else {
      localStorage.removeItem("authToken");
      return next("/login");
    }
  } catch (error) {
    console.error("[Router] Session check error:", error.message);
    
    // For network errors, create offline token
    if (error.code === "ERR_NETWORK" || error.code === "ECONNABORTED") {
      console.log("[Router] Network error - enabling offline mode");
      
      if (!isOfflineToken(token)) {
        try {
          // Extract username from existing token
          const payload = token.split(".")[1];
          const decoded = JSON.parse(atob(payload));
          const username = decoded.username || decoded.sub || "offline_user";
          
          // Create offline token
          const offlineToken = createOfflineToken(username);
          localStorage.setItem("authToken", offlineToken);
          console.log("[Router] Created offline token for:", username);
        } catch (e) {
          console.error("[Router] Error creating offline token:", e);
        }
      }
      return next();
    }
    
    // For auth errors, redirect to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("authToken");
      return next("/login");
    }
    
    // For other errors, continue navigation
    return next();
  }
});

// Helper functions for offline tokens
function isOfflineToken(token) {
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload));
    return decoded.offline_mode === true;
  } catch (e) {
    return false;
  }
}

function createOfflineToken(username) {
  const header = { alg: "HS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const expiry = now + 86400; // 24 hours
  const payload = {
    sub: username,
    username: username,
    offline_mode: true,
    iat: now,
    exp: expiry
  };

  const encodeBase64 = (obj) => {
    return btoa(JSON.stringify(obj))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  };

  const encodedHeader = encodeBase64(header);
  const encodedPayload = encodeBase64(payload);
  const signature = "OFFLINE"; // Simplified signature for offline mode

  return `${encodedHeader}.${encodedPayload}.${signature}`;
}

export default router;

