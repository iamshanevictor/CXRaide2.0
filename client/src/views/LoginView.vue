<template>
  <div class="login-container">
    <!-- Left illustration section -->
    <div class="illustration-section">
      <div class="illustration">
        <img src="@/assets/LOGO1.png" alt="CXRaide Logo" class="logo-image" />
      </div>
    </div>

    <!-- Right login form section -->
    <div class="login-form-section">
      <div class="login-card">
        <h1>CXRaide 2.0</h1>
        <p class="subtitle">
          Automatic Chest X-Ray Pattern Annotation and Classification
        </p>

        <div
          class="status-badge"
          :class="
            connectionStatus === 'Connected' ? 'connected' : 'disconnected'
          "
        >
          {{ connectionStatus }}
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">Username</label>
            <div class="input-icon">
              <span class="icon">👤</span>
              <input
                type="text"
                id="username"
                v-model="username"
                placeholder="Enter your username"
                required
                autofocus
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-icon">
              <span class="icon">🔒</span>
              <input
                type="password"
                id="password"
                v-model="password"
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button type="submit" class="login-button" :disabled="isLoading">
            <span v-if="isLoading">Logging in...</span>
            <span v-else>Login</span>
          </button>
        </form>

        <div class="additional-links">
          <a href="#" class="forgot-password">Forgot Password</a>
        </div>

        <div class="connection-info" v-if="debugInfo">
          <p>API URL: {{ apiUrl }}</p>
          <p>Protocol: {{ protocol }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { login, health, apiUrl } from "../utils/api";

export default {
  data() {
    return {
      username: "",
      password: "",
      error: null,
      isLoading: false,
      apiUrl: apiUrl,
      connectionStatus: "Checking...",
      debugInfo: false,
      // Safely access window properties
      protocol:
        typeof window !== "undefined" && window.location
          ? window.location.protocol
          : "http:",
    };
  },
  async created() {
    // Check server health on component creation
    await this.checkServerHealth();
  },
  methods: {
    async checkServerHealth() {
      try {
        const response = await health();
        this.connectionStatus =
          response.data.status === "healthy" ? "Connected" : "Server Error";
        console.log("[Login] Server health check:", response.data);
      } catch (error) {
        this.connectionStatus = "Connection Failed";
        console.error("[Login] Health check failed:", error);
        // Log detailed error information
        console.error("[Login] Error details:", {
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
        console.log("[Login] Attempting login to:", `${this.apiUrl}/login`);
        const response = await login(this.username, this.password);

        console.log("[Login] Login response:", response.data);
        if (response.data.token) {
          // Store the token securely in localStorage
          localStorage.setItem("authToken", response.data.token);
          console.log("[Login] Login successful, redirecting to home page");

          // Force a page reload to clear any stale state
          setTimeout(() => {
            this.$router.push("/home");
          }, 500);
        } else {
          console.error("[Login] No token received in response");
          throw new Error("No token received from server");
        }
      } catch (error) {
        console.error("[Login] Detailed login error:", {
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
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");

.login-container {
  display: flex;
  min-height: 100vh;
  font-family: "Montserrat", sans-serif;
}

/* Left section with illustration */
.illustration-section {
  flex: 1;
  background-color: #090c14;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.illustration-section::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at center,
    rgba(93, 175, 255, 0.05) 0%,
    rgba(13, 20, 37, 0) 70%
  );
  z-index: 0;
}

.illustration {
  max-width: 600px;
  width: 100%;
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.illustration img {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 15px rgba(93, 175, 255, 0.4));
}

.logo-image {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 0 8px rgba(93, 175, 255, 0.3));
  object-fit: contain;
  max-height: 300px;
  width: auto;
  margin: 0 auto;
}

/* Right section with login form */
.login-form-section {
  flex: 1;
  background: linear-gradient(135deg, #090c14 0%, #10172a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.login-form-section::after {
  content: "";
  position: absolute;
  bottom: 0;
  right: 0;
  width: 150px;
  height: 150px;
  background-color: rgba(93, 175, 255, 0.1);
  border-radius: 100% 0 0 0;
  z-index: 0;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(13, 20, 37, 0.8);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 0 20px rgba(93, 175, 255, 0.2), 0 0 40px rgba(69, 131, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(93, 175, 255, 0.1);
  position: relative;
  overflow: hidden;
  color: white;
}

.login-card::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at center,
    rgba(93, 175, 255, 0.05) 0%,
    rgba(13, 20, 37, 0) 70%
  );
  z-index: -1;
}

h1 {
  color: #ffffff;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 5px;
  text-shadow: 0 0 5px rgba(93, 175, 255, 0.3);
  letter-spacing: 1px;
  display: block;
}

.subtitle {
  font-size: 14px;
  color: #64a5ff;
  font-weight: 400;
  display: block;
  margin-bottom: 30px;
  text-shadow: none;
}

.status-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.connected {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 5px rgba(16, 185, 129, 0.2);
}

.disconnected {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 5px rgba(239, 68, 68, 0.2);
}

.login-form {
  margin-top: 30px;
}

.form-group {
  margin-bottom: 25px;
}

label {
  display: block;
  color: #a0aec0;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.input-icon {
  position: relative;
  width: 100%;
}

.icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #4b5563;
}

input {
  width: 100%;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(93, 175, 255, 0.2);
  border-radius: 8px;
  padding: 14px 16px 14px 45px;
  color: #ffffff;
  font-family: "Montserrat", sans-serif;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
}

input:focus {
  border-color: rgba(93, 175, 255, 0.6);
  box-shadow: 0 0 5px rgba(93, 175, 255, 0.2);
}

input::placeholder {
  color: #4b5563;
}

.error-message {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.login-button {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "Montserrat", sans-serif;
  letter-spacing: 0.5px;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: all 0.5s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.login-button:hover::before {
  left: 100%;
}

.login-button:disabled {
  background: linear-gradient(135deg, #64748b 0%, #334155 100%);
  cursor: not-allowed;
  box-shadow: none;
}

.additional-links {
  margin-top: 20px;
  text-align: center;
}

.forgot-password {
  color: #64a5ff;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.forgot-password:hover {
  color: #3b82f6;
  text-shadow: none;
}

.connection-info {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(93, 175, 255, 0.1);
  font-size: 12px;
  color: #64748b;
}

.connection-info p {
  margin: 5px 0;
}

/* Media queries for responsive design */
@media (max-width: 992px) {
  .login-container {
    flex-direction: column;
  }

  .illustration-section {
    display: none;
  }

  .login-form-section {
    padding: 30px 20px;
  }

  .login-card {
    padding: 30px 20px;
  }
}
</style>
