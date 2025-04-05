<template>
  <div class="home-container">
    <!-- Error state display -->
    <div v-if="hasError" class="error-panel">
      <h2>Application Error</h2>
      <p>{{ errorMessage }}</p>
      <div class="error-details" v-if="showErrorDetails">
        <div class="api-info">
          <p><strong>API URL:</strong> {{ apiUrl }}</p>
          <p><strong>Status:</strong> {{ connectionStatus }}</p>
          <p>
            <strong>Auth Token:</strong> {{ hasToken ? "Present" : "Missing" }}
          </p>
        </div>
        <pre v-if="errorDetails" class="error-trace">{{ errorDetails }}</pre>
      </div>
      <div class="error-actions">
        <button
          @click="showErrorDetails = !showErrorDetails"
          class="btn-secondary"
        >
          <span class="icon">📋</span>
          {{ showErrorDetails ? "Hide" : "Show" }} Details
        </button>
        <button @click="runDiagnostics" class="btn-secondary">
          <span class="icon">📊</span> Diagnostics
        </button>
        <button @click="retryLoading" class="btn-secondary">
          <span class="icon">🔄</span> Retry Connection
        </button>
        <button @click="backToLogin" class="btn-primary">
          <span class="icon">↩</span> Back to Login
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div v-else class="glass-panel">
      <header class="main-header">
        <div class="title-section">
          <h1>
            CXRaide <span class="subtitle">Medical Imaging Platform</span>
          </h1>
          <p class="welcome-message">
            Welcome, <span class="username">{{ username }}</span>
          </p>
        </div>
        <div class="actions">
          <button @click="runDiagnostics" class="btn-secondary">
            <span class="icon">📊</span> Diagnostics
          </button>
          <button @click="logout" class="btn-primary">
            <span class="icon">↪</span> Logout
          </button>
        </div>
      </header>

      <div class="dashboard-content">
        <div class="status-card">
          <h2>System Status</h2>
          <div class="status-item">
            <span class="status-label">API Connection:</span>
            <span
              class="status-value"
              :class="
                connectionStatus === 'Connected'
                  ? 'status-good'
                  : 'status-error'
              "
            >
              {{ connectionStatus }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">Authentication:</span>
            <span
              class="status-value"
              :class="isAuthenticated ? 'status-good' : 'status-error'"
            >
              {{ isAuthenticated ? "Active" : "Not Authenticated" }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">Environment:</span>
            <span class="status-value status-neutral">{{ hostName }}</span>
          </div>
        </div>

        <div class="connection-card">
          <h2>API Details</h2>
          <div class="detail-item">
            <span class="detail-label">API URL:</span>
            <span class="detail-value">{{ apiUrl }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Protocol:</span>
            <span class="detail-value">{{ protocol }}</span>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="loader-overlay">
        <div class="loader"></div>
        <p>Loading dashboard data...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiUrl, logout, checkSession, health } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";

export default {
  data() {
    return {
      apiUrl: apiUrl,
      username: "User",
      isLoading: true,
      isAuthenticated: false,
      connectionStatus: "Checking...",
      hasError: true, // Start with error state shown
      errorMessage: "Connecting to the server...",
      errorDetails: null,
      retryCount: 0,
      showErrorDetails: false,
      hasToken: false,
      // Safely access window properties
      protocol:
        typeof window !== "undefined" && window.location
          ? window.location.protocol
          : "http:",
      hostName:
        typeof window !== "undefined" && window.location
          ? window.location.hostname || "Local"
          : "Local",
    };
  },
  created() {
    // Check if token exists - safely access localStorage
    try {
      this.hasToken = !!localStorage.getItem("authToken");
    } catch (e) {
      console.error("[Home] Error accessing localStorage:", e);
      this.hasToken = false;
    }

    // Check server health first
    this.checkServerHealth();
  },
  methods: {
    async checkServerHealth() {
      try {
        // First check if the server is online
        const healthResponse = await health();
        console.log("[Home] Server health check:", healthResponse.data);

        if (healthResponse.data.status === "healthy") {
          this.connectionStatus = "Connected";
          // Now proceed to load main data
          this.loadHomeData();
        } else {
          throw new Error("Server reported unhealthy status");
        }
      } catch (error) {
        console.error("[Home] Health check failed:", error);
        this.handleError(
          error,
          "Unable to connect to the server. Please check your connection."
        );
      }
    },
    async loadHomeData() {
      this.isLoading = true;
      this.hasError = false;
      this.errorMessage = "Loading data...";

      try {
        // Extract username from token if available
        const token = localStorage.getItem("authToken");
        this.hasToken = !!token;

        if (!token) {
          console.warn("[Home] No auth token found, redirecting to login");
          this.backToLogin();
          return;
        }

        try {
          // JWT tokens are in format header.payload.signature
          const payload = token.split(".")[1];
          const decodedData = JSON.parse(atob(payload));
          this.username = decodedData.username || "User";
          console.log("[Home] Authenticated as:", this.username);
        } catch (e) {
          console.error("[Home] Error parsing token:", e);
          this.username = "User";
        }

        // Verify session is active
        const sessionResponse = await checkSession();

        if (sessionResponse.data.valid) {
          this.isAuthenticated = true;
          this.connectionStatus = "Connected";
          console.log("[Home] Session check result:", sessionResponse.data);
        } else {
          throw new Error("Session invalid");
        }
      } catch (error) {
        this.handleError(error);
      } finally {
        this.isLoading = false;
      }
    },
    handleError(error, customMessage = null) {
      console.error("[Home] Error:", error);
      this.connectionStatus = "Error";
      this.isAuthenticated = false;

      // Collect detailed error info for diagnostics
      this.errorDetails = JSON.stringify(
        {
          message: error.message,
          code: error.code,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url,
          time: new Date().toISOString(),
        },
        null,
        2
      );

      // Set error state and message
      this.hasError = true;

      if (customMessage) {
        this.errorMessage = customMessage;
      } else if (error.code === "ERR_NETWORK") {
        this.errorMessage =
          "Network connection error. The server is unreachable.";
      } else if (error.response?.status === 401) {
        this.errorMessage =
          "Your session has expired or is invalid. Please log in again.";
      } else if (error.response?.status === 500) {
        this.errorMessage =
          "The server encountered an internal error. Please try again later.";
      } else {
        this.errorMessage = error.message || "An unexpected error occurred.";
      }
    },
    async logout() {
      try {
        this.isLoading = true;
        await logout();
        this.backToLogin();
      } catch (error) {
        console.error("[Home] Logout error:", error);
        // Even if logout API fails, we should still redirect to login
        this.backToLogin();
      } finally {
        this.isLoading = false;
      }
    },
    runDiagnostics() {
      // Run network diagnostics and log results
      runNetworkTest();
      console.log("[Home] Network diagnostics completed");
    },
    retryLoading() {
      this.retryCount++;
      this.errorMessage = `Retrying connection (attempt ${this.retryCount})...`;
      console.log(`[Home] Retrying page load (attempt ${this.retryCount})`);
      this.checkServerHealth();
    },
    backToLogin() {
      // Always clear token before going back to login
      try {
        localStorage.removeItem("authToken");
      } catch (e) {
        console.error("[Home] Error removing token:", e);
      }
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #090c14 0%, #10172a 100%);
  font-family: "Montserrat", sans-serif;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;
}

.glass-panel {
  width: 100%;
  max-width: 1200px;
  background: rgba(13, 20, 37, 0.8);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 0 20px rgba(93, 175, 255, 0.2), 0 0 40px rgba(69, 131, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(93, 175, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.glass-panel::before {
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

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(93, 175, 255, 0.2);
}

.title-section h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 0 5px rgba(93, 175, 255, 0.3);
}

.subtitle {
  font-size: 16px;
  color: #64a5ff;
  font-weight: 400;
  margin-left: 10px;
}

.welcome-message {
  margin-top: 5px;
  font-size: 16px;
  color: #a0aec0;
}

.username {
  color: #64a5ff;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 15px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Montserrat", sans-serif;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  color: white;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: rgba(30, 41, 59, 0.8);
  color: #e2e8f0;
  box-shadow: 0 0 5px rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(93, 175, 255, 0.2);
}

.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.icon {
  font-size: 16px;
}

.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.status-card,
.connection-card {
  background: rgba(17, 25, 45, 0.6);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(93, 175, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #ffffff;
  position: relative;
  padding-bottom: 10px;
}

h2::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, transparent);
  border-radius: 2px;
}

.status-item,
.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(93, 175, 255, 0.1);
}

.status-item:last-child,
.detail-item:last-child {
  border-bottom: none;
}

.status-label,
.detail-label {
  color: #a0aec0;
  font-size: 14px;
}

.status-value,
.detail-value {
  font-weight: 500;
  font-size: 14px;
}

.status-good {
  color: #10b981;
  display: flex;
  align-items: center;
}

.status-good::before {
  content: "●";
  margin-right: 5px;
  color: #10b981;
}

.status-error {
  color: #ef4444;
  display: flex;
  align-items: center;
}

.status-error::before {
  content: "●";
  margin-right: 5px;
  color: #ef4444;
}

.status-neutral {
  color: #64a5ff;
}

.loader-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(10, 15, 30, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 20px;
  backdrop-filter: blur(5px);
  z-index: 10;
}

.loader {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

.loader-overlay p {
  color: #a0aec0;
  font-size: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .main-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    margin-top: 20px;
  }

  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

/* Error panel styles */
.error-panel {
  width: 100%;
  max-width: 600px;
  background: rgba(13, 20, 37, 0.8);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(239, 68, 68, 0.2);
  text-align: center;
}

.error-panel h2 {
  color: #ef4444;
  font-size: 28px;
  margin-bottom: 15px;
  font-weight: 600;
  text-shadow: 0 0 5px rgba(239, 68, 68, 0.2);
}

.error-panel p {
  color: #d1d5db;
  margin-bottom: 25px;
  line-height: 1.5;
}

.error-details {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  text-align: left;
  font-size: 14px;
}

.api-info p {
  margin: 5px 0;
  color: #94a3b8;
}

.error-trace {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 10px;
  overflow-x: auto;
  color: #94a3b8;
  font-family: monospace;
  font-size: 12px;
  margin: 10px 0;
  max-height: 150px;
  overflow-y: auto;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}
</style>
