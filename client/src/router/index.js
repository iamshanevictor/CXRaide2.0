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
    component: () => import("../views/HomeView.vue"), // Dynamic import
    meta: { requiresAuth: true },
  },
  {
    path: "/annotate",
    name: "annotate",
    component: () => import("../views/AnnotateView.vue"), // Dynamic import
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"), // Dynamic import
  },
  {
    path: "/upload-cxr",
    name: "upload-cxr",
    component: () => import("../views/UploadCXRView.vue"), // Dynamic import
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

// Track navigation attempts to prevent infinite loops
let navigationAttempts = 0;
const MAX_NAVIGATION_ATTEMPTS = 5;

// Reset navigation counter after a delay
setInterval(() => {
  if (navigationAttempts > 0) {
    console.log("[Router] Resetting navigation attempts counter");
    navigationAttempts = 0;
  }
}, 10000);

// Define a debounce function to prevent rapid navigation
// This function is defined but currently not used - removed or commented to fix ESLint error
/* 
const debounce = (fn, delay) => {
  let timeoutId;
  return function (...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      fn.apply(this, args);
      timeoutId = null;
    }, delay);
  };
};
*/

router.beforeEach(async (to, from) => {
  console.log("[Router] Navigation started to:", to.path, "from:", from.path);

  // Cancel any pending API requests to prevent errors
  modelService.cancelRequests();

  // Increment navigation attempts
  navigationAttempts++;

  // Prevent potential navigation loops
  if (navigationAttempts > MAX_NAVIGATION_ATTEMPTS) {
    console.error(
      "[Router] Too many navigation attempts detected, possible loop"
    );
    navigationAttempts = 0;

    // Force navigation to login and clear any auth state
    localStorage.removeItem("authToken");
    if (to.path !== "/login") {
      return "/login";
    }
    return true;
  }

  // Bypass auth check for login page
  if (to.path === "/login" || to.name === "login") {
    // If user is already logged in and trying to access login page, redirect to home
    const token = localStorage.getItem("authToken");
    if (token) {
      console.log("[Auth] User already has token, redirecting to home");
      return "/home";
    }
    return true;
  }

  const token = localStorage.getItem("authToken");

  // No token - redirect to login
  if (!token) {
    console.log("[Auth] No token found");
    return "/login";
  }

  try {
    // Use the API utility for session checking
    console.log("[Auth] Checking session validity");
    const response = await checkSession();

    if (response && response.data && response.data.valid) {
      console.log(
        "[Auth] Session is valid, user:",
        response.data.user?.username
      );
      // Successful navigation decreases the counter
      navigationAttempts = Math.max(0, navigationAttempts - 1);
      return true;
    } else {
      console.log("[Auth] Session is invalid");
      localStorage.removeItem("authToken");
      return "/login";
    }
  } catch (error) {
    console.error("[Auth] Session check failed:", error);

    // Only clear token if it's an authentication error (401)
    // For network errors, we'll still allow navigation to proceed
    if (error.response && error.response.status === 401) {
      console.log("[Auth] Unauthorized, clearing token");
      localStorage.removeItem("authToken");
      return "/login";
    }

    if (error.code === "ERR_NETWORK") {
      console.warn(
        "[Auth] Network error during session check - allowing navigation"
      );

      // For pages that require auth, let the page component handle the error display
      // This prevents a redirect loop when the API is unreachable
      if (to.meta.requiresAuth) {
        console.log(
          "[Auth] Page requires auth but API is unreachable - proceeding with caution"
        );
      }

      // Allow navigation to proceed despite network error
      return true;
    }

    // For other errors, clear token and redirect to login
    localStorage.removeItem("authToken");
    return "/login";
  }
});

export default router;
