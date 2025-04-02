import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomeView, meta: { requiresAuth: true } },
    { path: "/login", component: LoginView },
  ],
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("authToken");
    if (token) {
      try {
        await axios.get("http://localhost:5000/check-session", {
          headers: { Authorization: token },
        });
        next();
      } catch {
        next("/login");
      }
    } else {
      next("/login");
    }
  } else {
    next();
  }
});

export default router;
