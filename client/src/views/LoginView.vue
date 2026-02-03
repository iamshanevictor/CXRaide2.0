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
            <div class="input-group">
              <span class="input-icon">
                <i class="bi bi-person"></i>
              </span>
              <input
                type="text"
                id="username"
                v-model="username"
                placeholder="Enter your username"
                class="input-field"
                :disabled="isLoading"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-group">
              <span class="input-icon">
                <i class="bi bi-lock"></i>
              </span>
              <input
                type="password"
                id="password"
                v-model="password"
                placeholder="Enter your password"
                class="input-field"
                :disabled="isLoading"
                required
              />
            </div>
          </div>

          <div class="form-actions">
            <div class="remember-me">
              <input type="checkbox" id="remember" v-model="rememberMe" />
              <label for="remember">Remember me</label>
            </div>
            <a href="#" class="forgot-password">Forgot password?</a>
          </div>

          <div v-if="error" class="error-message">
            <span class="error-icon"
              ><i class="bi bi-exclamation-circle"></i
            ></span>
            <span>{{ error }}</span>
          </div>

          <button type="submit" class="auth-button" :disabled="isLoading">
            <span v-if="isLoading" class="loading-spinner">
              <i class="bi bi-arrow-repeat spin"></i>
            </span>
            <span v-else>
              <span class="button-icon"
                ><i class="bi bi-box-arrow-in-right"></i
              ></span>
              <span>Login</span>
            </span>
          </button>
        </form>

        <div class="connection-info" v-if="debugInfo">
          <p>API URL: {{ apiUrl }}</p>
          <p>Protocol: {{ protocol }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { health, apiUrl } from "../utils/api";
import pkg from "../../package.json";

export default {
  data() {
    return {
      username: "",
      password: "",
      rememberMe: false,
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
      appVersion: pkg.version,
    };
  },
  async created() {
    // Skip health check if Firebase is not configured yet
    const hasFirebase = Boolean(import.meta.env.VITE_FIREBASE_API_KEY);
    if (hasFirebase) {
      await this.checkServerHealth();
    } else {
      this.connectionStatus = "Temp Bypass";
      this.debugInfo = true;
    }
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
        const { firebaseEmailLogin } = await import("../services/firebaseAuth");
        const result = await firebaseEmailLogin(this.username, this.password);
        localStorage.setItem("authToken", `Bearer ${result.idToken}`);
        this.connectionStatus = "Connected";
        this.error = null;
        setTimeout(() => {
          this.$router.push("/home");
          this.isLoading = false;
        }, 300);
      } catch (error) {
        console.error("[Login] Firebase auth error:", error);
        this.error = "Login failed. Check credentials or Firebase config.";
        this.isLoading = false;
      }
    },
    // Helper function to create a mock JWT token
    createMockToken(username) {
      // Create header
      const header = {
        alg: "HS256",
        typ: "JWT"
      };
      
      // Create payload with 24 hour expiration
      const now = Math.floor(Date.now() / 1000);
      const payload = {
        sub: username,
        name: username,
        username: username,
        iat: now,
        exp: now + 86400, // 24 hours from now
        offline_mode: true // Flag to indicate this is a bypass token
      };
      
      // For mock token, we'll use base64 encoding (not actual JWT signing)
      const encodeBase64 = (obj) => {
        return btoa(JSON.stringify(obj))
          .replace(/=/g, '')
          .replace(/\+/g, '-')
          .replace(/\//g, '_');
      };
      
      // Create the token parts
      const headerEncoded = encodeBase64(header);
      const payloadEncoded = encodeBase64(payload);
      const signatureEncoded = encodeBase64({sig: "mock_signature"});
      
      // Combine into a JWT token format
      return `${headerEncoded}.${payloadEncoded}.${signatureEncoded}`;
    },
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

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

.input-group {
  position: relative;
  margin-bottom: 1.5rem;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #60a5fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-field {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  color: #e5e7eb;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.input-field::placeholder {
  color: #6b7280;
}

.input-field:disabled {
  background: rgba(15, 23, 42, 0.3);
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
  font-size: 0.85rem;
}

.forgot-password {
  color: #60a5fa;
  font-size: 0.85rem;
  text-decoration: none;
  transition: all 0.2s ease;
}

.forgot-password:hover {
  color: #3b82f6;
  text-decoration: underline;
}

.auth-button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.button-icon {
  display: flex;
  align-items: center;
  justify-content: center;
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

.auth-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.auth-button:disabled {
  background: linear-gradient(to right, #64748b, #94a3b8);
  cursor: not-allowed;
  box-shadow: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spin {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
