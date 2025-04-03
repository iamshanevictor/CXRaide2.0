<template>
  <div class="login">
    <h1>CXRaide Login</h1>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Username" />
      <input v-model="password" type="password" placeholder="Password" />
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? "Logging in..." : "Login" }}
      </button>
    </form>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
      error: null,
      isLoading: false,
    };
  },
  methods: {
    async handleLogin() {
      this.error = null;
      this.isLoading = true;

      try {
        // Get API URL from environment variables with fallback
        const apiUrl = import.meta.env?.VITE_API_URL || "http://localhost:5000";

        // Configure axios for the request
        const config = {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 10000, // 10 second timeout
        };

        const response = await axios.post(
          `${apiUrl}/login`,
          {
            username: this.username,
            password: this.password,
          },
          config
        );

        if (response.data.token) {
          localStorage.setItem("authToken", response.data.token);
          this.$router.push("/home");
        } else {
          throw new Error("No token received from server");
        }
      } catch (error) {
        if (error.code === "ECONNABORTED") {
          this.error =
            "Connection timed out. Please check your internet connection.";
        } else if (!error.response) {
          this.error = "Network error. Please check your internet connection.";
        } else {
          this.error =
            error.response?.data?.message || error.message || "Login failed";
        }
        console.error("Login error:", error);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px; /* Better for mobile */
}

button {
  padding: 12px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

.error-message {
  color: red;
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
}
</style>
