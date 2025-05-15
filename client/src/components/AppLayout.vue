<template>
  <div class="app-layout">
    <!-- Left Navigation Bar -->
    <div class="nav-sidebar">
      <div class="logo-container">
        <img
          src="@/assets/LOGO1.png"
          alt="CXRaide Logo"
          class="sidebar-logo"
        />
      </div>
      <div class="nav-items">
        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/home' }"
          @click="$router.push('/home')"
        >
          <div class="nav-icon"><i class="bi bi-clipboard2-pulse"></i></div>
          <div class="nav-label">Dashboard</div>
        </div>
        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/upload-cxr' }"
          @click="$router.push('/upload-cxr')"
        >
          <div class="nav-icon"><i class="bi bi-cloud-upload"></i></div>
          <div class="nav-label">Upload CXR</div>
        </div>
        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/annotate' }"
          @click="$router.push('/annotate')"
        >
          <div class="nav-icon"><i class="bi bi-pen"></i></div>
          <div class="nav-label">Annotate</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-file-earmark-text"></i></div>
          <div class="nav-label">Reports</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-database"></i></div>
          <div class="nav-label">Datasets</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-gear"></i></div>
          <div class="nav-label">Settings</div>
        </div>
      </div>
      <div class="nav-footer">
        <div class="nav-item" @click="logout">
          <div class="nav-icon"><i class="bi bi-box-arrow-right"></i></div>
          <div class="nav-label">Logout</div>
        </div>
      </div>
    </div>

    <!-- Main content area with dynamic header -->
    <div class="content-wrapper">
      <!-- Header with dynamic content based on route -->
      <div class="app-header">
        <h1>
          <span v-if="$route.path === '/home'">
            Welcome back, <span class="highlight">{{ username }}</span>!
          </span>
          <span v-else-if="$route.path === '/annotate'">
            Annotation : <span class="highlight">Edited by Radiologist | Annotated by AI</span>
          </span>
          <span v-else-if="$route.path === '/upload-cxr'">
            Upload Chest X-Ray
          </span>
          <span v-else>
            {{ pageTitle }}
          </span>
        </h1>

        <div class="header-actions">
          <button class="icon-button dark-mode-toggle">
            <span class="icon"><i class="bi bi-moon"></i></span>
          </button>
          <button class="icon-button notifications">
            <span class="icon"><i class="bi bi-bell"></i></span>
          </button>
          <div class="user-dropdown">
            <div class="user-avatar" @click="toggleUserMenu">
              {{ username.charAt(0) }}
            </div>
            <div class="dropdown-menu" v-show="showUserMenu">
              <div class="dropdown-item" @click="openUserSettings">
                <span class="dropdown-icon"><i class="bi bi-person-gear"></i></span>
                <span>User Settings</span>
              </div>
              <div class="dropdown-item" @click="logout">
                <span class="dropdown-icon"><i class="bi bi-box-arrow-right"></i></span>
                <span>Logout</span>
              </div>
            </div>
          </div>
        </div>
      </div>

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

      <!-- Main content slot for page-specific content -->
      <div v-else class="page-content">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import { apiUrl, logout } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";

export default {
  props: {
    pageTitle: {
      type: String,
      default: "CXRaide 2.0"
    }
  },
  data() {
    return {
      apiUrl: apiUrl,
      username: sessionStorage.getItem("username") || localStorage.getItem("username") || "User",
      showUserMenu: false,
      hasError: false,
      errorMessage: "",
      errorDetails: null,
      retryCount: 0,
      showErrorDetails: false,
      connectionStatus: "Connected",
      hasToken: false
    };
  },
  created() {
    try {
      this.hasToken = !!localStorage.getItem("authToken");

      // Extract username from token if available
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const payload = token.split(".")[1];
          const decodedData = JSON.parse(atob(payload));
          this.username = decodedData.username || "User";
          // Store username in sessionStorage for persistence
          sessionStorage.setItem("username", this.username);
        } catch (e) {
          console.error("Error parsing token:", e);
        }
      }
    } catch (e) {
      console.error("Error accessing localStorage:", e);
      this.hasToken = false;
    }

    // Add click listener to close dropdown when clicking outside
    document.addEventListener("click", this.closeUserMenu);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);
  },
  methods: {
    async logout() {
      try {
        await logout();
        this.backToLogin();
      } catch (error) {
        console.error("Logout error:", error);
        this.backToLogin();
      }
    },
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      console.log("User settings clicked (not implemented yet)");
      this.showUserMenu = false;
      alert("User settings feature coming soon!");
    },
    closeUserMenu(e) {
      if (this.showUserMenu && !e.target.closest(".user-dropdown")) {
        this.showUserMenu = false;
      }
    },
    runDiagnostics() {
      runNetworkTest();
      console.log("Network diagnostics completed");
    },
    retryLoading() {
      this.retryCount++;
      this.errorMessage = `Retrying connection (attempt ${this.retryCount})...`;
      console.log(`Retrying page load (attempt ${this.retryCount})`);
      this.$emit('retry-loading');
    },
    backToLogin() {
      try {
        localStorage.removeItem("authToken");
      } catch (e) {
        console.error("Error removing token:", e);
      }
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
/* Logo and sidebar styles */
.app-layout {
  display: flex;
  min-height: 100vh;
}

.content-wrapper {
  flex: 1;
  padding: 1.5rem;
  margin-left: 240px;
  width: calc(100% - 240px);
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.highlight {
  color: #e5e7eb;
  font-weight: 400;
}

.page-content {
  width: 100%;
}

/* Sidebar Navigation Styles */
.nav-sidebar {
  width: 240px;
  background: rgba(15, 23, 42, 0.8);
  border-right: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 40px;
  padding: 25px 0;
}

.sidebar-logo {
  width: 180px;
  height: auto;
  filter: drop-shadow(0 0 8px rgba(93, 175, 255, 0.4));
}

.nav-items {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.9rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

.nav-icon {
  margin-right: 1rem;
  font-size: 1.1rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

.nav-icon i {
  font-size: 1.2rem;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #e5e7eb;
}

.nav-footer {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
}

/* Header action styles */
.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.icon-button {
  background: rgba(15, 23, 42, 0.5);
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

.icon-button:hover {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.icon-button .icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-dropdown {
  position: relative;
}

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

/* Error panel styles */
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

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-secondary, .btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #e5e7eb;
}

.btn-secondary:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.5);
}

.btn-primary {
  background: linear-gradient(to right, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}

.btn-primary:hover {
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}
</style> 