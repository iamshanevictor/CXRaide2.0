<template>
  <div id="app">
    <!-- Offline mode notification -->
    <div v-if="isOfflineMode" class="offline-notification">
      <i class="bi bi-wifi-off"></i>
      <span>Offline Mode - Limited Functionality</span>
    </div>
    
    <!-- Top navigation progress bar (visible only during navigation) -->
    <div v-if="isNavigating" class="navigation-progress"></div>
    
    <transition name="fade" mode="out-in">
      <router-view
        v-if="!errorOccurred"
        @loading-start="startContentLoading"
        @loading-end="stopContentLoading"
      />
      <div v-else class="error-screen">
        <div class="error-container">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>
          <h2>Application Error</h2>
          <p>We encountered an unexpected issue. Please try again.</p>
          <button @click="reloadApp" class="reload-button">
            <i class="bi bi-arrow-clockwise"></i> Reload Application
          </button>
        </div>
      </div>
    </transition>
    
    <!-- Content loading overlay (visible only when specific content is loading) -->
    <div v-if="isContentLoading" class="content-loading-overlay">
      <div class="spinner">
        <i class="bi bi-arrow-repeat"></i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      errorOccurred: false,
      isNavigating: false, // For navigation between pages
      isContentLoading: false, // For loading content within pages
      navigationTimeout: null,
      contentLoadingTimeout: null,
      isOfflineMode: false,
    };
  },
  created() {
    // Check if we're in offline mode
    this.checkOfflineMode();
    
    // Setup interval to check offline mode every minute
    setInterval(this.checkOfflineMode, 60000);
    
    // Setup global navigation guards with subtle indicators
    this.$router.beforeEach(() => {
      // Show navigation progress bar
      this.startNavigation();
    });
    
    this.$router.afterEach(() => {
      this.checkOfflineMode();
      // Hide navigation progress bar after a short delay
      setTimeout(() => {
        this.stopNavigation();
      }, 200);
    });
  },
  errorCaptured(err, vm, info) {
    this.errorOccurred = true;
    console.error("Captured error:", err, "Component:", vm, "Info:", info);
    return false;
  },
  methods: {
    reloadApp() {
      window.location.reload();
    },
    startNavigation() {
      clearTimeout(this.navigationTimeout);
      this.isNavigating = true;
    },
    stopNavigation() {
      this.navigationTimeout = setTimeout(() => {
        this.isNavigating = false;
      }, 200);
    },
    startContentLoading() {
      clearTimeout(this.contentLoadingTimeout);
      // Add a slight delay before showing the loading indicator
      // to prevent flashing for quick operations
      this.contentLoadingTimeout = setTimeout(() => {
        this.isContentLoading = true;
      }, 300);
    },
    stopContentLoading() {
      clearTimeout(this.contentLoadingTimeout);
      this.isContentLoading = false;
    },
    checkOfflineMode() {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          this.isOfflineMode = false;
          return;
        }
        
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        this.isOfflineMode = decoded.offline_mode === true;
      } catch (error) {
        console.error('[App] Error checking offline mode:', error);
        this.isOfflineMode = false;
      }
    }
  },
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: "Montserrat", sans-serif;
  background: linear-gradient(135deg, #090c14 0%, #10172a 100%);
  color: #ffffff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

a {
  color: #64a5ff;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #3b82f6;
  text-decoration: underline;
}

button {
  font-family: "Montserrat", sans-serif;
}

/* Global select element styling */
select {
  appearance: none;
  background-color: rgba(15, 23, 42, 0.95);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>');
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 35px;
  cursor: pointer;
  color: #f3f4f6;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 0.75rem;
  font-size: 1rem;
  width: 100%;
  transition: border-color 0.2s, box-shadow 0.2s;
}

select:hover, select:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.5);
}

select option {
  background-color: rgba(15, 23, 42, 0.95);
  color: #f3f4f6;
  padding: 10px;
}

/* Navigation progress bar - thin line at the top of the page */
.navigation-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 100%;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  z-index: 1030;
  animation: loadingBar 2s infinite ease-in-out;
}

@keyframes loadingBar {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* Content loading overlay - for API calls within pages */
.content-loading-overlay {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1020;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.spinner {
  font-size: 24px;
  color: #3b82f6;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Error screen */
.error-screen {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(9, 12, 20, 0.95);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-container {
  background-color: #1e293b;
  border-radius: 0.75rem;
  padding: 2rem;
  max-width: 90%;
  width: 400px;
  text-align: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.error-icon {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-container h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #f3f4f6;
}

.error-container p {
  font-size: 1rem;
  margin-bottom: 1.5rem;
  color: #cbd5e1;
}

.reload-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.reload-button:hover {
  background-color: #2563eb;
}

.reload-button i {
  font-size: 1.25rem;
}

/* Transition animations for route changes */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Offline notification */
.offline-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #f97316;
  color: white;
  padding: 0.5rem;
  text-align: center;
  z-index: 1010;
  font-size: 0.9rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.offline-notification i {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .offline-notification {
    font-size: 0.8rem;
  }
}
</style>
