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
          <span class="icon"><i class="bi bi-clipboard-data"></i></span>
          {{ showErrorDetails ? "Hide" : "Show" }} Details
        </button>
        <button @click="runDiagnostics" class="btn-secondary">
          <span class="icon"><i class="bi bi-activity"></i></span> Diagnostics
        </button>
        <button @click="retryLoading" class="btn-secondary">
          <span class="icon"><i class="bi bi-arrow-clockwise"></i></span> Retry
          Connection
        </button>
        <button @click="backToLogin" class="btn-primary">
          <span class="icon"><i class="bi bi-box-arrow-left"></i></span> Back to
          Login
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div v-else class="dashboard-wrapper">
      <!-- Header with welcome message -->
      <HeaderBar :username="username">
        <template #title>
          Welcome back, <span class="highlight">{{ username }}</span>!
        </template>
      </HeaderBar>

      <!-- Main dashboard cards -->
      <div class="dashboard-grid">
        <!-- Model Information Card (Updated with more details) -->
        <div class="card primary-card model-info-card">
          <div class="card-header model-header">
            <h2 class="model-title">Model: SSD300_VGG16</h2>
            <div class="model-status-wrapper">
              <div
                class="model-status-badge"
                :class="{
                  'mock-model': modelInfo && modelInfo.using_mock_models,
                  'real-model': !modelInfo || !modelInfo.using_mock_models,
                }"
                v-if="modelInfo"
              >
                {{
                  modelInfo.using_mock_models ? "Mock Model" : "Real Model"
                }}
                <i
                  :class="
                    modelInfo.using_mock_models
                      ? 'bi bi-pc-display'
                      : 'bi bi-cpu-fill'
                  "
                ></i>
              </div>
            </div>
          </div>
          <div class="card-content model-content">
            <!-- Alert message when mock models are used -->
            <div
              class="mock-model-alert"
              v-if="modelInfo && modelInfo.using_mock_models"
            >
              <i class="bi bi-info-circle-fill"></i>
              <span>{{ modelInfo.explanation }}</span>
            </div>

            <!-- Model specs in a grid layout -->
            <div class="model-specs">
              <div class="spec-item">
                <div class="spec-label">Base:</div>
                <div class="spec-value">VGG16 backbone</div>
              </div>

              <div class="spec-item">
                <div class="spec-label">Input Size:</div>
                <div class="spec-value">300x300px</div>
              </div>

              <div class="spec-item">
                <div class="spec-label">Feature Layers:</div>
                <div class="spec-value">
                  conv4_3, conv7, conv8_2, conv9_2, conv10_2, conv11_2
                </div>
              </div>

              <div class="spec-item">
                <div class="spec-label">Training:</div>
                <div class="spec-value">
                  Transfer Learning with Fine-tuning
                </div>
              </div>

              <div class="spec-item">
                <div class="spec-label">Loss Function:</div>
                <div class="spec-value">Focal Loss + Smooth L1 Loss</div>
              </div>
            </div>

            <!-- Workflow section with improved styling - using arrows -->
            <div class="workflow-container">
              <div class="workflow-title">CXRaide 2.0 Workflow</div>
              <div class="workflow-steps">
                <div class="workflow-step">
                  <div class="step-circle step-active">1</div>
                  <div class="step-label">Upload CXR</div>
                </div>

                <div class="workflow-arrow">
                  <i class="bi bi-arrow-right"></i>
                </div>

                <div class="workflow-step">
                  <div class="step-circle">2</div>
                  <div class="step-label">Annotate</div>
                </div>

                <div class="workflow-arrow">
                  <i class="bi bi-arrow-right"></i>
                </div>

                <div class="workflow-step">
                  <div class="step-circle">3</div>
                  <div class="step-label">Generate Report</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- New content grid for the bottom containers -->
      <div class="content-grid">
        <!-- Performance Metrics Container -->
        <div class="performance-metrics-container">
          <div class="card-header">
            <h2>Performance Metrics</h2>
            <div class="iteration-badge">Iteration 3</div>
          </div>
          <div class="card-content">
            <div class="metrics-columns">
              <div class="metrics-column">
                <h3 class="metrics-category">Precision Metrics</h3>
                <div class="metric-row">
                  <div class="metric-name">AP@[IoU=0.50:0.95]:</div>
                  <div class="metric-value">31.02%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">AP@[IoU=0.50]:</div>
                  <div class="metric-value">34.56%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">AP@[IoU=0.75]:</div>
                  <div class="metric-value">33.09%</div>
                </div>
                <h4 class="metrics-subcategory">Precision by Area Size</h4>
                <div class="metric-row">
                  <div class="metric-name">Small:</div>
                  <div class="metric-value">37.91%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">Medium:</div>
                  <div class="metric-value">32.51%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">Large:</div>
                  <div class="metric-value">34.77%</div>
                </div>
              </div>
              <div class="metrics-column">
                <h3 class="metrics-category">Recall Metrics</h3>
                <div class="metric-row">
                  <div class="metric-name">AR@1:</div>
                  <div class="metric-value">88.55%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">AR@10:</div>
                  <div class="metric-value">88.66%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">AR@100:</div>
                  <div class="metric-value">88.66%</div>
                </div>
                <h4 class="metrics-subcategory">Recall by Area Size</h4>
                <div class="metric-row">
                  <div class="metric-name">Small:</div>
                  <div class="metric-value">83.58%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">Medium:</div>
                  <div class="metric-value">90.31%</div>
                </div>
                <div class="metric-row">
                  <div class="metric-name">Large:</div>
                  <div class="metric-value">91.41%</div>
                </div>
              </div>
            </div>
            <div class="metrics-footer">
              <div class="loss-stat">
                <div class="loss-label">Classification Loss:</div>
                <div class="loss-value">1.96</div>
              </div>
              <div class="loss-stat">
                <div class="loss-label">Localization Loss:</div>
                <div class="loss-value">0.0449</div>
              </div>
              <div class="loss-stat">
                <div class="loss-label">Total Loss:</div>
                <div class="loss-value">2.01</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dataset Information Container -->
        <div class="dataset-info-container">
          <div class="card-header">
            <h2>Dataset Information</h2>
            <div class="dataset-source">NIH + VinBig Datasets</div>
          </div>
          <div class="card-content">
            <div class="dataset-metrics">
              <div class="dataset-total">
                <span class="total-number">4,850</span>
                <span class="total-label">Total Images</span>
              </div>
              <div class="dataset-divider"></div>
              <div class="dataset-samples">
                <span class="samples-number">9,613</span>
                <span class="samples-label">Abnormality Samples</span>
              </div>
            </div>

            <div class="distribution-chart">
              <div class="distribution-item">
                <div class="distribution-label">Cardiomegaly</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 100%"></div>
                  <span class="distribution-value">2,405</span>
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">Pleural Thickening</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 82%"></div>
                  <span class="distribution-value">1,981</span>
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">Pulmonary Fibrosis</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 67%"></div>
                  <span class="distribution-value">1,617</span>
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">Pleural Effusion</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 49%"></div>
                  <span class="distribution-value">1,173</span>
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">Nodule/Mass</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 40%"></div>
                  <span class="distribution-value">960</span>
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">Other Classes</div>
                <div class="distribution-bar-container">
                  <div class="distribution-bar" style="width: 30%"></div>
                  <span class="distribution-value">1,477</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- System Status Container -->
        <div class="system-status-container">
          <div class="card-header">
            <h2>System Status</h2>
            <div class="status-timestamp">Last updated: 7:12:19 AM</div>
          </div>
          <div class="card-content">
            <div class="status-items">
              <div class="status-item">
                <div class="status-icon">
                  <i class="bi bi-cpu"></i>
                </div>
                <div class="status-info">
                  <div class="status-label">Model Service</div>
                  <div class="status-active-text">Online</div>
                  <div class="status-subtext">Operational</div>
                </div>
              </div>

              <div class="status-item">
                <div class="status-icon">
                  <i class="bi bi-server"></i>
                </div>
                <div class="status-info">
                  <div class="status-label">Server Load</div>
                  <div class="status-value">42%</div>
                  <div class="status-subtext">Normal range</div>
                </div>
              </div>

              <div class="status-item">
                <div class="status-icon">
                  <i class="bi bi-layers"></i>
                </div>
                <div class="status-info">
                  <div class="status-label">Processing Queue</div>
                  <div class="status-value">3 items</div>
                  <div class="status-subtext">Processing on schedule</div>
                </div>
              </div>

              <div class="status-item">
                <div class="status-icon">
                  <i class="bi bi-clock-history"></i>
                </div>
                <div class="status-info">
                  <div class="status-label">System Uptime</div>
                  <div class="status-value">5d 14h 22m</div>
                  <div class="status-subtext">Since last restart</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loader-overlay">
      <div class="loader"></div>
      <p>Loading dashboard data...</p>
    </div>
  </div>
</template>

<script>
import HeaderBar from '@/components/HeaderBar.vue';
import { apiUrl, logout, checkSession, health } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";
import ModelService from "@/services/modelService";

export default {
  name: "HomeView",
  components: {
    HeaderBar,
  },
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
      showUserMenu: false,
      // Safely access window properties
      protocol:
        typeof window !== "undefined" && window.location
          ? window.location.protocol
          : "http:",
      hostName:
        typeof window !== "undefined" && window.location
          ? window.location.hostname || "Local"
          : "Local",
      modelInfo: null,
      modelServiceActive: true,
      serverLoad: 42,
      processingQueue: 3,
      systemUptime: "5d 14h 22m",
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
  mounted() {
    // Handle server health check
    this.checkServerHealth();

    // Load user info
    const userData = localStorage.getItem("user");
    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        this.username = parsedUser.username || "User";
      } catch (e) {
        console.error("Error parsing user data:", e);
      }
    }

    // Check token
    this.hasToken = !!localStorage.getItem("authToken");

    // Check model status
    this.checkModelStatus();

    // Add click event listener to document to close dropdown when clicking outside
    document.addEventListener("click", this.closeUserMenu);
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    document.removeEventListener("click", this.closeUserMenu);
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
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      console.log("Open user settings");
      this.showUserMenu = false;
    },
    closeUserMenu(e) {
      // Close the menu when clicking outside
      if (this.showUserMenu && !e.target.closest(".user-dropdown")) {
        this.showUserMenu = false;
      }
    },
    async checkModelStatus() {
      try {
        const modelStatus = await ModelService.checkModelStatus();
        this.modelInfo = modelStatus;
        console.log("Model status:", modelStatus);
      } catch (error) {
        console.error("Error checking model status:", error);
      }
    },
    getCurrentTime() {
      const now = new Date();
      return now.toLocaleTimeString();
    },
    getServerLoadClass() {
      if (this.serverLoad < 50) return "status-good";
      if (this.serverLoad < 80) return "status-warning";
      return "status-critical";
    },
    getServerLoadColor() {
      if (this.serverLoad < 50) return "#10b981";
      if (this.serverLoad < 80) return "#f59e0b";
      return "#ef4444";
    },
    getQueueStatusClass() {
      if (this.processingQueue < 5) return "status-good";
      if (this.processingQueue < 15) return "status-warning";
      return "status-critical";
    },
    getQueueStatusText() {
      if (this.processingQueue < 5) return "Processing on schedule";
      if (this.processingQueue < 15) return "Slight delay expected";
      return "Heavy load, delays possible";
    },
  },
};
</script>

<style scoped>
/* Import Bootstrap Icons */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

.home-container {
  width: 100%;
}

.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 0;
}

/* App Layout with Sidebar */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Navigation Styles */
/* Navigation styles moved to NavSidebar.vue component */

/* Dashboard Layout Adjustments */
.dashboard-wrapper {  flex: 1;  padding: 1.5rem;  /* Navigation margin handled in AppLayout now */  width: 100%;}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.welcome-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
}

.highlight {
  background: linear-gradient(120deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Default styling for all icon buttons */
.icon-button {
  border: none;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Dark styling specifically for dark mode and notification buttons */
.dark-mode-toggle,
.notifications {
  background: rgba(13, 31, 65, 0.9);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.dark-mode-toggle:hover,
.notifications:hover {
  background: rgba(23, 41, 75, 0.9);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

/* Blue styling for user avatar */
.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  color: white;
}

.icon-button .icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 200px;
  background: rgba(15, 23, 42, 0.95);
  border-radius: 0.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3), 0 0 5px rgba(59, 130, 246, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  z-index: 100;
  transform-origin: top right;
  animation: dropdown-appear 0.2s ease-out forwards;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.dropdown-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dropdown-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  width: 20px;
}

.dropdown-item:not(:last-child) {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
  margin: 0 1.5rem 2rem;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }

  .model-info-card {
    grid-column: 1 / -1; /* Make it span the full width */
  }
}

.card,
.info-card,
.status-card,
.model-info-card,
.primary-card,
.secondary-card {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.card:hover,
.info-card:hover,
.status-card:hover,
.model-info-card:hover {
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.25);
  transform: translateY(-3px);
}

/* Override specific variations */
.primary-card {
  background: rgba(13, 18, 30, 0.95);
}

.secondary-card {
  background: rgba(13, 18, 30, 0.95);
}

.model-info-card {
  background: rgba(13, 18, 30, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.info-card,
.status-card {
  background: rgba(13, 18, 30, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
  padding-bottom: 1rem;
  margin-bottom: 1.25rem;
}

.model-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #f3f4f6;
  margin: 0;
}

.model-status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 600;
}

.model-status-badge i {
  font-size: 1rem;
}

.real-model {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.mock-model {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.model-specs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.spec-label {
  font-size: 0.85rem;
  color: #94a3b8;
}

.spec-value {
  font-size: 1rem;
  font-weight: 600;
  color: #f3f4f6;
}

/* Workflow section with improved styling - using arrows */
.workflow-container {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(59, 130, 246, 0.15);
}

.workflow-title {
  font-size: 1.1rem;
  color: #e5e7eb;
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.workflow-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem; /* Reduced gap between elements */
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.15);
  border: 2px solid #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 0.75rem;
  position: relative;
  z-index: 2;
}

.step-active {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.step-label {
  font-size: 0.9rem;
  color: #e5e7eb;
  text-align: center;
  max-width: 120px;
}

.workflow-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  font-size: 1.2rem;
  padding: 0 0.25rem; /* Reduced padding */
}

.workflow-arrow i {
  filter: drop-shadow(0 0 3px rgba(59, 130, 246, 0.5));
}

/* Remove the step-connector style that was using lines */
.step-connector {
  display: none; /* Hide the line connectors */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

.card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
}

.primary-card {
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.15),
    rgba(37, 99, 235, 0.1)
  );
}

.secondary-card {
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.15),
    rgba(79, 70, 229, 0.1)
  );
}

.card-content {
  flex-grow: 1;
  overflow: hidden;
}

.progress-ring {
  width: 8rem;
  height: 8rem;
  border-radius: 50%;
  background: conic-gradient(#3b82f6 0% 72%, rgba(59, 130, 246, 0.2) 72% 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.progress-ring::before {
  content: "";
  position: absolute;
  width: 6.5rem;
  height: 6.5rem;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.8);
}

.inner-content {
  position: relative;
  text-align: center;
}

.inner-content h2 {
  font-size: 1.75rem;
  margin: 0;
  background: linear-gradient(120deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.dataset-preview {
  text-align: center;
}

.dataset-preview h2 {
  font-size: 2.5rem;
  margin: 0;
  background: linear-gradient(120deg, #6366f1, #818cf8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.trend-up {
  font-size: 0.875rem;
  color: #34d399;
  margin-top: 1rem;
}

.analyses-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.analysis-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: rgba(15, 23, 42, 0.3);
  transition: all 0.2s ease;
}

.analysis-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.analysis-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  margin-right: 1rem;
  font-size: 1.25rem;
}

.analysis-details {
  flex: 1;
}

.analysis-details h3 {
  font-size: 1rem;
  margin: 0 0 0.25rem 0;
}

.analysis-details p {
  font-size: 0.75rem;
  color: #9ca3af;
  margin: 0;
}

.analysis-status {
  text-align: right;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.badge.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.chart-container {
  height: 15rem;
  position: relative;
}

.chart-placeholder {
  height: 10rem;
  position: relative;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.chart-line {
  position: absolute;
  height: 2px;
  width: 100%;
  left: 0;
  animation: wave 8s infinite ease-in-out;
}

.chart-line.blue {
  background: linear-gradient(
    90deg,
    transparent 0%,
    #3b82f6 50%,
    transparent 100%
  );
  top: 30%;
  animation-delay: 0s;
}

.chart-line.orange {
  background: linear-gradient(
    90deg,
    transparent 0%,
    #f59e0b 50%,
    transparent 100%
  );
  top: 60%;
  animation-delay: 1s;
}

@keyframes wave {
  0%,
  100% {
    transform: translateY(0) scaleX(1.1);
  }
  50% {
    transform: translateY(15px) scaleX(0.9);
  }
}

.chart-legend {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.legend-color.blue {
  background: #3b82f6;
}

.legend-color.orange {
  background: #f59e0b;
}

.legend-value {
  font-weight: 600;
  margin-left: 0.5rem;
}

.trend {
  font-size: 0.75rem;
}

.trend.up {
  color: #34d399;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-button:hover {
  background: rgba(59, 130, 246, 0.15);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.status-label {
  color: #9ca3af;
}

.status-good {
  color: #34d399;
}

.status-error {
  color: #ef4444;
}

.status-neutral {
  color: #9ca3af;
}

.date-selector {
  font-size: 0.875rem;
  color: #9ca3af;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
}

.error-panel {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-panel h2 {
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-details {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.error-trace {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  font-family: monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  word-break: break-all;
  color: #f87171;
}

.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.loader {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* New styles for academic content */
.methodology-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1rem 0;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 80px;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.step-description {
  font-size: 0.8rem;
  color: #e5e7eb;
}

.process-arrow {
  margin: 0 0.5rem;
  color: #60a5fa;
  font-size: 1.5rem;
  font-weight: 300;
}

.system-description {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #9ca3af;
  max-width: 250px;
  margin: 1rem auto 0;
}

.performance-content {
  height: auto;
  padding: 0;
}

.performance-table {
  display: flex;
  flex-direction: column;
  width: 100%;
  border-radius: 0.5rem;
  overflow: hidden;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.metric-row:last-child {
  border-bottom: none;
}

.header-row {
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.highlight-row {
  background: rgba(59, 130, 246, 0.2);
  font-weight: 500;
}

.subheader-row {
  background: rgba(15, 23, 42, 0.5);
  padding: 0.35rem 1rem;
  font-size: 0.8rem;
  color: #9ca3af;
  justify-content: flex-start;
}

.metric-subheader {
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-weight: 600;
}

.metric-header,
.metric-name {
  flex: 1;
  color: #e5e7eb;
}

.metric-header {
  color: #9ca3af;
}

.metric-value {
  font-weight: 600;
  color: #60a5fa;
  font-family: "Roboto Mono", monospace;
}

.size-row .metric-values {
  display: flex;
  gap: 1rem;
}

.size-row .metric-values div {
  color: #9ca3af;
  font-size: 0.8rem;
}

.size-row .metric-values span {
  color: #60a5fa;
  font-weight: 600;
  font-family: "Roboto Mono", monospace;
}

.classifications-grid-compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.classification-item-compact {
  padding: 0.65rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.classification-item-compact:hover {
  background: rgba(59, 130, 246, 0.15);
}

.classification-item-compact .classification-details {
  width: 100%;
}

.classification-item-compact .classification-details h3 {
  font-size: 0.85rem;
  margin: 0 0 0.4rem 0;
  color: #e5e7eb;
}

.auc-bar {
  height: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.auc-progress {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 1rem;
}

.auc-value {
  font-size: 0.7rem;
  color: #9ca3af;
}

.dataset-source {
  font-size: 0.75rem;
  color: #9ca3af;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
}

.dataset-content {
  padding: 1rem 0;
}

.dataset-metrics {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.dataset-total,
.dataset-samples {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.total-number,
.samples-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #60a5fa;
  margin-bottom: 0.5rem;
}

.total-label,
.samples-label {
  font-size: 0.9rem;
  color: #9ca3af;
}

.dataset-divider {
  width: 1px;
  height: 40px;
  background: rgba(59, 130, 246, 0.2);
  margin: 0 2rem;
}

.distribution-chart {
  flex-grow: 1;
  overflow-y: auto;
  margin-top: 1rem;
}

.distribution-item {
  margin-bottom: 0.5rem;
}

.distribution-label {
  min-width: 150px;
  font-size: 0.8rem;
  color: #e5e7eb;
}

.distribution-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.distribution-bar {
  height: 8px;
  background: #60a5fa;
  border-radius: 4px;
}

.distribution-value {
  font-size: 0.75rem;
  color: #9ca3af;
  width: 50px;
  text-align: right;
}

@media (max-width: 1100px) {
  .classifications-grid-compact {
    grid-template-columns: 1fr;
  }
}

/* New styles for model information */
.model-content {
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 0 0.5rem;
}

.model-architecture {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.architecture-item {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}

.architecture-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #94a3b8;
  min-width: 100px;
}

.architecture-value {
  font-size: 0.85rem;
  color: #e5e7eb;
}

.model-description {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #9ca3af;
  max-width: 300px;
  margin: 1rem auto 0;
}

/* Model information updates */
.system-workflow {
  margin-top: 1.25rem;
  width: 100%;
}

.workflow-title {
  font-size: 0.9rem;
  color: #e5e7eb;
  text-align: center;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.workflow-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.35rem;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

.step-label {
  font-size: 0.75rem;
  color: #e5e7eb;
}

.workflow-arrow {
  color: #60a5fa;
  font-size: 1.25rem;
  font-weight: 300;
  display: flex;
  align-items: center;
}

.workflow-arrow i {
  font-size: 1rem;
}

/* Performance metrics styles */
.metrics-content {
  padding: 0.75rem 1rem;
  height: 100%;
}

.metrics-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.metrics-column {
  min-width: 0; /* Prevent overflow */
}

.metrics-category {
  font-size: 0.95rem;
  color: #e5e7eb;
  margin: 0 0 0.75rem 0;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.metrics-subcategory {
  font-size: 0.8rem;
  color: #9ca3af;
  margin: 0.75rem 0 0.5rem 0;
  font-weight: 500;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
  flex-wrap: nowrap;
}

.metric-name {
  font-size: 0.8rem;
  color: #e5e7eb;
  margin-right: 0.5rem;
  white-space: nowrap;
}

.metric-value {
  font-size: 0.8rem;
  color: #60a5fa;
  font-weight: 600;
  font-family: "Roboto Mono", monospace;
  white-space: nowrap;
}

.metrics-footer {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
}

.loss-stat {
  text-align: center;
  padding: 0.5rem;
}

.loss-label {
  font-size: 0.7rem;
  color: #9ca3af;
  margin-bottom: 0.25rem;
  white-space: nowrap;
}

.loss-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #60a5fa;
  font-family: "Roboto Mono", monospace;
}

.iteration-badge {
  font-size: 0.75rem;
  background: rgba(59, 130, 246, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  color: #60a5fa;
  font-weight: 600;
}

/* Classification updates */
.classifications-grid-compact {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
}

@media (min-width: 480px) {
  .classifications-grid-compact {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Adjust responsive layouts */
@media (max-width: 1100px) {
  .metrics-columns {
    grid-template-columns: 1fr;
  }

  .metrics-footer {
    grid-template-columns: 1fr;
  }
}

/* Placeholder styles */
.placeholder-card {
  background: linear-gradient(
    135deg,
    rgba(30, 64, 175, 0.15),
    rgba(17, 24, 39, 0.1)
  );
}

.placeholder-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  padding: 1rem;
}

.placeholder-message {
  text-align: center;
  opacity: 0.8;
}

.placeholder-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.placeholder-message p {
  font-size: 0.9rem;
  color: #e5e7eb;
  margin-bottom: 1rem;
}

.placeholder-list {
  text-align: left;
  padding-left: 1.5rem;
  margin: 0.5rem 0 0 0;
}

.placeholder-list li {
  color: #9ca3af;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.placeholder-card:hover {
  box-shadow: 0 8px 32px rgba(30, 64, 175, 0.2);
  border-color: rgba(30, 64, 175, 0.4);
}

/* Add these styles to your existing CSS */
.model-status-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-status-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.mock-model {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
}

.real-model {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #10b981;
}

.model-status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.mock-model-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff7ed;
  border: 1px solid #fdba74;
  color: #9a3412;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 0.85rem;
}

.mock-model-alert i {
  font-size: 1.1rem;
}

/* New styles for system status indicators */
.system-status-card {
  margin-top: 1.5rem;
}

.status-timestamp {
  font-size: 0.85rem;
  color: #94a3b8;
  opacity: 0.8;
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba(23, 37, 84, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.status-icon i {
  font-size: 1rem;
  color: #60a5fa;
}

.status-active {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-inactive {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.status-neutral {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status-name {
  font-size: 0.9rem;
  color: #94a3b8;
}

.status-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.status-active-text {
  color: #38bdf8;
}

.status-inactive-text {
  color: #f87171;
}

.status-subtext {
  font-size: 0.85rem;
  color: #94a3b8;
}

.status-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  width: 100%;
  margin-top: 0.25rem;
}

.status-bar-fill {
  height: 100%;
  border-radius: 2px;
}

.info-status-container {
  display: flex;
  gap: 1.5rem;
  width: 100%;
  margin-bottom: 1.5rem;
}

.info-card,
.status-card {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
}

.info-card {
  flex: 1.7;
}

.status-card {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 0.75rem;
  padding: 1.25rem;
  border: 1px solid rgba(59, 130, 246, 0.15);
  width: 100%;
  max-width: 280px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.status-card h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f3f4f6;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-timestamp {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 500;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 0;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
}

.status-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba(23, 37, 84, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.status-icon i {
  font-size: 1rem;
  color: #60a5fa;
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 0.15rem;
}

.status-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.status-subtext {
  font-size: 0.7rem;
  color: #94a3b8;
  margin-top: 0.15rem;
}

.model-info-container {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 2rem;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.model-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #f3f4f6;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.model-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  padding: 0.35rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.model-specs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.spec-item {
  display: flex;
  flex-direction: column;
}

.spec-label {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 0.35rem;
}

.spec-value {
  font-size: 1rem;
  font-weight: 600;
  color: #e5e7eb;
}

/* Workflow section */
.workflow-container {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(59, 130, 246, 0.15);
}

.workflow-title {
  font-size: 1.1rem;
  color: #e5e7eb;
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.workflow-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.15);
  border: 2px solid #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 0.75rem;
  position: relative;
  z-index: 2;
}

.step-active {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.step-label {
  font-size: 0.9rem;
  color: #e5e7eb;
  text-align: center;
  max-width: 120px;
}

.step-connector {
  display: none; /* Hide the line connectors */
}

/* Make the layout responsive */
@media (min-width: 1024px) {
  .dashboard-card-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .model-info-container {
    grid-column: span 2;
  }

  .workflow-steps {
    gap: 2rem;
  }
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  width: calc(100% - 3rem);
  margin: 0 1.5rem 2rem;
}

.performance-metrics-container,
.dataset-info-container,
.system-status-container {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 10px rgba(59, 130, 246, 0.1);
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.performance-metrics-container .card-header,
.dataset-info-container .card-header,
.system-status-container .card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(13, 18, 30, 0.8);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.performance-metrics-container .card-content,
.dataset-info-container .card-content,
.system-status-container .card-content {
  padding: 1.5rem;
  flex: 1;
}
</style>
