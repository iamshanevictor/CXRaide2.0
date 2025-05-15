import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import axios from "axios";

// Configure axios defaults for better compatibility
axios.defaults.timeout = 30000; // 30 seconds timeout
axios.defaults.headers.common['Accept'] = 'application/json';

// Remove problematic headers that can cause CORS issues
delete axios.defaults.headers.common['X-Requested-With'];

const app = createApp(App);

// Configure axios globally
app.config.globalProperties.$axios = axios;

// Error handling
app.config.errorHandler = (err, vm, info) => {
  console.error("Vue error:", err);
  console.error("Component:", vm);
  console.error("Info:", info);
};

// Mount with router
app.use(router).mount("#app");

// Global error catcher
window.onerror = function (message, source, lineno, colno, error) {
  console.error("Global error:", { message, source, lineno, colno, error });
};

// Enable HMR (Hot Module Replacement) for development
if (module.hot) {
  module.hot.accept();
}
