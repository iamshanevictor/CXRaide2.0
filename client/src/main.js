import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import axios from "axios";

const app = createApp(App);

// Configure axios globally
app.config.globalProperties.$axios = axios;

// Error handling
app.config.errorHandler = (err, vm, info) => {
  console.error("Vue error:", err);
  console.error("Component:", vm);
  console.error("Info:", info);
};

// Mount with error boundary
app.use(router).mount("#app");

// Global error catcher
window.onerror = function (message, source, lineno, colno, error) {
  console.error("Global error:", { message, source, lineno, colno, error });
};

