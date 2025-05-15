<template>
  <page-layout
    :hasError="hasError"
    :errorMessage="errorMessage"
    :errorDetails="errorDetails"
    v-model:showErrorDetails="showErrorDetails"
    :connectionStatus="connectionStatus"
    :hasToken="hasToken"
    :apiUrl="apiUrl"
    :username="username"
    :isLoading="isLoading"
    :showMockWarning="modelInfo && modelInfo.using_mock_models"
    currentRoute="home"
    @logout="logout"
    @retry="retryLoading"
    @run-diagnostics="runDiagnostics"
    @back-to-login="backToLogin"
  >
    <template #header-title>
      Welcome back, <span class="highlight">{{ username }}</span>!
    </template>

    <!-- Main dashboard content -->
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
  </page-layout>
</template>

<script>
import { apiUrl, logout, checkSession, health } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";
import ModelService from "@/services/modelService";
import PageLayout from "@/components/PageLayout.vue";

export default {
  components: {
    PageLayout
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
    // Always emit start/end loading events to parent for SPA loading indication
    this.$emit("loading-start");
    
    // Check for offline mode first
    const token = localStorage.getItem("authToken");
    let isOffline = false;
    
    if (token) {
      try {
        const payload = token.split(".")[1];
        const decoded = JSON.parse(atob(payload));
        isOffline = decoded.offline_mode === true;
        
        if (isOffline) {
          console.log("[Home] Offline mode detected from token");
          this.setupMockData();
          return;
        }
      } catch (e) {
        console.error("[Home] Error checking offline mode:", e);
      }
    }
    
    // If not offline, load user data and dashboard data normally
    this.loadUserData();
    this.loadDashboardData();
  },
  mounted() {
    // Check if we've already set up offline mode in created()
    if (!this.hasError && !this.isLoading) {
      return;
    }
    
    // Handle server health check
    this.checkServerHealth();

    // Check token
    this.hasToken = !!localStorage.getItem("authToken");

    // Check model status
    this.checkModelStatus();
  },
  methods: {
    loadUserData() {
      // Get user info from token
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const payload = token.split(".")[1];
          const decoded = JSON.parse(atob(payload));
          this.username = decoded.username || "User";
          console.log("[Home] User from token:", this.username);
        } catch (e) {
          console.error("[Home] Error parsing token:", e);
          this.username = "User";
        }
      }
    },
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
        
        // Try to use offline mode as fallback
        this.setupMockData();
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
        this.$emit("loading-end");
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
    loadDashboardData() {
      console.log("[Home] Loading dashboard data");
      this.isLoading = true;
      this.hasError = false;
      
      // Check if we're in offline mode
      try {
        const token = localStorage.getItem("authToken");
        if (token) {
          const payload = token.split(".")[1];
          const decoded = JSON.parse(atob(payload));
          if (decoded.offline_mode === true) {
            console.log("[Home] Offline mode detected - using mock data");
            // In offline mode, use mock data
            this.setupMockData();
            return;
          }
        }
      } catch (e) {
        console.error("[Home] Error checking offline mode:", e);
      }
      
      // Online mode - make API calls
      this.checkServerHealth();
    },
    setupMockData() {
      // Setup mock data for offline mode
      console.log("[Home] Setting up mock data");
      this.hasError = false;
      this.connectionStatus = "Offline Mode";
      this.isAuthenticated = true;
      
      // Setup mock model information
      this.modelInfo = {
        using_mock_models: true,
        explanation: "Using offline mock data. Some features are limited.",
        version: "SSD300_VGG16",
        features: ["object_detection", "classification"],
        performance: {
          precision: 0.78,
          recall: 0.83,
          f1: 0.80
        }
      };
      
      // Setup mock system status
      this.serverLoad = 0;
      this.processingQueue = 0;
      this.systemUptime = "Offline";
      
      // Get username from token
      this.loadUserData();
      
      // Complete loading
      this.isLoading = false;
      this.$emit("loading-end");
    },
    fetchStatsAndData() {
      console.log("[Home] Fetching data in online mode");
      this.$emit("loading-start");
      
      // In a real implementation, you would make API calls here
      // For now, let's just set it up with mock data
      this.setupMockData();
    },
  },
};
</script>

<style scoped>
/* Import Bootstrap Icons */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

/* Dashboard specific styling */
.highlight {
  background: linear-gradient(120deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
  margin-bottom: 2rem;
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

/* Content grid for the bottom cards */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  width: 100%;
  margin-top: 2rem;
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

/* Metrics styles */
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
  font-family: monospace;
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
  font-family: monospace;
}

.iteration-badge {
  font-size: 0.75rem;
  background: rgba(59, 130, 246, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  color: #60a5fa;
  font-weight: 600;
}

/* Dataset section styles */
.dataset-source {
  font-size: 0.75rem;
  color: #9ca3af;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
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

/* System status styles */
.status-timestamp {
  font-size: 0.85rem;
  color: #94a3b8;
  opacity: 0.8;
}

.status-items {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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

.status-active-text {
  color: #38bdf8;
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.2;
}

.status-subtext {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.15rem;
}

/* Model status wrapper styles for the badge */
.model-status-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Responsive adjustments */
@media (max-width: 1280px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .system-status-container {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .performance-metrics-container,
  .dataset-info-container,
  .system-status-container {
    grid-column: 1;
  }
  
  .metrics-columns {
    grid-template-columns: 1fr;
  }
}
</style>
