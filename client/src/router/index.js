import { createRouter, createWebHistory } from "vue-router";
import { checkSession } from "../utils/api";

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
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"), // Dynamic import
  },
];

// Get the base URL from environment variables or use a default value
const baseUrl =
  window.__ENV__?.VITE_BASE_URL || import.meta.env?.VITE_BASE_URL || "/";

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes,
});

router.beforeEach(async (to, from) => {
  console.log("[Router] Navigation started to:", to.path, "from:", from.path);

  // Bypass auth check for login page
  if (to.name === "login") {
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

    if (response.data.valid) {
      console.log(
        "[Auth] Session is valid, user:",
        response.data.user?.username
      );
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
      // Allow navigation to proceed despite network error
      return true;
    }

    localStorage.removeItem("authToken");
    return "/login";
  }
});

export default router;
