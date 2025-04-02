import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import axios from "axios"; // Add missing import

const routes = [
  {
    path: "/",
    redirect: "/home", // Add explicit redirect
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
  history: createWebHistory(import.meta.env.BASE_URL), // Add base URL
  routes,
});

router.beforeEach(async (to, from, next) => {
  // Add route validation
  if (!to.matched.length) {
    next("/login");
    return;
  }

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("authToken");

    if (!token) {
      next({ name: "login" }); // Use named route
      return;
    }

    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/check-session`,
        { headers: { Authorization: token } }
      );

      if (response.status === 200) {
        next();
      } else {
        throw new Error("Invalid session");
      }
    } catch (error) {
      console.error("Session check failed:", error);
      localStorage.removeItem("authToken");
      next({ name: "login" });
    }
  } else {
    next();
  }
});

export default router;
