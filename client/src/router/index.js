import { createRouter, createWebHistory } from "vue-router";
import axios from "axios";

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
const baseUrl = import.meta.env?.VITE_BASE_URL || "/";

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes,
});

router.beforeEach(async (to) => {
  console.log("[Router] Navigation started to:", to.path);

  // Bypass auth check for login page
  if (to.name === "login") return true;

  const token = localStorage.getItem("authToken");

  // No token - redirect to login
  if (!token) {
    console.log("[Auth] No token found");
    return "/login";
  }

  try {
    const apiUrl = import.meta.env?.VITE_API_URL || "http://localhost:5000";
    const response = await axios.get(`${apiUrl}/check-session`, {
      headers: { Authorization: token },
    });
    return response.data.valid ? true : "/login";
  } catch (error) {
    console.error("[Auth] Session check failed:", error);
    localStorage.removeItem("authToken");
    return "/login";
  }
});

export default router;
