import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";

const routes = [
  {
    path: "/",
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
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("authToken");

    if (!token) {
      next("/login");
      return;
    }

    try {
      await axios.get(import.meta.env.VITE_API_URL + "/check-session", {
        headers: { Authorization: token },
      });
      next();
    } catch {
      localStorage.removeItem("authToken");
      next("/login");
    }
  } else {
    next();
  }
});

export default router;
