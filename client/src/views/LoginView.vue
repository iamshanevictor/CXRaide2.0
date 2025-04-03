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
    <div v-if="debugInfo" class="debug-info">
      <p>API URL: {{ apiUrl }}</p>
      <p>Connection Status: {{ connectionStatus }}</p>
      <p>Protocol: {{ protocol }}</p>
    </div>
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
      apiUrl: import.meta.env?.VITE_API_URL || "http://localhost:5000",
      connectionStatus: "Checking...",
      debugInfo: false,
      protocol: window.location.protocol,
    };
  },
  async created() {
    // Check server health on component creation
    await this.checkServerHealth();
  },
  methods: {
    async checkServerHealth() {
      try {
        const response = await axios.get(`${this.apiUrl}/health`, {
          timeout: 5000,
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          withCredentials: true,
        });
        this.connectionStatus =
          response.data.status === "healthy" ? "Connected" : "Server Error";
        console.log("Server health check:", response.data);
      } catch (error) {
        this.connectionStatus = "Connection Failed";
        console.error("Health check failed:", error);
        // Log detailed error information
        console.error("Error details:", {
          message: error.message,
          code: error.code,
          response: error.response?.data,
          status: error.response?.status,
        });
      }
    },
    async handleLogin() {
      this.error = null;
      this.isLoading = true;
      this.debugInfo = true;

      try {
        // Configure axios for the request
        const config = {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          timeout: 10000, // 10 second timeout
          withCredentials: true,
        };

        console.log("Attempting login to:", `${this.apiUrl}/login`);
        const response = await axios.post(
          `${this.apiUrl}/login`,
          {
            username: this.username,
            password: this.password,
          },
          config
        );

        console.log("Login response:", response.data);
        if (response.data.token) {
          localStorage.setItem("authToken", response.data.token);
          this.$router.push("/home");
        } else {
          throw new Error("No token received from server");
        }
      } catch (error) {
        console.error("Detailed login error:", {
          message: error.message,
          code: error.code,
          response: error.response?.data,
          status: error.response?.status,
        });

        if (error.code === "ECONNABORTED") {
          this.error =
            "Connection timed out. Please check your internet connection.";
        } else if (!error.response) {
          this.error = "Network error. Please check your internet connection.";
        } else if (error.response.status === 500) {
          this.error = "Server error. Please try again later.";
        } else if (error.response.status === 401) {
          this.error = "Invalid credentials. Please try again.";
        } else {
          this.error =
            error.response?.data?.message || error.message || "Login failed";
        }
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

.debug-info {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}
</style>
