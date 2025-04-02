import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import axios from "axios";

const app = createApp(App);

app.config.errorHandler = (err) => {
  console.error("Vue error:", err);
};

app.use(router);
app.mount("#app");
