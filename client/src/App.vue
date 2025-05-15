<template>
  <div id="app">
    <!-- Offline mode notification -->
    <div v-if="isOfflineMode" class="offline-notification">
      <i class="bi bi-wifi-off"></i>
      <span>Offline Mode - Limited Functionality</span>
    </div>
    
    <!-- Top navigation progress bar (visible only during navigation) -->
    <div v-if="isNavigating" class="navigation-progress"></div>
    
    <!-- Login page has its own layout -->
    <template v-if="$route.path === '/login'">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </template>
    
    <!-- All other routes use the app layout -->
    <template v-else>
      <transition name="fade" mode="out-in">
        <div v-if="errorOccurred" class="error-screen">
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
        <router-view 
          v-else 
          :key="$route.fullPath" 
          @loading-start="startContentLoading"
          @loading-end="stopContentLoading"
        />
      </transition>
    </template>
    
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

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
}

::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.6);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* Glow selection */
::selection {
  background: rgba(59, 130, 246, 0.3);
  color: #ffffff;
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
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(9, 12, 20, 0.95);
  z-index: 9999;
}

.error-container {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 12px;
  padding: 2.5rem;
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.2), 0 0 10px rgba(59, 130, 246, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  animation: error-appear 0.3s ease forwards;
}

@keyframes error-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.error-icon {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.error-container h2 {
  color: #ef4444;
  font-size: 1.75rem;
  margin-bottom: 1rem;
}

.error-container p {
  color: #e5e7eb;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.5;
}

.reload-button {
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.reload-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
}

.reload-button i {
  font-size: 1.25rem;
}

/* Offline mode notification */
.offline-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(234, 88, 12, 0.95);
  color: white;
  text-align: center;
  padding: 0.5rem;
  z-index: 9999;
  font-weight: 500;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.offline-notification i {
  font-size: 1.1rem;
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease-in-out, transform 0.15s ease-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
