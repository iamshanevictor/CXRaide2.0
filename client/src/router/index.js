import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import axios from "axios";

const routes = [
  {
    path: "/",
    redirect: "/home",
  },
  {
    path: "/home",
    name: "home",
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
];

const router = createRouter({
  history: createWebHistory(
    process.env.NODE_ENV === "production" ? "/" : import.meta.env.BASE_URL
  ),
  routes,
});

router.beforeEach(async (to) => {
  console.log(`[Router] Navigating to: ${to.path}`);

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("authToken");
    console.log(`[Auth] Token exists: ${!!token}`);

    if (!token) {
      console.log("[Auth] No token - redirecting to login");
      return "/login";
    }

    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/check-session`,
        { headers: { Authorization: token } }
      );
      console.log("[Auth] Session valid:", response.data.valid);
      return true;
    } catch (error) {
      console.error("[Auth] Session check failed:", error);
      localStorage.removeItem("authToken");
      return "/login";
    }
  }
});

export default router;
